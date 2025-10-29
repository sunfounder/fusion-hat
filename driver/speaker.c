/*
 * Fusion HAT Speaker Driver Module
 * Responsible for speaker initialization, control, and state management
 */

#include "main.h"


/**
 * @brief Show speaker status
 * @dev: Device structure
 * @attr: Device attribute
 * @buf: Buffer to store speaker status
 * 
 * Returns the number of bytes written to buffer or error code
 */
static ssize_t speaker_show(struct device *dev, struct device_attribute *attr, char *buf) {
    struct fusion_hat_dev *fusion_dev = dev_get_drvdata(dev);
    
    if (!fusion_dev) {
        pr_err("Fusion HAT: Invalid device in speaker_show\n");
        return -EINVAL;
    }
    return sprintf(buf, "%d\n", fusion_dev->speaker_status);
}

/**
 * @brief Set speaker status
 * @dev: Device structure
 * @attr: Device attribute
 * @buf: Buffer containing the new speaker status
 * @count: Number of bytes in buffer
 * 
 * Returns the number of bytes processed or error code
 */
static ssize_t speaker_store(struct device *dev, struct device_attribute *attr, const char *buf, size_t count) {
    struct fusion_hat_dev *fusion_dev = dev_get_drvdata(dev);
    unsigned int value;
    int ret;
    
    if (!fusion_dev || !fusion_dev->client) {
        pr_err("Fusion HAT: Invalid device or client in speaker_store\n");
        return -EINVAL;
    }
    
    /* Parse input value */
    ret = kstrtouint(buf, 10, &value);
    if (ret < 0) {
        dev_err(dev, "Invalid value for speaker: %d\n", ret);
        return ret;
    }
    
    /* Check if value is valid (0 or 1) */
    if (value > 1) {
        dev_err(dev, "Invalid speaker value, must be 0 or 1\n");
        return -EINVAL;
    }
    

    mutex_lock(&fusion_dev->lock);
    ret = fusion_hat_i2c_write_byte(fusion_dev->client, CMD_CONTROL_SPEAKER, value);
    mutex_unlock(&fusion_dev->lock);
    if (ret < 0) {
        dev_err(dev, "Failed to set speaker status: %d\n", ret);
        return ret;
    }
    fusion_dev->speaker_status = value;
    
    return count;
}

/**
 * @brief Device attribute for speaker control
 * 
 * This attribute allows userspace to read and write the speaker status.
 * The speaker status is represented as a single byte (0 or 1).
 */
static struct device_attribute dev_attr_speaker = {
    .attr = {.name = "speaker", .mode = 0666},
    .show = speaker_show,
    .store = speaker_store,
};

/**
 * @brief Initialize speaker
 * @dev: Fusion HAT device structure
 * 
 * Returns 0 on success, error code on failure
 */
int fusion_hat_speaker_init(struct fusion_hat_dev *dev) {
    int ret;

    if (!dev || !dev->client || !dev->device) {
        pr_err("Fusion HAT: Invalid device, client or device structure in speaker initialization\n");
        return -EINVAL;
    }
    
    /* Initialize LED state to off */
    dev->speaker_status = 0;
    
    ret = fusion_hat_i2c_write_byte(dev->client, CMD_CONTROL_SPEAKER, 0);
    if (ret < 0) {
        dev_err(&dev->client->dev, "Failed to initialize speaker: %d\n", ret);
        return ret;
    }
    dev->speaker_status = 0;
    
    /* Create sysfs attribute for speaker control */
    ret = device_create_file(dev->device, &dev_attr_speaker);
    if (ret < 0) {
        dev_err(&dev->client->dev, "Failed to create speaker sysfs attribute: %d\n", ret);
        return ret;
    }
    
    return 0;
}

/**
 * @brief Cleanup speaker
 * @dev: Fusion HAT device structure
 * 
 */
void fusion_hat_speaker_cleanup(struct fusion_hat_dev *dev) {
    if (!dev) {
        return;
    }
    
    /* Ensure speaker is turned off during cleanup */
    if (dev->client) {
        fusion_hat_i2c_write_byte(dev->client, CMD_CONTROL_SPEAKER, 0);
    }
    
    /* Remove sysfs attribute */
    if (dev->device) {
        device_remove_file(dev->device, &dev_attr_speaker);
    }
    
    if (dev->client) {
        dev_info(&dev->client->dev, "Speaker resources cleaned up\n");
    } else {
        pr_info("Fusion HAT: Speaker resources cleaned up\n");
    }
}

EXPORT_SYMBOL(fusion_hat_speaker_init);
EXPORT_SYMBOL(fusion_hat_speaker_cleanup);
