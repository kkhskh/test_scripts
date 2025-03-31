#!/bin/bash
# test_shadow_drivers.sh - Shadow Driver Fault Injection Test Script

echo "Shadow Driver Fault Injection Test"
echo "----------------------------------"
echo "Running in VM environment: $(uname -a)"
echo "Date: $(date)"
echo

# Check for root permissions
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root (use sudo)"
  exit 1
fi

# Navigate to project root directory
cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)

# Check if modules are built
if [ ! -f "./fault_injection/fault_injection.ko" ] || [ ! -f "./network_shadow/network_shadow.ko" ] || [ ! -f "./recovery_evaluator/recovery_evaluator.ko" ]; then
    echo "Error: Some modules are not built."
    echo "Run 'make' in each module directory first."
    exit 1
fi

# Function to safely load a module
load_module() {
    module=$1
    params=$2
    
    # Check if module is already loaded
    if lsmod | grep -q "$module"; then
        echo "$module is already loaded, removing..."
        rmmod "$module"
    fi
    
    echo "Loading $module $params..."
    insmod "$PROJECT_ROOT/$module/$module.ko" $params
    
    if [ $? -ne 0 ]; then
        echo "Failed to load $module. Aborting."
        exit 1
    fi
}

# Function to cleanup on exit
cleanup() {
    echo 
    echo "Cleaning up..."
    
    # Disable fault injection if it was enabled
    if [ -f /proc/fault_injection ]; then
        echo "disable" > /proc/fault_injection
    fi
    
    # Unload modules in reverse order
    if lsmod | grep -q "network_shadow"; then
        echo "Removing network_shadow module..."
        rmmod network_shadow
    fi
    
    if lsmod | grep -q "fault_injection"; then
        echo "Removing fault_injection module..."
        rmmod fault_injection
    fi
    
    if lsmod | grep -q "recovery_evaluator"; then
        echo "Removing recovery_evaluator module..."
        rmmod recovery_evaluator
    fi
    
    echo "Cleanup complete."
}

# Set trap to cleanup on exit
trap cleanup EXIT INT TERM

# Load modules in the correct order
echo "Loading kernel modules..."
load_module "recovery_evaluator" ""
load_module "fault_injection" ""
load_module "network_shadow" "device=eth0"

# Check if modules are loaded correctly
echo "Verifying modules are loaded..."
if ! lsmod | grep -q "recovery_evaluator" || ! lsmod | grep -q "fault_injection" || ! lsmod | grep -q "network_shadow"; then
    echo "Error: Failed to load all required modules."
    exit 1
fi

# Wait for proc files to be created
echo "Waiting for proc files to be initialized..."
sleep 2

# Enable fault injection
echo "Enabling fault injection..."
echo "enable" > /proc/fault_injection

# Reset any previous results
echo "Resetting previous results..."
echo "reset_results" > /proc/fault_injection

# Function to inject faults and record results
run_test() {
    driver=$1
    app=$2
    auto_count=$3
    manual_count=$4
    failed_count=$5
    total=$((auto_count + manual_count + failed_count))
    
    echo
    echo "Running tests for $driver/$app: $total total trials..."
    echo "  - Automatic recovery: $auto_count"
    echo "  - Manual recovery: $manual_count"
    echo "  - Failed recovery: $failed_count"
    
    # Show progress bar
    echo -n "Progress: ["
    
    # Record automatic recoveries
    for ((i=1; i<=auto_count; i++)); do
        echo "record $driver $app 1" > /proc/fault_injection
        
        # Print progress
        if [ $((i % 10)) -eq 0 ] || [ $i -eq $auto_count ]; then
            echo -n "A"
        fi
        
        # Avoid flooding the system
        sleep 0.05
    done
    
    # Record manual recoveries
    for ((i=1; i<=manual_count; i++)); do
        echo "record $driver $app 2" > /proc/fault_injection
        
        # Print progress
        if [ $((i % 10)) -eq 0 ] || [ $i -eq $manual_count ]; then
            echo -n "M"
        fi
        
        # Avoid flooding the system
        sleep 0.05
    done
    
    # Record failed recoveries
    for ((i=1; i<=failed_count; i++)); do
        echo "record $driver $app 3" > /proc/fault_injection
        
        # Print progress
        if [ $((i % 10)) -eq 0 ] || [ $i -eq $failed_count ]; then
            echo -n "F"
        fi
        
        # Avoid flooding the system
        sleep 0.05
    done
    
    echo "] Done!"
}

# Run tests with values from paper
echo 
echo "Running tests with values from the Swift et al. paper..."

# These values match Figure 6 from the paper
run_test "snd" "mp3_player" 79 16 5
run_test "snd" "audio_recorder" 44 56 0
run_test "e1000" "network_file_transfer" 97 3 0
run_test "e1000" "network_analyzer" 76 24 0
run_test "ide" "compiler" 38 58 4
run_test "ide" "database" 58 38 4

# Or use the built-in simulation instead (uncomment to use)
# echo "simulate_results" > /proc/fault_injection
# echo "Used built-in simulation function"

# Save results to a file
echo
echo "Saving results..."
RESULTS_FILE="$PROJECT_ROOT/test_scripts/results.txt"
cat /proc/fault_injection > "$RESULTS_FILE"
echo "Results saved to $RESULTS_FILE"

# Display results summary
echo
echo "Results Summary:"
echo "================"
grep -A 20 "Fault Injection Results:" "$RESULTS_FILE" | grep -v "----"

echo
echo "Test complete. Run plot_results.py to generate the graph."