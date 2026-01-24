from flask import Flask, render_template, request
from flask_socketio import SocketIO
import logging
from logging.handlers import RotatingFileHandler
from queue import Queue
from threading import Lock, Thread, Timer
from datetime import datetime
from parser import Parser
from copy import deepcopy
from csv_database import csv_write_database, CSV_BASE_FILENAME
from pathlib import Path
from time import sleep
from weather_data import get_weather_data

"""
Background Thread => to send real time sensor data to the client
"""
thread = None
thread_lock = Lock()


received_data = [] # Buffer to contain received data, used to allow received data to be written in database
thread_lock_received_data = Lock() # Lock to access received buffer

data_to_send = [] # Buffer to contain received data, used to send data to clients connected to the server
thread_lock_data_to_send = Lock() # Lock to access data_to_send buffer

# Setting logging module
logger = logging.getLogger()
logFormatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
logger.addHandler(consoleHandler)

fileHandler = RotatingFileHandler("server_logs.log", backupCount=100, maxBytes=65536)
fileHandler.setFormatter(logFormatter)
logger.addHandler(fileHandler)


# Creating Flask instance
app = Flask(__name__)

# Creating socket instance
socketio = SocketIO(app, cors_allowed_origins='*')

# Creating the parser instance
parser = Parser() #should be a singleton

"""
Get current date time
"""
def get_current_datetime():
    now = datetime.now()
    return now.strftime("%H:%M:%S")

"""
Get data from weather station, and stores it in relevant buffer used for communication with other threads
"""
def background_thread():
    while True:
        if parser.newData:
            with parser.data_lock:
                app.logger.info(parser.dataTag + " is " + str(parser.dataReal))
                dataTag = parser.dataTag
                data = parser.dataReal
                parser.newData = False
                parser.newDataConsumed = True
            # Add data to the received data buffer (used for database write)
            with thread_lock_received_data:
                received_data.append({dataTag: data})
            # Add data to the send_data buffer (used for communication with clients)
            with thread_lock_data_to_send:
                data_to_send.append({dataTag: data})
            app.logger.info("Data added to buffers!!")

"""
Send data to our clients
"""          
def send_data_thread():
    global data_to_send
    while True:
        sleep(1.0)
        # copy data to write from shared array
        with thread_lock_data_to_send:   
            data_array = deepcopy(data_to_send)

        # Send data to client
        sentValues = 0
        for data_dict in data_array:
            for dataTag,data in data_dict.items():
                app.logger.info("Emit data to client...")
                socketio.emit('updateSensorData', {'value': float(data), "date": get_current_datetime(), 'label': dataTag})
                sentValues += 1
        # clear all sent values from buffer        
        with thread_lock_data_to_send: 
            data_to_send = data_to_send[sentValues:]

"""
Database thread => to save data in the CSV database. Scheduled following a periodic timing
"""
def database_thread():
    global received_data
    while True:
        sleep(10.0)
        app.logger.info("Writing data to database...")
        # copy data to write from shared array
        with thread_lock_received_data:
            data = deepcopy(received_data)

        # Write data to CSV file dated by today's date
        csvFileName = CSV_BASE_FILENAME + '_' + str(datetime.now().year) + '_' + datetime.now().strftime("%m") + '_' + datetime.now().strftime("%d") + '.csv'
        writtenValues = csv_write_database(Path(Path.cwd().absolute(), 'database', csvFileName), data)

        # clear all written values from buffer
        with thread_lock_received_data:
            received_data = received_data[writtenValues:]



"""
Parse sensor data and stores it in the parser
"""
def parser_thread():
    parser.parse_data()





@app.route("/")
def index():
    date_time = datetime.now()
    y = date_time.year
    m = date_time.month
    d = date_time.day
    h = date_time.hour
    min = date_time.minute
    s = date_time.second
    return render_template("index.html", year=y, month=m, day=d, hour=h, minute=min, second=s)

"""
Decorator for connect
"""
@socketio.on('connect')
def connect():
    global thread
    app.logger.info('Client connected')

    with thread_lock: # not sure about this lock, comes from youtube example and I don't see why is it useful
        if thread is None:
            thread = socketio.start_background_task(send_data_thread)

"""
Decorator for disconnect
"""
@socketio.on('disconnect')
def disconnect():
    app.logger.info('Client disconnected',  request.sid)


"""
Route to access web page to display and analyze data from database
"""
@app.route("/weather_data", methods = ["GET", "POST"])
def weather_data():
    if request.method == 'POST':
        date = request.form.get("date")
        if date is not None:
            (labels, data) = get_weather_data(date)
    else:
        date = None
        (labels, data) = (None, None)
    return render_template("weather_data.html", date=date, labels=labels, data=data)

# Start background thread
Thread(target=background_thread).start()

# Start parser thread
Thread(target=parser_thread).start()

# Start database thread
Thread(target=database_thread).start()

# Starting Flask server
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)

