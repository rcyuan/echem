# echem

Working benchtop echem codebase



## Repository Structure

```
acquisition/    # Data acquisition -- just MUX interfacing for potentiostatic EIS for now
analysis/       # Just a basic .DTA/.csv parser for EIS data + quick plot scripts for now
```



## Potentiostatic EIS + MUX acquisition

### Set-up

Utilizing the MUX requires running potentiostatic EIS experiments through Gamry's toolkitpy package, rather than the Gamry Frameework software. The acquisition scripts require the 32-bit Python 3.7 installed by Gamry -- use this Python executable (e.g. within a virtual environment), not any other standard Python installs. Example set-up:

```bash
# 1. Create a virtual virtual environment (e.g. via venv) using Gamry-installed Python
"C:\Program Files (x86)\Gamry Instruments\Python37-32\python.exe" -m venv .venv

# 2. Activate virtual environment
.venv\Scripts\activate #(CMD/PowerShell)

# 3. Install dependencies
pip install -r acquisition/requirements.txt
pip install -r analysis/requirements.txt
```

> **Note:** Install `pyserial`, not `serial` — they are different packages. The requirements file specifies `pyserial` explicitly, but verify with `pip list` after install. 

> **Note:** `toolkitpy` (Gamry's instrument API) is not pip-installable. It is accessed directly from the Gamry Framework installation via a `sys.path` entry in the script.

---

### Usage

```bash
.venv\Script\activate  #(CMD/PowerShell)

# To run potentiostatic EIS on multiple channels:
python acquisition/eispot_mux.py --dataset-name my_experiment --channels 0-7, 9

# To turn individual channels on/off with MUX:
python acquisition/mux.py --set 0 3 12  #turn on channels 0, 3, 12
python acquisition/mux.py --none #turn off all channels
python acquisition/mux.py --all #turn on all channels

# To quickly plot .DTA/.csv EIS data:
python analysis/src/plotting/eis_viewer.py #by default, plots all files that are in /data/plot
```

Available arguments can be found within `eispot_mux.py` (for EIS) and `mux.py` (for MUX control). 

E.g. for potentiostatic EIS `eis_mux.py`:
- `--dataset-name` — output file prefix (required each run)
- `--channels` — accepts integers, ranges (`0-17`), or combos (`0-7,10,12`); defaults to all 32 channels
- `--mux-port` — COM port for multiplexer (default: `com3`)
- `--eis-freq-start` / `--eis-freq-stop` — frequency range in Hz (default: 100000 / 1)
- `--eis-ac-voltage` — AC voltage in V (default: 0.03)