/**
 * @file pwm.c
 * @brief Fusion Hat PWM Driver
 * 
 * This module provides PWM channel control and management for the Fusion Hat
 * device. The interface design is modeled after the Linux kernel PWM subsystem
 * to provide a consistent and familiar API.
 */

#include <linux/module.h>
#include <linux/i2c.h>
#include <linux/device.h>
#include <linux/slab.h>
#include <linux/mutex.h>
#include <linux/err.h>
#include <linux/uaccess.h>
#include <linux/string.h>
#include <linux/kobject.h>
#include "main.h"

// Number of PWM channels
#define FUSION_HAT_PWM_CHANNELS 12

/**
 * @struct fusion_hat_pwm_channel
 * @brief PWM channel subdirectory structure
 * 
 * This structure represents a single PWM channel's sysfs directory and attributes.
 */
struct fusion_hat_pwm_channel {
    struct kobject kobj;            // Channel kobject
    int channel;                    // Channel number
    struct fusion_hat_dev *dev;     // Device pointer
    struct kobj_attribute period_attr;      // Period attribute
    struct kobj_attribute duty_cycle_attr;  // Duty cycle attribute
    struct kobj_attribute enable_attr;      // Enable attribute
    char name[16];                  // Channel name
};

// PWM subdirectory kobject structure
static struct kobject *pwm_kobj;

// PWM channel array
static struct fusion_hat_pwm_channel pwm_channels[FUSION_HAT_PWM_CHANNELS];

/*
 * Get timer index
 * @channel: PWM channel number
 * @return: Corresponding timer index
 */
static inline uint8_t get_timer_index(int channel)
{
    // Channels 0-3 use timer 0, 4-7 use timer 1, 8-11 use timer 2
    return channel / 4;
}

// 函数原型声明
int fusion_hat_write_pwm_value(struct i2c_client *client, uint8_t channel, uint16_t value);
int fusion_hat_write_period_value(struct i2c_client *client, uint8_t channel, uint16_t period);
int fusion_hat_write_prescaler_value(struct i2c_client *client, uint8_t channel, uint16_t prescaler);

/*
 * Set PWM value function
 * @client: I2C client
 * @channel: PWM channel (0-11)
 * @value: PWM value (0-65535)
 * @return: 0 on success, error code on failure
 */
int fusion_hat_write_pwm_value(struct i2c_client *client, uint8_t channel, uint16_t value)
{
    int ret;
    uint8_t reg;
    struct fusion_hat_dev *dev = i2c_get_clientdata(client);
    
    // Check channel validity
    if (channel >= FUSION_HAT_PWM_CHANNELS) return -EINVAL;
    
    // Calculate command address
    reg = CMD_SET_PWM_VALUE_BASE + (channel * 2);
    
    // Write to I2C device
    printk(KERN_DEBUG "fusion_hat_write_pwm_value: reg = %u, value = %u\n", reg, value);
    ret = fusion_hat_i2c_write_word(client, reg, value, true);
    if (ret < 0)  return ret;
    
    // Update cached PWM value
    if (dev) dev->pwm_values[channel] = value;
    
    return 0;
}

/*
 * Set PWM period value
 * @client: I2C client
 * @channel: PWM channel (0-11)
 * @period: Period value
 * @return: 0 on success, error code on failure
 */
int fusion_hat_write_period_value(struct i2c_client *client, uint8_t channel, uint16_t period)
{
    int ret;
    uint8_t reg, timer;
    struct fusion_hat_dev *dev = i2c_get_clientdata(client);
    
    // 检查通道有效性
    if (channel >= FUSION_HAT_PWM_CHANNELS) return -EINVAL;

    // Get timer index
    timer = get_timer_index(channel);
    
    // 计算命令地址
    reg = CMD_SET_TIMER_PERIOD_BASE + (timer * 2);
    
    // 写入I2C设备
    ret = fusion_hat_i2c_write_word(client, reg, period, true);
    if (ret < 0) return ret;
    
    // Update cached period value
    if (dev) dev->timer_periods[timer] = period;
    
    return 0;
}

/*
 * @brief Write PWM prescaler value
 * @param client I2C client
 * @param channel PWM channel (0-11)
 * @param prescaler Prescaler value
 * @return 0 on success, error code on failure
 */

int fusion_hat_write_prescaler_value(struct i2c_client *client, uint8_t channel, uint16_t prescaler)
{
    int ret;
    uint8_t reg, timer;
    struct fusion_hat_dev *dev = i2c_get_clientdata(client);
    
    // 检查通道有效性
    if (channel >= FUSION_HAT_PWM_CHANNELS) return -EINVAL;
    
    // 获取定时器索引
    timer = get_timer_index(channel);
    
    // 计算命令地址
    reg = CMD_SET_TIMER_PRESCALER_BASE + (timer * 2);
    
    // 写入I2C设备
    ret = fusion_hat_i2c_write_word(client, reg, prescaler, true);
    if (ret < 0) return ret;
    
    // Update cached prescaler value
    if (dev) dev->timer_prescalers[timer] = prescaler;
    
    return 0;
}

