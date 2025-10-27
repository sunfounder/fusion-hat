/*
 * Fusion Hat I2C通信模块
 * 包含所有I2C通信相关的功能实现
 */

#include "main.h"

/*
 * 从I2C设备读取一个字节
 * @client: I2C客户端
 * @cmd: 命令字节
 * @value: 存储读取结果的指针
 * @return: 成功返回0，失败返回错误码
 */
int fusion_hat_i2c_read_byte(struct i2c_client *client, uint8_t cmd, uint8_t *value)
{
    int ret;
    
    if (!client || !value) {
        return -EINVAL;
    }
    
    // 发送命令并读取单个字节
    ret = i2c_smbus_read_byte_data(client, cmd);
    if (ret < 0) {
        dev_err(&client->dev, "I2C read byte failed: %d\n", ret);
        return ret;
    }
    
    *value = (uint8_t)ret;
    return 0;
}
EXPORT_SYMBOL(fusion_hat_i2c_read_byte);

/*
 * 向I2C设备写入一个字节
 * @client: I2C客户端
 * @cmd: 命令字节
 * @value: 要写入的值
 * @return: 成功返回0，失败返回错误码
 */
int fusion_hat_i2c_write_byte(struct i2c_client *client, uint8_t cmd, uint8_t value)
{
    int ret;
    
    if (!client) {
        return -EINVAL;
    }
    
    // 发送命令和数据
    ret = i2c_smbus_write_byte_data(client, cmd, value);
    if (ret < 0) {
        dev_err(&client->dev, "I2C write byte failed: %d\n", ret);
        return ret;
    }
    
    return 0;
}
EXPORT_SYMBOL(fusion_hat_i2c_write_byte);

/*
 * 从I2C设备读取一个字（两个字节）
 * @client: I2C客户端
 * @cmd: 命令字节
 * @value: 存储读取结果的指针
 * @return: 成功返回0，失败返回错误码
 */
int fusion_hat_i2c_read_word(struct i2c_client *client, uint8_t cmd, uint16_t *value, bool big_endian)
{
    int ret;
    
    if (!client || !value) {
        return -EINVAL;
    }
    
    // 直接使用SMBus读取一个字
    ret = i2c_smbus_read_word_data(client, cmd);
    if (ret < 0) {
        dev_err(&client->dev, "I2C read word failed: %d\n", ret);
        return ret;
    }
    
    // i2c_smbus_read_word_data默认返回的数据是小端格式
    // 我们需要将其转换为我们需要的大端格式
    if (!big_endian) {
        *value = ((ret & 0xFF) << 8) | ((ret >> 8) & 0xFF);
    } else {
        *value = ret;
    }
    return 0;
}
EXPORT_SYMBOL(fusion_hat_i2c_read_word);

/*
 * 向I2C设备写入一个字（两个字节）
 * @client: I2C客户端
 * @cmd: 命令字节
 * @value: 要写入的值
 * @return: 成功返回0，失败返回错误码
 */
int fusion_hat_i2c_write_word(struct i2c_client *client, uint8_t cmd, uint16_t value, bool big_endian)
{
    int ret;
    
    if (!client) {
        return -EINVAL;
    }
    
    // 将大端格式转换为SMBus需要的小端格式
    if (!big_endian) {
        value = ((value & 0xFF) << 8) | ((value >> 8) & 0xFF);
    }
    
    // 直接使用SMBus写入一个字
    ret = i2c_smbus_write_word_data(client, cmd, value);
    if (ret < 0) {
        dev_err(&client->dev, "I2C write word failed: %d\n", ret);
        return ret;
    }
    
    return 0;
}
EXPORT_SYMBOL(fusion_hat_i2c_write_word);

/*
 * 从I2C设备一次性读取多个字节（使用I2C块读取功能）
 * @client: I2C客户端
 * @cmd: 命令字节
 * @buffer: 存储读取结果的缓冲区
 * @len: 要读取的字节数（最大32字节）
 * @return: 成功返回读取的字节数，失败返回错误码
 */
int fusion_hat_i2c_read_block_bytes(struct i2c_client *client, uint8_t cmd, uint8_t *buffer, uint8_t len)
{
    int ret;
    
    if (!client || !buffer || len == 0 || len > 32) {
        return -EINVAL;
    }
    
    // 使用i2c_smbus_read_i2c_block_data一次性读取多个字节
    ret = i2c_smbus_read_i2c_block_data(client, cmd, len, buffer);
    if (ret < 0) {
        dev_err(&client->dev, "I2C block read failed: %d\n", ret);
        return ret;
    }
    
    return ret;
}
EXPORT_SYMBOL(fusion_hat_i2c_read_block_bytes);
