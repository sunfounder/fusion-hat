/*
 * Fusion Hat Driver Header
 * 用于定义共享的数据结构、宏和函数声明
 */

#ifndef FUSION_HAT_H
#define FUSION_HAT_H

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
#include <linux/iio/sysfs.h>
#include <linux/iio/events.h>
#include <linux/iio/buffer.h>
#include <linux/device.h>
#include <linux/sysfs.h>
#include <linux/kobject.h>
#include <linux/pwm.h>
#include <linux/of.h>
#include <linux/of_device.h>

// 设备名称和I2C地址
#define FUSION_HAT_NAME "fusion_hat"
#define FUSION_HAT_I2C_ADDR 0x17

// 命令定义 - ADC相关
#define CMD_READ_ADC_BASE 0x10 // ADC基础地址
#define CMD_READ_A0_H 0x10 // ADC0 高位数据
#define CMD_READ_A0_L 0x11 // ADC0 低位数据
#define CMD_READ_A1_H 0x12 // ADC1 高位数据
#define CMD_READ_A1_L 0x13 // ADC1 低位数据
#define CMD_READ_A2_H 0x14 // ADC2 高位数据
#define CMD_READ_A2_L 0x15 // ADC2 低位数据
#define CMD_READ_A3_H 0x16 // ADC3 高位数据
#define CMD_READ_A3_L 0x17 // ADC3 低位数据
#define CMD_READ_BATTERY_H 0x18 // 电池电压ADC 高位数据
#define CMD_READ_BATTERY_L 0x19 // 电池电压ADC 低位数据

// PWM
#define CMD_SET_TIMER_PRESCALER_BASE 0x40 // 定时器预分频器基础地址
#define CMD_SET_TIMER0_PRESCALER_H 0x40  // 定时器0预分频器 高位 PWM0-3
#define CMD_SET_TIMER0_PRESCALER_L 0x41  // 定时器0预分频器 低位 PWM0-3
#define CMD_SET_TIMER1_PRESCALER_H 0x42  // 定时器1预分频器 高位 PWM4-7
#define CMD_SET_TIMER1_PRESCALER_L 0x43  // 定时器1预分频器 低位 PWM4-7
#define CMD_SET_TIMER2_PRESCALER_H 0x44  // 定时器2预分频器 高位 PWM8-11
#define CMD_SET_TIMER2_PRESCALER_L 0x45  // 定时器2预分频器 低位 PWM8-11

#define CMD_SET_TIMER_PERIOD_BASE 0x50 // 定时器周期寄存器基础地址
#define CMD_SET_TIMER0_PERIOD_H 0x50  // 定时器0周期寄存器 高位 PWM0-3
#define CMD_SET_TIMER0_PERIOD_L 0x51  // 定时器0周期寄存器 低位 PWM0-3
#define CMD_SET_TIMER1_PERIOD_H 0x52  // 定时器1周期寄存器 高位 PWM4-7
#define CMD_SET_TIMER1_PERIOD_L 0x53  // 定时器1周期寄存器 低位 PWM4-7
#define CMD_SET_TIMER2_PERIOD_H 0x54  // 定时器2周期寄存器 高位 PWM8-11
#define CMD_SET_TIMER2_PERIOD_L 0x55  // 定时器2周期寄存器 低位 PWM8-11

