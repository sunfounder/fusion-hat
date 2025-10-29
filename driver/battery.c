/**
 * @file battery.c
 * @brief Fusion Hat Battery Driver
 *
 * This module provides battery monitoring and power supply management
 * for the Fusion Hat, including voltage measurement, charge status detection,
 * and integration with the Linux power supply subsystem.
 */

#include <linux/module.h>
#include <linux/i2c.h>
#include <linux/power_supply.h>
#include <linux/mutex.h>

#include "main.h"

/**
 * @brief List of supported power supply properties
 */
static enum power_supply_property fusion_hat_props[] = {
    POWER_SUPPLY_PROP_PRESENT,
    POWER_SUPPLY_PROP_ONLINE,
    POWER_SUPPLY_PROP_STATUS,
    POWER_SUPPLY_PROP_CAPACITY,
    POWER_SUPPLY_PROP_VOLTAGE_NOW,
    POWER_SUPPLY_PROP_VOLTAGE_MAX,
    POWER_SUPPLY_PROP_VOLTAGE_MIN,
    POWER_SUPPLY_PROP_VOLTAGE_MAX_DESIGN,
    POWER_SUPPLY_PROP_VOLTAGE_MIN_DESIGN,
    POWER_SUPPLY_PROP_CHARGE_FULL_DESIGN,
    POWER_SUPPLY_PROP_CHARGE_NOW,
    POWER_SUPPLY_PROP_CHARGE_FULL,
    POWER_SUPPLY_PROP_MODEL_NAME,
    POWER_SUPPLY_PROP_MANUFACTURER,
    POWER_SUPPLY_PROP_TECHNOLOGY,
    POWER_SUPPLY_PROP_SCOPE,
    POWER_SUPPLY_PROP_CAPACITY_LEVEL,
};

/**
 * @brief Update battery status data
 * @param dev Fusion HAT device structure
 */
void fusion_hat_update_battery_status(struct fusion_hat_dev *dev)
{
    uint16_t battery_adc_value;
    uint8_t charging_status;
    uint32_t battery_voltage_mv;
    int battery_level;
    int ret;
    
    mutex_lock(&dev->lock);
    
    ret = fusion_hat_i2c_read_word(dev->client, CMD_READ_BATTERY_H, &battery_adc_value, true);
    if (ret != 0) {
        dev_err(&dev->client->dev, "Failed to read battery voltage: %d\n", ret);
        mutex_unlock(&dev->lock);
        return;
    }
    
    ret = fusion_hat_i2c_read_byte(dev->client, CMD_READ_CHARGING_STATUS, &charging_status);
    if (ret != 0) {
        dev_err(&dev->client->dev, "Failed to read charging status: %d\n", ret);
        mutex_unlock(&dev->lock);
        return;
    }

    battery_voltage_mv = (battery_adc_value * ADC_REFERENCE_VOLTAGE) / ADC_MAX_VALUE;
    battery_voltage_mv *= BATTERY_DIVIDER;

    dev->battery_voltage = battery_voltage_mv;

    dev->charging = charging_status ? true : false;
        
    if (battery_voltage_mv < BATTERY_MIN_VOLTAGE)
        battery_level = 0;
    else if (battery_voltage_mv > BATTERY_MAX_VOLTAGE)
        battery_level = 100;
    else
        battery_level = ((battery_voltage_mv - BATTERY_MIN_VOLTAGE) * 100) / 
                        (BATTERY_MAX_VOLTAGE - BATTERY_MIN_VOLTAGE);
    
    dev->battery_level = battery_level;
    
    mutex_unlock(&dev->lock);
    
    if (fusion_dev->battery)
        power_supply_changed(fusion_dev->battery);
}

/**
 * @brief Get power supply property values
 * @param psy Power supply object
 * @param psp Property to retrieve
 * @param val Pointer to store property value
 * @return 0 on success, error code on failure
 */
