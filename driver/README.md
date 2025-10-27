# Fusion Hat Linux 内核驱动 - 子系统集成版本

本驱动为树莓派上的 Fusion Hat 硬件模块提供 Linux 内核级支持，实现了电池管理、多通道 ADC 读取、多通道 PWM 控制、按键和 LED 功能。本版本使用Linux标准子系统，PWM功能集成到PWM子系统，其他功能通过sysfs接口提供。

## 功能特性

- ✅ **电池管理**：自动监控电池电压、电量，支持低电量提醒和自动关机
- ✅ **电源管理集成**：与 upower 集成，在桌面状态栏显示电池信息
- ✅ **多通道 ADC 读取**：支持读取 4 个通道的模拟量值（如传感器数据）
- ✅ **多通道 PWM 控制**：支持 12 个 PWM 通道，集成到Linux PWM子系统
- ✅ **按键支持**：通过 I2C 读取按键状态，支持多位按键和长按关机
- ✅ **LED 和喇叭控制**：支持控制板载 LED 和喇叭
- ✅ **I2C 通信**：基于 I2C 协议与硬件通信，使用新的寄存器接口
- ✅ **设备树支持**：通过设备树覆盖文件加载驱动
- ✅ **关机信号处理**：支持三种关机信号（无关机请求、低电量关机、按键关机）
- ✅ **子系统集成接口**：使用Linux标准PWM子系统和sysfs接口提供设备访问

## 接口说明

### 1. PWM子系统接口

PWM功能已集成到Linux PWM子系统，通过标准PWM接口访问：

- PWM设备位置：`/sys/class/pwm/`
- 每个PWM通道命名为：`pwmchipX:pwmY`（X为PWM芯片ID，Y为通道号0-11）

#### 使用方法

```bash
# 导出PWM通道0
sudo echo 0 > /sys/class/pwm/pwmchipX/export

# 设置周期 (纳秒)
sudo echo 20000000 > /sys/class/pwm/pwmchipX:pwm0/period

# 设置占空比 (纳秒)
sudo echo 10000000 > /sys/class/pwm/pwmchipX:pwm0/duty_cycle

# 启用PWM
sudo echo 1 > /sys/class/pwm/pwmchipX:pwm0/enable

# 禁用PWM
sudo echo 0 > /sys/class/pwm/pwmchipX:pwm0/enable

# 取消导出PWM通道
sudo echo 0 > /sys/class/pwm/pwmchipX/unexport
```

### 2. Sysfs接口

其他功能通过sysfs接口在`/sys/class/fusion_hat/fusion_hat/`目录下提供：

- `A0`, `A1`, `A2`, `A3` - 4个ADC通道读取
- `button` - 按钮状态
- `charging` - 充电状态
- `battery_voltage` - 电池电压
- `led` - LED控制
- `speaker` - 扬声器控制
- `firmware_version` - 固件版本号

## 使用方法

### 读取ADC值

ADC文件以"ADC原始值 电压值(mV)"的格式返回数据：

```bash
# 读取ADC0的值
cat /sys/class/fusion_hat/fusion_hat/A0
# 输出示例: 2048 1650  (表示ADC原始值为2048，电压为1650mV)
```

### 读取传感器数据

```bash
# 读取按钮状态
cat /sys/class/fusion_hat/fusion_hat/button

# 读取充电状态
cat /sys/class/fusion_hat/fusion_hat/charging

# 读取电池电压 (mV)
cat /sys/class/fusion_hat/fusion_hat/battery_voltage

# 读取固件版本号
cat /sys/class/fusion_hat/fusion_hat/firmware_version
```

### 控制功能

```bash
# 控制LED (0: 关闭, 1: 打开)
sudo echo 1 > /sys/class/fusion_hat/fusion_hat/led

# 控制扬声器 (0: 关闭, 1: 打开)
sudo echo 1 > /sys/class/fusion_hat/fusion_hat/speaker
```

## 安装驱动

### 编译与安装

1. 确保已安装内核开发工具

   ```bash
   sudo apt-get update
   sudo apt-get install build-essential linux-headers-$(uname -r)
   ```

2. 编译驱动程序：
   ```
   cd /path/to/fusion_hat/driver
   make
   ```

3. 安装驱动程序：
   ```
   sudo make install
   ```

4. 加载模块：
   ```
   sudo modprobe fusion_hat
   ```

### 卸载驱动

```bash
sudo modprobe -r fusion_hat
sudo make uninstall
```

### 疑难解答

1. **接口不存在**：
   - 确保驱动已正确加载：`lsmod | grep fusion_hat`
   - 检查是否有错误信息：`dmesg | grep fusion_hat`
   - 检查sysfs接口：`ls -la /sys/class/fusion_hat/fusion_hat/`
   - 检查PWM接口：`ls -la /sys/class/pwm/`

2. **权限问题**：
   - 使用sudo访问sysfs接口
   - 可创建udev规则设置合适的权限

