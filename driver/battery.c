#include <linux/module.h>
#include <linux/i2c.h>
#include <linux/kernel.h>
#include <linux/power_supply.h>
#include <linux/workqueue.h>
#include <linux/mutex.h>
#include <linux/device.h>

#include "main.h"

/**
 * fusion_hat_battery_update - Periodic worker function to update battery status
 * @work: Work structure passed to the worker
 * 
 * This function reads battery voltage and charging status from hardware,
 * calculates battery level percentage, updates device state, and notifies
 * the power supply subsystem of changes.
 */
static void fusion_hat_battery_update(struct work_struct *work)
{
    uint16_t battery_adc_value;
    uint8_t charging_status;
    uint32_t battery_voltage_mv;
    int battery_level;
    int ret;
    
    // Read battery voltage from ADC
    ret = fusion_hat_i2c_read_word(fusion_dev->client, CMD_READ_BATTERY_H, &battery_adc_value, false);
    if (ret != 0) {
        dev_err(&fusion_dev->client->dev, "Failed to read battery voltage: %d\n", ret);
        schedule_delayed_work((struct delayed_work *)work, msecs_to_jiffies(1000));
        return;
    }
    
    // Read charging status
    ret = fusion_hat_i2c_read_byte(fusion_dev->client, CMD_READ_CHARGING_STATUS, &charging_status);
    if (ret != 0) {
        dev_err(&fusion_dev->client->dev, "Failed to read charging status: %d\n", ret);
        schedule_delayed_work((struct delayed_work *)work, msecs_to_jiffies(1000));
        return;
    }

    // Calculate battery voltage (mV) with proper scaling
    battery_voltage_mv = (battery_adc_value * ADC_REFERENCE_VOLTAGE) / ADC_MAX_VALUE;
    battery_voltage_mv *= BATTERY_DIVIDER; // Apply voltage divider correction
    fusion_dev->battery_voltage = battery_voltage_mv;

    // Update charging state
    fusion_dev->charging = charging_status ? true : false;
        
    // Calculate battery level percentage using linear approximation
    if (battery_voltage_mv < BATTERY_MIN_VOLTAGE)
        battery_level = 0;
    else if (battery_voltage_mv > BATTERY_MAX_VOLTAGE)
        battery_level = 100;
    else
        battery_level = ((battery_voltage_mv - BATTERY_MIN_VOLTAGE) * 100) / 
                        (BATTERY_MAX_VOLTAGE - BATTERY_MIN_VOLTAGE);
    
    fusion_dev->battery_level = battery_level;
        
    // Notify power supply subsystem of status change
    if (fusion_dev->battery)
        power_supply_changed(fusion_dev->battery);

    // Schedule next battery check (1 second interval)
    schedule_delayed_work((struct delayed_work *)work, msecs_to_jiffies(1000));
}

// Delayed work for periodic battery status updates
static DECLARE_DELAYED_WORK(battery_work, fusion_hat_battery_update);

/**
 * fusion_hat_get_property - Get power supply property values
 * @psy: Power supply object
 * @psp: Property to retrieve
 * @val: Pointer to store property value
 * 
 * Returns: 0 on success, error code on failure
 */
static int fusion_hat_get_property(struct power_supply *psy, enum power_supply_property psp, union power_supply_propval *val)
{
    struct fusion_hat_dev *dev = power_supply_get_drvdata(psy);
    
    switch (psp) {
    case POWER_SUPPLY_PROP_PRESENT:
        val->intval = 1; // Always present in this design
        break;
    case POWER_SUPPLY_PROP_ONLINE:
        val->intval = 1; // Always online in this design
        break;
    case POWER_SUPPLY_PROP_STATUS:
        if (dev->charging)
            val->intval = POWER_SUPPLY_STATUS_CHARGING;
        else if (dev->battery_level >= 98)
            val->intval = POWER_SUPPLY_STATUS_FULL;
        else
            val->intval = POWER_SUPPLY_STATUS_DISCHARGING;
        break;
    case POWER_SUPPLY_PROP_CAPACITY:
        val->intval = dev->battery_level;
        break;
    case POWER_SUPPLY_PROP_VOLTAGE_NOW:
        val->intval = dev->battery_voltage * 1000; // Convert mV to uV
        break;
    case POWER_SUPPLY_PROP_MODEL_NAME:
        val->strval = "Fusion Hat";
        break;
    case POWER_SUPPLY_PROP_MANUFACTURER:
        val->strval = "SunFounder";
        break;
    default:
        return -EINVAL;
    }
    return 0;
}