static int fusion_hat_get_property(struct power_supply *psy, enum power_supply_property psp, union power_supply_propval *val)
{
    struct fusion_hat_dev *dev = power_supply_get_drvdata(psy);
    
    // Assumed full capacity for charge-related properties (mAh)
    const int BATTERY_FULL_CHARGE_MAH = 2000;
    
    switch (psp) {
    case POWER_SUPPLY_PROP_PRESENT:
        val->intval = 1;
        break;
    case POWER_SUPPLY_PROP_ONLINE:
        val->intval = 1;
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
        val->intval = dev->battery_voltage * 1000; // mV to uV
        break;
    case POWER_SUPPLY_PROP_VOLTAGE_MAX:
        val->intval = BATTERY_MAX_VOLTAGE * 1000; // mV to uV
        break;
    case POWER_SUPPLY_PROP_VOLTAGE_MIN:
        val->intval = BATTERY_MIN_VOLTAGE * 1000; // mV to uV
        break;
    case POWER_SUPPLY_PROP_VOLTAGE_MAX_DESIGN:
        val->intval = BATTERY_MAX_VOLTAGE * 1000; // mV to uV
        break;
    case POWER_SUPPLY_PROP_VOLTAGE_MIN_DESIGN:
        val->intval = BATTERY_MIN_VOLTAGE * 1000; // mV to uV
        break;
    case POWER_SUPPLY_PROP_CHARGE_FULL_DESIGN:
        val->intval = BATTERY_FULL_CHARGE_MAH * 1000; // mAh to uAh
        break;
    case POWER_SUPPLY_PROP_CHARGE_NOW:
        val->intval = (BATTERY_FULL_CHARGE_MAH * dev->battery_level / 100) * 1000; // mAh to uAh
        break;
    case POWER_SUPPLY_PROP_CHARGE_FULL:
        val->intval = BATTERY_FULL_CHARGE_MAH * 1000; // mAh to uAh
        break;
    case POWER_SUPPLY_PROP_MODEL_NAME:
        val->strval = "Fusion Hat";
        break;
    case POWER_SUPPLY_PROP_MANUFACTURER:
        val->strval = "SunFounder";
        break;
    case POWER_SUPPLY_PROP_TECHNOLOGY:
        val->intval = POWER_SUPPLY_TECHNOLOGY_LION;
        break;
    case POWER_SUPPLY_PROP_SCOPE:
        val->intval = POWER_SUPPLY_SCOPE_SYSTEM;
        break;
    case POWER_SUPPLY_PROP_CAPACITY_LEVEL:
        if (dev->battery_level >= 90)
            val->intval = POWER_SUPPLY_CAPACITY_LEVEL_FULL;
        else if (dev->battery_level >= 70)
            val->intval = POWER_SUPPLY_CAPACITY_LEVEL_HIGH;
        else if (dev->battery_level >= 30)
            val->intval = POWER_SUPPLY_CAPACITY_LEVEL_NORMAL;
        else if (dev->battery_level >= 10)
            val->intval = POWER_SUPPLY_CAPACITY_LEVEL_LOW;
        else
            val->intval = POWER_SUPPLY_CAPACITY_LEVEL_CRITICAL;
        break;
    default:
        return -EINVAL;
    }
    return 0;
}

/**
 * @brief Initialize battery subsystem
 * @param dev Fusion HAT device structure
 * @return 0 on success, negative error code on failure
 */
int fusion_hat_battery_init(struct fusion_hat_dev *dev)
{
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
    
    // Initial battery status update
    fusion_hat_update_battery_status(dev);
    
    return 0;
}

/**
 * @brief Cleanup battery subsystem
 * @param dev Fusion HAT device structure
 */
void fusion_hat_battery_cleanup(struct fusion_hat_dev *dev)
{
    if (dev->battery) {
        power_supply_unregister(dev->battery);
        dev->battery = NULL;
    }
}

// Export symbols for use by other modules
EXPORT_SYMBOL(fusion_hat_battery_init);
EXPORT_SYMBOL(fusion_hat_battery_cleanup);
EXPORT_SYMBOL(fusion_hat_update_battery_status);
