import gamry_parser
import pandas as pd

def parse_eis_file(filepath):
    """Parse EIS file (.dta or .csv) and return standardized DataFrame"""
    if filepath.endswith('.dta') or filepath.endswith('.DTA'):
        return parse_dta_file(filepath)
    elif filepath.endswith('.csv'):
        return parse_csv_file(filepath)
    else:
        raise ValueError(f"Unsupported file type: {filepath}")

def parse_dta_file(filepath):
    """Parse .dta file using gamry_parser"""
    z = gamry_parser.Impedance()
    z.load(filepath)
    raw_data = z.curves[0]  # This returns the DataFrame
    return standardize_eis_data(raw_data)

def parse_csv_file(filepath):
    """Parse CSV file"""
    raw_data = pd.read_csv(
        filepath, 
        skiprows=1,
        usecols=range(6), 
        names=['Point', 'Freq', 'Zreal', 'Zimag', 'Zmod', 'Zphz']
    )
    return standardize_eis_data(raw_data)

def standardize_eis_data(raw_data):
    """Convert raw data to standard format"""
    return pd.DataFrame({
        'frequency_hz': raw_data['Freq'],
        'z_real_ohm': raw_data['Zreal'],
        'z_imag_ohm': raw_data['Zimag'],
        'z_magnitude_ohm': raw_data['Zmod'],
        'phase_deg': raw_data['Zphz']
    })