# src/plotting/eis_plotter.py
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
import yaml
import pandas as pd
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
import sys
import os
import numpy as np
from matplotlib.markers import MarkerStyle

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.parsers.eis_parser import parse_eis_file

# Set up seaborn style for nicer defaults
sns.set_style("whitegrid")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']

def apply_standard_eis_layout(ax, title="EIS Data", config=None):
    """Apply standard EIS plot layout to any matplotlib axes"""
    # Use config if provided, otherwise use defaults
    if config:
        style_config = config.get('style', {})
        title_font_size = style_config.get('title_font_size', 16)
        axis_font_size = style_config.get('axis_font_size', 12)
        legend_font_size = style_config.get('legend_font_size', 10)
        figure_size = style_config.get('figure_size', [10, 6])
    else:
        # Defaults for auto plots
        title_font_size = 18
        axis_font_size = 14
        legend_font_size = 12
        figure_size = [10, 8]
    
    # Set title
    ax.set_title(title, fontsize=title_font_size, fontweight='bold', pad=20)
    
    # Set axis labels and scales
    ax.set_xlabel("Frequency (Hz)", fontsize=axis_font_size, fontweight='bold')
    ax.set_ylabel("Impedance Magnitude (Ω)", fontsize=axis_font_size, fontweight='bold')
    
    # Set log scales
    ax.set_xscale('log')
    ax.set_yscale('log')
    
    # Style the axes
    ax.tick_params(axis='both', which='major', labelsize=axis_font_size-2, 
                   length=5, width=1, direction='out')
    ax.tick_params(axis='both', which='minor', length=3, width=0.5, direction='out')
    
    # Grid styling
    ax.grid(True, which='major', alpha=0.6, linewidth=0.8)
    ax.grid(True, which='minor', alpha=0.3, linewidth=0.4)
    
    # Spine styling
    for spine in ax.spines.values():
        spine.set_linewidth(1)
        spine.set_color('black')
    
    # Set figure size if we have access to the figure
    fig = ax.get_figure()
    if fig:
        fig.set_size_inches(figure_size[0], figure_size[1])
        fig.tight_layout()
    
    return ax

def select_files():
    """Open file dialog to select EIS files"""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    file_paths = filedialog.askopenfilenames(
        title="Select EIS Files",
        filetypes=[
            ("EIS files", "*.dta *.csv *.DTA"),
            ("DTA files", "*.dta *.DTA"), 
            ("CSV files", "*.csv"),
            ("All files", "*.*")
        ]
    )
    
    root.destroy()
    return list(file_paths)

def select_directory():
    """Open dialog to select a directory containing EIS files"""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    directory = filedialog.askdirectory(title="Select Directory with EIS Files")
    
    root.destroy()
    return directory

def load_eis_files_from_directory(directory_path):
    """Load all EIS files from a directory"""
    directory = Path(directory_path)
    eis_extensions = ['.dta', '.DTA', '.csv']
    
    file_paths = []
    for ext in eis_extensions:
        file_paths.extend(directory.glob(f'*{ext}'))
    
    # Sort alphabetically
    file_paths = sorted([str(path) for path in file_paths])
    
    print(f"Loading {len(file_paths)} files from {directory_path}")
    
    data_files = {}
    for file_path in file_paths:
        try:
            filename = Path(file_path).name
            df = parse_eis_file(file_path)
            data_files[filename] = df
            print(f"  ✓ {filename} ({len(df)} points)")
        except Exception as e:
            print(f"  ✗ Error loading {filename}: {e}")
    
    print(f"Successfully loaded {len(data_files)} files")
    return data_files

def load_eis_files_from_paths(file_paths):
    """Load EIS files from specific file paths"""
    print(f"Loading {len(file_paths)} specified files...")
    
    data_files = {}
    for file_path in file_paths:
        try:
            filename = Path(file_path).name
            df = parse_eis_file(file_path)
            data_files[filename] = df
            print(f"  ✓ {filename} ({len(df)} points)")
        except Exception as e:
            print(f"  ✗ Error loading {filename}: {e}")
    
    print(f"Successfully loaded {len(data_files)} files")
    return data_files

