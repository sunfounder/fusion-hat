/**
 * @file main.h
 * @brief Fusion Hat Driver Header
 *
 * This header defines shared data structures, macros, and function declarations
 * for the Fusion Hat driver modules.
 */

#ifndef FUSION_HAT_H
#define FUSION_HAT_H

#include <linux/module.h>
#include <linux/i2c.h>
#include <linux/kernel.h>
#include <linux/mutex.h>
#include <linux/workqueue.h>
#include <linux/power_supply.h>
#include <linux/iio/iio.h>
#include <linux/device.h>
#include <linux/sysfs.h>
#include <linux/kobject.h>
#include <linux/pwm.h>
#include <linux/of.h>
#include <linux/input.h>

// Driver version
#define VERSION "1.0.0-a2"

// Device name and I2C address
#define FUSION_HAT_NAME "fusion_hat"
#define FUSION_HAT_I2C_ADDR 0x17

// Command definitions - ADC related
#define CMD_READ_ADC_BASE 0x10          // ADC base address
#define CMD_READ_A0_H 0x10              // ADC0 high byte
#define CMD_READ_A0_L 0x11              // ADC0 low byte
#define CMD_READ_A1_H 0x12              // ADC1 high byte
#define CMD_READ_A1_L 0x13              // ADC1 low byte
#define CMD_READ_A2_H 0x14              // ADC2 high byte
#define CMD_READ_A2_L 0x15              // ADC2 low byte
#define CMD_READ_A3_H 0x16              // ADC3 high byte
#define CMD_READ_A3_L 0x17              // ADC3 low byte
#define CMD_READ_BATTERY_H 0x18         // Battery voltage ADC high byte
#define CMD_READ_BATTERY_L 0x19         // Battery voltage ADC low byte

// PWM commands
#define CMD_SET_TIMER_PRESCALER_BASE 0x40  // Timer prescaler base address
#define CMD_SET_TIMER0_PRESCALER_H 0x40     // Timer0 prescaler high byte (PWM0-3)
#define CMD_SET_TIMER0_PRESCALER_L 0x41     // Timer0 prescaler low byte (PWM0-3)
#define CMD_SET_TIMER1_PRESCALER_H 0x42     // Timer1 prescaler high byte (PWM4-7)
#define CMD_SET_TIMER1_PRESCALER_L 0x43     // Timer1 prescaler low byte (PWM4-7)
#define CMD_SET_TIMER2_PRESCALER_H 0x44     // Timer2 prescaler high byte (PWM8-11)
#define CMD_SET_TIMER2_PRESCALER_L 0x45     // Timer2 prescaler low byte (PWM8-11)

#define CMD_SET_TIMER_PERIOD_BASE 0x50      // Timer period register base address
#define CMD_SET_TIMER0_PERIOD_H 0x50        // Timer0 period register high byte
#define CMD_SET_TIMER0_PERIOD_L 0x51        // Timer0 period register low byte
#define CMD_SET_TIMER1_PERIOD_H 0x52        // Timer1 period register high byte
#define CMD_SET_TIMER1_PERIOD_L 0x53        // Timer1 period register low byte
#define CMD_SET_TIMER2_PERIOD_H 0x54        // Timer2 period register high byte
#define CMD_SET_TIMER2_PERIOD_L 0x55        // Timer2 period register low byte

