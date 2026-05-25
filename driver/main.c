#include <linux/module.h>
#include <linux/i2c.h>
#include <linux/kernel.h>
#include <linux/platform_device.h>
#include <linux/err.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/uaccess.h>
#include <linux/gpio.h>
#include <linux/of_gpio.h>
#include <linux/poll.h>
#include <linux/interrupt.h>
#include <linux/string.h>
#include <linux/mutex.h>
#include <linux/workqueue.h>
#include <linux/atomic.h>
#include <linux/power_supply.h>
#include <linux/rtc.h>
#include <linux/suspend.h>
#include <linux/iio/iio.h>
#include <linux/device.h>
#include <linux/sysfs.h>
#include <linux/kobject.h>
#include <linux/pwm.h>
#include <linux/of.h>
#include <linux/of_device.h>

// Include shared header file
#include "main.h"

// Module parameters for specifying I2C bus number when not using device tree
static int i2c_bus = 1;  // Default to I2C bus 1
module_param(i2c_bus, int, S_IRUGO);
MODULE_PARM_DESC(i2c_bus, "I2C bus number to use (default: 1)");

// Global variable definitions (matching extern declarations in header file)
struct fusion_hat_dev *fusion_dev;
struct workqueue_struct *main_wq;

/**
 * fusion_hat_main_work - Main periodic work function
 * @work: Work structure passed to the worker
 * 
 * This function periodically updates battery status and checks for shutdown conditions.
 */
static void fusion_hat_main_work(struct work_struct *work) {
    struct delayed_work *delayed_work = container_of(work, struct delayed_work, work);
    
    // Update battery status
    fusion_hat_update_battery_status(fusion_dev);

    // Check for shutdown requests
    fusion_hat_shutdown_request_work(fusion_dev);
    
    // Reschedule work to run again after MAIN_INTERVAL milliseconds
    schedule_delayed_work(delayed_work, msecs_to_jiffies(MAIN_INTERVAL));
}

// Main periodic work for battery and shutdown checks
static DECLARE_DELAYED_WORK(main_work, fusion_hat_main_work);

/**
 * @brief Show driver version
 * @dev: Device structure
 * @attr: Device attribute
 * @buf: Buffer to store driver version
 * 
 * Returns the number of bytes written to buffer or error code
 */
static ssize_t version_show(struct device *dev, struct device_attribute *attr, char *buf) {
    return sprintf(buf, "%s\n", VERSION);
}

/**
 * @brief Read firmware version
 * @dev: Device structure
 * @attr: Device attribute
 * @buf: Buffer to store firmware version
 * 
 * Returns the number of bytes written to buffer or error code
 */
static ssize_t firmware_version_show(struct device *dev, struct device_attribute *attr, char *buf) {
    int ret = 0;
    uint8_t version_bytes[3];
    struct fusion_hat_dev *fusion_dev = dev_get_drvdata(dev);
    
    mutex_lock(&fusion_dev->lock);
    
    // Read 3 bytes of firmware version data at once using I2C block read
    ret = fusion_hat_i2c_read_block_bytes(fusion_dev->client, CMD_READ_FIRMWARE_VERSION, version_bytes, 3);
    
    mutex_unlock(&fusion_dev->lock);
    
    if (ret < 0) {
        return ret;
    }
    
    // Process and format firmware version number
    return sprintf(buf, "%u.%u.%u\n", 
                  version_bytes[0], 
                  version_bytes[1], 
                  version_bytes[2]);
}

// sysfs attribute definitions
static DEVICE_ATTR_RO(version);
static DEVICE_ATTR_RO(button);
static DEVICE_ATTR_RO(firmware_version);

/**
 * @brief Attribute list for Fusion HAT sysfs interface
 */
static struct attribute *fusion_hat_attrs[] = {
    &dev_attr_version.attr,
    &dev_attr_button.attr,
    &dev_attr_firmware_version.attr,
    NULL,
};

/**
 * @brief Attribute group for Fusion HAT sysfs interface
 */
static struct attribute_group fusion_hat_attr_group = {
    .attrs = fusion_hat_attrs,
};