/**
 * @brief Show the current PWM period
 * @param kobj The kobject for this channel
 * @param attr The attribute structure
 * @param buf The buffer to write the period value to
 * @return Number of bytes written to buffer
 */
static ssize_t period_show(struct kobject *kobj, struct kobj_attribute *attr, char *buf) {
    struct fusion_hat_pwm_channel *pwm_chan = container_of(kobj, struct fusion_hat_pwm_channel, kobj);
    int channel = pwm_chan->channel;
    struct fusion_hat_dev *fusion_dev = pwm_chan->dev;
    uint32_t period = fusion_dev->pwm_periods[channel];
    
    return sprintf(buf, "%u\n", period);
}

/**
 * @brief Set the PWM period
 * @param kobj The kobject for this channel
 * @param attr The attribute structure
 * @param buf The buffer containing the new period value
 * @param count Number of bytes in the buffer
 * @return Number of bytes processed or error code
 */
static ssize_t period_store(struct kobject *kobj, struct kobj_attribute *attr, const char *buf, size_t count) {
    struct fusion_hat_pwm_channel *pwm_chan = container_of(kobj, struct fusion_hat_pwm_channel, kobj);
    int channel = pwm_chan->channel;
    struct fusion_hat_dev *fusion_dev = pwm_chan->dev;
    uint32_t period;
    int ret;
    
    if (kstrtou32(buf, 10, &period) < 0) {
        return -EINVAL;
    }
    
    // Calculate prescaler from period
    // First calculate frequency
    uint32_t frequency = 1000000 / period;
    // Calculate prescaler from frequency
    uint32_t prescaler = PWM_CORE_FREQUENCY / frequency / (PWM_PERIOD_VALUE + 1) - 1;
    if (prescaler == 0) prescaler = 1;
    // Limit prescaler maximum to 65535
    if (prescaler > 65535) prescaler = 65535;
    
    mutex_lock(&fusion_dev->lock);
    ret = fusion_hat_write_prescaler_value(fusion_dev->client, channel, prescaler);
    if (ret >= 0) {
        fusion_dev->pwm_periods[channel] = period;
    }
    mutex_unlock(&fusion_dev->lock);
    
    return ret < 0 ? ret : count;
}

/**
 * @brief Show the current PWM duty cycle
 * @param kobj The kobject for this channel
 * @param attr The attribute structure
 * @param buf The buffer to write the duty cycle value to
 * @return Number of bytes written to buffer
 */
static ssize_t duty_cycle_show(struct kobject *kobj, struct kobj_attribute *attr, char *buf) {
    struct fusion_hat_pwm_channel *pwm_chan = container_of(kobj, struct fusion_hat_pwm_channel, kobj);
    int channel = pwm_chan->channel;
    struct fusion_hat_dev *fusion_dev = pwm_chan->dev;
    uint32_t value = fusion_dev->pwm_duty_cycles[channel];
    
    return sprintf(buf, "%u\n", value);
}

/**
 * @brief Set the PWM duty cycle
 * @param kobj The kobject for this channel
 * @param attr The attribute structure
 * @param buf The buffer containing the new duty cycle value
 * @param count Number of bytes in the buffer
 * @return Number of bytes processed or error code
 */
static ssize_t duty_cycle_store(struct kobject *kobj, struct kobj_attribute *attr, const char *buf, size_t count) {
    struct fusion_hat_pwm_channel *pwm_chan = container_of(kobj, struct fusion_hat_pwm_channel, kobj);
    int channel = pwm_chan->channel;
    struct fusion_hat_dev *fusion_dev = pwm_chan->dev;
    uint32_t input_value;
    uint16_t pwm_value;
    int ret;
    
    // check if enabled
    if (!fusion_dev->pwm_enabled[channel]) {
        return -EINVAL;
    }
    
    // Parse input value
    if (kstrtou32(buf, 10, &input_value) < 0) {
        return -EINVAL;
    }
    
    // Calculate PWM value from duty cycle (ms)
    printk(KERN_DEBUG "duty_cycle_store: input_value = %u, period = %u\n", input_value, fusion_dev->pwm_periods[channel]);
    pwm_value = (uint32_t)input_value * PWM_PERIOD_VALUE / fusion_dev->pwm_periods[channel];
    printk(KERN_DEBUG "duty_cycle_store: pwm_value = %u\n", pwm_value);
    
    mutex_lock(&fusion_dev->lock);
    ret = fusion_hat_write_pwm_value(fusion_dev->client, channel, pwm_value);
    if (ret >= 0) {
        fusion_dev->pwm_duty_cycles[channel] = input_value;
    }
    mutex_unlock(&fusion_dev->lock);
    
    return ret < 0 ? ret : count;
}