#define CMD_SET_PWM_VALUE_BASE 0x60         // PWM value register base address
#define CMD_SET_PWM0_VALUE_H 0x60           // PWM0 value register high byte
#define CMD_SET_PWM0_VALUE_L 0x61           // PWM0 value register low byte
#define CMD_SET_PWM1_VALUE_H 0x62           // PWM1 value register high byte
#define CMD_SET_PWM1_VALUE_L 0x63           // PWM1 value register low byte
#define CMD_SET_PWM2_VALUE_H 0x64           // PWM2 value register high byte
#define CMD_SET_PWM2_VALUE_L 0x65           // PWM2 value register low byte
#define CMD_SET_PWM3_VALUE_H 0x66           // PWM3 value register high byte
#define CMD_SET_PWM3_VALUE_L 0x67           // PWM3 value register low byte
#define CMD_SET_PWM4_VALUE_H 0x68           // PWM4 value register high byte
#define CMD_SET_PWM4_VALUE_L 0x69           // PWM4 value register low byte
#define CMD_SET_PWM5_VALUE_H 0x6A           // PWM5 value register high byte
#define CMD_SET_PWM5_VALUE_L 0x6B           // PWM5 value register low byte
#define CMD_SET_PWM6_VALUE_H 0x6C           // PWM6 value register high byte
#define CMD_SET_PWM6_VALUE_L 0x6D           // PWM6 value register low byte
#define CMD_SET_PWM7_VALUE_H 0x6E           // PWM7 value register high byte
#define CMD_SET_PWM7_VALUE_L 0x6F           // PWM7 value register low byte
#define CMD_SET_PWM8_VALUE_H 0x70           // PWM8 value register high byte
#define CMD_SET_PWM8_VALUE_L 0x71           // PWM8 value register low byte
#define CMD_SET_PWM9_VALUE_H 0x72           // PWM9 value register high byte
#define CMD_SET_PWM9_VALUE_L 0x73           // PWM9 value register low byte
#define CMD_SET_PWM10_VALUE_H 0x74          // PWM10 value register high byte
#define CMD_SET_PWM10_VALUE_L 0x75          // PWM10 value register low byte
#define CMD_SET_PWM11_VALUE_H 0x76          // PWM11 value register high byte
#define CMD_SET_PWM11_VALUE_L 0x77          // PWM11 value register low byte

// Sensor commands
#define CMD_READ_BUTTON_STATUS 0x24        // 8-bit, 1=pressed, 0=released
#define CMD_READ_CHARGING_STATUS 0x25      // 8-bit, 1=charging, 0=not charging
#define CMD_READ_SHUTDOWN_STATUS 0x26      // 8-bit, shutdown request type

// Control commands
#define CMD_CONTROL_LED 0x30               // 8-bit, 1=on, 0=off
#define CMD_CONTROL_SPEAKER 0x31           // 8-bit, 1=on, 0=off

// System commands
#define CMD_READ_FIRMWARE_VERSION 0x05     // 24-bit firmware version

// Constant definitions
#define ADC_REFERENCE_VOLTAGE 3300         // ADC reference voltage (3.3V)
#define ADC_MAX_VALUE 4095                 // ADC max value (12-bit)
#define BATTERY_DIVIDER 3                  // Battery voltage divider ratio
#define BATTERY_MAX_VOLTAGE 8400           // Battery max voltage (8.4V)
#define BATTERY_MIN_VOLTAGE 6400           // Battery min voltage (6.4V)
#define SHUTDOWN_REQUEST_NONE 0            // No shutdown request
#define SHUTDOWN_REQUEST_BATTERY 1         // Low battery shutdown request
#define SHUTDOWN_REQUEST_BUTTON 2          // Button shutdown request
#define PWM_CORE_FREQUENCY 72000000        // PWM core frequency (72MHz)
#define PWM_DEFAULT_PRESCALER 22           // Default PWM prescaler
#define PWM_PERIOD_VALUE 65535             // PWM period value (16-bit resolution)
#define PWM_DEFAULT_PERIOD 20000           // Default PWM period (20ms)
#define PWM_TIMER_COUNT 3                  // Number of timers

// PWM channel count
#define FUSION_HAT_PWM_CHANNELS 12

/**
 * @brief IIO channel definition structure
 */
struct fusion_hat_iio_channel {
    struct fusion_hat_dev *fusion_dev;
    int channel;
    struct iio_dev *indio_dev;
};

// IIO device array size definition
#define FUSION_HAT_NUM_ADC_CHANNELS 4

