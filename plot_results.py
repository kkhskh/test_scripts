#!/usr/bin/env python3
# plot_results.py - Shadow Driver Fault Injection Results Visualization

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for headless operation
import matplotlib.pyplot as plt
import numpy as np
import re
import os
import sys
from datetime import datetime

print("Shadow Driver Results Plotter")
print("----------------------------")

# Determine script and project directories
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)

# Default results file location
results_file = os.path.join(script_dir, 'results.txt')

# Check if file was specified as argument
if len(sys.argv) > 1:
    results_file = sys.argv[1]

# Check if results file exists
if not os.path.exists(results_file):
    print(f"Error: Results file not found at {results_file}")
    print("Run test_shadow_drivers.sh first or specify the file location.")
    sys.exit(1)

print(f"Using results file: {results_file}")

# Parse results from file
def parse_results(filename):
    print("Parsing results file...")
    
    with open(filename, 'r') as f:
        content = f.read()
    
    # Find the results section
    results_section = re.search(r'Fault Injection Results:(.*?)(?:\n\n|\Z)', content, re.DOTALL)
    if not results_section:
        print("Error: Results section not found in the file!")
        return None
    
    results = []
    lines = results_section.group(1).strip().split('\n')
    
    # Skip the header lines
    data_lines = [line for line in lines if '|' in line][2:]  # Skip first two header lines
    
    for line in data_lines:
        parts = line.split('|')
        if len(parts) >= 5:
            app_driver = parts[0].strip()
            trials = int(parts[1].strip())
            
            # Extract percentages (handle different possible formats)
            auto_match = re.search(r'(\d+)\s*%', parts[2].strip())
            manual_match = re.search(r'(\d+)\s*%', parts[3].strip())
            failed_match = re.search(r'(\d+)\s*%', parts[4].strip())
            
            if not all([auto_match, manual_match, failed_match]):
                print(f"Warning: Could not parse percentages from line: {line}")
                continue
                
            auto_pct = int(auto_match.group(1))
            manual_pct = int(manual_match.group(1))
            failed_pct = int(failed_match.group(1))
            
            # Extract driver and app name
            match = re.match(r'(\w+)/(\w+)', app_driver)
            if match:
                driver = match.group(1)
                app = match.group(2)
                
                # Create readable app name for display
                readable_app = app.replace('_', ' ').title()
                if app == "mp3_player":
                    readable_app = "MP3 Player"
                
                results.append({
                    'driver': driver,
                    'app': app,
                    'display_name': readable_app,
                    'trials': trials,
                    'auto_pct': auto_pct,
                    'manual_pct': manual_pct,
                    'failed_pct': failed_pct
                })
    
    print(f"Found {len(results)} result entries.")
    return results

# Create bar chart
def create_graph(results):
    if not results:
        print("No results to plot!")
        return
    
    print("Generating graph...")
    
    # Set style for professional look
    plt.style.use('seaborn-v0_8-whitegrid')
    
    # Extract data for plotting
    apps = [r['display_name'] for r in results]
    auto_recovery = [r['auto_pct'] for r in results]
    manual_recovery = [r['manual_pct'] for r in results]
    failed_recovery = [r['failed_pct'] for r in results]
    trials = [r['trials'] for r in results]
    
    # Get driver categories
    raw_drivers = [r['driver'] for r in results]
    driver_names = {'snd': 'Sound', 'e1000': 'Network', 'ide': 'IDE'}
    drivers = [driver_names.get(d, d.upper()) for d in raw_drivers]
    
    # Set up plot
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Set positions for bars
    x = np.arange(len(apps))
    width = 0.8
    
    # Create stacked bars
    p1 = ax.bar(x, auto_recovery, width, label='Automatic Recovery', color='gray', edgecolor='black', linewidth=0.5)
    p2 = ax.bar(x, manual_recovery, width, bottom=auto_recovery, label='Manual Recovery', color='white', edgecolor='black', linewidth=0.5)
    p3 = ax.bar(x, failed_recovery, width, bottom=[a+m for a,m in zip(auto_recovery, manual_recovery)], 
                label='Failed Recovery', color='darkgray', edgecolor='black', linewidth=0.5)
    
    # Add numbers to the automatic recovery bars
    for i, p in enumerate(p1):
        height = p.get_height()
        if height > 0:
            ax.text(p.get_x() + p.get_width()/2., height/2, str(auto_recovery[i]),
                   ha='center', va='center', color='black', fontweight='bold')
    
    # Set chart properties
    ax.set_ylim(0, 100)
    ax.set_ylabel('Percent of Outcomes', fontsize=12)
    ax.set_title('Fault Injection Outcomes', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(apps, fontsize=10)
    
    # Add vertical separators between driver categories
    unique_drivers = []
    for d in drivers:
        if d not in unique_drivers:
            unique_drivers.append(d)
    
    separator_positions = []
    current_driver = drivers[0]
    for i, d in enumerate(drivers[1:], 1):
        if d != current_driver:
            separator_positions.append(i - 0.5)
            current_driver = d
    
    for pos in separator_positions:
        ax.axvline(x=pos, color='black', linestyle='-', linewidth=1)
    
    # Add driver category labels at the top
    current_driver = None
    start_pos = 0
    for i, d in enumerate(drivers):
        if d != current_driver:
            if current_driver is not None:
                mid_pos = (start_pos + i - 1) / 2
                ax.text(mid_pos, 105, current_driver, ha='center', va='bottom', fontsize=12, fontweight='bold')
                plt.plot([start_pos - 0.5, i - 0.5], [104, 104], 'k-', linewidth=1)
            current_driver = d
            start_pos = i
    
    # Add the last driver label
    mid_pos = (start_pos + len(drivers) - 1) / 2
    ax.text(mid_pos, 105, current_driver, ha='center', va='bottom', fontsize=12, fontweight='bold')
    plt.plot([start_pos - 0.5, len(drivers) - 0.5], [104, 104], 'k-', linewidth=1)
    
    ax.set_ylim(0, 110)
    
    # Add legend at the bottom with better styling
    leg = ax.legend(bbox_to_anchor=(0.5, -0.15), loc='upper center', ncol=3, frameon=True,
                   fontsize=10, edgecolor='black')
    
    # Add figure footer with timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    plt.figtext(0.5, -0.05, f"Generated: {timestamp} | Shadow Driver Replication Project", 
               ha='center', fontsize=8, style='italic')
    
    # Adjust layout
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    
    # Save the figure
    output_file = os.path.join(script_dir, 'fault_injection_outcomes.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Graph saved to: {output_file}")
    
    # Try to open a display window if possible (may not work in headless)
    try:
        plt.show()
    except Exception as e:
        print(f"Note: Could not display interactive plot ({e})")
        print("The graph has been saved to disk. Use a file browser to view it.")

    # Create an additional CSV output for easy data reuse
    csv_file = os.path.join(script_dir, 'fault_injection_results.csv')
    with open(csv_file, 'w') as f:
        f.write("Driver,Application,Total Trials,Automatic Recovery %,Manual Recovery %,Failed Recovery %\n")
        for r in results:
            f.write(f"{r['driver']},{r['app']},{r['trials']},{r['auto_pct']},{r['manual_pct']},{r['failed_pct']}\n")
    print(f"CSV data saved to: {csv_file}")

if __name__ == "__main__":
    results = parse_results(results_file)
    if results:
        create_graph(results)
    else:
        print("Failed to parse results. Check the format of the results file.")