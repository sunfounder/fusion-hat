# Fusion Hat Linux Driver Makefile
# This Makefile handles the compilation, installation, and uninstallation of the Fusion Hat kernel module
# and device tree overlay file, with automatic detection of overlay directory paths

# Kernel build directory and current directory paths
KDIR ?= /lib/modules/$(shell uname -r)/build
PWD := $(shell pwd)

# Extract version from main.h
DRIVER_VERSION := $(shell grep '^\#define VERSION' main.h | awk '{print $$3}' | tr -d '"')

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

# DKMS source destination
DKMS_SRC := /usr/src/fusion_hat-$(DRIVER_VERSION)

# Check that kernel build directory is usable
check_kdir = \
	(if [ ! -d "$(KDIR)" ]; then \
		echo "ERROR: Kernel build directory not found: $(KDIR)" >&2; \
		echo "" >&2; \
		echo "Install kernel headers first:" >&2; \
		echo "  sudo apt install linux-headers-$$(uname -r)" >&2; \
		echo "" >&2; \
		exit 1; \
	elif [ ! -f "$(KDIR)/Makefile" ]; then \
		echo "ERROR: Kernel build directory is incomplete: $(KDIR)" >&2; \
		echo "The build symlink exists but the target is missing." >&2; \
		echo "" >&2; \
		echo "Reinstall kernel headers:" >&2; \
		echo "  sudo apt install --reinstall linux-headers-$$(uname -r)" >&2; \
		echo "" >&2; \
		exit 1; \
	fi)

# Default target - Compile kernel module and device tree overlay
all:
	@echo "Building Fusion Hat driver and device tree overlay..."
	@$(check_kdir)
	$(MAKE) -C $(KDIR) M=$(PWD) modules
	@echo "Compiling device tree overlay..."
	$(DTC) -@ -I dts -O dtb -o $(DTBO_NAME) sunfounder-fusionhat-overlay.dts
	@echo "Build completed successfully."

# Clean target - Remove build artifacts
clean:
	@echo "Cleaning build files..."
	@if [ -f "$(KDIR)/Makefile" ]; then \
		$(MAKE) -C $(KDIR) M=$(PWD) clean; \
	else \
		echo "  Skipping module clean (build directory not available)"; \
	fi
	rm -f $(DTBO_NAME)
	rm -f Module.symvers Module.markers modules.order
	@echo "Clean completed."

# Modules install target - Install kernel module and ensure dependencies are loaded
modules_install:
	@echo "Installing kernel module..."
	@$(check_kdir)
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

# DKMS install - register module with DKMS so it auto-rebuilds on kernel updates
dkms_install:
	@echo "Installing Fusion Hat driver via DKMS (version $(DRIVER_VERSION))..."
	@# Check if DKMS is installed
	@if ! command -v dkms >/dev/null 2>&1; then \
	    echo "DKMS not found. Installing dkms package..."; \
	    sudo apt-get update && sudo apt-get install -y dkms || { \
	        echo "Error: Failed to install DKMS. Please install it manually: sudo apt-get install dkms"; \
	        exit 1; \
	    }; \
	fi
	@# Clean up any old non-DKMS module files (left over from prior modules_install)
	@sudo rm -f /lib/modules/$(shell uname -r)/extra/fusion_hat.ko* /lib/modules/$(shell uname -r)/updates/fusion_hat.ko* 2>/dev/null || true
	@# Remove ALL previous DKMS registrations for this module (any version)
	-@for ver in $$(dkms status fusion_hat 2>/dev/null | sed -n 's/^fusion_hat\/\([^,]*\).*/\1/p' | sort -u); do \
	    sudo dkms remove -m fusion_hat -v $$ver --all 2>/dev/null || true; \
	done
	@# Copy source files to /usr/src/
	@echo "Copying source to $(DKMS_SRC)..."
	@sudo mkdir -p $(DKMS_SRC)
	@sudo cp -f *.c *.h Makefile dkms.conf $(DKMS_SRC)/
	@# Generate dkms.conf with correct version at destination
	@sudo sed -i 's/^PACKAGE_VERSION=.*/PACKAGE_VERSION="$(DRIVER_VERSION)"/' $(DKMS_SRC)/dkms.conf
	@# Add, build, and install via DKMS
	@sudo dkms add -m fusion_hat -v $(DRIVER_VERSION)
	@sudo dkms build -m fusion_hat -v $(DRIVER_VERSION)
	@sudo dkms install -m fusion_hat -v $(DRIVER_VERSION)
	@echo "DKMS installation completed. The driver will auto-rebuild on kernel updates."

