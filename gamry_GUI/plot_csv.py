import os
import pandas as pd

data_dir = r"C:\Users\rachel.yuan\src\echem\data\071625"
filename = "ps-eis-071625-02.csv"
csv = pd.read_csv(os.path.join(data_dir, filename), skiprows=1, 
                  usecols=range(5),
                  names=['Point', 'Freq', 'Zmod', 'Zimag', 'IE Range'])
print(csv)


