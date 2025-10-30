# Fusion Hat Linux Driver Makefile
# This Makefile handles the compilation, installation, and uninstallation of the Fusion Hat kernel module
# and device tree overlay file, with automatic detection of overlay directory paths

# Kernel build directory and current directory paths
KDIR ?= /lib/modules/$(shell uname -r)/build
PWD := $(shell pwd)

# Module definition - Combine all source files into a single module
obj-m += fusion_hat.o
fusion_hat-objs := \
	i2c.o \
	adc.o \
	battery.o \
	shutdown.o \
	pwm.o \
	button.o \
	led.o \
	speaker.o \
	main.o

# Compilation flags
ccflags-y += -DMODULE

# Device Tree Compiler and overlay file settings
DTC := dtc
DTBO_NAME := sunfounder-fusionhat.dtbo

# Automatically detect the correct overlay directory path
# Common overlay directories in different Linux systems
OVERLAY_DIRS := \
    /boot/firmware/overlays \
    /boot/overlays \
    /lib/firmware \
    /boot/dtb/overlays

# Find the first existing overlay directory
OVERLAY_DIR := $(firstword $(wildcard $(OVERLAY_DIRS)))

# Default target - Compile kernel module and device tree overlay
all:
	@echo "Building Fusion Hat driver and device tree overlay..."
	$(MAKE) -C $(KDIR) M=$(PWD) modules
	@echo "Compiling device tree overlay..."
	$(DTC) -@ -I dts -O dtb -o $(DTBO_NAME) sunfounder-fusionhat-overlay.dts
	@echo "Build completed successfully."

# Clean target - Remove build artifacts
clean:
	@echo "Cleaning build files..."
	$(MAKE) -C $(KDIR) M=$(PWD) clean
	rm -f $(DTBO_NAME)
	rm -f Module.symvers Module.markers modules.order
	@echo "Clean completed."

# Modules install target - Install kernel module and ensure dependencies are loaded
modules_install:
	@echo "Installing kernel module..."
	$(MAKE) -C $(KDIR) M=$(PWD) modules_install
	@echo "Loading required IIO subsystem module..."
	@sudo modprobe industrialio || echo "Warning: Failed to automatically load industrialio module. Please load it manually."
	@echo "Updating module dependencies..."
	depmod -a
	@echo "Module installation completed."

# Helper target to display the detected overlay directory
display-overlay-dir:
	@echo "Detected overlay directory: $(OVERLAY_DIR)"
	@if [ ! -d "$(OVERLAY_DIR)" ]; then \
	    echo "Error: Detected overlay directory does not exist."; \
	    exit 1; \
	fi

# Install dtoverlay
install-overlay:
	@echo "Installing device tree overlay to $(OVERLAY_DIR)/"
	@# Verify overlay directory exists
	@if [ ! -d "$(OVERLAY_DIR)" ]; then \
	    echo "Error: Overlay directory $(OVERLAY_DIR) does not exist."; \
	    exit 1; \
	fi
	@cp -f $(DTBO_NAME) $(OVERLAY_DIR)/ || { echo "Error: Permission denied. Please run with sudo privileges."; exit 1; }

# Full install target - Install both module and device tree overlay
install:
	@echo "Installing Fusion Hat driver and device tree overlay..."
	rmmod fusion_hat || echo "Warning: Failed to unload fusion_hat module. It may be in use or require additional privileges."
	@$(MAKE) modules_install
	@$(MAKE) install-overlay
	@echo "Loading fusion_hat module..."
	@sudo modprobe fusion_hat || echo "Warning: Failed to load fusion_hat module. Please check the driver installation."
	@echo "Installation completed successfully."

# Uninstall target - Remove module and device tree overlay
uninstall:
	@echo "Uninstalling Fusion Hat driver..."
	# Unload the module if it's currently loaded
	@if lsmod | grep -q fusion_hat; then \
	    echo "Unloading fusion_hat module..."; \
	    sudo rmmod fusion_hat || echo "Warning: Failed to unload fusion_hat module. It may be in use or require additional privileges."; \
	fi
	# Try removing from both possible locations
	rm -f /lib/modules/$(shell uname -r)/extra/fusion_hat.ko /lib/modules/$(shell uname -r)/updates/fusion_hat.ko || echo "Warning: Module file not found or permission denied."
	@echo "Updating module dependencies..."
	depmod -a || echo "Note: There might be module dependency issues. Please check if all Fusion Hat modules are properly removed."
	@echo "Removing device tree overlay from $(OVERLAY_DIR)/"
	rm -f $(OVERLAY_DIR)/$(DTBO_NAME) || { echo "Error: Permission denied or overlay file not found. Please run with sudo privileges."; exit 1; }
	@echo "Uninstall completed. You may need to reboot to fully remove all traces of the module."