/**
 * @brief Main device structure for Fusion Hat
 * 
 * Contains all necessary data and state for Fusion Hat functionality.
 */
struct fusion_hat_dev {
    struct i2c_client *client;
    struct class *class;
    struct device *device;
    struct mutex lock;
    
    // PWM related
    bool pwm_enabled[FUSION_HAT_PWM_CHANNELS];
    uint32_t pwm_duty_cycles[FUSION_HAT_PWM_CHANNELS];
    uint32_t pwm_periods[FUSION_HAT_PWM_CHANNELS];
    uint32_t pwm_values[FUSION_HAT_PWM_CHANNELS];
    uint16_t timer_periods[PWM_TIMER_COUNT];
    uint16_t timer_prescalers[PWM_TIMER_COUNT];
    
    // Battery related
    struct power_supply *battery;
    struct power_supply_desc battery_desc;
    bool charging;          // Charging status
    int battery_level;      // Battery level percentage
    int battery_voltage;    // Battery voltage (mV)
    
    // ADC related
    struct iio_dev *iio_devs[FUSION_HAT_NUM_ADC_CHANNELS];
    
    // Button
    struct input_dev *input_dev;
    
    // LED
    uint8_t led_status;     // LED status (0=off, 1=on)
    struct kobject led_kobj;
    
    // Speaker
    uint8_t speaker_status; // Speaker status (0=off, 1=on)
};

// External variable declarations
extern struct fusion_hat_dev *fusion_dev;
extern struct workqueue_struct *main_wq;

// Function declarations
// PWM
int fusion_hat_pwm_probe(struct fusion_hat_dev *dev);
void fusion_hat_pwm_remove(struct fusion_hat_dev *dev);

// I2C communication
int fusion_hat_i2c_read_byte(struct i2c_client *client, uint8_t cmd, uint8_t *value);
int fusion_hat_i2c_write_byte(struct i2c_client *client, uint8_t cmd, uint8_t value);
int fusion_hat_i2c_read_word(struct i2c_client *client, uint8_t cmd, uint16_t *value, bool big_endian);
int fusion_hat_i2c_write_word(struct i2c_client *client, uint8_t cmd, uint16_t value, bool big_endian);
int fusion_hat_i2c_read_block_bytes(struct i2c_client *client, uint8_t cmd, uint8_t *buffer, uint8_t len);

// ADC
int fusion_hat_read_adc(struct i2c_client *client, int channel, uint16_t *value);
int fusion_hat_create_iio_devices(struct fusion_hat_dev *fusion_dev);
void fusion_hat_cleanup_iio_devices(struct fusion_hat_dev *fusion_dev);

// ADC IIO subsystem
int fusion_hat_adc_probe(struct fusion_hat_dev *dev);
void fusion_hat_adc_remove(struct fusion_hat_dev *dev);

// Battery subsystem
int fusion_hat_battery_init(struct fusion_hat_dev *dev);
void fusion_hat_battery_cleanup(struct fusion_hat_dev *dev);
void fusion_hat_update_battery_status(struct fusion_hat_dev *dev);

// Button
int fusion_hat_button_init(struct fusion_hat_dev *dev);
void fusion_hat_button_cleanup(struct fusion_hat_dev *dev);
void fusion_hat_button_poll_work(struct work_struct *work);
ssize_t button_show(struct device *dev, struct device_attribute *attr, char *buf);

// Shutdown control
int fusion_hat_check_hardware_shutdown_request(struct fusion_hat_dev *dev);
void fusion_hat_execute_shutdown(struct fusion_hat_dev *dev, int request_type);
void fusion_hat_shutdown_request_work(struct fusion_hat_dev *dev);

// LED
int fusion_hat_led_init(struct fusion_hat_dev *dev);
void fusion_hat_led_cleanup(struct fusion_hat_dev *dev);

#endif /* FUSION_HAT_H */