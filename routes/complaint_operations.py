from datetime import datetime
from bson import ObjectId

def handle_complaint_forward(mongo, from_station_id, to_station_name, complaint_id):
    try:
        # Find target station
        to_station = mongo.db.police_stations.find_one({'station_name': to_station_name})
        if not to_station:
            return False, "Station not found"
        
        # Get complaint details
        complaint = mongo.db.complaints.find_one({'complaint_id': int(complaint_id)})
        if not complaint:
            return False, "Complaint not found"

        # Remove complaint from current station
        mongo.db.police_stations.update_one(
            {'_id': ObjectId(from_station_id)},
            {
                '$pull': {'complaints': str(complaint['_id'])},
                '$inc': {'forward_count': 1}
            }
        )

        # Add complaint to target station
        mongo.db.police_stations.update_one(
            {'_id': to_station['_id']},
            {'$push': {'complaints': str(complaint['_id'])}}
        )

        # Update complaint status
        mongo.db.complaints.update_one(
            {'complaint_id': int(complaint_id)},
            {
                '$set': {
                    'status': 'submitted',
                    'current_station': to_station['_id']
                },
                '$push': {
                    'status_history': {
                        'status': 'submitted',
                        'date': datetime.now(),
                        'notes': f'Forwarded to {to_station_name}'
                    }
                }
            }
        )
        
        return True, "Successfully forwarded complaint"
    except Exception as e:
        return False, f"Error forwarding complaint: {str(e)}"

def handle_complaint_reject(mongo, station_id, complaint_id):
    try:
        # Get complaint details
        complaint = mongo.db.complaints.find_one({'complaint_id': int(complaint_id)})
        if not complaint:
            return False, "Complaint not found"

        # Remove complaint from station's array
        mongo.db.police_stations.update_one(
            {'_id': ObjectId(station_id)},
            {'$pull': {'complaints': str(complaint['_id'])}}
        )

        # Update complaint status
        mongo.db.complaints.update_one(
            {'complaint_id': int(complaint_id)},
            {
                '$set': {
                    'status': 'rejected',
                    'current_station': None
                },
                '$push': {
                    'status_history': {
                        'status': 'rejected',
                        'date': datetime.now(),
                        'notes': 'Complaint rejected by police station'
                    }
                }
            }
        )

        return True, "Successfully rejected complaint"
    except Exception as e:
        return False, f"Error rejecting complaint: {str(e)}"