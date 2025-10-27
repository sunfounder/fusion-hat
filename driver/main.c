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
#include <linux/suspend.h> // 用于pm_power_off
#include <linux/iio/iio.h>
#include <linux/device.h>
#include <linux/sysfs.h>
#include <linux/kobject.h>
#include <linux/pwm.h>
#include <linux/of.h>
#include <linux/of_device.h>

// 包含共享头文件
#include "main.h"

#define FUSION_HAT_NAME "fusion_hat"
#define FUSION_HAT_I2C_ADDR 0x17

// 模块参数，用于不使用设备树时指定I2C总线号和地址
static int i2c_bus = 1;  // 默认使用I2C总线1
module_param(i2c_bus, int, S_IRUGO);
MODULE_PARM_DESC(i2c_bus, "I2C bus number to use (default: 1)");

// 全局变量定义（与头文件中的extern声明匹配）
struct fusion_hat_dev *fusion_dev;
struct workqueue_struct *shutdown_wq;

// 设置PWM函数 - 与更新后的I2C word写入函数兼容
static int fusion_hat_set_pwm(struct i2c_client *client, uint8_t channel, uint16_t value)
{
    uint8_t reg_h;
    int ret;
    
    if (channel > 11) {
        dev_err(&client->dev, "Invalid PWM channel %d\n", channel);
        return -EINVAL;
    }
    
    // 根据通道选择对应的寄存器
    reg_h = CMD_SET_PWM0_VALUE_H + (channel * 2);
    
    // 注意：i2c_smbus_write_word_data使用小端格式，我们需要确保值的格式正确
    ret = fusion_hat_i2c_write_word(client, reg_h, value, true);
    if (ret < 0) {
        dev_err(&client->dev, "Failed to set PWM channel %d: %d\n", channel, ret);
    }
    
    return ret;
}

// 初始化PWM定时器的函数
static int fusion_hat_init_pwm_timer(struct i2c_client *client, uint8_t timer, uint16_t prescaler, uint16_t period)
{
    uint8_t reg_psc_h, reg_per_h;
    
    if (timer > 2) {
        return -EINVAL;
    }
    
    // 根据定时器选择对应的寄存器
    switch (timer) {
    case 0:
        reg_psc_h = CMD_SET_TIMER0_PRESCALER_H;
        reg_per_h = CMD_SET_TIMER0_PERIOD_H;
        break;
    case 1:
        reg_psc_h = CMD_SET_TIMER1_PRESCALER_H;
        reg_per_h = CMD_SET_TIMER1_PERIOD_H;
        break;
    case 2:
        reg_psc_h = CMD_SET_TIMER2_PRESCALER_H;
        reg_per_h = CMD_SET_TIMER2_PERIOD_H;
        break;
    default:
        return -EINVAL;
    }
    
    // 设置预分频器
    if (fusion_hat_i2c_write_word(client, reg_psc_h, prescaler, true) < 0) {
        return -EIO;
    }
    
    // 设置周期
    return fusion_hat_i2c_write_word(client, reg_per_h, period, true);
}

// 电池相关函数声明（在battery.c中实现）
extern int fusion_hat_battery_init(struct fusion_hat_dev *dev);
extern void fusion_hat_battery_cleanup(struct fusion_hat_dev *dev);
extern ssize_t charging_show(struct device *dev, struct device_attribute *attr, char *buf);

// 中断处理函数
static irqreturn_t fusion_hat_irq_handler(int irq, void *dev_id)
{
    struct fusion_hat_dev *dev = dev_id;
    uint8_t button_status;
    int ret;
    
    // 读取按键状态
    ret = fusion_hat_i2c_read_byte(dev->client, CMD_READ_BUTTON_STATUS, &button_status);
    if (ret != 0) {
        return IRQ_HANDLED;
    }
    
    // 检查电源键（bit 0）
    if (button_status & 0x01) { // 电源键按下
        // 记录按键状态和时间戳
        dev->button_press_time = jiffies;
        
        // 检查是否需要关机
        // 读取关机状态
        ret = fusion_hat_i2c_read_byte(dev->client, CMD_READ_SHUTDOWN_STATUS, &button_status);
        if (ret == 0 && button_status == 2) {
            dev_info(&dev->client->dev, "按键关机请求\n");
            queue_work(shutdown_wq, &dev->shutdown_work);
        }
    } else if (dev->button_press_time != 0) {
        // 计算按下时长
        unsigned long press_duration = jiffies - dev->button_press_time;
        dev->button_press_time = 0;
        
        // 长按关机（3秒）
        if (press_duration > msecs_to_jiffies(3000)) {
            dev_info(&dev->client->dev, "检测到长按电源键，准备关机...\n");
            queue_work(shutdown_wq, &dev->shutdown_work);
        }
    }
    
    return IRQ_HANDLED;
}

