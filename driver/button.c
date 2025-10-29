#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/input.h>  // For input subsystem and KEY_* definitions
#include <linux/interrupt.h>
#include <linux/workqueue.h>
#include <linux/mutex.h>
#include <linux/i2c.h>
#include "main.h"

#define BUTTON_POLL_INTERVAL 20  // 20ms polling interval

// Button polling work
static DECLARE_DELAYED_WORK(button_poll_work, fusion_hat_button_poll_work);

/**
 * @brief Button status polling work function
 * @param work Pointer to the work structure
 * 
 * This function reads the button status from hardware and reports button events
 * to the input subsystem.
 */
extern struct fusion_hat_dev *fusion_dev; // Reference to global device structure

void fusion_hat_button_poll_work(struct work_struct *work)
{
    struct fusion_hat_dev *dev = fusion_dev;  // Get global device reference
    uint8_t button_status;
    static uint8_t last_status = 0;

    if (!dev || !dev->input_dev) {
        schedule_delayed_work(&button_poll_work, msecs_to_jiffies(BUTTON_POLL_INTERVAL));
        return;
    }

    mutex_lock(&dev->lock);
    int ret = fusion_hat_i2c_read_byte(dev->client, CMD_READ_BUTTON_STATUS, &button_status);
    mutex_unlock(&dev->lock);

    if (ret < 0) {
        dev_err(&dev->client->dev, "Failed to read button status: %d\n", ret);
        schedule_delayed_work(&button_poll_work, msecs_to_jiffies(BUTTON_POLL_INTERVAL));
        return;
    }

    // Only check the first bit (USR button)
    bool current_state = (button_status & 0x01); // 0 = not pressed, 1 = pressed
    bool previous_state = (last_status & 0x01);

    if (current_state != previous_state) {
        // Report button press/release events with proper input events sequence
        input_event(dev->input_dev, EV_KEY, BTN_0, current_state);
        input_event(dev->input_dev, EV_SYN, SYN_REPORT, 0);
        last_status = button_status;
        dev_dbg(&dev->client->dev, "Button event: %s\n", current_state ? "pressed" : "released");
    }

    // Schedule next poll
    schedule_delayed_work(&button_poll_work, msecs_to_jiffies(BUTTON_POLL_INTERVAL));
}

/**
 * @brief Initialize the button subsystem
 * @param dev Pointer to the Fusion HAT device structure
 * @return 0 on success, negative error code on failure
 */
int fusion_hat_button_init(struct fusion_hat_dev *dev)
{
    int ret;

    dev_info(&dev->client->dev, "Initializing button subsystem\n");

    // Allocate input device
    dev->input_dev = input_allocate_device();
    if (!dev->input_dev) {
        dev_err(&dev->client->dev, "Failed to allocate input device\n");
        return -ENOMEM;
    }

    // Set input device name
    dev->input_dev->name = "Fusion HAT USR Custom Button";
    
    // Set phys name to indicate it's a custom button, not a keyboard
    dev->input_dev->phys = "fusion-hat/button/0";
    dev->input_dev->id.bustype = BUS_I2C;
    dev->input_dev->dev.parent = &dev->client->dev;

    // Set up capabilities - only one button (USR)
    input_set_capability(dev->input_dev, EV_KEY, BTN_0); // Use BTN_0 (generic button) instead of keyboard key

    // Register input device
    ret = input_register_device(dev->input_dev);
    if (ret < 0) {
        dev_err(&dev->client->dev, "Failed to register input device: %d\n", ret);
        input_free_device(dev->input_dev);
        dev->input_dev = NULL;
        return ret;
    }

    // Schedule next poll - this is required since we're reading from I2C device
    // which doesn't have hardware interrupt line exposed to host
    schedule_delayed_work(&button_poll_work, msecs_to_jiffies(BUTTON_POLL_INTERVAL));

    dev_info(&dev->client->dev, "USR button initialized successfully\n");
    return 0;
}

/**
 * @brief Clean up the button subsystem
 * @param dev Pointer to the Fusion HAT device structure
 */
void fusion_hat_button_cleanup(struct fusion_hat_dev *dev)
{
    dev_info(&dev->client->dev, "Cleaning up USR button\n");

    // Cancel button polling
    cancel_delayed_work_sync(&button_poll_work);

    // Unregister and free input device
    if (dev->input_dev) {
        input_unregister_device(dev->input_dev);
        dev->input_dev = NULL;
    }

    dev_info(&dev->client->dev, "Button subsystem cleanup completed\n");
}

/**
 * @brief Button status show function for sysfs
 * @param dev Device pointer
 * @param attr Device attribute
 * @param buf Buffer to store the button status
 * @return Number of bytes written or error code
 * 
 * Only USR button is available: 0 = not pressed, 1 = pressed
 */
ssize_t button_show(struct device *dev, struct device_attribute *attr, char *buf)
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
    
    // Only return the status of the USR button (bit 0)
    return sprintf(buf, "%u\n", (button_status & 0x01));
}

// Export symbols for use by other modules
EXPORT_SYMBOL(fusion_hat_button_init);
EXPORT_SYMBOL(fusion_hat_button_cleanup);
EXPORT_SYMBOL(fusion_hat_button_poll_work);
EXPORT_SYMBOL(button_show);
