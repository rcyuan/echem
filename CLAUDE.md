# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Electrochemistry research codebase for impedance spectroscopy (EIS) measurements. Workflow: acquire multi-channel EIS data via Gamry potentiostat + multiplexer → parse binary .DTA or CSV files → visualize interactively with Plotly.

## Environment Setup

Activate the local virtual environment before running any scripts:
```bash
source .venv/Scripts/activate  # Windows Git Bash
# or
.venv\Scripts\activate         # Windows CMD/PowerShell
```

Install dependencies for the relevant subdirectory:
```bash
pip install -r acquisition/requirements.txt  # Gamry workstation
pip install -r analysis/requirements.txt     # analysis / visualization
```

## Running Scripts

**Data acquisition (requires Gamry hardware + multiplexer):**
```bash
python acquisition/ps-eis-mux-RY.py --channels 0-7 --eis-freq-start 100000 --eis-freq-stop 1 --file-path data/experiment_name
```

**Multiplexer control:**
```bash
python acquisition/mux.py --port COM3 --channel 0
```

**Interactive EIS visualization:**
```python
from analysis.src.plotting.eis_viewer import EISViewer
viewer = EISViewer()
viewer.add_directory("data/experiment_folder")
viewer.plot()
```

**Functional plotting API:**
```python
from analysis.src.plotting.eis_plotter import plot_eis_data
plot_eis_data(directory="data/experiment_folder")         # auto-style
plot_eis_data(directory="data/...", config="style.yaml")  # YAML-styled
```

## Architecture

```
acquisition/ps-eis-mux-RY.py   # Main acquisition: Gamry toolkitpy + mux.py → CSV output
acquisition/mux.py              # RS-232 multiplexer control (up to 32 channels)
acquisition/main.py             # PySide2 GUI stub (not fully integrated)

analysis/src/
  parsers/eis_parser.py         # parse_eis_file() dispatches .dta/.csv → standardized DataFrame
  plotting/eis_plotter.py       # Functional Plotly plotting (auto or YAML config)
  plotting/eis_viewer.py        # OOP wrapper: EISViewer with incremental file loading

analysis/parse_data.py          # Batch parser: walks directories, extracts metadata from filenames
```

**Standardized EIS DataFrame columns:** `frequency_hz`, `z_real_ohm`, `z_imag_ohm`, `z_magnitude_ohm`, `phase_deg`

**Data files:** Binary Gamry `.DTA` files and ASCII `.csv` files, stored in dated experiment folders under `data/` (e.g., `031326_W212-D32_baseline-t20`). Filename metadata encodes experiment type, date, probe number, and electrode.

**Gamry toolkitpy** is accessed via system path injection in acquisition scripts — requires Gamry Framework to be installed on the system.
