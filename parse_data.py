import importlib
import inspect
import os
from pathlib import Path
import gamry_parser  
import pandas as pd

def build_parser_dict():
    # get module files
    base_path = os.path.dirname(gamry_parser.__file__)
    module_files = [
        f for f in os.listdir(base_path)
        if f.endswith('.py') and f != '__init__.py' and f != 'version.py'
    ]

    # build parser dict from modules
    parser_dict = {}
    for module_file in module_files:
        # dynamically import module
        module_name = os.path.splitext(module_file)[0]
        module = importlib.import_module(f'gamry_parser.{module_name}')

        # inspect module & get name of the only class defined
        classes = inspect.getmembers(module, inspect.isclass)
        local_classes = [cls for name, cls in classes if cls.__module__ == module.__name__]
        if len(local_classes) != 1:
            raise RuntimeError(f"Expected exactly one class in {module.__name__}, found {len(local_classes)}.")

        # save to dict
        parser_dict[module_name] = local_classes[0]  
    return parser_dict

def get_site_size(probe_num, E_num):
    # !! assumes v2 flex wafer numbering !!
    
    # figure out site design based on probe_num (e.g. all large sites, all small sites, or mixed)
    probe_num = int(probe_num)
    if 1 <= probe_num <= 14 or 25 <= probe_num <= 34 or 55 <= probe_num <= 70:
        sites = 'large'
        refs = 'large'
    elif 35 <= probe_num <= 54:
        if probe_num >= 45: 
            sites = 'mix'
            refs = 'small'
        else:
            sites = 'mix'
            refs = 'large'
    elif 15 <= probe_num <= 24:
        sites = 'small'
        refs = 'large'

    # determine if this site is large or small (or N/A, e.g. if all shorted)
    if E_num.isdigit():
        if (sites == 'large') or ((sites == 'mix') and (int(E_num) % 2 == 0)):
            site_size = 'large'
        elif (sites == 'small') or ((sites == 'mix') and (int(E_num) % 2 != 0)):
            site_size = 'small'
    elif (E_num == 'tip') | (E_num == 'shank'):
        site_size = refs
    else:
        site_size = 'N/A'
    return site_size


def parse_files(data_dir):
    # build dictionary of parsers
    parser_dict = build_parser_dict()

    #specify .dta files to parse
    data_dir = '/Users/rachelyuan/data/gamry' #search within here, including this folder and any subfolders
    DTA_files = []
    for root, _, files in os.walk(data_dir):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith('.DTA'):
                DTA_files.append(file_path)

    # loop over files; parse metadata & data from each
    eis_meta = []
    cv_meta = []
    chrono_meta = []
    data = {}
    for file in DTA_files:
        # load file with the appropriate parser by matching to entry parser_dict
        filename = Path(file).stem
        filename_split = filename.split('_')
        expt_tag = filename_split[0] #first item should always be exp't tag ID
        
        if expt_tag in parser_dict:
            parser_cls = parser_dict[expt_tag]
            parser = parser_cls() 
            # print(f"Using parser {parser_cls.__name__} for file: {filename}")
            parser.load(file) #load/parse file
        else:
            print(f"No parser found for file: {filename}")
            continue

        data[filename] = [parser.curve(n) for n in parser.curve_indices] #list of dataframes for each curve
        
        probe_num = filename_split[2].split('-')[1][1:]
        E_num = filename_split[3]
        # store metadata
        record = {
            'filename': filename,
            'expt_type': filename_split[0],
            'expt_date': filename_split[1],
            'ID': filename_split[2],
            'E_num': E_num,
            'site_size': get_site_size(probe_num, E_num),
            'electrode': filename_split[4],
            'electrolyte': filename_split[5],
            'repeat': filename_split[6],
        }
        
        match expt_tag:
            case 'EISPOT' | 'GALVEIS':
                eis_meta.append(record)
            case 'CV': 
                record['scan_rate'] = parser.scan_rate
                record['v_range'] = parser.v_range
                record['num_curves'] = parser.curve_count
                cv_meta.append(record)
            case 'CHRONOA' | 'CHRONOP':
                record['sample_time'] = parser.sample_time
                record['sample_count'] = parser.sample_count
                chrono_meta.append(record)
            case _:
                print(f"Skipping {expt_tag} file ({filename})") #skip non-EIS/CV/CHRONOA/CHRONOP experiments (for now?)
    
    return data, eis_meta, cv_meta, chrono_meta