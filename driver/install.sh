#!/bin/bash

# Fusion Hat Driver Installation Script
# This script handles the compilation, installation, and loading of the Fusion Hat kernel module
# It includes error handling, logging, and user interaction for reboot confirmation

# Check for root privileges - required for module installation
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

# =========================================
# Configuration Variables
# Define basic settings and status indicators
USERNAME=$(getent passwd 1000 | cut -d: -f1)  # Get main user (UID 1000)
HOME=$(getent passwd 1000 | cut -d: -f6)      # Get main user's home directory
SUCCESS="\033[32m[✓]\033[0m"                # Success indicator with green color
FAILED="\033[31m[✗]\033[0m"                 # Failure indicator with red color

FORCE_REINSTALL=false                        # Flag for forced reinstallation
ERROR_HAPPENED=false                         # Flag to track if any errors occurred
ERROR_LOGS=""                                # Store error logs for reporting
# =========================================


# =========================================
# Utility Functions

# Cleanup function to remove temporary build files
cleanup() {
    log_title "Cleanup"
    run "make clean" "Clean driver build files"
}

# Handle interrupt signals (Ctrl+C) during installation
handle_interrupt() {
    # Restore cursor visibility
    tput cnorm
    
    # Display appropriate message based on installation state
    if [ "$ERROR_HAPPENED" = true ]; then
        echo -e "\n\033[31mUser interrupted. Error logs:\033[0m"
        echo "$ERROR_LOGS"
        echo "Please check $LOG_FILE for more details."
    else
        echo -e "\n\033[33mUser canceled installation.\033[0m"
    fi
    
    # Perform cleanup before exiting
    cleanup
    exit 1
}

# Set up interrupt handling for SIGINT (Ctrl+C)
trap handle_interrupt SIGINT
# =========================================


# =========================================
# Logging Functions
LOG_FILE="/tmp/install.log"  # Path to installation log file

# Initialize log file - remove if exists and create new
if [ -f "$LOG_FILE" ]; then
    rm $LOG_FILE
fi
touch $LOG_FILE

# Log message to both console and log file
log() {
    echo -e "$1"
    echo "$1" >> $LOG_FILE
}

# Log section title with blue color formatting
log_title() {
    echo -e "\033[34m$1\033[0m"
    echo "[$1]" >> $LOG_FILE
}
# =========================================


# =========================================
# Command Execution Function
# Runs commands with visual feedback, logging, and error tracking
run() {
    local cmd="$1"           # Command to execute
    local info="$2"          # Description of the command
    local delay=0.1          # Delay for spinner animation
    local spinstr='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'  # Spinner characters for visual feedback
    local i=0                # Counter for spinner animation
    
    # Hide cursor during command execution
    tput civis
    
    # Execute command in background and capture output
    eval $cmd > /tmp/cmd_output.log 2>&1 &
    local pid=$!
    
    # Display spinner animation while command is running
    while [ -d /proc/$pid ]; do
        local char=${spinstr:$i:1}
        printf "\r\033[36m[%s]\033[0m %s" "$char" "$info"
        i=$(( (i+1) % ${#spinstr} ))
        sleep $delay
    done
    
    # Wait for command completion and get exit status
    wait $pid
    local result=$?
    
    # Restore cursor visibility
    tput cnorm
    
    # Process command result
    if [ $result -eq 0 ]; then
        # Success - display success indicator
        printf "\r$SUCCESS %s\n" "$info"
        echo "[✓] $info" >> $LOG_FILE
    else
        # Failure - update error flags and logs
        printf "\r$FAILED %s\n" "$info"
        ERROR_HAPPENED=true
        ERROR_LOGS+=`cat /tmp/cmd_output.log`
        echo "[✗] $info" >> $LOG_FILE
    fi
    
    # Save command output to log file and clean up
    cat /tmp/cmd_output.log >> $LOG_FILE
    rm -f /tmp/cmd_output.log
    
    # Return command's exit status
    return $result
}
# =========================================


# =========================================
# Main Installation Process
log_title "Fusion Hat Driver Installation"

# Unload existing module if loaded to ensure clean installation
if lsmod | grep -q fusion_hat; then
    run "rmmod fusion_hat" "Unload existing fusion_hat module"
fi

# Clean previous build files
run "make clean" "Clean previous compilation"

# Compile the driver
run "make all" "Compile driver"

# Install the compiled module
run "make install" "Install new compiled module"

# Load the newly compiled module
run "insmod fusion_hat.ko" "Load new compiled module"
# =========================================


# =========================================
# Post-Installation Handling
if [ "$ERROR_HAPPENED" = false ]; then
    # Installation successful
    log "$SUCCESS Installation completed successfully."
    
    # Prompt user for reboot
    read -p "Do you want to reboot now? (y/n) " -n 1 -r
    while true; do
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            log "$SUCCESS Rebooting system..."
            sleep 1
            reboot
        elif [[ $REPLY =~ ^[Nn]$ ]]; then
            log "$FAILED Reboot canceled. Please reboot manually to ensure proper operation."
            break
        else
            log "$FAILED Invalid input. Please enter y or n."
            read -p "Do you want to reboot now? (y/n) " -n 1 -r
        fi
    done
else
    # Installation failed - display error information
    echo -e "$FAILED Installation failed: $ERROR_LOGS"
    echo -e "$FAILED Please check $LOG_FILE for more details."
    exit 1
fi
# =========================================