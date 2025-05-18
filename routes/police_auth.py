from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from models.police_station import PoliceStation

def create_police_auth_blueprint(mongo):
    police_auth = Blueprint('police_auth', __name__)

    @police_auth.route('/police/register', methods=['POST'])
    def register_police():
        data = request.json
        
        # Check if police station already exists
        existing_station = mongo.db.police_stations.find_one({'station_name': data['station_name']})
        if existing_station:
            return jsonify({'error': 'Police station already registered'}), 400
        
        # Create new police station
        hashed_password = generate_password_hash(data['password'])
        police_station = PoliceStation(
            station_name=data['station_name'],
            jurisdiction=data['jurisdiction'],
            area=data['area'],
            contact=data['contact'],
            password=hashed_password
        )
        
        # Insert into database
        station_id = mongo.db.police_stations.insert_one(police_station.to_dict()).inserted_id
        
        return jsonify({'message': 'Police station registered successfully'}), 201

    @police_auth.route('/police/login', methods=['POST'])
    def login_police():
        data = request.json
        
        # Find police station
        station = mongo.db.police_stations.find_one({'station_name': data['station_name']})
        
        if station and check_password_hash(station['password'], data['password']):
            session['police_station_id'] = str(station['_id'])
            return jsonify({'message': 'Logged in successfully'}), 200
        
        return jsonify({'error': 'Invalid credentials'}), 401

    @police_auth.route('/police/logout')
    def logout_police():
        session.pop('police_station_id', None)
        return jsonify({'message': 'Logged out successfully'}), 200

    return police_auth