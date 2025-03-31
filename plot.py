#!/usr/bin/env python3
# plot_results.py - Shadow Driver Fault Injection Results Visualization

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for headless operation
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
from datetime import datetime

print("Shadow Driver Results Plotter")
print("----------------------------")

# Determine script directory
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define our simulation results based on the data you provided
simulation_results = [
    {'driver': 'snd', 'app': 'mp3_player', 'display_name': 'MP3 Player', 
     'total_trials': 100, 'auto_pct': 79, 'manual_pct': 16, 'failed_pct': 5},
    
    {'driver': 'snd', 'app': 'audio_recorder', 'display_name': 'Audio Recorder', 
     'total_trials': 100, 'auto_pct': 44, 'manual_pct': 56, 'failed_pct': 0},
    
    {'driver': 'e1000', 'app': 'network_file_transfer', 'display_name': 'Network File Transfer', 
     'total_trials': 100, 'auto_pct': 97, 'manual_pct': 3, 'failed_pct': 0},
    
    {'driver': 'e1000', 'app': 'network_analyzer', 'display_name': 'Network Analyzer', 
     'total_trials': 100, 'auto_pct': 76, 'manual_pct': 24, 'failed_pct': 0},
    
    {'driver': 'ide', 'app': 'compiler', 'display_name': 'Compiler', 
     'total_trials': 100, 'auto_pct': 38, 'manual_pct': 58, 'failed_pct': 4},
    
    {'driver': 'ide', 'app': 'database', 'display_name': 'Database', 
     'total_trials': 100, 'auto_pct': 58, 'manual_pct': 38, 'failed_pct': 4}
]

def create_graph(results):
    print("Generating graph based on simulation results...")
    
    # Set a cleaner, more paper-like style
    plt.style.use('seaborn-v0_8-whitegrid')
    plt.rcParams['axes.grid'] = True
    plt.rcParams['grid.linestyle'] = ':'
    plt.rcParams['grid.linewidth'] = 0.5
    plt.rcParams['grid.color'] = '#CCCCCC'
    
    # Extract data for plotting
    apps = [r['app'] for r in results]
    display_names = [r['display_name'] for r in results]
    auto_pcts = [r['auto_pct'] for r in results]
    manual_pcts = [r['manual_pct'] for r in results]
    failed_pcts = [r['failed_pct'] for r in results]
    total_trials = [r['total_trials'] for r in results]
    
    # Get driver categories
    raw_drivers = [r['driver'] for r in results]
    driver_names = {'snd': 'Sound', 'e1000': 'Network', 'ide': 'IDE'}
    drivers = [driver_names.get(d, d.upper()) for d in raw_drivers]
    
    # Set up plot with a figure similar to the paper
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # Set positions for bars
    x = np.arange(len(apps))
    width = 0.6  # Match paper's bar width
    
    # Create stacked bars with paper-matching colors
    auto_color = '#AAAAAA'       # Light gray for auto recovery
    manual_color = '#FFFFFF'     # White for manual recovery  
    failed_color = '#555555'     # Dark gray for failed recovery
    
    # Calculate the bottom positions for stacking
    manual_bottom = auto_pcts
    failed_bottom = [a + m for a, m in zip(auto_pcts, manual_pcts)]
    
    # Create stacked bars
    p1 = ax.bar(x, auto_pcts, width, color=auto_color, edgecolor='black', linewidth=0.5)
    p2 = ax.bar(x, manual_pcts, width, bottom=manual_bottom, color=manual_color, 
                edgecolor='black', linewidth=0.5)
    p3 = ax.bar(x, failed_pcts, width, bottom=failed_bottom, color=failed_color, 
                edgecolor='black', linewidth=0.5)
    
    # Add automatic recovery percentages inside the bars
    for i, v in enumerate(auto_pcts):
        ax.text(i, v/2, str(v), ha='center', va='center', fontweight='bold')
    
    # Set chart properties to match paper
    ax.set_ylim(0, 100)
    ax.set_ylabel('Percent of Outcomes', fontsize=12)
    ax.set_title('Fault Injection Outcomes', fontsize=14, fontweight='bold', pad=15)
    ax.set_xticks(x)
    
    # Set lowercase app names to match paper
    paper_style_names = [app.replace('_', ' ').lower() for app in apps]
    ax.set_xticklabels(paper_style_names, fontsize=10)
    
    # Set y-axis to show percentages
    ax.set_yticks(range(0, 101, 20))
    ax.set_yticklabels([f"{i}%" for i in range(0, 101, 20)])
    
    # Add vertical separators between driver categories
    current_driver = drivers[0]
    for i, d in enumerate(drivers[1:], 1):
        if d != current_driver:
            ax.axvline(x=i-0.5, color='black', linestyle='-', linewidth=0.8)
            current_driver = d
    
    # Add driver category labels at the top
    current_driver = None
    start_pos = 0
    for i, d in enumerate(drivers):
        if d != current_driver:
            if current_driver is not None:
                mid_pos = (start_pos + i - 1) / 2
                ax.text(mid_pos, 105, current_driver, ha='center', va='bottom', fontsize=12)
            current_driver = d
            start_pos = i
    
    # Add the last driver label
    mid_pos = (start_pos + len(drivers) - 1) / 2
    ax.text(mid_pos, 105, current_driver, ha='center', va='bottom', fontsize=12)
    
    # Draw horizontal line at top of chart (100%)
    ax.axhline(y=100, color='black', linestyle='-', linewidth=0.8)
    
    # Add legend at the bottom to match paper
    leg = ax.legend([p1, p2, p3], 
                   ["Automatic Recovery", "Manual Recovery", "Failed Recovery"],
                   loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=3, 
                   frameon=False, fontsize=10)
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    # Save the figure to match paper as closely as possible
    output_file = os.path.join(script_dir, 'fault_injection_outcomes.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Graph saved to: {output_file}")
    
    # Also save as PDF for publication-quality reproduction
    pdf_file = os.path.join(script_dir, 'fault_injection_outcomes.pdf')
    plt.savefig(pdf_file, format='pdf', bbox_inches='tight')
    print(f"PDF saved to: {pdf_file}")
    
    # Try to open a display window if possible (may not work in headless)
    try:
        plt.show()
    except Exception as e:
        print(f"Note: Could not display interactive plot ({e})")

    # Print a summary of the data
    print("\nSimulation Results Summary:")
    print("-------------------------")
    for r in results:
        print(f"{r['display_name']} ({r['driver']}): {r['auto_pct']}% auto, "
              f"{r['manual_pct']}% manual, {r['failed_pct']}% failed")

if __name__ == "__main__":
    print("Creating graph based on our simulation results")
    create_graph(simulation_results)
    print("\nDone! The graph shows our simulation results that match the paper trends.")