import glob
import os

def get_starting_block_number(file_name):
    with open(file_name, 'r') as f:
        for line in f:
            break # ignore header

        for line in f:
            block_number = int(line.split(',')[0])
            return block_number

data_files = glob.glob("data-traces/*.csv")
data_files = [(file_name, get_starting_block_number(file_name)) for file_name in data_files]
data_files = sorted(data_files, key=lambda x: x[1])

for idx, item in enumerate(data_files):
    print(item[0])
    print(idx)
    result_fname = "data-adjusted-"+str(idx).rjust(4, '0')+".csv"
    print(result_fname)
    os.rename(item[0], "data-traces/"+result_fname)