# DKMS uninstall - remove module from DKMS
dkms_uninstall:
	@echo "Removing Fusion Hat driver from DKMS..."
	@if command -v dkms >/dev/null 2>&1; then \
	    sudo dkms remove -m fusion_hat -v $(DRIVER_VERSION) --all || echo "DKMS module not found."; \
	    sudo rm -rf $(DKMS_SRC) || echo "Source directory already removed."; \
	fi
	@echo "DKMS uninstall completed."

# Full install target - uses DKMS if available, falls back to traditional method
install:
	@echo "Installing Fusion Hat driver and device tree overlay..."
	@# Unload module if loaded
	-@sudo rmmod fusion_hat 2>/dev/null || echo "Module not currently loaded."
	@# Try DKMS first, fall back to traditional install
	@if command -v dkms >/dev/null 2>&1; then \
	    echo "DKMS detected, using DKMS for module installation..."; \
	    $(MAKE) dkms_install; \
	else \
	    echo "DKMS not found, using traditional installation (driver will NOT auto-rebuild on kernel updates)."; \
	    echo "Install DKMS (sudo apt-get install dkms) and re-run 'sudo make install' for auto-rebuild support."; \
	    $(MAKE) modules_install; \
	fi
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
	# Try DKMS uninstall first
	-@$(MAKE) dkms_uninstall
	# Also try removing from traditional locations
	rm -f /lib/modules/$(shell uname -r)/extra/fusion_hat.ko /lib/modules/$(shell uname -r)/updates/fusion_hat.ko || echo "Warning: Module file not found or permission denied."
	@echo "Updating module dependencies..."
	depmod -a || echo "Note: There might be module dependency issues. Please check if all Fusion Hat modules are properly removed."
	@echo "Removing device tree overlay from $(OVERLAY_DIR)/"
	rm -f $(OVERLAY_DIR)/$(DTBO_NAME) || { echo "Error: Permission denied or overlay file not found. Please run with sudo privileges."; exit 1; }
	@echo "Uninstall completed. You may need to reboot to fully remove all traces of the module."

# Status - check driver installation state
status:
	@echo "=== Fusion Hat Driver Status ==="
	@echo ""
	@# Check if module file exists
	@if [ -f /lib/modules/$(shell uname -r)/extra/fusion_hat.ko ] || [ -f /lib/modules/$(shell uname -r)/updates/fusion_hat.ko ]; then \
	    echo "Module file    : INSTALLED"; \
	else \
	    echo "Module file    : MISSING"; \
	fi
	@# Check DKMS registration
	@if command -v dkms >/dev/null 2>&1; then \
	    if dkms status fusion_hat 2>/dev/null | grep -q fusion_hat; then \
	        echo "DKMS status    : $(shell dkms status fusion_hat 2>/dev/null | head -1)"; \
	    else \
	        echo "DKMS status    : not registered (run 'sudo make install' to register)"; \
	    fi; \
	else \
	    echo "DKMS status    : DKMS not installed (run 'sudo apt-get install dkms')"; \
	fi
	@# Check if module is loaded
	@if lsmod | grep -q fusion_hat; then \
	    echo "Module loaded  : YES"; \
	else \
	    echo "Module loaded  : NO"; \
	fi
	@# Check sysfs interface
	@if [ -d /sys/class/fusion_hat ]; then \
	    echo "sysfs interface: /sys/class/fusion_hat/ EXISTS"; \
	else \
	    echo "sysfs interface: /sys/class/fusion_hat/ MISSING"; \
	fi
	@echo ""

.PHONY: dkms_install dkms_uninstall status
