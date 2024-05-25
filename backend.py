from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_socketio import SocketIO, emit, send
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session
import threading
from datetime import datetime, timedelta


user_sessions = {}
lock = threading.Lock()

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


@app.route('/chat_room.html')
def chat():
    if 'username' not in session:
        return redirect(url_for('home'))
    username = session['username']
    return render_template('chat_room.html', page='chat_room', username=username)


@socketio.on('join')
def on_join(data):
    username = data['username']
    session['username'] = username
    join_message = {'username': 'Server', 'text': f"{username} has joined the chat room."}
    send(join_message, broadcast=True)


@socketio.on('message')
def handle_message(data):
    if 'username' in session:
        username = session['username']
        text = data['text']
        emit('message', {'username': username, 'text': text}, broadcast=True)


@app.route('/check_username', methods=['POST'])
def check_username():
    data = request.get_json()
    username = data['username']
    user = mongo.db.users.find_one({"username": username})
    return jsonify({"exists": bool(user)})


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
            for username, last_activity in user_sessions.items():
                responsive_time = current_time - last_activity

                if responsive_time > timedelta(seconds=30):
                    print("Logging out user:", username)
                    mongo.db.users.update_one({"username": username}, {"$set": {"is_active": False}})
                    user_to_be_removed.append(username)

            for username in user_to_be_removed:
                del user_sessions[username]
                with app.app_context():
                    session.pop('username', None)

            user_to_be_removed.clear()

        threading.Event().wait(10)


activity_thread = threading.Thread(target=check_user_activity)
activity_thread.daemon = True
activity_thread.start()


@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    data = request.get_json()
    username = data.get('username')

    user_sessions[username] = datetime.now()

    print('Received heartbeat from user:', username)

    return "", 200


@socketio.on('disconnect')
def handle_disconnect():
    username = session.get('username')
    if username:
        with lock:
            if username in user_sessions:
                del user_sessions[username]
        mongo.db.users.update_one({"username": username}, {"$set": {"is_active": False}})
        session.clear()
        print(f"User {username} disconnected")
        print('huh')

        socketio.emit('redirect')


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