3. **编译错误**：
   - 确保已安装匹配当前内核版本的头文件：`linux-headers-$(uname -r)`

4. **PWM子系统相关**：
   - 确认PWM芯片已注册：`ls /sys/class/pwm/`
   - 检查PWM通道数量是否正确

## 与标准Linux子系统集成的优势

1. **标准化接口**：使用Linux标准接口，便于与其他应用程序和库集成
2. **兼容性**：遵循Linux内核驱动开发最佳实践
3. **更好的资源管理**：通过内核子系统管理硬件资源
4. **可扩展性**：更容易添加新功能和支持新硬件
5. **性能优化**：使用内核子系统的优化路径

## 硬件寄存器接口

### I2C 地址
```c
#define FUSION_HAT_I2C_ADDR 0x17
```

### ADC 数据读取
```c
#define CMD_READ_A0_H 0x10  // ADC0 高位数据
#define CMD_READ_A0_L 0x11  // ADC0 低位数据
#define CMD_READ_A1_H 0x12  // ADC1 高位数据
#define CMD_READ_A1_L 0x13  // ADC1 低位数据
#define CMD_READ_A2_H 0x14  // ADC2 高位数据
#define CMD_READ_A2_L 0x15  // ADC2 低位数据
#define CMD_READ_A3_H 0x16  // ADC3 高位数据
#define CMD_READ_A3_L 0x17  // ADC3 低位数据
#define CMD_READ_BATTERY_H 0x18  // 电池电压ADC 高位数据
#define CMD_READ_BATTERY_L 0x19  // 电池电压ADC 低位数据
```

### PWM 控制
```c
// 定时器控制
#define CMD_SET_TIMER0_PRESCALER_H 0x40  // 定时器0预分频器 高位 PWM0-3
#define CMD_SET_TIMER0_PRESCALER_L 0x41  // 定时器0预分频器 低位 PWM0-3
#define CMD_SET_TIMER1_PRESCALER_H 0x42  // 定时器1预分频器 高位 PWM4-7
#define CMD_SET_TIMER1_PRESCALER_L 0x43  // 定时器1预分频器 低位 PWM4-7
#define CMD_SET_TIMER2_PRESCALER_H 0x44  // 定时器2预分频器 高位 PWM8-11
#define CMD_SET_TIMER2_PRESCALER_L 0x45  // 定时器2预分频器 低位 PWM8-11
#define CMD_SET_TIMER0_PERIOD_H 0x50  // 定时器0周期寄存器 高位 PWM0-3
#define CMD_SET_TIMER0_PERIOD_L 0x51  // 定时器0周期寄存器 低位 PWM0-3
#define CMD_SET_TIMER1_PERIOD_H 0x52  // 定时器1周期寄存器 高位 PWM4-7
#define CMD_SET_TIMER1_PERIOD_L 0x53  // 定时器1周期寄存器 低位 PWM4-7
#define CMD_SET_TIMER2_PERIOD_H 0x54  // 定时器2周期寄存器 高位 PWM8-11
#define CMD_SET_TIMER2_PERIOD_L 0x55  // 定时器2周期寄存器 低位 PWM8-11

// PWM 通道值
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
```

### 传感器和控制
```c
// 传感器
#define CMD_READ_BUTTON_STATUS 0x24    // 8位，1表示按下，0表示松开
#define CMD_READ_CHARGING_STATUS 0x25  // 8位，1表示充电中，0表示未充电
#define CMD_READ_SHUTDOWN_STATUS 0x26  // 8位，0表示没有关机请求，1表示底电池电量关机请求，2表示按键关机请求

// 控制
#define CMD_CONTROL_LED 0x30           // 8位，1表示点亮，0表示熄灭
#define CMD_CONTROL_SPEAKER 0x31       // 8位，1表示开启，0表示关闭

// 系统
#define CMD_READ_FIRMWARE_VERSION 0x05 // 24位 固件版本号
```

### 常量定义
```c
#define ADC_REFERENCE_VOLTAGE 3300 // ADC参考电压 3.3V
#define ADC_MAX_VALUE 4095         // ADC最大数值 12位
#define BATTERY_DIVIDER 2          // 电池电压 divider，比例
```

## 安装说明

### 依赖要求

- 树莓派系统（Raspberry Pi OS 或 Ubuntu）
- Linux 内核头文件
- I2C 接口已启用

### 编译安装

1. 确保已启用 I2C 接口：
   ```bash
   sudo raspi-config nonint do_i2c 0
   ```

2. 安装编译依赖：
   ```bash
   sudo apt update
   sudo apt install -y build-essential raspberrypi-kernel-headers
   ```

3. 编译驱动和设备树覆盖文件：
   ```bash
   make
   ```

4. 安装驱动和设备树覆盖文件：
   ```bash
   sudo make install
   ```

5. 重启系统或加载设备树覆盖文件：
   ```bash
   sudo dtoverlay fusion_hat.dtbo
   sudo modprobe fusion_hat
   ```