// 关机工作函数
static void fusion_hat_shutdown_work(struct work_struct *work)
{
    struct fusion_hat_dev *dev = container_of(work, struct fusion_hat_dev, shutdown_work);
    dev_info(&dev->client->dev, "Shutting down system...\n");
    // 发送系统关机命令
    // if (pm_power_off)
    //     pm_power_off();
}



// PWM子系统实现 - 使用现代API
static int fusion_hat_pwm_request(struct pwm_chip *chip, struct pwm_device *pwm)
{
    return 0;
}

static void fusion_hat_pwm_free(struct pwm_chip *chip, struct pwm_device *pwm)
{
    struct fusion_hat_dev *dev = container_of(chip, struct fusion_hat_dev, pwm_chip);
    
    // 释放时将PWM值设为0
    mutex_lock(&dev->lock);
    fusion_hat_set_pwm(dev->client, pwm->hwpwm, 0);
    dev->pwm_values[pwm->hwpwm] = 0;
    dev->pwm_enabled[pwm->hwpwm] = false;
    mutex_unlock(&dev->lock);
}

// 现代PWM API - 使用apply函数替代config/enable/disable
static int fusion_hat_pwm_apply(struct pwm_chip *chip, struct pwm_device *pwm, 
                              const struct pwm_state *state)
{
    struct fusion_hat_dev *dev = container_of(chip, struct fusion_hat_dev, pwm_chip);
    uint8_t timer = pwm->hwpwm / 4; // 每个定时器控制4个PWM通道
    uint16_t value, period;
    int ret = 0;
    
    mutex_lock(&dev->lock);
    
    // 计算周期和占空比
    if (state->period == 0) {
        mutex_unlock(&dev->lock);
        return -EINVAL;
    }
    
    // 假设系统时钟为1MHz，转换为微秒
    period = state->period / 1000;
    
    // 转换占空比为0-4095范围
    if (state->enabled) {
        value = (state->duty_cycle * 4095) / state->period;
    } else {
        value = 0; // 禁用时设置为0
    }
    
    // 如果周期变化，更新定时器
    if (dev->timer_periods[timer] != period) {
        ret = fusion_hat_init_pwm_timer(dev->client, timer, 0, period);
        if (ret == 0) {
            dev->timer_periods[timer] = period;
        }
    }
    
    // 更新PWM占空比
    if (ret == 0) {
        ret = fusion_hat_set_pwm(dev->client, pwm->hwpwm, value);
        if (ret == 0) {
            dev->pwm_values[pwm->hwpwm] = value;
            dev->pwm_enabled[pwm->hwpwm] = state->enabled;
        }
    }
    
    mutex_unlock(&dev->lock);
    return ret;
}

// 获取当前PWM状态 - 修复返回类型为int
static int fusion_hat_pwm_get_state(struct pwm_chip *chip, struct pwm_device *pwm, 
                                   struct pwm_state *state)
{
    struct fusion_hat_dev *dev = container_of(chip, struct fusion_hat_dev, pwm_chip);
    uint8_t timer = pwm->hwpwm / 4;
    
    mutex_lock(&dev->lock);
    
    // 设置当前状态
    state->enabled = dev->pwm_enabled[pwm->hwpwm];
    state->period = dev->timer_periods[timer] * 1000; // 转换回纳秒
    state->duty_cycle = (dev->pwm_values[pwm->hwpwm] * state->period) / 4095;
    state->polarity = PWM_POLARITY_NORMAL;
    
    mutex_unlock(&dev->lock);
    return 0; // 返回成功
}

// 现代PWM操作结构
static const struct pwm_ops fusion_hat_pwm_ops = {
    .request = fusion_hat_pwm_request,
    .free = fusion_hat_pwm_free,
    .apply = fusion_hat_pwm_apply,
    .get_state = fusion_hat_pwm_get_state,
};

// IIO相关功能已在adc.c中实现，这里不再重复定义

