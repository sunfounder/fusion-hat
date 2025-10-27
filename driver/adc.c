/*
 * Fusion Hat ADC模块
 * 包含ADC读取和IIO设备相关的功能实现
 */

#include "main.h"

// 设备名称
#define FUSION_HAT_ADC_NAME "fusion-hat"

// IIO通道描述
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

/*
 * 读取ADC值
 * @client: I2C客户端
 * @channel: ADC通道(0-3)
 * @value: 存储读取结果的指针
 * @return: 成功返回0，失败返回错误码
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

    ret = fusion_hat_i2c_read_word(client, reg, value, false);  // false表示需要大端格式
    
    if (ret < 0) {
        return ret;
    }
    
    return 0;
}
EXPORT_SYMBOL(fusion_hat_read_adc);

/*
 * IIO设备读取原始数据函数
 */
static int fusion_hat_iio_read_raw(struct iio_dev *indio_dev, struct iio_chan_spec const *chan,
                                int *val, int *val2, long mask)
{
    // 使用iio_device_get_drvdata获取设备指针（标准做法）
    struct fusion_hat_dev *dev = iio_device_get_drvdata(indio_dev);
    uint16_t adc_value;
    int ret;
    
    if (!dev) {
        return -EINVAL;
    }
    
    switch (mask) {
    case IIO_CHAN_INFO_RAW:
        // 读取ADC原始值
        mutex_lock(&dev->lock);
        ret = fusion_hat_read_adc(dev->client, chan->channel, &adc_value);
        mutex_unlock(&dev->lock);
        
        if (ret < 0) {
            return ret;
        }
        
        *val = adc_value;
        return IIO_VAL_INT;
        
    case IIO_CHAN_INFO_SCALE:
        // 使用IIO_VAL_FRACTIONAL类型，这样计算结果就是ADC_REFERENCE_VOLTAGE/ADC_MAX_VALUE mV/位
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

// 创建ADC IIO设备
int fusion_hat_adc_probe(struct fusion_hat_dev *dev)
{
    int ret;
    
    printk(KERN_INFO "Fusion Hat ADC: Creating single IIO device with all channels\n");
    
    // 只创建一个IIO设备，包含所有4个通道
    // 我们不需要在私有数据中存储额外信息，通过iio_dev到dev的映射使用container_of宏
    dev->iio_devs[0] = iio_device_alloc(&dev->client->dev, 0); // 0表示不需要额外的私有数据
    if (!dev->iio_devs[0]) {
        printk(KERN_ERR "Fusion Hat ADC: Failed to allocate IIO device\n");
        return -ENOMEM;
    }
    
    // 存储指向fusion_hat_dev的指针在IIO设备的dev.driver_data中（更标准的做法）
    iio_device_set_drvdata(dev->iio_devs[0], dev);
    
    // 配置IIO设备
    dev->iio_devs[0]->name = FUSION_HAT_ADC_NAME;
    dev->iio_devs[0]->dev.parent = &dev->client->dev;
    dev->iio_devs[0]->info = &fusion_hat_iio_info;
    dev->iio_devs[0]->modes = INDIO_DIRECT_MODE;
    dev->iio_devs[0]->channels = fusion_hat_iio_channels;
    dev->iio_devs[0]->num_channels = ARRAY_SIZE(fusion_hat_iio_channels);
    
    // 注册IIO设备
    ret = iio_device_register(dev->iio_devs[0]);
    if (ret) {
        printk(KERN_ERR "Fusion Hat ADC: Failed to register IIO device\n");
        iio_device_free(dev->iio_devs[0]);
        dev->iio_devs[0] = NULL;
        return ret;
    }
    
    printk(KERN_INFO "Fusion Hat ADC: IIO device created successfully\n");
    return 0;
}
EXPORT_SYMBOL(fusion_hat_adc_probe);

// 清理ADC IIO设备
void fusion_hat_adc_remove(struct fusion_hat_dev *dev)
{
    printk(KERN_INFO "Fusion Hat ADC: Removing IIO device\n");
    
    // 只需要清理一个设备
    if (dev->iio_devs[0]) {
        iio_device_unregister(dev->iio_devs[0]);
        iio_device_free(dev->iio_devs[0]);
        dev->iio_devs[0] = NULL;
    }
}
EXPORT_SYMBOL(fusion_hat_adc_remove);
