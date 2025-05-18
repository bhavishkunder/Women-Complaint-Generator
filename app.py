from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
import os
from collections import Counter
from dotenv import load_dotenv
from datetime import datetime
from agents import process_incident, update_incident_details
from models.complaint import Complaint
from routes.complaint_operations import handle_complaint_forward, handle_complaint_reject
from utils.complaint_classifier import classify_severity, analyze_complaint
from datetime import datetime, timedelta

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/safety"
app.secret_key = os.getenv("SECRET_KEY")
mongo = PyMongo(app)

# Only import blueprints after app is created
from routes.police_auth import create_police_auth_blueprint

# Create and register the blueprint
police_auth = create_police_auth_blueprint(mongo)
app.register_blueprint(police_auth)

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/police-login')
def police_login():
    return render_template('police-login.html')
    

@app.route('/police/pdashboard')
def pdashboard():
    # Ensure the user is logged in (you can implement more advanced session management)
    # For now, it's just a placeholder check
    return render_template('police-dashboard.html')
    
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    user = mongo.db.users.find_one({'_id': ObjectId(session['user_id'])})
    return render_template('dashboard.html', user=user)

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
        'address': data['address'],
        'complaint_ids': [],
        'nearest_station': None  # Added this field
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

@app.route('/update_incident', methods=['POST'])
def update_incident():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    data = request.form
    original_description = data.get('original_description')
    date = data.get('date')
    time = data.get('time')
    place = data.get('place')

    # Update the description with the new details
    updated_description = update_incident_details(
        original_description,
        date=date,
        time=time,
        place=place
    )

    # Get user information
    user = mongo.db.users.find_one({'_id': ObjectId(session['user_id'])})

    # Process the updated incident
    result = process_incident(
        updated_description,
        user['name'],
        user['contact'],
        user['email'],
        user['address']
    )

    return jsonify(result)


@app.route('/update-nearest-station', methods=['POST'])
def update_nearest_station():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    data = request.json
    station_name = data.get('station_name')
    
    if not station_name:
        return jsonify({'error': 'Station name not provided'}), 400
        
    # Store station name in session
    session['nearest_station'] = station_name
    
    # Update user document in database
    mongo.db.users.update_one(
        {'_id': ObjectId(session['user_id'])},
        {'$set': {'nearest_station': station_name}}
    )
    
    return jsonify({'message': 'Station name updated'})

@app.route('/forward-to-police', methods=['POST'])
def forward_to_police():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    
    # Get station name from session
    station_name = session.get('nearest_station')
    print(f"Looking for station: {station_name}")  # Debug log
    
    if not station_name:
        return jsonify({'error': 'Nearest police station not set'}), 400
    
    data = request.json
    complaint_result = data.get('complaint_result')
    
    # Check if the police station is registered
    police_station = mongo.db.police_stations.find_one({'station_name': station_name})
    print(f"Found police station: {police_station}")  # Debug log
    
    if not police_station:
        # Auto-register the police station if it doesn't exist
        try:
            police_station_id = mongo.db.police_stations.insert_one({
                'station_name': station_name,
                'complaints': [],
                'created_at': datetime.now()
            }).inserted_id
            police_station = mongo.db.police_stations.find_one({'_id': police_station_id})
            print(f"Auto-registered police station: {police_station}")  # Debug log
        except Exception as e:
            print(f"Error registering police station: {str(e)}")  # Debug log
            return jsonify({'error': 'Error registering police station'}), 500
    
    # Read current counter
    counter_path = os.path.join(os.path.dirname(__file__), 'count.txt')
    try:
        with open(counter_path, 'r') as f:
            current_count = int(f.read().strip() or '0')
    except FileNotFoundError:
        current_count = 0
    except Exception as e:
        print(f"Error reading counter: {str(e)}")  # Debug log
        return jsonify({'error': 'Error reading complaint counter'}), 500
    
    # Increment counter
    new_count = current_count + 1
    try:
        with open(counter_path, 'w') as f:
            f.write(str(new_count))
    except Exception as e:
        print(f"Error writing counter: {str(e)}")  # Debug log
        return jsonify({'error': 'Error updating complaint counter'}), 500
    
    try:
        # Create new complaint with initial 'submitted' status
        complaint = Complaint(
            complaint_id=new_count,
            complaint_result=complaint_result,
            user_id=session['user_id'],
            status='submitted'
        )
        
        # Store complaint in MongoDB
        complaint_id = mongo.db.complaints.insert_one(complaint.to_dict()).inserted_id
        print(f"Created complaint: {complaint_id}")  # Debug log
        
        # Update user's complaint IDs array
        mongo.db.users.update_one(
            {'_id': ObjectId(session['user_id'])},
            {'$push': {'complaint_ids': new_count}}
        )
        
        # Update police station's complaints array
        mongo.db.police_stations.update_one(
            {'_id': police_station['_id']},
            {'$push': {'complaints': str(complaint_id)}}
        )
        
        return jsonify({
            'success': True,
            'complaint_id': new_count,
            'status': 'submitted',
            'forwarded_to': station_name
        })
        
    except Exception as e:
        print(f"Error processing complaint: {str(e)}")  # Debug log
        return jsonify({'error': 'Error processing complaint'}), 500


