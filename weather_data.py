from csv_database import CSV_BASE_FILENAME
import pandas as pd
from pathlib import Path
# Allow to generate figures from CSV database

def get_weather_data(date):
    # date is received in yyyy-mm-dd format
    #print("###########################Test")

    year = date[0:4]
    month = date[5:7]
    day = date[8:10]
    csv_file = f"{CSV_BASE_FILENAME}_{year}_{month}_{day}.csv"
    csvfilepath = Path(Path.cwd().absolute(), 'database', csv_file)

    # Return nothing if no csv file found
    if not csvfilepath.is_file():
        return (None, None)
    #else read data from csv file
    df = pd.read_csv(Path(Path.cwd().absolute(), 'database', csv_file))

    #get timestamp as a time at format h:m:s
    time = convert_to_h_m_s(df['TIMESTAMP'].tolist())
    #get a dict of list { 'datalabel1':[d1, d2, d3]...}
    data = {}
    for series_name, series in df.items():
        data[series_name] = series.tolist()

    return (time, data)



def convert_to_h_m_s(datetime_list):
    time_list = []
    for datetime in datetime_list:
        # datetime format is => 2026-01-19 11:05:50
        time = datetime.split(' ')[1]
        time_list.append(time)
    return time_list
