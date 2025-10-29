/**
 * @file adc.c
 * @brief Fusion Hat ADC Driver
 * 
 * This module provides ADC reading functionality and IIO device integration
 * for the Fusion Hat, supporting 4 channels of analog input with proper scaling.
 */

#include "main.h"
#include <linux/module.h>
#include <linux/iio/iio.h>
#include <linux/i2c.h>
#include <linux/mutex.h>

// Device name
#define FUSION_HAT_ADC_NAME "fusion-hat"


static int fusion_hat_iio_read_raw(struct iio_dev *indio_dev, struct iio_chan_spec const *chan,
                                int *val, int *val2, long mask);

/**
 * @brief IIO channel descriptors for 4 ADC channels
 */
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
 * @brief IIO device information structure
 */
static const struct iio_info fusion_hat_iio_info = {
    .read_raw = fusion_hat_iio_read_raw,
};

/**
 * @brief Read ADC value from specified channel
 * @param client I2C client
 * @param channel ADC channel (0-3)
 * @param value Pointer to store the read result
 * @return 0 on success, negative error code on failure
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
    ret = fusion_hat_i2c_read_word(client, reg, value, true);
    
    if (ret < 0) {
        return ret;
    }
    
    return 0;
}

/**
 * @brief Read raw data from IIO device
 * @param indio_dev IIO device pointer
 * @param chan Channel specification
 * @param val Pointer to store integer value
 * @param val2 Pointer to store fractional value
 * @param mask Information mask
 * @return IIO value type on success, negative error code on failure
 */
static int fusion_hat_iio_read_raw(struct iio_dev *indio_dev, struct iio_chan_spec const *chan,
                                int *val, int *val2, long mask) {
    struct fusion_hat_dev *dev = iio_device_get_drvdata(indio_dev);
    uint16_t adc_value;
    int ret;
    
    if (!dev) {
        return -EINVAL;
    }
    
    switch (mask) {
    case IIO_CHAN_INFO_RAW:
        mutex_lock(&dev->lock);
        ret = fusion_hat_read_adc(dev->client, chan->channel, &adc_value);
        mutex_unlock(&dev->lock);
        
        if (ret < 0) {
            return ret;
        }
        
        *val = adc_value;
        return IIO_VAL_INT;
        
    case IIO_CHAN_INFO_SCALE:
        *val = ADC_REFERENCE_VOLTAGE;  // 3300mV
        *val2 = ADC_MAX_VALUE + 1;     // 4096
        return IIO_VAL_FRACTIONAL;
        
    default:
        return -EINVAL;
    }
}

/**
 * @brief Initialize ADC IIO device
 * @param dev Fusion Hat device structure
 * @return 0 on success, negative error code on failure
 */
int fusion_hat_adc_probe(struct fusion_hat_dev *dev)
{
    int ret;
    
    dev->iio_devs[0] = iio_device_alloc(&dev->client->dev, 0);
    if (!dev->iio_devs[0]) {
        dev_err(&dev->client->dev, "Failed to allocate IIO device\n");
        return -ENOMEM;
    }
    
    iio_device_set_drvdata(dev->iio_devs[0], dev);
    
    dev->iio_devs[0]->name = FUSION_HAT_ADC_NAME;
    dev->iio_devs[0]->dev.parent = &dev->client->dev;
    dev->iio_devs[0]->info = &fusion_hat_iio_info;
    dev->iio_devs[0]->modes = INDIO_DIRECT_MODE;
    dev->iio_devs[0]->channels = fusion_hat_iio_channels;
    dev->iio_devs[0]->num_channels = ARRAY_SIZE(fusion_hat_iio_channels);
    
    ret = iio_device_register(dev->iio_devs[0]);
    if (ret) {
        dev_err(&dev->client->dev, "Failed to register IIO device\n");
        iio_device_free(dev->iio_devs[0]);
        dev->iio_devs[0] = NULL;
        return ret;
    }
    
    return 0;
}

/**
 * @brief Clean up ADC IIO device
 * @param dev Fusion Hat device structure
 */
void fusion_hat_adc_remove(struct fusion_hat_dev *dev)
{
    if (dev->iio_devs[0]) {
        iio_device_unregister(dev->iio_devs[0]);
        iio_device_free(dev->iio_devs[0]);
        dev->iio_devs[0] = NULL;
    }
}

// Export functions for use by other modules
EXPORT_SYMBOL(fusion_hat_read_adc);
EXPORT_SYMBOL(fusion_hat_adc_probe);
EXPORT_SYMBOL(fusion_hat_adc_remove);
