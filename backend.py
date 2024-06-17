from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_socketio import SocketIO, emit, send, join_room, leave_room
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
import threading
from datetime import datetime, timedelta
import secrets
import string


user_sessions = {}
user_last_activity = {}
lock = threading.Lock()
public_room_id = "we6Tv77yM70LHhRyIprn"

app = Flask(__name__)
app.config["SECRET_KEY"] = "its_a_secret_lmaoooo_ahahaha"
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"] = "../Chat-app/flask_session_data"
app.config["MONGO_URI"] = "mongodb://localhost:27017/Summers"
Session(app)

socketio = SocketIO(app)
mongo = PyMongo(app)


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = mongo.db.users.find_one({"username": username})
        if user and check_password_hash(user["password"], password):
            session['username'] = username
            return redirect(url_for('chat'))
        else:
            return "Invalid credentials!", 401
    return render_template('home.html')


@app.route('/signup.html')
def signup():
    return render_template('signup.html')


@app.route('/general_chat_room/we6Tv77yM70LHhRyIprn')
def chat():
    if 'username' not in session:
        return redirect(url_for('home'))
    username = session['username']
    return render_template('general_chat_room.html', page='chat_room', username=username, room_id=public_room_id)


@app.route('/chatroom/<room_id>')
def chat_room(room_id):
    if 'username' not in session:
        return redirect(url_for('home'))
    username = session['username']
    return render_template('my_chat_room.html', page='chat_room', username=username, room_id=room_id)


@app.route('/my_space.html')
def my_space():
    if 'username' not in session:
        return redirect(url_for('home'))
    username = session['username']
    return render_template('my_space.html', page='my_space', username=username)


@socketio.on('join')
def on_join(data):
    try:
        username = data['username']
        room_id = data.get('room_id')  # Adjust to fetch room_id if used

        if not username:
            raise ValueError('Username not provided in join request')

        session['username'] = username

        join_message = {'username': 'Server', 'text': f"{username} has joined the chat room."}
        join_room(room_id)
        send(join_message, room=room_id)

    except KeyError as e:
        print(f"Error: Missing key {e}")

    except ValueError as ve:
        print(f"Error: {ve}")
        # Handle value error (eg. username not provided)

    except Exception as ex:
        print(f"Error: {ex}")


@socketio.on('message')
def handle_message(data):
    if 'username' in session:
        print(data)
        username = session['username']
        text = data['text']
        room_id = data.get('room_id')
        emit('message', {'username': username, 'text': text}, room=room_id)


@app.route('/check_username', methods=['POST'])
def check_username():
    data = request.get_json()
    username = data['username']
    user = mongo.db.users.find_one({"username": username})
    return jsonify({"exists": bool(user)})


@socketio.on('connect')
def handle_connect():
    username = session.get('username')
    if username:
        user_sessions[username] = request.sid
        print(user_sessions)


def generate_room_id():
    room_id_length = 20
    characters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    room_id = ''.join(secrets.choice(characters) for i in range(room_id_length))
    if room_id != public_room_id:
        print(f"Room ID is: {room_id}")
        return f"room_{room_id}"
    else:
        generate_room_id()


@app.route('/sending_request_for_username', methods=['POST'])
def check_and_send_username():
    data = request.get_json()
    username = data.get("username")
    himself = data.get("my_name")

    if username != himself:
        user = mongo.db.users.find_one({"username": username})
        if user:
            recipient_sid = user_sessions.get(username)
            if recipient_sid:
                room_id = generate_room_id()
                emit('friend_search_notification', {'username': himself, 'roomId': room_id}, room=recipient_sid, namespace='/')
                return jsonify({"exists": True, "roomId": room_id})
        return jsonify({"exists": False})
    return jsonify({"exists": False})


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']

    if mongo.db.users.find_one({"username": username}):
        return jsonify({"success": False, "message": "Username already exists"}), 400

    hashed_password = generate_password_hash(password)
    user = {
        "username": username,
        "password": hashed_password,
        "is_active": False  # used to check if user is already logged in (not while reg-ing, ofc lmao)
    }
    mongo.db.users.insert_one(user)

    return jsonify({"success": True, "message": "User registered successfully"}), 201


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    user = mongo.db.users.find_one({"username": username})
    if user:
        if user.get('is_active'):
            return jsonify({"success": False, "message": "Invalid username or password"}), 403
        if check_password_hash(user["password"], password):
            session['username'] = username
            mongo.db.users.update_one({"username": username}, {"$set": {"is_active": True}})
            return jsonify({"success": True, "message": "Logged in successfully"}), 200

    return jsonify({"success": False, "message": "Invalid username or password"}), 401


@app.route('/set_inactive', methods=['POST'])
def set_inactive():
    data = request.get_json()
    username = data.get('username')

    if data:
        mongo.db.users.update_one({"username": username}, {"$set": {"is_active": False}})
        session.clear()
        return jsonify({"success": True}), 200
    else:
        return jsonify({"success": False}), 400


def check_user_activity():
    while True:
        current_time = datetime.now()

        with lock:
            user_to_be_removed = []
            for username, last_activity in user_last_activity.items():
                responsive_time = current_time - last_activity

                if responsive_time > timedelta(seconds=15):
                    print("Logging out user:", username)
                    mongo.db.users.update_one({"username": username}, {"$set": {"is_active": False}})
                    user_to_be_removed.append(username)

            for username in user_to_be_removed:
                del user_sessions[username]
                with app.test_request_context():
                    session.pop('username', None)

            user_to_be_removed.clear()

        threading.Event().wait(5)


activity_thread = threading.Thread(target=check_user_activity)
activity_thread.daemon = True
activity_thread.start()


@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    data = request.get_json()
    username = data.get('username')

    with lock:
        user_last_activity[username] = datetime.now()

    print('Received heartbeat from user:', username)
    status = mongo.db.users.find_one({"username": username})
    if status and not status.get('is_active'):
        mongo.db.users.update_one({"username": username}, {"$set": {"is_active": True}})

    return "", 200


# @socketio.on('disconnect')
# def handle_disconnect():
#     username = session.get('username')
#     if username:
#         # with lock:
#             # if username in user_sessions:
#                 # del user_sessions[username]
#         # mongo.db.users.update_one({"username": username}, {"$set": {"is_active": False}})
#         # session.clear()
#         print(f"User {username} disconnected")


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