@app.route('/get_user_complaints', methods=['GET'])
def get_user_complaints():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
        
    try:
        user = mongo.db.users.find_one({'_id': ObjectId(session['user_id'])})
        complaints = list(mongo.db.complaints.find({'user_id': session['user_id']}))
        
        for complaint in complaints:
            complaint['_id'] = str(complaint['_id'])
            complaint['date_created'] = complaint['date_created'].strftime('%Y-%m-%d %H:%M:%S')
            
            # Get the user's nearest police station
            nearest_station = user.get('nearest_station')
            if nearest_station:
                police_station = mongo.db.police_stations.find_one({'station_name': nearest_station})
                if police_station:
                    complaint['station_name'] = police_station['station_name']
                    complaint['station_jurisdiction'] = police_station['jurisdiction']
                    complaint['station_contact'] = police_station['contact']
                else:
                    complaint['station_name'] = 'Not Assigned'
            else:
                complaint['station_name'] = 'Not Assigned'
        
        return jsonify({
            'complaints': complaints,
            'total_complaints': len(complaints)
        })
    except Exception as e:
        print(f"Error fetching complaints: {str(e)}")
        return jsonify({'error': 'Failed to fetch complaints'}), 500



@app.route('/get_received_complaints')
def get_received_complaints():
    if 'police_station_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    # Fetch the police station's data
    police_station = mongo.db.police_stations.find_one({'_id': ObjectId(session['police_station_id'])})
    if not police_station:
        return jsonify({'error': 'Police station not found'}), 404
    
    complaint_ids = police_station.get('complaints', [])

    # Fetch the corresponding complaints from the database
    complaints = []
    for complaint_id in complaint_ids:
        complaint = mongo.db.complaints.find_one({'_id': ObjectId(complaint_id)})
        if complaint:
            complaint_data = {
                'complaint_id': complaint['complaint_id'],
                'status': complaint['status'],
                'complaint_type': complaint['complaint_type'],
                'details': complaint['complaint_result']
            }
            complaints.append(complaint_data)

    return jsonify({'complaints': complaints})


@app.route('/get_station_info')
def get_station_info():
    if 'police_station_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
        
    station = mongo.db.police_stations.find_one({'_id': ObjectId(session['police_station_id'])})
    if not station:
        return jsonify({'error': 'Station not found'}), 404
        
    return jsonify({
        'station_name': station['station_name']
    })

