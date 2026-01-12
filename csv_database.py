import csv
from pathlib import Path

CSV_BASE_FILENAME = 'weather_data_'

FIELDNAMES = ["TEMPERATURE_INTERNAL", "TEMPERATURE", "PRESSURE", "WIND_SPEED", "HUMIDITY"]
## TO DO LATER => make a better way to manage fieldnames

"""
Write data in CSV file
:param csvfilepath: (Path object) csv file path
:param data: (list(Dictionary)) data to write in format [{key1: value1}, {key2:value2}...].
:return: the number of values written in the database. Because the csv is structured by line, last values may not be written if they do not form a complete line at execution
"""
def csv_write_database(csvfilepath, data):

    # 1 - Check if CSV file exist and creates it if it does not exist
    if not csvfilepath.is_file():
        csv_create(csvfilepath)
    # 2 - Structure data received to match csv format. We assume we received data ordered
    structured_data = [{}]
    i = 0
    for dict in data: #data is a list of dict
        for key, value in dict.items():
            structured_data[i][key] = value
            # if I completed a  line jump to the next one
            if len(structured_data[i]) == len(FIELDNAMES):
                structured_data.append({})
                i += 1
    #remove last line if incomplete and compute numbers of values to write in db
    if len(structured_data[-1]) < len(FIELDNAMES):
        structured_data.pop()
    writeValueNb = len(structured_data)*len(FIELDNAMES)


    # 3 - Add data to file
    with open(csvfilepath, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES,  delimiter=',')
        writer.writerows(structured_data)
        print(f"Written {writeValueNb} values in db!!!")
    return writeValueNb

"""
Create new csv file. Overwrite any already existing file with same path
"""
def csv_create(csvfilepath):
    with open(csvfilepath, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES,  delimiter=',')
        writer.writeheader()

"""
Save specified data  in file in parameter
data shall be in format :
{ 'field': data }
"""                   
def csv_write_single_data(csvfilepath, data):

    with open(csvfilepath, 'r', newline='') as csvfile:
        # Get existing csv columns (fields)
        reader = csv.DictReader(csvfile, delimiter=',')
        fieldnames = reader.fieldnames

        # If the CSV file is empty, there is no fieldnames so fieldnames is None. However we need it to be an array to append new fields
        if fieldnames == None:
            fieldnames = []
        # extend with new fields if needed
        for key in data.keys():
            if not key in fieldnames:
                fieldnames.append(key)
        print(fieldnames)

        # add data to csv file
    with open(csvfilepath, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames,  delimiter=',')
        writer.writeheader()
        writer.writerow(data)