#!/usr/bin/env python
from threading import Lock
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
import pyxinput

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

controllers = []

@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

@app.route("/init")
def init():
    global controllers
    for i in range(4):
        controllers.append(pyxinput.vController())
    return str(len(controllers))

@app.route("/controller")
def controller():
    return render_template('controller.html', async_mode=socketio.async_mode)


@socketio.on("state_update", namespace='/controller')
def state_update(message):
    id = int(message["cn"])
    event = message["event"]
    
    DPAD_OFF = 0
    DPAD_UP = 1
    DPAD_DOWN = 2
    DPAD_LEFT = 4
    DPAD_RIGHT = 8

    print(message)

    if event == "accelerate":
        controllers[id].set_value("TriggerR", 1)
    elif event == "accelerate_stop":
        controllers[id].set_value("TriggerR", 0)
    elif event == "reverse":
        controllers[id].set_value("TriggerL", 1)
    elif event == "reverse_stop":
        controllers[id].set_value("TriggerL", 0)
    elif event == "up":
        controllers[id].set_value("Dpad", DPAD_UP)
    elif event == "down":
        controllers[id].set_value("Dpad", DPAD_DOWN)
    elif event == "left":
        controllers[id].set_value("Dpad", DPAD_LEFT)
    elif event == "right":
        controllers[id].set_value("Dpad", DPAD_RIGHT)
    elif event == "dpad_up":
        controllers[id].set_value("Dpad", DPAD_OFF)
    elif event == "a_down":
        controllers[id].set_value("BtnA", 1)
    elif event == "a_up":
        controllers[id].set_value("BtnA", 0)
    elif event == "b_down":
        controllers[id].set_value("BtnB", 1)
    elif event == "b_up":
        controllers[id].set_value("BtnB", 0)
    elif event == "tilt":
        tilt = float(message["beta"]/-90)*1.4
        controllers[id].set_value("AxisLx", tilt)

if __name__ == '__main__':
    socketio.run(app, "0.0.0.0", debug=True)