// List of supported power supply properties
static enum power_supply_property fusion_hat_props[] = {
    POWER_SUPPLY_PROP_PRESENT,
    POWER_SUPPLY_PROP_ONLINE,
    POWER_SUPPLY_PROP_STATUS,
    POWER_SUPPLY_PROP_CAPACITY,
    POWER_SUPPLY_PROP_VOLTAGE_NOW,
    POWER_SUPPLY_PROP_MODEL_NAME,
    POWER_SUPPLY_PROP_MANUFACTURER,
};

/**
 * charging_show - sysfs attribute show function for charging status
 * @dev: Device structure
 * @attr: Device attribute
 * @buf: Buffer to store output
 * 
 * Returns: Number of bytes written to buffer
 */
ssize_t charging_show(struct device *dev, struct device_attribute *attr, char *buf)
{
    int ret;
    uint8_t charging_status;
    struct fusion_hat_dev *fusion_dev = dev_get_drvdata(dev);
    
    mutex_lock(&fusion_dev->lock);
    ret = fusion_hat_i2c_read_byte(fusion_dev->client, CMD_READ_CHARGING_STATUS, &charging_status);
    mutex_unlock(&fusion_dev->lock);
    
    if (ret < 0)
        return ret;
    
    return sprintf(buf, "%u\n", charging_status);
}



/**
 * fusion_hat_battery_init - Initialize battery subsystem
 * @dev: Fusion HAT device structure
 * 
 * Sets up power supply descriptor, registers with Linux power supply subsystem,
 * initializes battery state variables, and starts periodic status monitoring.
 * 
 * Returns: 0 on success, negative error code on failure
 */
int fusion_hat_battery_init(struct fusion_hat_dev *dev)
{
    int ret = 0;
    
    // Configure power supply descriptor
    dev->battery_desc.name = "fusion-hat";
    dev->battery_desc.type = POWER_SUPPLY_TYPE_BATTERY;
    dev->battery_desc.properties = fusion_hat_props;
    dev->battery_desc.num_properties = ARRAY_SIZE(fusion_hat_props);
    dev->battery_desc.get_property = fusion_hat_get_property;
    
    // Register with power supply subsystem
    struct power_supply_config psy_cfg = {};
    psy_cfg.drv_data = dev;
    
    dev->battery = power_supply_register(&dev->client->dev, &dev->battery_desc, &psy_cfg);
    if (IS_ERR(dev->battery)) {
        dev_err(&dev->client->dev, "Failed to register power supply\n");
        return PTR_ERR(dev->battery);
    }
    
    // Initialize battery state variables
    dev->charging = false;
    dev->battery_level = 0;
    dev->battery_voltage = 0;
    
    // Start periodic battery monitoring (1-second interval)
    schedule_delayed_work(&battery_work, msecs_to_jiffies(1000));
    
    return 0;
}

/**
 * fusion_hat_battery_cleanup - Cleanup battery subsystem
 * @dev: Fusion HAT device structure
 * 
 * Cancels periodic work and unregisters from power supply subsystem.
 */
void fusion_hat_battery_cleanup(struct fusion_hat_dev *dev)
{
    // Cancel periodic battery monitoring
    cancel_delayed_work_sync(&battery_work);
    
    // Unregister from power supply subsystem
    if (dev->battery) {
        power_supply_unregister(dev->battery);
        dev->battery = NULL;
    }
}

// Export symbols for use by other modules
EXPORT_SYMBOL(fusion_hat_battery_init);
EXPORT_SYMBOL(fusion_hat_battery_cleanup);
EXPORT_SYMBOL(charging_show);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("SunFounder");
MODULE_DESCRIPTION("Fusion Hat Battery Driver");
MODULE_VERSION("1.0");