#define CMD_SET_PWM_VALUE_BASE 0x60  // PWM值寄存器基础地址
#define CMD_SET_PWM0_VALUE_H 0x60  // PWM0值寄存器，高位
#define CMD_SET_PWM0_VALUE_L 0x61  // PWM0值寄存器，低位
#define CMD_SET_PWM1_VALUE_H 0x62  // PWM1值寄存器，高位
#define CMD_SET_PWM1_VALUE_L 0x63  // PWM1值寄存器，低位
#define CMD_SET_PWM2_VALUE_H 0x64  // PWM2值寄存器，高位
#define CMD_SET_PWM2_VALUE_L 0x65  // PWM2值寄存器，低位
#define CMD_SET_PWM3_VALUE_H 0x66  // PWM3值寄存器，高位
#define CMD_SET_PWM3_VALUE_L 0x67  // PWM3值寄存器，低位
#define CMD_SET_PWM4_VALUE_H 0x68  // PWM4值寄存器，高位
#define CMD_SET_PWM4_VALUE_L 0x69  // PWM4值寄存器，低位
#define CMD_SET_PWM5_VALUE_H 0x6A  // PWM5值寄存器，高位
#define CMD_SET_PWM5_VALUE_L 0x6B  // PWM5值寄存器，低位
#define CMD_SET_PWM6_VALUE_H 0x6C  // PWM6值寄存器，高位
#define CMD_SET_PWM6_VALUE_L 0x6D  // PWM6值寄存器，低位
#define CMD_SET_PWM7_VALUE_H 0x6E  // PWM7值寄存器，高位
#define CMD_SET_PWM7_VALUE_L 0x6F  // PWM7值寄存器，低位
#define CMD_SET_PWM8_VALUE_H 0x70  // PWM8值寄存器，高位
#define CMD_SET_PWM8_VALUE_L 0x71  // PWM8值寄存器，低位
#define CMD_SET_PWM9_VALUE_H 0x72  // PWM9值寄存器，高位
#define CMD_SET_PWM9_VALUE_L 0x73  // PWM9值寄存器，低位
#define CMD_SET_PWM10_VALUE_H 0x74  // PWM10值寄存器，高位
#define CMD_SET_PWM10_VALUE_L 0x75  // PWM10值寄存器，低位
#define CMD_SET_PWM11_VALUE_H 0x76  // PWM11值寄存器，高位
#define CMD_SET_PWM11_VALUE_L 0x77  // PWM11值寄存器，低位
// Sensor
#define CMD_READ_BUTTON_STATUS 0x24    // 8位，1表示按下，0表示松开
#define CMD_READ_CHARGING_STATUS 0x25  // 8位，1表示充电中，0表示未充电
#define CMD_READ_SHUTDOWN_STATUS 0x26  // 8位，0表示没有关机请求，1表示底电池电量关机请求，2表示按键关机请求
// Control
#define CMD_CONTROL_LED 0x30           // 8位，1表示点亮，0表示熄灭
#define CMD_CONTROL_SPEAKER 0x31       // 8位，1表示开启，0表示关闭
// System
#define CMD_READ_FIRMWARE_VERSION 0x05 // 24位 固件版本号

// 常量定义
#define ADC_REFERENCE_VOLTAGE 3300 // ADC参考电压 3.3V
#define ADC_MAX_VALUE 4095 // ADC最大数值 12位
#define BATTERY_DIVIDER 3 // 电池电压 divider，比例
#define BATTERY_MAX_VOLTAGE 8400 // 电池最大电压 8.4V
#define BATTERY_MIN_VOLTAGE 6400 // 电池最小电压 6.4V
#define SHUTDOWN_REQUEST_NONE 0 // 无关机请求
#define SHUTDOWN_REQUEST_BATTERY 1 // 电池电量关机请求
#define SHUTDOWN_REQUEST_BUTTON 2 // 按键关机请求
#define PWM_CORE_FREQUENCY 72000000 // PWM核心频率 72MHz
#define PWM_DEFAULT_PRESCALER 22 // 默认PWM预分频器值 22
#define PWM_PERIOD_VALUE 65535 // 默认PWM周期 65535 us
#define PWM_TIMER_COUNT 3 // 定时器数量

// PWM通道数量
#define FUSION_HAT_PWM_CHANNELS 12


// IIO通道定义
struct fusion_hat_iio_channel {
    struct fusion_hat_dev *fusion_dev;
    int channel;
    struct iio_dev *indio_dev; // IIO设备指针
};

// IIO设备数组大小定义
#define FUSION_HAT_NUM_ADC_CHANNELS 4

