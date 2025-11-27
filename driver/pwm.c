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
#include <linux/mutex.h>
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

/**
 * @brief Get timer index
 * @param channel PWM channel number
 * @return Corresponding timer index
 * 
 * Channels 0-3 use timer 0, 4-7 use timer 1, 8-11 use timer 2
 */
static inline uint8_t get_timer_index(int channel) {
    return channel / 4;
}

// Function prototypes
int fusion_hat_write_pwm_value(struct i2c_client *client, uint8_t channel, uint16_t value);
int fusion_hat_write_period_value(struct i2c_client *client, uint8_t channel, uint16_t period);
int fusion_hat_write_prescaler_value(struct i2c_client *client, uint8_t channel, uint16_t prescaler);

/**
 * @brief Set PWM value
 * @param client I2C client
 * @param channel PWM channel (0-11)
 * @param value PWM value (0-65535)
 * @return 0 on success, error code on failure
 */
int fusion_hat_write_pwm_value(struct i2c_client *client, uint8_t channel, uint16_t value) {
    uint8_t reg;
    
    if (channel >= FUSION_HAT_PWM_CHANNELS) return -EINVAL;
    
    reg = CMD_SET_PWM_VALUE_BASE + channel;
    return fusion_hat_i2c_write_word(client, reg, value, true);
}

/**
 * @brief Set PWM period value
 * @param client I2C client
 * @param channel PWM channel (0-11)
 * @param period Period value
 * @return 0 on success, error code on failure
 */
int fusion_hat_write_period_value(struct i2c_client *client, uint8_t channel, uint16_t period) {
    uint8_t reg, timer;
    
    if (channel >= FUSION_HAT_PWM_CHANNELS) return -EINVAL;
    timer = get_timer_index(channel);
    reg = CMD_SET_TIMER_PERIOD_BASE + timer;
    
    return fusion_hat_i2c_write_word(client, reg, period, true);
}

/**
 * @brief Write PWM prescaler value
 * @param client I2C client
 * @param channel PWM channel (0-11)
 * @param prescaler Prescaler value
 * @return 0 on success, error code on failure
 */
int fusion_hat_write_prescaler_value(struct i2c_client *client, uint8_t channel, uint16_t prescaler) {
    uint8_t reg, timer;
    
    if (channel >= FUSION_HAT_PWM_CHANNELS) return -EINVAL;

    timer = get_timer_index(channel);
    reg = CMD_SET_TIMER_PRESCALER_BASE + timer;
    return fusion_hat_i2c_write_word(client, reg, prescaler, true);
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
    
    if (kstrtou32(buf, 10, &period) < 0) return -EINVAL;
    
    // Calculate prescaler from period
    uint32_t frequency = 1000000 / period;
    uint32_t prescaler = PWM_CORE_FREQUENCY / frequency / (PWM_PERIOD_VALUE + 1) - 1;
    if (prescaler == 0) prescaler = 1;
    if (prescaler > 65535) prescaler = 65535;
    
    mutex_lock(&fusion_dev->lock);
    ret = fusion_hat_write_prescaler_value(fusion_dev->client, channel, prescaler);
    mutex_unlock(&fusion_dev->lock);
    if (ret >= 0) fusion_dev->pwm_periods[channel] = period;
    
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
    
    // Check if enabled
    if (!fusion_dev->pwm_enabled[channel]) return -EINVAL;
    
    // Parse input value
    if (kstrtou32(buf, 10, &input_value) < 0) return -EINVAL;
    
    // Calculate PWM value from duty cycle (ms)
    pwm_value = (uint32_t)input_value * PWM_PERIOD_VALUE / fusion_dev->pwm_periods[channel];
    
    mutex_lock(&fusion_dev->lock);
    ret = fusion_hat_write_pwm_value(fusion_dev->client, channel, pwm_value);
    mutex_unlock(&fusion_dev->lock);
    if (ret >= 0) fusion_dev->pwm_duty_cycles[channel] = input_value;
    
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
    
    if (kstrtou8(buf, 10, &enable) < 0) return -EINVAL;
    
    mutex_lock(&fusion_dev->lock);
    fusion_dev->pwm_enabled[channel] = enable ? true : false;
    mutex_unlock(&fusion_dev->lock);
    // If disabling PWM, set value to 0
    if (!enable) fusion_hat_write_pwm_value(fusion_dev->client, channel, 0);
    
    return count;
}

/**
 * @brief PWM channel release function
 * 
 * Note: pwm_channels is a static array, no memory needs to be freed
 */
static void fusion_hat_pwm_channel_release(struct kobject *kobj) {
    // Since pwm_channels is a static array, no need to call kfree
    // Only perform necessary cleanup operations
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

/**
 * @brief PWM initialization function
 * @param dev Fusion HAT device structure
 * @return 0 on success, error code on failure
 */
int fusion_hat_pwm_probe(struct fusion_hat_dev *dev) {
    int ret;
    uint8_t i;
    
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

/**
 * @brief PWM cleanup function
 * @param dev Fusion HAT device structure
 */
void fusion_hat_pwm_remove(struct fusion_hat_dev *dev)
{
    uint8_t i;
    
    // Turn off all PWM channels
    for (i = 0; i < FUSION_HAT_PWM_CHANNELS; i++) {
        mutex_lock(&dev->lock);
        fusion_hat_write_pwm_value(dev->client, i, 0);
        dev->pwm_enabled[i] = false;
        mutex_unlock(&dev->lock);
    }
    
    // Only clean up sysfs entries if pwm_kobj was created
    if (pwm_kobj) {
        // Remove sysfs attributes and channel subdirectories
        for (i = 0; i < FUSION_HAT_PWM_CHANNELS; i++) {
            // Remove sysfs attributes
            sysfs_remove_file(&pwm_channels[i].kobj, &pwm_channels[i].enable_attr.attr);
            sysfs_remove_file(&pwm_channels[i].kobj, &pwm_channels[i].duty_cycle_attr.attr);
            sysfs_remove_file(&pwm_channels[i].kobj, &pwm_channels[i].period_attr.attr);
            
            // Remove channel subdirectory
            kobject_put(&pwm_channels[i].kobj);
        }
        
        // Remove pwm subdirectory
        kobject_put(pwm_kobj);
        pwm_kobj = NULL;
    }
}

// Export functions for use by other modules
EXPORT_SYMBOL(fusion_hat_pwm_probe);
EXPORT_SYMBOL(fusion_hat_pwm_remove);
