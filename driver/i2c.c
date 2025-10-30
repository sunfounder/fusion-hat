/*
 * Fusion Hat I2C Communication Module
 * Contains all I2C communication related implementations
 */

#include "main.h"
#include <linux/i2c.h>
#include <linux/device.h>

/**
 * fusion_hat_i2c_read_byte - Read a single byte from I2C device
 * @client: I2C client handle
 * @cmd: Command byte to send
 * @value: Pointer to store the read result
 * 
 * Returns 0 on success, negative error code on failure.
 */
int fusion_hat_i2c_read_byte(struct i2c_client *client, uint8_t cmd, uint8_t *value) {
    int ret;
    
    if (!client || !value) return -EINVAL;
    
    // Send command and read single byte
    ret = i2c_smbus_read_byte_data(client, cmd);
    if (ret < 0) {
        dev_err(&client->dev, "I2C read byte failed: %d\n", ret);
        return ret;
    }
    
    *value = (uint8_t)ret;
    return 0;
}

/**
 * fusion_hat_i2c_write_byte - Write a single byte to I2C device
 * @client: I2C client handle
 * @cmd: Command byte to send
 * @value: Value to write
 * 
 * Returns 0 on success, negative error code on failure.
 */
int fusion_hat_i2c_write_byte(struct i2c_client *client, uint8_t cmd, uint8_t value) {
    int ret;
    
    if (!client) return -EINVAL;

    // Send command and data
    ret = i2c_smbus_write_byte_data(client, cmd, value);
    if (ret < 0) {
        dev_err(&client->dev, "I2C write byte failed: %d\n", ret);
        return ret;
    }
    
    return 0;
}

/**
 * fusion_hat_i2c_read_word - Read a word (two bytes) from I2C device
 * @client: I2C client handle
 * @cmd: Command byte to send
 * @value: Pointer to store the read result
 * @big_endian: Whether to convert to big-endian format
 * 
 * Returns 0 on success, negative error code on failure.
 */
int fusion_hat_i2c_read_word(struct i2c_client *client, uint8_t cmd, uint16_t *value, bool big_endian) {
    int ret;
    
    if (!client || !value) return -EINVAL;
    
    // Read word using SMBus
    ret = i2c_smbus_read_word_data(client, cmd);
    if (ret < 0) {
        dev_err(&client->dev, "I2C read word failed: %d\n", ret);
        return ret;
    }
    
    // Convert endianness if needed
    if (big_endian) {
        *value = ((ret & 0xFF) << 8) | ((ret >> 8) & 0xFF);
    } else {
        *value = ret;
    }
    return 0;
}

/**
 * fusion_hat_i2c_write_word - Write a word (two bytes) to I2C device
 * @client: I2C client handle
 * @cmd: Command byte to send
 * @value: Value to write
 * @big_endian: Whether input value is big-endian
 * 
 * Returns 0 on success, negative error code on failure.
 */
int fusion_hat_i2c_write_word(struct i2c_client *client, uint8_t cmd, uint16_t value, bool big_endian) {
    int ret;
    
    if (!client) return -EINVAL;
    
    // Convert endianness if needed
    if (big_endian) {
        value = ((value & 0xFF) << 8) | ((value >> 8) & 0xFF);
    }
    
    // Write word using SMBus
    ret = i2c_smbus_write_word_data(client, cmd, value);
    if (ret < 0) {
        dev_err(&client->dev, "I2C write word failed: %d\n", ret);
        return ret;
    }
    
    return 0;
}

/**
 * fusion_hat_i2c_read_block_bytes - Read multiple bytes from I2C device
 * @client: I2C client handle
 * @cmd: Command byte to send
 * @buffer: Buffer to store the read results
 * @len: Number of bytes to read (max 32 bytes)
 * 
 * Returns number of bytes read on success, negative error code on failure.
 */
int fusion_hat_i2c_read_block_bytes(struct i2c_client *client, uint8_t cmd, uint8_t *buffer, uint8_t len) {
    int ret;
    
    if (!client || !buffer || len == 0 || len > 32) return -EINVAL;
    
    // Read multiple bytes using SMBus block read
    ret = i2c_smbus_read_i2c_block_data(client, cmd, len, buffer);
    if (ret < 0) {
        dev_err(&client->dev, "I2C block read failed: %d\n", ret);
        return ret;
    }
    
    return ret;
}

EXPORT_SYMBOL(fusion_hat_i2c_read_byte);
EXPORT_SYMBOL(fusion_hat_i2c_write_byte);
EXPORT_SYMBOL(fusion_hat_i2c_read_word);
EXPORT_SYMBOL(fusion_hat_i2c_write_word);
EXPORT_SYMBOL(fusion_hat_i2c_read_block_bytes);
