/*
 * Fusion HAT LED Driver Module
 * Responsible for LED initialization, control, and state management
 * Using kobject for sysfs interface
 */

#include <linux/module.h>
#include <linux/i2c.h>
#include <linux/device.h>
#include <linux/kernel.h>
#include <linux/uaccess.h>
#include <linux/kobject.h>
#include <linux/sysfs.h>

#include "main.h"

// LED sysfs show function
static ssize_t led_show(struct device *dev, struct device_attribute *attr, char *buf)
{
    struct fusion_hat_dev *fusion_dev = dev_get_drvdata(dev);
    
    if (!fusion_dev) {
        pr_err("Fusion HAT: Invalid device in led_show\n");
        return -EINVAL;
    }
    
    return sprintf(buf, "%u\n", fusion_dev->led_status);
}

// LED sysfs store function
static ssize_t led_store(struct device *dev, struct device_attribute *attr, const char *buf, size_t count)
{
    struct fusion_hat_dev *fusion_dev = dev_get_drvdata(dev);
    unsigned long value;
    int ret;
    
    if (!fusion_dev || !fusion_dev->client) {
        pr_err("Fusion HAT: Invalid device or client in led_store\n");
        return -EINVAL;
    }
    
    /* Parse input value */
    ret = kstrtoul(buf, 10, &value);
    if (ret < 0) {
        dev_err(dev, "Invalid value for LED: %d\n", ret);
        return ret;
    }
    
    /* Check if value is valid (0 or 1) */
    if (value > 1) {
        dev_err(dev, "Invalid LED value, must be 0 or 1\n");
        return -EINVAL;
    }
    
    /* Update LED state */
    mutex_lock(&fusion_dev->lock);
    fusion_dev->led_status = value;
    
    /* Send I2C command to update LED */
    ret = fusion_hat_i2c_write_byte(fusion_dev->client, CMD_CONTROL_LED, fusion_dev->led_status);
    mutex_unlock(&fusion_dev->lock);
    
    if (ret < 0) {
        dev_err(dev, "Failed to update LED state: %d\n", ret);
        return ret;
    }
    
    dev_info(dev, "LED state updated to %u\n", fusion_dev->led_status);
    return count;
}

// Define device attribute for LED with 0666 permissions
static struct device_attribute dev_attr_led = {
    .attr = {.name = "led", .mode = 0666},
    .show = led_show,
    .store = led_store,
};

/**
 * fusion_hat_led_init - Initialize LED subsystem
 * @dev: fusion hat device structure
 * 
 * Function: Turn off LED and create sysfs attribute
 * Return: 0 on success, error code on failure
 */
int fusion_hat_led_init(struct fusion_hat_dev *dev) {
    int ret = 0;
    
    if (!dev || !dev->client || !dev->device) {
        pr_err("Fusion HAT: Invalid device, client or device structure in LED initialization\n");
        return -EINVAL;
    }
    
    /* Initialize LED state to off */
    dev->led_status = 0;
    
    /* Send I2C command to turn off LED */
    ret = fusion_hat_i2c_write_byte(dev->client, CMD_CONTROL_LED, 0);
    if (ret < 0) {
        dev_err(&dev->client->dev, "Failed to initialize LED: %d\n", ret);
        return ret;
    }
    
    /* Create sysfs attribute for LED control */
    ret = device_create_file(dev->device, &dev_attr_led);
    if (ret < 0) {
        dev_err(&dev->client->dev, "Failed to create LED sysfs attribute: %d\n", ret);
        return ret;
    }
    
    dev_info(&dev->client->dev, "LED initialized and turned off\n");
    return 0;
}
EXPORT_SYMBOL(fusion_hat_led_init);

/**
 * fusion_hat_led_cleanup - Clean up LED resources
 * @dev: fusion hat device structure
 * 
 * Function: Ensure LED is turned off and remove sysfs attribute
 */
void fusion_hat_led_cleanup(struct fusion_hat_dev *dev) {
    if (!dev) {
        return;
    }
    
    /* Ensure LED is turned off during cleanup */
    if (dev->client) {
        fusion_hat_i2c_write_byte(dev->client, CMD_CONTROL_LED, 0);
    }
    
    /* Remove sysfs attribute */
    if (dev->device) {
        device_remove_file(dev->device, &dev_attr_led);
    }
    
    if (dev->client) {
        dev_info(&dev->client->dev, "LED resources cleaned up\n");
    } else {
        pr_info("Fusion HAT: LED resources cleaned up\n");
    }
}
EXPORT_SYMBOL(fusion_hat_led_cleanup);
