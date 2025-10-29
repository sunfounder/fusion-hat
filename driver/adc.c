/*
 * Fusion Hat ADC Module
 * Contains ADC reading and IIO device related functionality
 */

#include "main.h"

// Device name
#define FUSION_HAT_ADC_NAME "fusion-hat"

// IIO channel descriptors
static const struct iio_chan_spec fusion_hat_iio_channels[] = {
    {
        .type = IIO_VOLTAGE,
        .indexed = 1,
        .channel = 0,
        .info_mask_separate = BIT(IIO_CHAN_INFO_RAW) | BIT(IIO_CHAN_INFO_SCALE),
        .datasheet_name = "ain0",
    },
    {
        .type = IIO_VOLTAGE,
        .indexed = 1,
        .channel = 1,
        .info_mask_separate = BIT(IIO_CHAN_INFO_RAW) | BIT(IIO_CHAN_INFO_SCALE),
        .datasheet_name = "ain1",
    },
    {
        .type = IIO_VOLTAGE,
        .indexed = 1,
        .channel = 2,
        .info_mask_separate = BIT(IIO_CHAN_INFO_RAW) | BIT(IIO_CHAN_INFO_SCALE),
        .datasheet_name = "ain2",
    },
    {
        .type = IIO_VOLTAGE,
        .indexed = 1,
        .channel = 3,
        .info_mask_separate = BIT(IIO_CHAN_INFO_RAW) | BIT(IIO_CHAN_INFO_SCALE),
        .datasheet_name = "ain3",
    },
};

/**
 * fusion_hat_read_adc - Read ADC value from specified channel
 * @client: I2C client
 * @channel: ADC channel (0-3)
 * @value: Pointer to store the read result
 * @return: 0 on success, negative error code on failure
 */
int fusion_hat_read_adc(struct i2c_client *client, int channel, uint16_t *value)
{
    uint8_t reg;
    int ret;
    
    if (!client || !value) {
        return -EINVAL;
    }
    
    if (channel < 0 || channel > 3) {
        return -EINVAL;
    }
    
    reg = CMD_READ_ADC_BASE + (channel * 2);
    ret = fusion_hat_i2c_read_word(client, reg, value, true);  // true indicates big-endian format
    
    if (ret < 0) {
        return ret;
    }
    
    return 0;
}
EXPORT_SYMBOL(fusion_hat_read_adc);

/**
 * fusion_hat_iio_read_raw - Read raw data from IIO device
 * @indio_dev: IIO device pointer
 * @chan: Channel specification
 * @val: Pointer to store integer value
 * @val2: Pointer to store fractional value
 * @mask: Information mask
 * @return: IIO value type on success, negative error code on failure
 */
static int fusion_hat_iio_read_raw(struct iio_dev *indio_dev, struct iio_chan_spec const *chan,
                                int *val, int *val2, long mask)
{
    // Get device pointer using iio_device_get_drvdata (standard practice)
    struct fusion_hat_dev *dev = iio_device_get_drvdata(indio_dev);
    uint16_t adc_value;
    int ret;
    
    if (!dev) {
        return -EINVAL;
    }
    
    switch (mask) {
    case IIO_CHAN_INFO_RAW:
        // Read raw ADC value with lock protection
        mutex_lock(&dev->lock);
        ret = fusion_hat_read_adc(dev->client, chan->channel, &adc_value);
        mutex_unlock(&dev->lock);
        
        if (ret < 0) {
            return ret;
        }
        
        *val = adc_value;
        return IIO_VAL_INT;
        
    case IIO_CHAN_INFO_SCALE:
        // Use IIO_VAL_FRACTIONAL to calculate scale as ADC_REFERENCE_VOLTAGE/ADC_MAX_VALUE mV/bit
        *val = ADC_REFERENCE_VOLTAGE;  // 3300mV
        *val2 = ADC_MAX_VALUE + 1;     // 4096
        return IIO_VAL_FRACTIONAL;
        
    default:
        return -EINVAL;
    }
}

// IIO信息结构体
static const struct iio_info fusion_hat_iio_info = {
    .read_raw = fusion_hat_iio_read_raw,
};

/**
 * fusion_hat_adc_probe - Initialize ADC IIO device
 * @dev: Fusion Hat device structure
 * @return: 0 on success, negative error code on failure
 */
int fusion_hat_adc_probe(struct fusion_hat_dev *dev)
{
    int ret;
    
    // Create a single IIO device with all 4 channels
    dev->iio_devs[0] = iio_device_alloc(&dev->client->dev, 0); // 0 indicates no additional private data needed
    if (!dev->iio_devs[0]) {
        printk(KERN_ERR "Fusion Hat ADC: Failed to allocate IIO device\n");
        return -ENOMEM;
    }
    
    // Store pointer to fusion_hat_dev in IIO device's driver data
    iio_device_set_drvdata(dev->iio_devs[0], dev);
    
    // Configure IIO device
    dev->iio_devs[0]->name = FUSION_HAT_ADC_NAME;
    dev->iio_devs[0]->dev.parent = &dev->client->dev;
    dev->iio_devs[0]->info = &fusion_hat_iio_info;
    dev->iio_devs[0]->modes = INDIO_DIRECT_MODE;
    dev->iio_devs[0]->channels = fusion_hat_iio_channels;
    dev->iio_devs[0]->num_channels = ARRAY_SIZE(fusion_hat_iio_channels);
    
    // Register IIO device
    ret = iio_device_register(dev->iio_devs[0]);
    if (ret) {
        printk(KERN_ERR "Fusion Hat ADC: Failed to register IIO device\n");
        iio_device_free(dev->iio_devs[0]);
        dev->iio_devs[0] = NULL;
        return ret;
    }
    
    return 0;
}
EXPORT_SYMBOL(fusion_hat_adc_probe);

/**
 * fusion_hat_adc_remove - Clean up ADC IIO device
 * @dev: Fusion Hat device structure
 */
void fusion_hat_adc_remove(struct fusion_hat_dev *dev)
{
    // Clean up the IIO device if it exists
    if (dev->iio_devs[0]) {
        iio_device_unregister(dev->iio_devs[0]);
        iio_device_free(dev->iio_devs[0]);
        dev->iio_devs[0] = NULL;
    }
}
EXPORT_SYMBOL(fusion_hat_adc_remove);
