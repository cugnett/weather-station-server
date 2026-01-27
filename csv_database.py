import csv
import datetime
from pathlib import Path
from collections import defaultdict

CSV_BASE_FILENAME = 'weather_data_'

FIELDNAMES = ["TIMESTAMP", "TEMPERATURE_INTERNAL", "TEMPERATURE", "PRESSURE", "WIND_SPEED", "HUMIDITY"]
## TO DO LATER => make a better way to manage fieldnames
## TO DO LATER => give the timestamp responsability to the weather station by setting up a Real Time Clock
"""
Write data in CSV file
:param csvfilepath: (Path object) csv file path
:param data: (list(Dictionary)) data to write in format [{key1: value1}, {key2:value2}...].
:return: the number of values written in the database. Because the csv is structured by line, last values may not be written if they do not form a complete line at execution
"""
def csv_write_database(data):

    # 1 - Structure data received to match csv format. We assume we received data ordered
    structured_data = [{}]
    i = 0
    for dict in data: #data is a list of dict
        for key, value in dict.items():
            structured_data[i][key] = value
            # if I completed a line jump to the next one
            if len(structured_data[i]) == len(FIELDNAMES):
                structured_data.append({})
                i += 1
    # remove last line if incomplete and compute numbers of values to write in db
    if len(structured_data[-1]) < len(FIELDNAMES):
        structured_data.pop()
    writeValueNb = len(structured_data)*len(FIELDNAMES)

    # 2 - Generate a csv file name corresponding to the timestamp date for each line (it's ok because we don't have much data to treat)
    #csvfilepath = generate_filepaths(structured_data)
    datedStructuredData = defaultdict(list)
    for dict in structured_data:
        # determine date
        currentDate = dict["TIMESTAMP"].date().strftime("%Y_%m_%d")
        datedStructuredData[currentDate].append(dict)
    
    # 3 - For each date we add data in a different file
    for date, dataToWrite in datedStructuredData.items():
        # Generate filepath
        csvFileName = CSV_BASE_FILENAME + '_' + date + '.csv'
        csvfilepath = Path(Path.cwd().absolute(), 'database', csvFileName)
        # Check if CSV file exist and creates it if it does not exist
        if not csvfilepath.is_file():
            csv_create(csvfilepath)

        # Add data to file
        with open(csvfilepath, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES,  delimiter=',')
            writer.writerows(dataToWrite)
            #print(f"Written {writeValueNb} values in db!!!")
    return writeValueNb

"""
Create new csv file. Overwrite any already existing file with same path
"""
def csv_create(csvfilepath):
    with open(csvfilepath, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=FIELDNAMES,  delimiter=',')
        writer.writeheader()