// 按钮状态读取函数
static ssize_t button_show(struct device *dev, struct device_attribute *attr, char *buf)
{
    int ret;
    uint8_t button_status;
    struct fusion_hat_dev *fusion_dev = dev_get_drvdata(dev);
    
    mutex_lock(&fusion_dev->lock);
    ret = fusion_hat_i2c_read_byte(fusion_dev->client, CMD_READ_BUTTON_STATUS, &button_status);
    mutex_unlock(&fusion_dev->lock);
    
    if (ret < 0) {
        return ret;
    }
    
    return sprintf(buf, "%u\n", button_status);
}



// LED控制函数
static ssize_t led_show(struct device *dev, struct device_attribute *attr, char *buf)
{
    // LED状态读取暂不实现
    return sprintf(buf, "0\n");
}

static ssize_t led_store(struct device *dev, struct device_attribute *attr, const char *buf, size_t count)
{
    int ret;
    unsigned int value;
    struct fusion_hat_dev *fusion_dev = dev_get_drvdata(dev);
    
    ret = kstrtouint(buf, 10, &value);
    if (ret < 0) {
        return ret;
    }
    
    mutex_lock(&fusion_dev->lock);
    ret = fusion_hat_i2c_write_byte(fusion_dev->client, CMD_CONTROL_LED, value ? 1 : 0);
    mutex_unlock(&fusion_dev->lock);
    
    return ret < 0 ? ret : count;
}

// 扬声器控制函数
static ssize_t speaker_show(struct device *dev, struct device_attribute *attr, char *buf)
{
    // 扬声器状态读取暂不实现
    return sprintf(buf, "0\n");
}

static ssize_t speaker_store(struct device *dev, struct device_attribute *attr, const char *buf, size_t count)
{
    int ret;
    unsigned int value;
    struct fusion_hat_dev *fusion_dev = dev_get_drvdata(dev);
    
    ret = kstrtouint(buf, 10, &value);
    if (ret < 0) {
        return ret;
    }
    
    mutex_lock(&fusion_dev->lock);
    ret = fusion_hat_i2c_write_byte(fusion_dev->client, CMD_CONTROL_SPEAKER, value ? 1 : 0);
    mutex_unlock(&fusion_dev->lock);
    
    return ret < 0 ? ret : count;
}

// 固件版本读取函数
static ssize_t firmware_version_show(struct device *dev, struct device_attribute *attr, char *buf)
{
    int ret = 0;
    uint8_t version_bytes[3];
    struct fusion_hat_dev *fusion_dev = dev_get_drvdata(dev);
    
    mutex_lock(&fusion_dev->lock);
    
    // 一次性读取3位固件版本数据（使用I2C块读取功能）
    ret = fusion_hat_i2c_read_block_bytes(fusion_dev->client, CMD_READ_FIRMWARE_VERSION, version_bytes, 3);
    
    mutex_unlock(&fusion_dev->lock);
    
    if (ret < 0) {
        return ret;
    }
    
    // 直接处理并格式化固件版本号
    return sprintf(buf, "%u.%u.%u\n", 
                  version_bytes[0], 
                  version_bytes[1], 
                  version_bytes[2]);
}

// sysfs属性定义
static DEVICE_ATTR_RO(button);
static DEVICE_ATTR_RO(charging);
static DEVICE_ATTR_RW(led);
static DEVICE_ATTR_RW(speaker);
static DEVICE_ATTR_RO(firmware_version);

// 属性列表
static struct attribute *fusion_hat_attrs[] = {
    &dev_attr_button.attr,
    &dev_attr_charging.attr,
    &dev_attr_led.attr,
    &dev_attr_speaker.attr,
    &dev_attr_firmware_version.attr,
    NULL,
};

// 属性组
static struct attribute_group fusion_hat_attr_group = {
    .attrs = fusion_hat_attrs,
};

// 设置属性的show/store函数指针
static const struct attribute_group *fusion_hat_attr_groups[] = {
    &fusion_hat_attr_group,
    NULL,
};

// 设备操作结构体，用于设置sysfs属性的处理函数
static struct device_type fusion_hat_device_type = {
    .name = FUSION_HAT_NAME,
};

