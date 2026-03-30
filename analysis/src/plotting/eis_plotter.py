# src/plotting/eis_plotter.py
import plotly.graph_objects as go
import plotly.express as px
import yaml
import pandas as pd
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.parsers.eis_parser import parse_eis_file

def apply_standard_eis_layout(fig, title="EIS Data", config=None):
    """Apply standard EIS plot layout to any figure"""
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
    
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=title_font_size)
        ),
        xaxis=dict(
            title=dict(
                text="Frequency (Hz)",
                font=dict(size=axis_font_size)
            ),
            type="log",
            # showgrid=True,
            # gridwidth=1,
            # gridcolor='lightgray',
            showline=True,
            linewidth=1,
            linecolor='black',
            mirror=True,
            ticks='outside',
            ticklen=5,
            tickfont=dict(size=axis_font_size),
            minor=dict(
                ticklen=3,
                tickcolor='black',
                # showgrid=True,
                # gridcolor='lightgray',
                # gridwidth=0.5
            )
        ),
        yaxis=dict(
            title=dict(
                text="Impedance Magnitude (Ω)",
                font=dict(size=axis_font_size)
            ),
            type="log", 
            # showgrid=True,
            # gridwidth=1,
            # gridcolor='lightgray',
            showline=True,
            linewidth=1,
            linecolor='black',
            mirror=True,
            ticks='outside',
            ticklen=5,
            tickfont=dict(size=axis_font_size),
            minor=dict(
                ticklen=3,
                tickcolor='black',
                # showgrid=True,
                # gridcolor='lightgray',
                # gridwidth=0.5
            )
        ),
        width=figure_size[0] * 100,  # Convert to pixels
        height=figure_size[1] * 100,
        showlegend=True,
        legend=dict(
            font=dict(size=legend_font_size)
        ),
        plot_bgcolor='white'
    )
    
    return fig

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

def create_auto_plot(data_files):
    """Create plot with automatic colors and markers"""
    if not data_files:
        print("No data files provided.")
        return None
    
    fig = go.Figure()
    
    # Auto-generated colors and markers
    colors = px.colors.qualitative.Set1 + px.colors.qualitative.Set2  # 20 distinct colors
    markers = ['circle', 'square', 'diamond', 'cross', 'x', 'triangle-up', 
               'triangle-down', 'pentagon', 'hexagon', 'star']
    
    for i, (filename, df) in enumerate(data_files.items()):
        # Cycle through colors and markers
        color = colors[i % len(colors)]
        marker = markers[i % len(markers)]
        
        # Create hover text with filename, frequency, and impedance
        hover_text = [
            f"File: {filename}<br>"
            f"Frequency: {freq:.2e} Hz<br>"
            f"Impedance: {z:.2e} Ω"
            for freq, z in zip(df['frequency_hz'], df['z_magnitude_ohm'])
        ]
        
        fig.add_trace(go.Scatter(
            x=df['frequency_hz'],
            y=df['z_magnitude_ohm'],
            mode='markers+lines',
            name=filename,
            line=dict(color=color, width=2),
            marker=dict(
                symbol=marker,
                size=8,
                color=color,
                line=dict(width=1, color='white')
            ),
            hovertemplate='%{hovertext}<extra></extra>',
            hovertext=hover_text
        ))
    
    # Apply standard layout
    apply_standard_eis_layout(fig, "EIS Data Viewer")
    
    # Add viewer-specific styling
    fig.update_layout(
        legend=dict(
            x=1.02,
            y=1,
            xanchor='left',
            yanchor='top'
        ),
        margin=dict(r=200),  # Extra space for legend
        autosize=True  # Responsive sizing
    )
    
    # Add instructions
    fig.add_annotation(
        text="💡 Click legend items to show/hide traces<br>"
             "🖱️ Hover over points for details<br>"
             "💾 Use camera icon to save image",
        xref="paper", yref="paper",
        x=0.02, y=0.98,
        xanchor="left", yanchor="top",
        showarrow=False,
        font=dict(size=10),
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="gray",
        borderwidth=1
    )
    
    fig.show()
    return fig

