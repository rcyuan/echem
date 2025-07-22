# src/plotting/eis_plotter.py
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from pathlib import Path
import tkinter as tk
from tkinter import filedialog
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.parsers.eis_parser import parse_eis_file

class EISPlotter:
    """Interactive EIS data plotter using Plotly"""
    
    def __init__(self):
        self.data_files = {}  # filename -> DataFrame
        self.colors = px.colors.qualitative.Set1 + px.colors.qualitative.Set2  # 20 distinct colors
        self.markers = ['circle', 'square', 'diamond', 'cross', 'x', 'triangle-up', 
                       'triangle-down', 'pentagon', 'hexagon', 'star']
        
    def select_files(self):
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
        return file_paths
    
    def select_directory(self):
        """Open dialog to select a directory containing EIS files"""
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        directory = filedialog.askdirectory(title="Select Directory with EIS Files")
        
        root.destroy()
        return directory
    
    def get_files_from_directory(self, directory_path):
        """Get all EIS files from a directory"""
        if not directory_path:
            return []
        
        directory = Path(directory_path)
        eis_extensions = ['.dta', '.DTA', '.csv']
        
        file_paths = []
        for ext in eis_extensions:
            file_paths.extend(directory.glob(f'*{ext}'))
        
        # Convert to strings and sort alphabetically
        file_paths = sorted([str(path) for path in file_paths])
        
        print(f"Found {len(file_paths)} EIS files in {directory_path}")
        if file_paths:
            print("Files found:")
            for file_path in file_paths:
                print(f"  {Path(file_path).name}")
        
        return file_paths
    
    
    def load_files(self, file_paths):
        """Load and parse selected files"""
        print("Loading files...")
        for file_path in file_paths:
            try:
                filename = Path(file_path).name
                print(f"  Loading: {filename}")
                df = parse_eis_file(file_path)
                self.data_files[filename] = df
                print(f"    ✓ Loaded {len(df)} data points")
            except Exception as e:
                print(f"    ✗ Error loading {filename}: {e}")
        
        print(f"Successfully loaded {len(self.data_files)} files")
    
    def create_plot(self):
        """Create interactive Plotly figure"""
        fig = go.Figure()
        
        for i, (filename, df) in enumerate(self.data_files.items()):
            # Cycle through colors and markers
            color = self.colors[i % len(self.colors)]
            marker = self.markers[i % len(self.markers)]
            
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
                line=dict(color=color, width=1),
                marker=dict(
                    symbol=marker,
                    size=5,
                    color=color
                ),
                hovertemplate='%{hovertext}<extra></extra>',
                hovertext=hover_text
            ))
        
        # Configure layout with log scales and formatting
        fig.update_layout(
            title="EIS Data Viewer",
            xaxis=dict(
                title="Frequency (Hz)",
                type="log",
                # showgrid=True,
                # gridwidth=1,
                # gridcolor='lightgray',
                showline=True,
                linewidth=2,
                linecolor='black',
                mirror=True,
                ticks='outside',
                ticklen=5,
                minor=dict(
                    ticklen=3,
                    tickcolor='black',
                    showgrid=False,
                    gridcolor='lightgray',
                    gridwidth=0.5
                )
            ),
            yaxis=dict(
                title="Impedance Magnitude (Ω)",
                type="log",
                # showgrid=True,
                # gridwidth=1,
                # gridcolor='lightgray',
                showline=True,
                linewidth=2,
                linecolor='black',
                mirror=True,
                ticks='outside',
                ticklen=5,
                minor=dict(
                    ticklen=3,
                    tickcolor='black',
                    showgrid=False,
                    gridcolor='lightgray',
                    gridwidth=0.5
                )
            ),
            # width=1500,   # Your preferred width
            # height=1000,   # Your preferred height
            autosize=True,
            showlegend=True,
            legend=dict(
                x=1.02,
                y=1,
                xanchor='left',
                yanchor='top'
            ),
            margin=dict(r=200),  # Extra space for legend
            plot_bgcolor='white'
        )
        
        return fig
    
    def add_files(self):
        """Add additional files to existing plot"""
        new_file_paths = self.select_files()
        if new_file_paths:
            self.load_files(new_file_paths)
            return self.update_plot()
        return None
    
    def list_loaded_files(self):
        """Print list of currently loaded files"""
        if not self.data_files:
            print("No files currently loaded.")
        else:
            print("Currently loaded files:")
            for i, filename in enumerate(self.data_files.keys(), 1):
                print(f"  {i}. {filename}")
    
    def update_plot(self):
        """Refresh the plot with current files"""
        if not self.data_files:
            print("No files to plot.")
            return None
        
        fig = self.create_plot()
        # fig.add_annotation(
        #     text="💡 Click legend items to show/hide traces<br>"
        #          "🖱️ Hover over points for details<br>"
        #          "💾 Use camera icon to save image<br>"
        #          "➕ Use plotter.add_files() to add more data",
        #     xref="paper", yref="paper",
        #     x=0.02, y=0.98,
        #     xanchor="left", yanchor="top",
        #     showarrow=False,
        #     font=dict(size=10),
        #     bgcolor="rgba(255,255,255,0.8)",
        #     bordercolor="gray",
        #     borderwidth=1
        # )
        fig.show()
        return fig

    def plot_files(self, file_paths=None):
        """Main function to load files and create plot"""
        if file_paths is None:
            file_paths = self.select_files()
        
        if not file_paths:
            print("No files selected.")
            return None
        
        self.load_files(file_paths)
        return self.update_plot()

    def plot_directory(self, directory_path=None):
        """Plot all EIS files from a directory"""
        if directory_path is None:
            directory_path = self.select_directory()
        
        if not directory_path:
            print("No directory selected.")
            return None
        
        file_paths = self.get_files_from_directory(directory_path)
        
        if not file_paths:
            print("No EIS files found in the selected directory.")
            return None
        
        self.load_files(file_paths)
        return self.update_plot()
    
    def add_directory(self):
        """Add all files from a directory to existing plot"""
        directory_path = self.select_directory()
        if directory_path:
            file_paths = self.get_files_from_directory(directory_path)
            if file_paths:
                self.load_files(file_paths)
                return self.update_plot()
        return None


def main():
    """Example usage"""
    plotter = EISPlotter()
    
    # Option 1: Interactive file selection
    # fig = plotter.plot_files()
    
    # Option 2: Programmatic file selection (uncomment to use)
    # file_paths = [
    #     "/Users/rachelyuan/analysis/echem/eis_analysis/data/raw/dta/EISPOT_071625_1K-20M_E2_banana.DTA",
    #     "/Users/rachelyuan/analysis/echem/eis_analysis/data/raw/csv/ps-eis-071625-02.csv"
    # ]
    # fig = plotter.plot_files(file_paths)

    # Option 3: Plot entire directory
    # fig = plotter.plot_directory()

    # Option 4: Programmatic directory (uncomment to use)
    fig = plotter.plot_directory("/Users/rachelyuan/analysis/echem/eis_analysis/data/plot")

if __name__ == "__main__":
    main()