### 配置设备树

编辑 `/boot/config.txt` 文件，添加以下行：

```
dtparam=i2c_arm=on
dtoverlay=fusion_hat
```

### 重启系统

```bash
sudo reboot
```

## 自动安装脚本

使用提供的安装脚本可以一键完成所有安装步骤：

```bash
chmod +x install.sh
sudo ./install.sh
```

脚本会自动安装依赖、编译驱动、配置设备树、设置开机自启动等。

## 使用方法

### 设备节点

驱动安装成功后，会在系统中创建以下设备节点：
- `/dev/fusion_hat` - 主设备节点，通过 ioctl 进行通信
- `/sys/class/power_supply/fusion_hat_battery/` - 电池信息（会被 upower 自动识别）

### IOCTL 命令接口

驱动使用标准的 ioctl 宏定义接口，通过 `/dev/fusion_hat` 设备节点通信：

| 命令 | 描述 | 参数 | 返回值 |
|------|------|------|--------|
| `FUSION_HAT_IOCTL_READ_ADC` | 读取指定通道ADC值 | `{channel, 0, 0}` | `{channel, adc_value, voltage_mv}` |
| `FUSION_HAT_IOCTL_SET_PWM` | 设置指定通道PWM值 | `{channel, value}` | 无 |
| `FUSION_HAT_IOCTL_INIT_PWM_TIMER` | 初始化PWM定时器 | `{timer, prescaler, period}` | 无 |
| `FUSION_HAT_IOCTL_READ_BUTTON` | 读取按键状态 | 无 | 8位按键状态值 |
| `FUSION_HAT_IOCTL_READ_FIRMWARE` | 读取固件版本号 | 无 | 24位版本号 |
| `FUSION_HAT_IOCTL_CONTROL_LED` | 控制LED | 0或1 | 无 |
| `FUSION_HAT_IOCTL_CONTROL_SPEAKER` | 控制喇叭 | 0或1 | 无 |

### 数据结构

```c
// ADC请求结构体
typedef struct {
    uint8_t channel;  // ADC通道 (0-3)
    uint16_t value;   // ADC原始值
    uint16_t voltage; // 计算的电压值 (mV)
} fusion_hat_adc_req;

// PWM请求结构体
typedef struct {
    uint8_t channel;  // PWM通道 (0-11)
    uint16_t value;   // PWM值 (0-65535)
} fusion_hat_pwm_req;

// PWM定时器请求结构体
typedef struct {
    uint8_t timer;     // 定时器编号 (0-2)
    uint16_t prescaler; // 预分频器值
    uint16_t period;   // 周期值
} fusion_hat_timer_req;
```

### Python 示例

请参考 `fusion_hat_example.py` 文件获取完整的 Python 示例代码，该文件演示了：

- 固件版本读取
- 多通道 ADC 读取
- PWM 定时器初始化和多通道 PWM 控制
- 电池信息读取和电量计算
- 按键状态检测
- LED 和喇叭控制
- upower 集成状态检查

### 使用方法

```bash
python3 fusion_hat_example.py
```

## 电源管理集成

驱动会自动将电池信息注册到 Linux 电源管理系统，桌面环境会在右上角显示电池图标和电量信息。

可以使用以下命令查看电池信息：

```bash
upower -i /org/freedesktop/UPower/devices/battery_fusion_hat_battery
```

## 关机信号处理

驱动支持三种关机信号状态：

1. **0** - 无关机请求
2. **1** - 低电量关机请求（当电池电压低于阈值时触发）
3. **2** - 按键关机请求（当电源键长按超过设定时间时触发）

当检测到关机信号时，驱动会播放提示音并触发系统关机。

## 调试

### 查看驱动日志

```bash
dmesg | grep fusion_hat
```

### 检查设备树覆盖

```bash
dtoverlay -l
```

### 检查设备节点权限

```bash
sudo chmod 666 /dev/fusion_hat
```

### 监控电池信息

```bash
upower -i /org/freedesktop/UPower/devices/battery_fusion_hat_battery
```

## 注意事项

- 确保 I2C 地址 0x17 未被其他设备占用
- 电池电压测量基于分压电阻，如需更精确的测量，可能需要校准
- 低电量关机阈值可在驱动代码中修改
- PWM 周期和占空比的设置会影响输出频率和精度
- 系统启动时自动加载驱动和设备树覆盖文件

## 故障排除

### 驱动加载失败
- 检查 I2C 接口是否启用
- 确认 Fusion Hat 硬件已正确连接
- 查看 dmesg 日志获取详细错误信息

### 电池信息未显示
- 检查 upower 服务是否正常运行
- 尝试重启 upower 服务：`sudo systemctl restart upower`
- 确认电池已正确连接

### PWM 输出异常
- 确保已正确初始化 PWM 定时器
- 检查 PWM 通道是否被其他功能占用
- 验证 PWM 值在有效范围内 (0-65535)

## 许可证

GPL-2.0