// I2C驱动探测函数
static int fusion_hat_probe(struct i2c_client *client)
{
    int ret;
    
    printk(KERN_INFO "FUSION_HAT: Probe function STARTED for address 0x%02x\n", client->addr);
    printk(KERN_INFO "FUSION_HAT: I2C adapter name: %s\n", client->adapter->name);
    dev_info(&client->dev, "Fusion Hat Driver: Probe started, checking I2C functionality\n");
    
    // 检查I2C设备是否可达
    if (!i2c_check_functionality(client->adapter, I2C_FUNC_I2C)) {
        printk(KERN_ERR "Fusion Hat Driver: I2C adapter doesn't support required functionality\n");
        dev_err(&client->dev, "I2C适配器不支持所需功能\n");
        return -ENODEV;
    }
    
    printk(KERN_INFO "Fusion Hat Driver: I2C functionality check passed\n");
    dev_info(&client->dev, "I2C functionality check completed successfully\n");
    printk(KERN_INFO "Fusion Hat Driver: Proceeding with device initialization\n");
    
    // 分配设备结构体
    fusion_dev = devm_kzalloc(&client->dev, sizeof(struct fusion_hat_dev), GFP_KERNEL);
    if (!fusion_dev) {
        printk(KERN_ERR "Fusion Hat Driver: Failed to allocate memory\n");
        return -ENOMEM;
    }
    
    fusion_dev->client = client;
    i2c_set_clientdata(client, fusion_dev);
    
    // 初始化互斥锁
    mutex_init(&fusion_dev->lock);
    
    // 初始化button_press_time
    fusion_dev->button_press_time = 0;
    
    // 初始化PWM启用状态
    for (int i = 0; i < FUSION_HAT_PWM_CHANNELS; i++) {
        fusion_dev->pwm_enabled[i] = false;
    }
    
    // 创建class - 使用现代API，只有一个参数
    fusion_dev->class = class_create(FUSION_HAT_NAME);
    if (IS_ERR(fusion_dev->class)) {
        ret = PTR_ERR(fusion_dev->class);
        dev_err(&client->dev, "Failed to create class: %d\n", ret);
        return ret;
    }
    
    // 在/sys/class/fusion_hat/下创建设备
    fusion_dev->device = device_create_with_groups(fusion_dev->class, NULL, MKDEV(0, 0), 
                                                 fusion_dev, fusion_hat_attr_groups, 
                                                 FUSION_HAT_NAME);
    if (IS_ERR(fusion_dev->device)) {
        ret = PTR_ERR(fusion_dev->device);
        dev_err(&client->dev, "Failed to create device: %d\n", ret);
        goto error_device;
    }
    
    // 设置设备类型
    fusion_dev->device->type = &fusion_hat_device_type;
    
    // 初始化PWM子系统
    fusion_dev->pwm_chip.ops = &fusion_hat_pwm_ops;
    fusion_dev->pwm_chip.npwm = FUSION_HAT_PWM_CHANNELS;
    
    // 临时注释掉PWM芯片添加，以便驱动可以正常加载
    // ret = pwmchip_add(&fusion_dev->pwm_chip);
    // if (ret < 0) {
    //     dev_err(&client->dev, "Failed to add PWM chip: %d\n", ret);
    //     goto error_pwm;
    // }
    dev_info(&client->dev, "PWM subsystem initialization skipped for testing\n");
    
    // 初始化工作队列
    shutdown_wq = create_workqueue("fusion_hat_shutdown");
    if (!shutdown_wq) {
        ret = -ENOMEM;
        goto error_device;
    }
    
    INIT_WORK(&fusion_dev->shutdown_work, fusion_hat_shutdown_work);
    
    // 初始化电池子系统
    ret = fusion_hat_battery_init(fusion_dev);
    if (ret < 0) {
        dev_err(&client->dev, "Failed to initialize battery subsystem: %d\n", ret);
        goto error_power;
    }
    
    // 创建IIO设备 - 使用adc.c中的实现
    printk(KERN_INFO "Fusion Hat Driver: Creating IIO device using ADC implementation\n");
    ret = fusion_hat_adc_probe(fusion_dev);
    if (ret) {
        printk(KERN_ERR "Fusion Hat Driver: Failed to create ADC IIO device\n");
        goto error_adc;
    }
    
    // 注册中断（假设按键通过GPIO连接）
    fusion_dev->irq = gpio_to_irq(4); // 假设按键连接到GPIO4
    if (fusion_dev->irq >= 0) {
        ret = request_irq(fusion_dev->irq, fusion_hat_irq_handler, 
                         IRQF_TRIGGER_FALLING, "fusion_hat_button", fusion_dev);
        if (ret < 0) {
            dev_warn(&client->dev, "Failed to request IRQ: %d\n", ret);
        }
    }
    
    // 初始化PWM定时器（默认配置）
    fusion_hat_init_pwm_timer(client, 0, 0, 20000); // 定时器0，50Hz
    fusion_hat_init_pwm_timer(client, 1, 0, 20000); // 定时器1，50Hz
    fusion_hat_init_pwm_timer(client, 2, 0, 20000); // 定时器2，50Hz
    
    // 初始化PWM值和定时器设置
    for (int i = 0; i < FUSION_HAT_PWM_CHANNELS; i++) {
        fusion_dev->pwm_values[i] = 0;
    }
    for (int i = 0; i < 3; i++) {
        fusion_dev->timer_periods[i] = 20000;
        fusion_dev->timer_prescalers[i] = 0;
    }
    

    
    printk(KERN_INFO "Fusion Hat Driver: Probe successful, device initialized\n");
    dev_info(&client->dev, "Fusion Hat driver probed successfully\n");
    printk(KERN_INFO "Fusion Hat Driver: Module loaded and ready\n");
    return 0;
    
    error_adc:
    fusion_hat_battery_cleanup(fusion_dev);
    // 如果在IIO设备创建后失败，执行ADC移除操作
    fusion_hat_adc_remove(fusion_dev);
    
    error_power:
        destroy_workqueue(shutdown_wq);
    
    error_device:
        device_destroy(fusion_dev->class, MKDEV(0, 0));
        class_destroy(fusion_dev->class);
    
    return ret;
}