def create_config_plot(data_files, config_path, save_path=None, show_plot=True):
    """Create plot based on config file specifications"""
    # Load config
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        print(f"✓ Loaded configuration from {config_path}")
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file {config_path} not found.")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML file: {e}")
    
    if 'files' not in config:
        raise ValueError("Config must contain 'files' section with individual file specifications.")
    
    # Create figure and axis
    figure_size = config.get('style', {}).get('figure_size', [10, 8])
    fig, ax = plt.subplots(figsize=figure_size)
    
    file_configs = config['files']
    plot_settings = config.get('plot_settings', {})
    
    for filename, file_config in file_configs.items():
        if filename not in data_files:
            print(f"⚠️  File '{filename}' specified in config but not found in loaded data")
            continue
        
        df = data_files[filename]
        
        # Get styling from config with defaults
        color = file_config.get('color', '#1f77b4')  # matplotlib default blue
        marker = file_config.get('marker', 'o')
        line_width = plot_settings.get('line_width', 2)
        marker_size = plot_settings.get('marker_size', 6)
        alpha = file_config.get('alpha', 0.8)
        linestyle = file_config.get('linestyle', '-')
        
        # Plot the data
        ax.plot(df['frequency_hz'], df['z_magnitude_ohm'],
               marker=marker, linestyle=linestyle, linewidth=line_width, 
               markersize=marker_size, color=color, label=filename, alpha=alpha,
               markerfacecolor=color, markeredgecolor='white', markeredgewidth=0.5)
    
    # Apply standard layout using config
    title = config.get('title', 'EIS Data')
    apply_standard_eis_layout(ax, title, config)
    
    # Legend configuration
    legend_config = config.get('legend', {})
    if legend_config.get('show', True):
        legend_location = legend_config.get('location', 'best')
        legend_fontsize = config.get('style', {}).get('legend_font_size', 10)
        
        if legend_location == 'outside':
            ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=legend_fontsize)
            plt.subplots_adjust(right=0.75)
        else:
            ax.legend(loc=legend_location, fontsize=legend_fontsize)
    
    # Add instructions as text box
    textstr = ('💡 Legend shows all traces\n'
               '📊 Log-log scale for frequency vs impedance\n'
               '💾 Use toolbar to save image')
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=props)


    plt.tight_layout()
    plt.show(block=True)
    
    # Save if path provided
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {save_path}")
    
    return fig, ax

def plot_eis_data(directory_path=None, file_paths=None, config_path=None, 
                  save_path=None, show_plot=True):
    """
    Main function to plot EIS data with flexible input options
    
    Args:
        directory_path (str, optional): Path to directory containing EIS files
        file_paths (list, optional): List of specific file paths to load
        config_path (str, optional): Path to YAML config for styled plotting
        save_path (str, optional): Path to save the plot image
        show_plot (bool): Whether to display the plot (default: True)
        
    Returns:
        tuple: (matplotlib.figure.Figure, matplotlib.axes.Axes) The created plot objects
        
    Usage:
        # Auto plot from directory
        fig, ax = plot_eis_data(directory_path="data/experiment/")
        
        # Auto plot with file dialog
        fig, ax = plot_eis_data()
        
        # Config-based plot
        fig, ax = plot_eis_data(directory_path="data/", config_path="config/plot.yaml")
        
        # Specific files with config and save
        fig, ax = plot_eis_data(file_paths=["file1.dta", "file2.csv"], 
                               config_path="config/plot.yaml", 
                               save_path="output/eis_plot.png")
    """
    
    # Load data files
    if directory_path:
        data_files = load_eis_files_from_directory(directory_path)
    elif file_paths:
        data_files = load_eis_files_from_paths(file_paths)
    else:
        # Open file dialog
        selected_files = select_files()
        if not selected_files:
            print("No files selected.")
            return None, None
        data_files = load_eis_files_from_paths(selected_files)
    
    # Create plot based on whether config is provided
    if config_path:
        return create_config_plot(data_files, config_path, save_path, show_plot)
    else:
        return create_auto_plot(data_files, save_path, show_plot)

def plot_directory(directory_path=None, config_path=None, save_path=None, show_plot=True):
    """Convenience function to plot all files from a directory"""
    if directory_path is None:
        directory_path = select_directory()
        if not directory_path:
            print("No directory selected.")
            return None, None
    
    return plot_eis_data(directory_path=directory_path, config_path=config_path,
                        save_path=save_path, show_plot=show_plot)

def save_plot_formats(fig, base_path, formats=['png', 'pdf', 'svg']):
    """Save plot in multiple formats"""
    base = Path(base_path).with_suffix('')
    saved_files = []
    
    for fmt in formats:
        output_path = f"{base}.{fmt}"
        fig.savefig(output_path, dpi=300, bbox_inches='tight', format=fmt)
        saved_files.append(output_path)
        print(f"Saved: {output_path}")
    
    return saved_files

def main():
    """Example usage"""
    print("=== Static EIS Plotting Examples ===")
    
    # Example 1: Auto plot with file dialog (commented out for non-interactive use)
    # print("1. Auto plot with file selection dialog:")
    # fig, ax = plot_eis_data()
    
    # Example 2: Auto plot from directory with save
    # print("2. Auto plot from directory with save:")
    # fig, ax = plot_eis_data(
    #     directory_path="/Users/rachelyuan/analysis/echem/eis_analysis/data/plot",
    #     save_path="output/auto_eis_plot.png"
    # )
    
    # Example 3: Config-based plot
    print("3. Config-based presentation plot:")
    
    try:
        fig, ax = plot_eis_data(
            directory_path="/Users/rachelyuan/analysis/echem/eis_analysis/data/plot", 
            config_path="/Users/rachelyuan/analysis/echem/eis_analysis/config/test_config.yaml",
            save_path="output/config_eis_plot.png"
        )
        # fig.show(block=True)
        # Save in multiple formats
        # if fig:
        #     save_plot_formats(fig, "output/multi_format_plot", ['png', 'pdf', 'svg'])

    except FileNotFoundError:
        print("   Create config/test_config.yaml to test config plotting")
    
    # Example 4: Directory plotting with optional config
    # print("4. Directory plotting with optional config:")
    # fig, ax = plot_directory()  # Opens directory dialog
    # fig, ax = plot_directory("data/experiment/", "config/plot.yaml", "output/dir_plot.png")

if __name__ == "__main__":
    main()