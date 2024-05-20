from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_socketio import SocketIO, emit, send
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from flask_session import Session


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
    if 'username' in session:
        username = session['username']
        send(f"{username} has joined the chat room.", broadcast=True)


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
        "is_active": False                  #check if users is already logged in
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


@app.route('/set_inactive')
def set_inactive():
    username = session.get('username')

    if username:
        mongo.db.users.update_one({"username": username}, {"$set": {"is_active": False}})
        return jsonify({"success": True}), 200
    else:
        return jsonify({"success": False}), 400


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
