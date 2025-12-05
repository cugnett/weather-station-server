from flask import Flask, render_template, request
from flask_socketio import SocketIO
from random import random
from threading import Lock
from datetime import datetime

"""
Background Thread => to send real time sensor data to the client
"""
thread = None
thread_lock = Lock()

# Creating Flask instance
app = Flask(__name__)

# Creating socket instance
socketio = SocketIO(app, cors_allowed_origins='*')


"""
Get current date time
"""
def get_current_datetime():
    now = datetime.now()
    return now.strftime("%m/%d/%Y %H:%M:%S")

"""
Generate random sequence of dummy sensor values and send it to our clients
"""
def background_thread():
    print("Generating random sensor values")
    while True:
        dummy_sensor_value = round(random() * 100, 3)
        socketio.emit('updateSensorData', {'value': dummy_sensor_value, "date": get_current_datetime()})
        socketio.sleep(1)



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

    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)

"""
Decorator for disconnect
"""
@socketio.on('disconnect')
def disconnect():
    print('Client disconnected',  request.sid)

# # Testing and learning Can be removed later
# @app.route("/time")
# def time():
#     date_time = datetime.datetime.now()
#     h = date_time.hour
#     m = date_time.minute
#     s = date_time.second
#     return render_template("time.html", hour=h, minute=m, second=s)

# liste_eleves = [
#     {'nom':'Doe', 'prenom':'John', 'classe': '2A'},
#     {'nom':'Doe1', 'prenom':'John1', 'classe': '3A'},
#     {'nom':'Doe2', 'prenom':'John2', 'classe': '3A'},
#     {'nom':'Doe3', 'prenom':'John3', 'classe': '2A'},
#     {'nom':'Doe4', 'prenom':'John4', 'classe': '2A'},
    
# ]

# @app.route("/eleves")
# def eleves():
#     classe = request.args.get('c')
#     if classe:
#         eleves_select = [eleve for eleve in liste_eleves if eleve['classe'] == classe]
#     else:
#         eleves_select = []
#     return render_template("eleves.html", eleves=eleves_select)

# @app.route("/formulaires")
# def formulaires():
#     return render_template("formulaires.html")

# @app.route("/traitement", methods = ["POST"])
# def traitement():
#     donnees = request.form
#     return render_template("traitement.html", donnees=donnees)

"""
Route to access web page to display and analyze data from database
"""
@app.route("/weather_data")
def weather_data():
    return render_template("weather_data.html")

# Starting Flask server
if __name__ == '__main__':
    app.run(debug=True)