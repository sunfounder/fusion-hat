#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/input.h>
#include <linux/workqueue.h>
#include <linux/mutex.h>
#include <linux/i2c.h>
#include "main.h"

#define BUTTON_POLL_INTERVAL 20  // Polling interval in milliseconds

// Button polling work
static DECLARE_DELAYED_WORK(button_poll_work, fusion_hat_button_poll_work);

/**
 * fusion_hat_button_poll_work - Poll button status and report events
 * @work: Pointer to the work structure
 * 
 * Reads button status from hardware via I2C and reports button press/release
 * events to the input subsystem when state changes are detected.
 */
extern struct fusion_hat_dev *fusion_dev;

void fusion_hat_button_poll_work(struct work_struct *work)
{
    struct fusion_hat_dev *dev = fusion_dev;
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

    // Check USR button state (bit 0)
    bool current_state = (button_status & 0x01);
    bool previous_state = (last_status & 0x01);

    if (current_state != previous_state) {
        // Report button event
        input_event(dev->input_dev, EV_KEY, BTN_0, current_state);
        input_event(dev->input_dev, EV_SYN, SYN_REPORT, 0);
        last_status = button_status;
    }

    // Schedule next poll
    schedule_delayed_work(&button_poll_work, msecs_to_jiffies(BUTTON_POLL_INTERVAL));
}

/**
 * fusion_hat_button_init - Initialize button subsystem
 * @dev: Pointer to the Fusion HAT device structure
 * 
 * Returns 0 on success, negative error code on failure.
 */
int fusion_hat_button_init(struct fusion_hat_dev *dev)
{
    int ret;

    // Allocate input device
    dev->input_dev = input_allocate_device();
    if (!dev->input_dev) {
        dev_err(&dev->client->dev, "Failed to allocate input device\n");
        return -ENOMEM;
    }

    // Configure input device
    dev->input_dev->name = "Fusion HAT USR Custom Button";
    dev->input_dev->phys = "fusion-hat/button/0";
    dev->input_dev->id.bustype = BUS_I2C;
    dev->input_dev->dev.parent = &dev->client->dev;

    // Configure button capability
    input_set_capability(dev->input_dev, EV_KEY, BTN_0);

    // Register input device
    ret = input_register_device(dev->input_dev);
    if (ret < 0) {
        dev_err(&dev->client->dev, "Failed to register input device: %d\n", ret);
        input_free_device(dev->input_dev);
        dev->input_dev = NULL;
        return ret;
    }

    // Start button polling
    schedule_delayed_work(&button_poll_work, msecs_to_jiffies(BUTTON_POLL_INTERVAL));

    return 0;
}

/**
 * fusion_hat_button_cleanup - Clean up button subsystem
 * @dev: Pointer to the Fusion HAT device structure
 */
void fusion_hat_button_cleanup(struct fusion_hat_dev *dev)
{
    // Cancel button polling work
    cancel_delayed_work_sync(&button_poll_work);

    // Unregister and free input device
    if (dev->input_dev) {
        input_unregister_device(dev->input_dev);
        dev->input_dev = NULL;
    }
}

/**
 * button_show - Show button status via sysfs
 * @dev: Device pointer
 * @attr: Device attribute
 * @buf: Buffer to store the button status
 * 
 * Returns number of bytes written or error code.
 * Shows USR button state: 0 = not pressed, 1 = pressed.
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
    
    // Return USR button status (bit 0)
    return sprintf(buf, "%u\n", (button_status & 0x01));
}

// Export symbols for use by other modules
EXPORT_SYMBOL(fusion_hat_button_init);
EXPORT_SYMBOL(fusion_hat_button_cleanup);
EXPORT_SYMBOL(fusion_hat_button_poll_work);
EXPORT_SYMBOL(button_show);
