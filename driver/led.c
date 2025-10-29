/*
 * Fusion HAT LED Driver Module
 * Responsible for LED initialization, control, and state management
 */

#include <linux/module.h>
#include <linux/i2c.h>
#include <linux/device.h>
#include <linux/kernel.h>
#include <linux/uaccess.h>

#include "main.h"

/**
 * fusion_hat_led_init - Initialize LED subsystem
 * @dev: fusion hat device structure
 * 
 * Function: Turn off LED and save state during initialization
 * Return: 0 on success, error code on failure
 */
int fusion_hat_led_init(struct fusion_hat_dev *dev) {
    int ret = 0;
    
    /* Initialize LED state to off */
    dev->led_status = 0;
    
    /* Send I2C command to turn off LED */
    ret = fusion_hat_i2c_write_byte(dev->client, CMD_CONTROL_LED, 0);
    if (ret < 0) {
        dev_err(&dev->client->dev, "Failed to initialize LED: %d\n", ret);
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
 * Function: Ensure LED is turned off when device is removed
 */
void fusion_hat_led_cleanup(struct fusion_hat_dev *dev) {
    /* Ensure LED is turned off during cleanup */
    fusion_hat_i2c_write_byte(dev->client, CMD_CONTROL_LED, 0);
    dev_info(&dev->client->dev, "LED resources cleaned up\n");
}
EXPORT_SYMBOL(fusion_hat_led_cleanup);

/**
 * led_show - Display current LED state
 * @dev: device structure
 * @attr: device attribute
 * @buf: return buffer
 * 
 * Function: Return current LED state value via sysfs interface
 * Return: Number of bytes written to buffer
 */
ssize_t led_show(struct device *dev, struct device_attribute *attr, char *buf) {
    struct i2c_client *client = to_i2c_client(dev);
    struct fusion_hat_dev *fusion_dev = i2c_get_clientdata(client);
    
    /* Return saved LED state value (0=off, 1=on) */
    return sprintf(buf, "%u\n", fusion_dev->led_status);
}
EXPORT_SYMBOL(led_show);

/**
 * led_store - Set LED state
 * @dev: device structure
 * @attr: device attribute
 * @buf: input buffer
 * @count: input data size
 * 
 * Function: Control LED on/off state via sysfs interface and save it
 * Return: Number of bytes processed or error code
 */
ssize_t led_store(struct device *dev, struct device_attribute *attr, const char *buf, size_t count) {
    struct i2c_client *client = to_i2c_client(dev);
    struct fusion_hat_dev *fusion_dev = i2c_get_clientdata(client);
    int ret = 0;
    unsigned long val;
    uint8_t led_value;
    
    /* Parse input value */
    ret = kstrtoul(buf, 10, &val);
    if (ret < 0) {
        dev_err(dev, "Invalid LED value: %s\n", buf);
        return ret;
    }
    
    /* Set LED state (0=off, 1=on) */
    led_value = (val > 0) ? 1 : 0;
    fusion_dev->led_status = led_value;
    
    /* Send I2C command to control LED */
    ret = fusion_hat_i2c_write_byte(client, CMD_CONTROL_LED, led_value);
    if (ret < 0) {
        dev_err(dev, "Failed to control LED: %d\n", ret);
        return ret;
    }
    
    dev_info(dev, "LED set to %s\n", led_value ? "on" : "off");
    return count;
}
EXPORT_SYMBOL(led_store);
