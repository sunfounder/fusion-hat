# Fusion Hat Linux Driver Makefile

KDIR ?= /lib/modules/$(shell uname -r)/build
PWD := $(shell pwd)

# 将所有源文件组合到fusion_hat模块中
obj-m += fusion_hat.o
# 组合所有源文件到一个模块中
fusion_hat-objs := main.o i2c.o adc.o battery.o shutdown.o pwm.o button.o

# 编译标志
ccflags-y += -DMODULE

# 确保IIO子系统模块在加载我们的模块之前已经加载
modules_install:
	$(MAKE) -C $(KDIR) M=$(PWD) modules_install
	@echo "确保IIO子系统模块已加载"
	@sudo modprobe industrialio || echo "无法自动加载industrialio模块，请手动加载"
	depmod -a

# 设备树覆盖文件
DTC := dtc
DTBO_NAME := sunfounder-fusionhat.dtbo

all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules
	$(DTC) -@ -I dts -O dtb -o $(DTBO_NAME) sunfounder-fusionhat-overlay.dts

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean
	rm -f $(DTBO_NAME)
	rm -f Module.symvers Module.markers modules.order
	echo "已清理所有编译缓存文件"

uninstall:
	rm -f /lib/modules/$(shell uname -r)/extra/fusion_hat.ko
	depmod -a
	rm -f /boot/firmware/overlays/$(DTBO_NAME) || echo "请使用sudo权限运行卸载命令"

install:
	@echo "正在安装模块和设备树覆盖文件..."
	@$(MAKE) modules_install
	@echo "安装设备树覆盖文件到/boot/firmware/overlays/"
	@cp -f $(DTBO_NAME) /boot/firmware/overlays/ || echo "请使用sudo权限运行安装命令"