/**
 * @brief Attribute group array for Fusion HAT sysfs interface
 */
static const struct attribute_group *fusion_hat_attr_groups[] = {
    &fusion_hat_attr_group,
    NULL,
};

/**
 * @brief Device type structure for Fusion HAT
 */
static struct device_type fusion_hat_device_type = {
    .name = FUSION_HAT_NAME,
};

/**
 * @brief I2C driver probe function for Fusion HAT
 * @client: I2C client structure
 * 
 * Initializes the Fusion HAT device and subsystems.
 * Returns 0 on success, negative error code on failure
 */
static int fusion_hat_probe(struct i2c_client *client) {
    int ret;
    
    // Check if I2C adapter supports required functionality
    if (!i2c_check_functionality(client->adapter, I2C_FUNC_I2C)) {
        dev_err(&client->dev, "I2C adapter doesn't support required functionality\n");
        return -ENODEV;
    }
    
    // Allocate device structure
    fusion_dev = devm_kzalloc(&client->dev, sizeof(struct fusion_hat_dev), GFP_KERNEL);
    if (!fusion_dev) {
        return -ENOMEM;
    }
    
    fusion_dev->client = client;
    i2c_set_clientdata(client, fusion_dev);
    
    // Create main workqueue
    main_wq = create_workqueue("fusion-hat-main");
    if (!main_wq) {
        dev_err(&client->dev, "Failed to create main workqueue\n");
        return -ENOMEM;
    }
    
    // Initialize mutex lock
    mutex_init(&fusion_dev->lock);
    
    // Create device class using modern API
    fusion_dev->class = class_create(FUSION_HAT_NAME);
    if (IS_ERR(fusion_dev->class)) {
        ret = PTR_ERR(fusion_dev->class);
        dev_err(&client->dev, "Failed to create class: %d\n", ret);
        return ret;
    }
    
    // Create device under /sys/class/fusion_hat/
    fusion_dev->device = device_create_with_groups(fusion_dev->class, NULL, MKDEV(0, 0), 
                                                 fusion_dev, fusion_hat_attr_groups, 
                                                 FUSION_HAT_NAME);
    if (IS_ERR(fusion_dev->device)) {
        ret = PTR_ERR(fusion_dev->device);
        dev_err(&client->dev, "Failed to create device: %d\n", ret);
        goto error_device;
    }
    
    // Set device type
    fusion_dev->device->type = &fusion_hat_device_type;
    
    // Initialize PWM subsystem
    ret = fusion_hat_pwm_probe(fusion_dev);
    if (ret < 0) {
        dev_err(&client->dev, "Failed to initialize PWM subsystem: %d\n", ret);
        goto error_pwm;
    }
    
    // Initialize button subsystem
    ret = fusion_hat_button_init(fusion_dev);
    if (ret < 0) {
        dev_err(&client->dev, "Failed to initialize button subsystem: %d\n", ret);
        goto error_button;
    }
    
    // Initialize LED subsystem
    ret = fusion_hat_led_init(fusion_dev);
    if (ret < 0) {
        dev_err(&client->dev, "Failed to initialize LED subsystem: %d\n", ret);
        goto error_led;
    }

    // Initialize speaker subsystem
    ret = fusion_hat_speaker_init(fusion_dev);
    if (ret < 0) {
        dev_err(&client->dev, "Failed to initialize speaker subsystem: %d\n", ret);
        goto error_speaker;
    }
    
    // Initialize battery subsystem
    ret = fusion_hat_battery_init(fusion_dev);
    if (ret < 0) {
        dev_err(&client->dev, "Failed to initialize battery subsystem: %d\n", ret);
        goto error_battery;
    }
    
    // Create IIO device using implementation from adc.c
    ret = fusion_hat_adc_probe(fusion_dev);
    if (ret) {
        dev_err(&client->dev, "Failed to create ADC IIO device\n");
        goto error_adc;
    }
    
    // Initialize and schedule periodic battery check work
    schedule_delayed_work(&main_work, msecs_to_jiffies(MAIN_INTERVAL));
    
    dev_info(&client->dev, "Fusion Hat driver probed successfully\n");
    return 0;
    
    error_adc:
        fusion_hat_adc_remove(fusion_dev);
    error_battery:
        fusion_hat_battery_cleanup(fusion_dev);
    error_led:
        fusion_hat_led_cleanup(fusion_dev);
    error_button:
        fusion_hat_button_cleanup(fusion_dev);
    error_speaker:
        fusion_hat_speaker_cleanup(fusion_dev);
    error_pwm:
        fusion_hat_pwm_remove(fusion_dev);
    error_device:
        device_destroy(fusion_dev->class, MKDEV(0, 0));
        class_destroy(fusion_dev->class);
    
    return ret;
}