/**
 * @brief Show the current PWM enable state
 * @param kobj The kobject for this channel
 * @param attr The attribute structure
 * @param buf The buffer to write the enable state to
 * @return Number of bytes written to buffer
 */
static ssize_t enable_show(struct kobject *kobj, struct kobj_attribute *attr, char *buf) {
    struct fusion_hat_pwm_channel *pwm_chan = container_of(kobj, struct fusion_hat_pwm_channel, kobj);
    int channel = pwm_chan->channel;
    struct fusion_hat_dev *fusion_dev = pwm_chan->dev;
    
    return sprintf(buf, "%u\n", fusion_dev->pwm_enabled[channel] ? 1 : 0);
}

/**
 * @brief Set the PWM enable state
 * @param kobj The kobject for this channel
 * @param attr The attribute structure
 * @param buf The buffer containing the new enable state
 * @param count Number of bytes in the buffer
 * @return Number of bytes processed or error code
 */
static ssize_t enable_store(struct kobject *kobj, struct kobj_attribute *attr, const char *buf, size_t count) {
    struct fusion_hat_pwm_channel *pwm_chan = container_of(kobj, struct fusion_hat_pwm_channel, kobj);
    int channel = pwm_chan->channel;
    struct fusion_hat_dev *fusion_dev = pwm_chan->dev;
    uint8_t enable;
    
    if (kstrtou8(buf, 10, &enable) < 0) {
        return -EINVAL;
    }
    
    mutex_lock(&fusion_dev->lock);
    fusion_dev->pwm_enabled[channel] = enable ? true : false;
    // If disabling PWM, set value to 0
    if (!enable) {
        fusion_hat_write_pwm_value(fusion_dev->client, channel, 0);
    }
    mutex_unlock(&fusion_dev->lock);
    
    return count;
}

/*
 * PWM channel release function
 * Note: pwm_channels is a static array, no memory needs to be freed
 */
static void fusion_hat_pwm_channel_release(struct kobject *kobj) {
    // Since pwm_channels is a static array, no need to call kfree
    // Only perform necessary cleanup operations
    printk(KERN_DEBUG "Fusion Hat PWM: Releasing pwm channel kobject\n");
}

/**
 * @brief PWM channel kobject type
 * 
 * Defines the sysfs operations and release function for PWM channel kobjects.
 */
static const struct kobj_type pwm_channel_ktype = {
    .sysfs_ops = &kobj_sysfs_ops,
    .release = fusion_hat_pwm_channel_release,
};

/*
 * PWM initialization function
 * @dev: Fusion HAT device structure
 * @return: 0 on success, error code on failure
 */