@app.route('/update_complaint_status', methods=['POST'])
def update_complaint_status():
    if 'police_station_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    data = request.json
    complaint_id = data.get('complaint_id')
    new_status = data.get('status')
    forward_to = data.get('forward_to')

    # Update valid statuses to include reject
    VALID_STATUSES = ['submitted', 'acknowledged', 'under_investigation', 'resolved', 'forwarded', 'rejected']
    
    if new_status not in VALID_STATUSES:
        return jsonify({'error': 'Invalid status'}), 400

    try:
        # Handle forwarding
        if new_status == 'forwarded':
            if not forward_to:
                return jsonify({'error': 'Forward station not specified'}), 400
            
            success, message = handle_complaint_forward(
                mongo, 
                session['police_station_id'], 
                forward_to, 
                complaint_id
            )
            
            if not success:
                return jsonify({'error': message}), 400

        # Handle rejection
        elif new_status == 'rejected':
            success, message = handle_complaint_reject(
                mongo, 
                session['police_station_id'], 
                complaint_id
            )
            
            if not success:
                return jsonify({'error': message}), 400

        # Handle other status updates
        else:
            complaint = mongo.db.complaints.find_one({'complaint_id': int(complaint_id)})
            if not complaint:
                return jsonify({'error': 'Complaint not found'}), 404

            mongo.db.complaints.update_one(
                {'complaint_id': int(complaint_id)},
                {
                    '$set': {'status': new_status},
                    '$push': {
                        'status_history': {
                            'status': new_status,
                            'date': datetime.now(),
                            'notes': f'Status updated to {new_status}'
                        }
                    }
                }
            )

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_classified_complaints')
def get_classified_complaints():
    try:
        if 'police_station_id' not in session:
            return jsonify({'error': 'Not logged in'}), 401

        complaints = mongo.db.complaints.find({
            'status': 'submitted'
        })

        classified_complaints = []
        for complaint in complaints:
            try:
                if 'severity' not in complaint:
                    classification = classify_severity(complaint['complaint_result'])
                    detailed_analysis = analyze_complaint(complaint['complaint_result'])
                    
                    mongo.db.complaints.update_one(
                        {'_id': complaint['_id']},
                        {
                            '$set': {
                                'severity': classification['severity'],
                                'ai_analysis': detailed_analysis,
                                'classification_confidence': classification['confidence'],
                                'classification_date': datetime.now()
                            }
                        }
                    )
                    complaint.update({
                        'severity': classification['severity'],
                        'ai_analysis': detailed_analysis
                    })

                classified_complaints.append({
                    'complaint_id': complaint['complaint_id'],
                    'complaint_type': complaint.get('complaint_type', 'Unclassified'),
                    'severity': complaint.get('severity', 'Unclassified'),
                    'ai_analysis': complaint.get('ai_analysis', 'Analysis pending'),
                    'details': complaint['complaint_result']
                })
            except Exception as e:
                print(f"Error processing complaint {complaint.get('complaint_id')}: {str(e)}")
                continue

        return jsonify({'complaints': classified_complaints})
    except Exception as e:
        print(f"Route error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
@app.route('/get_emergency_alerts')
def get_emergency_alerts():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    user = mongo.db.users.find_one({'_id': ObjectId(session['user_id'])})
    nearest_station = user.get('nearest_station')

    if not nearest_station:
        return jsonify({'error': 'Nearest police station not set'}), 400

    # Get complaints for the nearest police station
    police_station = mongo.db.police_stations.find_one({'station_name': nearest_station})
    if not police_station:
        return jsonify({'error': 'Police station not found'}), 404

    complaint_ids = police_station.get('complaints', [])
    
    # Convert cursor to list immediately to allow multiple iterations
    complaints_list = list(mongo.db.complaints.find({
        '_id': {'$in': [ObjectId(id) for id in complaint_ids]}
    }))

    # Count complaint types
    complaint_types = [complaint.get('complaint_type') for complaint in complaints_list 
                      if complaint.get('complaint_type')]
    type_counts = Counter(complaint_types)

    # Filter for types with more than 2 occurrences
    alerts = [{'type': type, 'count': count} 
             for type, count in type_counts.items() 
             if count >= 2]

    return jsonify({'alerts': alerts})

def calculate_avg_resolution_time(complaints):
    total_time = 0
    resolved_count = 0
    
    for complaint in complaints:
        if complaint['status'] == 'resolved':
            status_history = complaint.get('status_history', [])
            if status_history:
                submission_date = status_history[0]['date']
                resolution_date = next(
                    (entry['date'] for entry in reversed(status_history) 
                     if entry['status'] == 'resolved'), 
                    None
                )
                if resolution_date:
                    time_diff = resolution_date - submission_date
                    total_time += time_diff.days
                    resolved_count += 1
    
    return round(total_time / resolved_count if resolved_count > 0 else 0, 1)

def get_monthly_trends(complaints):
    trends = {}
    current_date = datetime.now()
    
    # Get last 6 months
    for i in range(6):
        date = current_date - timedelta(days=30 * i)
        month_key = date.strftime('%b %Y')
        trends[month_key] = 0
    
    # Count complaints per month
    for complaint in complaints:
        complaint_date = complaint['date_created']
        month_key = complaint_date.strftime('%b %Y')
        if month_key in trends:
            trends[month_key] += 1
    
    return [{'month': k, 'count': v} for k, v in trends.items()]

@app.route('/get_station_statistics')
def get_station_statistics():
    if 'police_station_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    # Get police station and its complaints
    station = mongo.db.police_stations.find_one({'_id': ObjectId(session['police_station_id'])})
    if not station:
        return jsonify({'error': 'Station not found'}), 404
    
    complaint_ids = station.get('complaints', [])
    complaints = list(mongo.db.complaints.find({
        '_id': {'$in': [ObjectId(id) for id in complaint_ids]}
    }))
    
    total_complaints = len(complaints)
    resolved_complaints = sum(1 for c in complaints if c['status'] == 'resolved')
    acknowledged_complaints = sum(1 for c in complaints if c['status'] in ['acknowledged', 'under_investigation', 'resolved'])
    
    # Calculate statistics
    statistics = {
        'total_complaints': total_complaints,
        'resolution_rate': round((resolved_complaints / total_complaints * 100) if total_complaints > 0 else 0, 1),
        'status_distribution': {
            'Submitted': sum(1 for c in complaints if c['status'] == 'submitted'),
            'Acknowledged': sum(1 for c in complaints if c['status'] == 'acknowledged'),
            'Under Investigation': sum(1 for c in complaints if c['status'] == 'under_investigation'),
            'Resolved': resolved_complaints,
            'Forwarded': sum(1 for c in complaints if c['status'] == 'forwarded')
        },
        'monthly_trends': get_monthly_trends(complaints),
        'avg_resolution_time': calculate_avg_resolution_time(complaints),
        'forward_rate': round((station.get('forward_count', 0) / total_complaints * 100) if total_complaints > 0 else 0, 1),
        'acknowledgment_rate': round((acknowledged_complaints / total_complaints * 100) if total_complaints > 0 else 0, 1),
        'severity_distribution': {
            'High': sum(1 for c in complaints if c.get('severity') == 'high'),
            'Medium': sum(1 for c in complaints if c.get('severity') == 'medium'),
            'Low': sum(1 for c in complaints if c.get('severity') == 'low')
        }
    }
    
    return jsonify(statistics)

@app.route('/track_complaints')
def track_complaints():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    user = mongo.db.users.find_one({'_id': ObjectId(session['user_id'])})
    return render_template('track.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)