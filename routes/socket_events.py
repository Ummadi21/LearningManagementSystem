from flask_socketio import emit
from extensions import socketio

# Send welcome message to all connected clients
@socketio.on('connect')
def handle_connect():
    print("Client connected")
    emit('server_message', {'msg': 'Welcome to LMS Notifications!'})

# Broadcast course update to all
def send_course_update(course_name):
    socketio.emit('course_update', {
        "msg": f"New update in course: {course_name}"
    })

# Disconnect event
@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")