int fusion_hat_pwm_probe(struct fusion_hat_dev *dev) {
    int ret;
    uint8_t i;
    
    printk(KERN_INFO "Fusion Hat PWM: Initializing PWM subsystem\n");
    
    // Initialize PWM states
    for (i = 0; i < FUSION_HAT_PWM_CHANNELS; i++) {
        dev->pwm_enabled[i] = false;
        dev->pwm_duty_cycles[i] = 0;
        dev->pwm_periods[i] = PWM_DEFAULT_PERIOD;
    }
    
    // Initialize all channels with default period and prescaler values
    for (i = 0; i < FUSION_HAT_PWM_CHANNELS; i++) {
        // Set default period
        ret = fusion_hat_write_period_value(dev->client, i, PWM_PERIOD_VALUE);
        if (ret < 0) {
            dev_err(&dev->client->dev, "Failed to initialize channel %d: %d\n", i, ret);
            return ret;
        }
        
        // Set default prescaler
        ret = fusion_hat_write_prescaler_value(dev->client, i, PWM_DEFAULT_PRESCALER);
        if (ret < 0) {
            dev_err(&dev->client->dev, "Failed to initialize channel %d: %d\n", i, ret);
            return ret;
        }
    }
    
    // Create pwm subdirectory in sysfs
    pwm_kobj = kobject_create_and_add("pwm", &dev->device->kobj);
    if (!pwm_kobj) {
        dev_err(&dev->client->dev, "Failed to create pwm kobject\n");
        return -ENOMEM;
    }
    
    // Create subdirectory and attributes for each PWM channel
    for (i = 0; i < FUSION_HAT_PWM_CHANNELS; i++) {
        // Set channel information
        snprintf(pwm_channels[i].name, sizeof(pwm_channels[i].name), "pwm%d", i);
        pwm_channels[i].channel = i;
        pwm_channels[i].dev = dev;
        
        // Initialize sysfs attributes with 0666 permissions (rw-rw-rw-)
        // to allow access for all users without requiring sudo
        pwm_channels[i].period_attr.attr.name = "period";
        pwm_channels[i].period_attr.attr.mode = 0666;
        pwm_channels[i].period_attr.show = period_show;
        pwm_channels[i].period_attr.store = period_store;
        
        pwm_channels[i].duty_cycle_attr.attr.name = "duty_cycle";
        pwm_channels[i].duty_cycle_attr.attr.mode = 0666;
        pwm_channels[i].duty_cycle_attr.show = duty_cycle_show;
        pwm_channels[i].duty_cycle_attr.store = duty_cycle_store;
        
        pwm_channels[i].enable_attr.attr.name = "enable";
        pwm_channels[i].enable_attr.attr.mode = 0666;
        pwm_channels[i].enable_attr.show = enable_show;
        pwm_channels[i].enable_attr.store = enable_store;
        
        // Create channel subdirectory
        ret = kobject_init_and_add(&pwm_channels[i].kobj, &pwm_channel_ktype, pwm_kobj, "%s", pwm_channels[i].name);
        if (ret < 0) {
            dev_err(&dev->client->dev, "Failed to create pwm%d kobject: %d\n", i, ret);
            goto cleanup;
        }
        
        // Create attributes in channel subdirectory
        ret = sysfs_create_file(&pwm_channels[i].kobj, &pwm_channels[i].period_attr.attr);
        if (ret < 0) {
            dev_err(&dev->client->dev, "Failed to create period attribute for pwm%d: %d\n", i, ret);
            goto cleanup;
        }
        
        ret = sysfs_create_file(&pwm_channels[i].kobj, &pwm_channels[i].duty_cycle_attr.attr);
        if (ret < 0) {
            dev_err(&dev->client->dev, "Failed to create duty_cycle attribute for pwm%d: %d\n", i, ret);
            sysfs_remove_file(&pwm_channels[i].kobj, &pwm_channels[i].period_attr.attr);
            goto cleanup;
        }
        
        ret = sysfs_create_file(&pwm_channels[i].kobj, &pwm_channels[i].enable_attr.attr);
        if (ret < 0) {
            dev_err(&dev->client->dev, "Failed to create enable attribute for pwm%d: %d\n", i, ret);
            sysfs_remove_file(&pwm_channels[i].kobj, &pwm_channels[i].duty_cycle_attr.attr);
            sysfs_remove_file(&pwm_channels[i].kobj, &pwm_channels[i].period_attr.attr);
            goto cleanup;
        }
    }
    
    printk(KERN_INFO "Fusion Hat PWM: PWM subsystem initialized successfully\n");
    return 0;
    
cleanup:
    // Clean up allocated resources
    for (i = i - 1; i >= 0; i--) {
        sysfs_remove_file(&pwm_channels[i].kobj, &pwm_channels[i].enable_attr.attr);
        sysfs_remove_file(&pwm_channels[i].kobj, &pwm_channels[i].duty_cycle_attr.attr);
        sysfs_remove_file(&pwm_channels[i].kobj, &pwm_channels[i].period_attr.attr);
        kobject_put(&pwm_channels[i].kobj);
    }
    
    if (pwm_kobj) {
        kobject_put(pwm_kobj);
        pwm_kobj = NULL;
    }
    
    return ret;
}

/*
 * PWM cleanup function
 * @dev: Fusion HAT device structure
 */
void fusion_hat_pwm_remove(struct fusion_hat_dev *dev)
{
    uint8_t i;
    
    printk(KERN_INFO "Fusion Hat PWM: Removing PWM subsystem\n");
    
    // Turn off all PWM channels
    for (i = 0; i < FUSION_HAT_PWM_CHANNELS; i++) {
        mutex_lock(&dev->lock);
        fusion_hat_write_pwm_value(dev->client, i, 0);
        dev->pwm_enabled[i] = false;
        mutex_unlock(&dev->lock);
        
        // Remove sysfs attributes
        sysfs_remove_file(&pwm_channels[i].kobj, &pwm_channels[i].enable_attr.attr);
        sysfs_remove_file(&pwm_channels[i].kobj, &pwm_channels[i].duty_cycle_attr.attr);
        sysfs_remove_file(&pwm_channels[i].kobj, &pwm_channels[i].period_attr.attr);
        
        // Remove channel subdirectory
        kobject_put(&pwm_channels[i].kobj);
    }
    
    // Remove pwm subdirectory
    if (pwm_kobj) {
        kobject_put(pwm_kobj);
        pwm_kobj = NULL;
    }
    
    printk(KERN_INFO "Fusion Hat PWM: PWM subsystem removed successfully\n");
}

// Export functions for use by other modules
EXPORT_SYMBOL(fusion_hat_pwm_probe);
EXPORT_SYMBOL(fusion_hat_pwm_remove);