// 主设备结构体
struct fusion_hat_dev {
    struct i2c_client *client;
    struct class *class;
    struct device *device;
    struct mutex lock;
    // PWM相关
    bool pwm_enabled[FUSION_HAT_PWM_CHANNELS];
    uint32_t pwm_duty_cycles[FUSION_HAT_PWM_CHANNELS];
    uint32_t pwm_periods[FUSION_HAT_PWM_CHANNELS];
    uint32_t pwm_values[FUSION_HAT_PWM_CHANNELS];
    uint16_t timer_periods[PWM_TIMER_COUNT];
    uint16_t timer_prescalers[PWM_TIMER_COUNT];
    // 电池相关
    struct power_supply *battery;
    struct power_supply_desc battery_desc;
    bool charging;          // 充电状态
    int battery_level;      // 电池电量百分比
    int battery_voltage;    // 电池电压（mV）
    // ADC相关
    struct iio_dev *iio_devs[FUSION_HAT_NUM_ADC_CHANNELS];
    // Button
    struct input_dev *input_dev;   // Input device for buttons
    // LED
    uint8_t led_status;      // LED状态（0=关闭，1=开启）
    // Speaker
    uint8_t speaker_status;  // 扬声器状态（0=关闭，1=开启）
};

// 外部变量声明
extern struct fusion_hat_dev *fusion_dev;
// 主工作队列
extern struct workqueue_struct *main_wq;

// PWM相关函数声明
extern int fusion_hat_pwm_probe(struct fusion_hat_dev *dev);
extern void fusion_hat_pwm_remove(struct fusion_hat_dev *dev);

// I2C通信函数声明
extern int fusion_hat_i2c_read_byte(struct i2c_client *client, uint8_t cmd, uint8_t *value);
extern int fusion_hat_i2c_write_byte(struct i2c_client *client, uint8_t cmd, uint8_t value);
extern int fusion_hat_i2c_read_word(struct i2c_client *client, uint8_t cmd, uint16_t *value, bool big_endian);
extern int fusion_hat_i2c_write_word(struct i2c_client *client, uint8_t cmd, uint16_t value, bool big_endian);
extern int fusion_hat_i2c_read_block_bytes(struct i2c_client *client, uint8_t cmd, uint8_t *buffer, uint8_t len);

// ADC相关函数声明
extern int fusion_hat_read_adc(struct i2c_client *client, int channel, uint16_t *value);
extern int fusion_hat_create_iio_devices(struct fusion_hat_dev *fusion_dev);
extern void fusion_hat_cleanup_iio_devices(struct fusion_hat_dev *fusion_dev);

// ADC IIO子系统函数
extern int fusion_hat_adc_probe(struct fusion_hat_dev *dev);
extern void fusion_hat_adc_remove(struct fusion_hat_dev *dev);

// 电池子系统函数
extern int fusion_hat_battery_init(struct fusion_hat_dev *dev);
extern void fusion_hat_battery_cleanup(struct fusion_hat_dev *dev);
extern void fusion_hat_update_battery_status(struct fusion_hat_dev *dev);

// 按钮相关函数
extern int fusion_hat_button_init(struct fusion_hat_dev *dev);
extern void fusion_hat_button_cleanup(struct fusion_hat_dev *dev);
extern void fusion_hat_button_poll_work(struct work_struct *work);
extern ssize_t button_show(struct device *dev, struct device_attribute *attr, char *buf);

// 关机控制函数
extern int fusion_hat_check_hardware_shutdown_request(struct fusion_hat_dev *dev);
extern void fusion_hat_execute_shutdown(struct fusion_hat_dev *dev, int request_type);
extern void fusion_hat_shutdown_request_work(struct fusion_hat_dev *dev);

// LED相关函数
extern int fusion_hat_led_init(struct fusion_hat_dev *dev);
extern void fusion_hat_led_cleanup(struct fusion_hat_dev *dev);
extern ssize_t led_show(struct device *dev, struct device_attribute *attr, char *buf);
extern ssize_t led_store(struct device *dev, struct device_attribute *attr, const char *buf, size_t count);

#endif /* FUSION_HAT_H */