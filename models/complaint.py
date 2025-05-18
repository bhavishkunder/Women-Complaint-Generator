from datetime import datetime
from bson import ObjectId

class Complaint:
    # Define valid status options as class variable
    VALID_STATUSES = ['submitted', 'acknowledged', 'under_investigation', 'resolved', 'forwarded']
    
    def __init__(self, complaint_id, complaint_result, user_id, complaint_type=None, status='submitted'):
        self.complaint_id = complaint_id
        self.complaint_result = complaint_result
        self.complaint_type = self._extract_complaint_type(complaint_result)  # Extract type from result
        self.user_id = user_id
        self.status = status
        self.date_created = datetime.now()
        self.status_history = [
            {
                'status': status,
                'date': self.date_created,
                'notes': 'Complaint initially submitted'
            }
        ]

    def _extract_complaint_type(self, complaint_result):
        """Extract complaint type from the complaint result text"""
        if not isinstance(complaint_result, str):
            return None
        
        lines = complaint_result.split('\n')
        for line in lines:
            # Look for lines containing 'Type of Complaint' with flexible surrounding characters
            if 'Type of Complaint' in line:
                # Extract the type, removing any surrounding markers
                type_parts = line.split('Type of Complaint')
                if len(type_parts) > 1:
                    # Remove common markers like **, :, etc.
                    complaint_type = type_parts[1].strip(' :*')
                    return complaint_type

    def to_dict(self):
        return {
            'complaint_id': self.complaint_id,
            'complaint_result': self.complaint_result,
            'complaint_type': self.complaint_type,  # Added complaint_type to dictionary
            'user_id': self.user_id,
            'date_created': self.date_created,
            'status': self.status,
            'status_history': self.status_history
        }
    
    @staticmethod
    def validate_status(status):
        if status not in Complaint.VALID_STATUSES:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(Complaint.VALID_STATUSES)}")
        return True