/**
 * @brief I2C driver remove function for Fusion HAT
 * @client: I2C client structure
 * 
 * Cleans up resources allocated by the Fusion HAT driver
 */
static void fusion_hat_remove(struct i2c_client *client) {
    struct fusion_hat_dev *dev = i2c_get_clientdata(client);
    
    // Cancel periodic work
    cancel_delayed_work_sync(&main_work);
    
    // Clean up workqueue
    if (main_wq) {
        destroy_workqueue(main_wq);
        main_wq = NULL;
    }
    
    // Clean up battery subsystem
    fusion_hat_battery_cleanup(dev);
    
    // Clean up button subsystem
    fusion_hat_button_cleanup(dev);
    
    // Clean up LED subsystem
    fusion_hat_led_cleanup(dev);
    
    // Clean up PWM subsystem
    fusion_hat_pwm_remove(dev);
    
    // Clean up IIO device using implementation from adc.c
    fusion_hat_adc_remove(dev);

    // Clean up device and class
    device_destroy(dev->class, dev->device->devt);
    class_destroy(dev->class);
    
    dev_info(&client->dev, "Fusion Hat driver removed\n");
}

/**
 * @brief I2C device ID table for Fusion HAT
 * 
 * Specifies the device ID and address for matching I2C devices
 */
static const struct i2c_device_id fusion_hat_id[] = {
    { FUSION_HAT_NAME, 0x17 }, // Explicitly specify device address
    {}
};
MODULE_DEVICE_TABLE(i2c, fusion_hat_id);

/**
 * @brief Device tree match table for Fusion HAT
 * 
 * Specifies compatible strings for device tree matching
 */
static const struct of_device_id fusion_hat_of_match[] = {
    { .compatible = "sunfounder,fusion_hat" },
    {}
};
MODULE_DEVICE_TABLE(of, fusion_hat_of_match);

/**
 * @brief I2C driver structure for Fusion HAT
 * 
 * Defines the Fusion HAT I2C driver with probe, remove and matching functions
 */
static struct i2c_driver fusion_hat_driver = {
    .driver = {
        .name = FUSION_HAT_NAME,
        .owner = THIS_MODULE,
        .of_match_table = fusion_hat_of_match,
    },
    .probe = fusion_hat_probe,
    .remove = fusion_hat_remove,
    .id_table = fusion_hat_id,
};

/**
 * @brief Module initialization function for Fusion HAT driver
 * 
 * Registers the I2C driver
 */
static int __init fusion_hat_init(void) {
    return i2c_add_driver(&fusion_hat_driver);
}

/**
 * @brief Module exit function for Fusion HAT driver
 * 
 * Unregisters the I2C driver
 */
static void __exit fusion_hat_exit(void) {
    i2c_del_driver(&fusion_hat_driver);
}

module_init(fusion_hat_init);
module_exit(fusion_hat_exit);

// Module parameter for debugging
// static int debug = 1;  // Debug messages enabled by default
// module_param(debug, int, S_IRUGO);
// MODULE_PARM_DESC(debug, "Enable debug messages (default: 1)");

MODULE_LICENSE("GPL");
MODULE_AUTHOR("SunFounder");
MODULE_DESCRIPTION("Fusion Hat Driver for Raspberry Pi");
MODULE_VERSION(VERSION);

// Module dependency declaration
MODULE_IMPORT_NS(IIO);
