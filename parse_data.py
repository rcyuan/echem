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

def get_site_ref_sizes(probe_num):
    # !! assumes v2 flex wafer numbering !!
    probe_num = int(probe_num)
    if 1 <= probe_num <= 14 or 25 <= probe_num <= 34 or 55 <= probe_num <= 70:
        return 'large', 'large'
    elif 35 <= probe_num <= 54:
        if probe_num >= 45: 
            return 'mix', 'small'
        else:
            return 'mix', 'large'
    elif 15 <= probe_num <= 24:
        return 'small', 'large'


def parse_files(data_dir):
    # build dictionary of parsers
    parser_dict = build_parser_dict()

    #specify .dta files to parse
    DTA_files = []
    for root, _, files in os.walk(data_dir):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith('.DTA'):
                DTA_files.append(file_path)

    # loop over files; parse metadata & data from each
    metadata = []
    data = {}
    for file in DTA_files:
        # load file with the appropriate parser by matching to entry parser_dict
        filename = Path(file).stem
        filename_split = filename.split("_")
        expt_tag = filename_split[0].lower() #first item should always be exp't tag ID
        if expt_tag in parser_dict:
            parser_cls = parser_dict[expt_tag]
            parser = parser_cls() 
            # print(f"Using parser {parser_cls.__name__} for file: {filename}")
            parser.load(file) #load/parse file
        else:
            print(f"No parser found for file: {filename}")
            continue

        # store data
        data[filename] = parser.curves
        
        # store metadata
        record = {
            "filename": filename,
            "expt_type": filename_split[0],
            "expt_date": filename_split[1],
            "ID": filename_split[2],
            **dict(zip(["site_size", "ref_size"], get_site_ref_sizes(filename_split[2].split('-')[1][1:]))),
            "E_num": filename_split[3],
            "electrode": filename_split[4],
            "electrolyte": filename_split[5],
            "repeat": filename_split[6],
        }
        metadata.append(record)
    return pd.DataFrame(metadata), data