// I2C驱动移除函数
static void fusion_hat_remove(struct i2c_client *client)
{
    struct fusion_hat_dev *dev = i2c_get_clientdata(client);
    
    // 释放中断
    if (dev->irq >= 0) {
        free_irq(dev->irq, dev);
    }
    
    // 清理电池子系统
    fusion_hat_battery_cleanup(dev);
    
    // 清理IIO设备 - 使用adc.c中的实现
    printk(KERN_INFO "Fusion Hat Driver: Cleaning up ADC IIO device\n");
    fusion_hat_adc_remove(dev);
    
    // 销毁工作队列
    destroy_workqueue(shutdown_wq);
    
    // 移除PWM子系统 - 由于在probe中注释了pwmchip_add，这里也需要注释掉pwmchip_remove
    // printk(KERN_INFO "Fusion Hat Driver: Removing PWM chip\n");
    // pwmchip_remove(&dev->pwm_chip);
    
    // 清理device和class
    device_destroy(dev->class, dev->device->devt);
    class_destroy(dev->class);
    
    printk(KERN_INFO "Fusion Hat Driver: Driver removed\n");
    dev_info(&client->dev, "Fusion Hat driver removed\n");
}

// I2C设备ID表
static const struct i2c_device_id fusion_hat_id[] = {
    { FUSION_HAT_NAME, 0x17 }, // 明确指定设备地址
    {}
};
MODULE_DEVICE_TABLE(i2c, fusion_hat_id);

// 设备树匹配表
static const struct of_device_id fusion_hat_of_match[] = {
    { .compatible = "sunfounder,fusion_hat" },
    {}
};
MODULE_DEVICE_TABLE(of, fusion_hat_of_match);

// I2C驱动结构体定义
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

// 添加模块初始化和退出函数，确保dmesg有输出信息
static int __init fusion_hat_init(void)
{
    printk(KERN_INFO "Fusion Hat Driver: Module loading started\n");
    return i2c_add_driver(&fusion_hat_driver);
}

static void __exit fusion_hat_exit(void)
{
    printk(KERN_INFO "Fusion Hat Driver: Module unloading\n");
    i2c_del_driver(&fusion_hat_driver);
}

module_init(fusion_hat_init);
module_exit(fusion_hat_exit);
// 移除自动注册宏，使用显式的初始化和退出函数
// module_i2c_driver(fusion_hat_driver);

// 模块参数，用于调试
static int debug = 1;  // 默认启用调试信息
module_param(debug, int, S_IRUGO);
MODULE_PARM_DESC(debug, "Enable debug messages (default: 1)");

// 移除postcore_initcall以避免重复的模块初始化

MODULE_LICENSE("GPL");
MODULE_AUTHOR("SunFounder");
MODULE_DESCRIPTION("Fusion Hat Driver for Raspberry Pi - Subsystem Integration");
MODULE_VERSION("1.0");

// 添加模块依赖声明
MODULE_IMPORT_NS(IIO);