def create_config_plot(data_files, config_path):
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
    
    fig = go.Figure()
    file_configs = config['files']
    
    for filename, file_config in file_configs.items():
        if filename not in data_files:
            print(f"⚠️  File '{filename}' specified in config but not found in loaded data")
            continue
        
        df = data_files[filename]
        
        # Get styling from config
        color = file_config.get('color', '#AEC7E8')
        marker = file_config.get('marker', 'circle')
        
        # Create hover text with filename, frequency, and impedance
        hover_text = [
            f"File: {filename}<br>"
            f"Frequency: {freq:.2e} Hz<br>"
            f"Impedance: {z:.2e} Ω"
            for freq, z in zip(df['frequency_hz'], df['z_magnitude_ohm'])
        ]

        fig.add_trace(go.Scatter(
            x=df['frequency_hz'],
            y=df['z_magnitude_ohm'],
            mode='markers+lines',
            name=filename,
            line=dict(
                color=color, 
                width=config.get('plot_settings', {}).get('line_width', 2)
            ),
            marker=dict(
                symbol=marker,
                size=config.get('plot_settings', {}).get('marker_size', 8),
                color=color
            ),
            hovertemplate='%{hovertext}<extra></extra>',
            hovertext=hover_text
        ))
    
    # Apply standard layout using config
    title = config.get('title', 'EIS Data')
    apply_standard_eis_layout(fig, title, config)
    
    fig.show()
    return fig

def plot_eis_data(directory_path=None, file_paths=None, config_path=None):
    """
    Main function to plot EIS data with flexible input options
    
    Args:
        directory_path (str, optional): Path to directory containing EIS files
        file_paths (list, optional): List of specific file paths to load
        config_path (str, optional): Path to YAML config for styled plotting
        
    Returns:
        plotly.graph_objects.Figure: The created plot
        
    Usage:
        # Auto plot from directory
        plot_eis_data(directory_path="data/experiment/")
        
        # Auto plot with file dialog
        plot_eis_data()
        
        # Config-based plot
        plot_eis_data(directory_path="data/", config_path="config/plot.yaml")
        
        # Specific files with config
        plot_eis_data(file_paths=["file1.dta", "file2.csv"], config_path="config/plot.yaml")
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
            return None
        data_files = load_eis_files_from_paths(selected_files)
    
    # Create plot based on whether config is provided
    if config_path:
        return create_config_plot(data_files, config_path)
    else:
        return create_auto_plot(data_files)

def plot_directory(directory_path=None, config_path=None):
    """Convenience function to plot all files from a directory"""
    if directory_path is None:
        directory_path = select_directory()
        if not directory_path:
            print("No directory selected.")
            return None
    
    return plot_eis_data(directory_path=directory_path, config_path=config_path)


def main():
    """Example usage"""
    # print("=== Simple EIS Plotting Examples ===")
    
    # Example 1: Auto plot with file dialog
    # print("1. Auto plot with file selection dialog:")
    # fig1 = plot_eis_data()
    
    # Example 2: Auto plot from directory
    # print("2. Auto plot from directory:")
    # fig2 = plot_eis_data(directory_path="/Users/rachelyuan/analysis/echem/eis_analysis/data/plot")
    
    # Example 3: Config-based plot
    print("3. Config-based presentation plot:")
    try:
        fig3 = plot_eis_data(directory_path="/Users/rachelyuan/analysis/echem/eis_analysis/data/plot", config_path="/Users/rachelyuan/analysis/echem/eis_analysis/config/test_config.yaml")
        pass
    except FileNotFoundError:
        print("   Create config/manual_plot.yaml to test config plotting")
    
    # Example 4: Directory convenience function
    # print("4. Directory plotting with optional config:")
    # fig4 = plot_directory()  # Opens directory dialog
    # fig5 = plot_directory("data/experiment/", "config/plot.yaml")


if __name__ == "__main__":
    main()