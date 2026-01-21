from flask import Flask, render_template, request
from flask_socketio import SocketIO
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


received_data = [] # Shared buffer to save received data
thread_lock_received_data = Lock() # Lock to get received data from shared buffer

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
Get data from weather station, send it to our clients
"""
def background_thread():
    while True:
        if parser.newData:
                with parser.data_lock:
                    print(parser.dataTag + " is " + str(parser.dataReal))
                    dataTag = parser.dataTag
                    data = parser.dataReal
                    parser.newData = False
                # Send data to client
                socketio.emit('updateSensorData', {'value': float(data), "date": get_current_datetime(), 'label': dataTag})
                # Add data to the shared buffer
                with thread_lock_received_data:
                    add_received_data(dataTag,data)

def add_received_data(dataTag,data):
        received_data.append({dataTag: data})           

"""
Database thread => to save data in the CSV database. Scheduled following a periodic timing
"""
def database_thread():
    global received_data
    while True:
        sleep(10.0)
        print("Writing data to database...")
        # copy data to write from shared array
        with thread_lock_received_data:
            data = deepcopy(received_data)

        # Write data to CSV file dated by today's date
        csvFileName = CSV_BASE_FILENAME + '_' + str(datetime.now().year) + '_' + datetime.now().strftime("%m") + '_' + datetime.now().strftime("%d") + '.csv'
        writtenValues = csv_write_database(Path(Path.cwd().absolute(), 'database', csvFileName), data)

        # clear all written values from buffer
        with thread_lock_received_data:
            received_data = received_data[writtenValues-1:]



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
    print('Client connected')

    with thread_lock: # not sure about this lock, comes from youtube example and I don't see why is it useful
        if thread is None:
            thread = socketio.start_background_task(background_thread)

"""
Decorator for disconnect
"""
@socketio.on('disconnect')
def disconnect():
    print('Client disconnected',  request.sid)


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


# Start parser thread
Thread(target=parser_thread).start()

# Start database thread
Thread(target=database_thread).start()

# Starting Flask server
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)

