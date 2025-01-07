from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv
from datetime import datetime
from agents import process_incident

load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/safety"
app.secret_key = os.getenv("SECRET_KEY")
mongo = PyMongo(app)

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    user = mongo.db.users.find_one({'_id': ObjectId(session['user_id'])})
    return render_template('dashboard.html', user=user)

# New routes
@app.route('/emergency')
def emergency():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    user = mongo.db.users.find_one({'_id': ObjectId(session['user_id'])})
    return render_template('emergency.html', user=user)

@app.route('/resources')
def resources():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    user = mongo.db.users.find_one({'_id': ObjectId(session['user_id'])})
    return render_template('resources.html', user=user)

@app.route('/community')
def community():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    user = mongo.db.users.find_one({'_id': ObjectId(session['user_id'])})
    return render_template('community.html', user=user)

@app.route('/settings')
def settings():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    user = mongo.db.users.find_one({'_id': ObjectId(session['user_id'])})
    return render_template('settings.html', user=user)

@app.route('/register', methods=['POST'])
def register():
    data = request.form
    existing_user = mongo.db.users.find_one({'email': data['email']})
    if existing_user:
        return jsonify({'error': 'Email already exists'}), 400
    
    hashed_password = generate_password_hash(data['password'])
    user_id = mongo.db.users.insert_one({
        'name': data['name'],
        'email': data['email'],
        'password': hashed_password,
        'contact': data['contact'],
        'address': data['address']
    }).inserted_id
    
    session['user_id'] = str(user_id)
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.form
    user = mongo.db.users.find_one({'email': data['email']})
    if user and check_password_hash(user['password'], data['password']):
        session['user_id'] = str(user['_id'])
        return jsonify({'message': 'Logged in successfully'}), 200
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/process_incident', methods=['POST'])
def handle_incident():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    
    data = request.form
    description = data['description']
    user = mongo.db.users.find_one({'_id': ObjectId(session['user_id'])})

    result = process_incident(description, user['name'], user['contact'], user['email'], user['address'])

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)