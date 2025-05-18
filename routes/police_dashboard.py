from flask import Blueprint, jsonify, session, request, current_app
from bson import ObjectId
from datetime import datetime
from models.complaint import Complaint

police_dashboard = Blueprint('police_dashboard', __name__)

@police_dashboard.route('/get_station_data')
def get_station_data():
    if 'police_station_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    police_station = current_app.mongo.db.police_stations.find_one({'_id': ObjectId(session['police_station_id'])})
    if not police_station:
        return jsonify({'error': 'Police station not found'}), 404
    
    return jsonify({
        'station_name': police_station['station_name'],
        'jurisdiction': police_station['jurisdiction'],
        'area': police_station['area'],
        'contact': police_station['contact']
    })

@police_dashboard.route('/get_received_complaints')
def get_received_complaints():
    if 'police_station_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    police_station = current_app.mongo.db.police_stations.find_one({'_id': ObjectId(session['police_station_id'])})
    if not police_station:
        return jsonify({'error': 'Police station not found'}), 404
    
    complaint_ids = police_station.get('complaints', [])

    complaints = []
    for complaint_id in complaint_ids:
        complaint = current_app.mongo.db.complaints.find_one({'_id': ObjectId(complaint_id)})
        if complaint:
            complaint['_id'] = str(complaint['_id'])
            complaint['date_created'] = complaint['date_created'].isoformat()
            if complaint.get('status_history'):
                for history in complaint['status_history']:
                    history['date'] = history['date'].isoformat()
            complaints.append(complaint)

    return jsonify({'complaints': complaints})

@police_dashboard.route('/update_complaint_status', methods=['POST'])
def update_complaint_status():
    if 'police_station_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    data = request.get_json()
    complaint_id = data.get('complaint_id')
    new_status = data.get('status')

    if new_status not in Complaint.VALID_STATUSES:
        return jsonify({'error': 'Invalid status'}), 400

    complaint = current_app.mongo.db.complaints.find_one({'complaint_id': complaint_id})
    if not complaint:
        return jsonify({'error': 'Complaint not found'}), 404

    status_update = {
        'status': new_status,
        'date': datetime.now(),
        'notes': f'Status updated to {new_status}'
    }

    result = current_app.mongo.db.complaints.update_one(
        {'complaint_id': complaint_id},
        {
            '$set': {'status': new_status},
            '$push': {'status_history': status_update}
        }
    )

    if result.modified_count == 0:
        return jsonify({'error': 'Failed to update status'}), 500

    return jsonify({'message': 'Status updated successfully'})

@police_dashboard.route('/forward_complaint', methods=['POST'])
def forward_complaint():
    if 'police_station_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    data = request.get_json()
    complaint_id = data.get('complaint_id')
    target_station_name = data.get('station_name')

    if not complaint_id or not target_station_name:
        return jsonify({'error': 'Missing required fields'}), 400

    target_station = current_app.mongo.db.police_stations.find_one({'station_name': target_station_name})
    if not target_station:
        return jsonify({'error': 'Target police station not found'}), 404

    complaint = current_app.mongo.db.complaints.find_one({'complaint_id': complaint_id})
    if not complaint:
        return jsonify({'error': 'Complaint not found'}), 404

    current_station = current_app.mongo.db.police_stations.find_one({'_id': ObjectId(session['police_station_id'])})
    if str(complaint['_id']) in current_station.get('complaints', []):
        current_app.mongo.db.police_stations.update_one(
            {'_id': ObjectId(session['police_station_id'])},
            {'$pull': {'complaints': str(complaint['_id'])}}
        )

    current_app.mongo.db.police_stations.update_one(
        {'_id': target_station['_id']},
        {'$addToSet': {'complaints': str(complaint['_id'])}}
    )

    status_update = {
        'status': 'forwarded',
        'date': datetime.now(),
        'notes': f'Forwarded to {target_station_name} police station'
    }

    current_app.mongo.db.complaints.update_one(
        {'complaint_id': complaint_id},
        {
            '$set': {'status': 'forwarded'},
            '$push': {'status_history': status_update}
        }
    )

    return jsonify({
        'message': 'Complaint forwarded successfully',
        'forwarded_to': target_station_name
    })