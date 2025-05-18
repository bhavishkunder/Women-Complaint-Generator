from datetime import datetime
from bson import ObjectId

class PoliceStation:
    def __init__(self, station_name, jurisdiction, area, contact, password, complaints=None, forward_count=0):
        self.station_name = station_name
        self.jurisdiction = jurisdiction
        self.area = area
        self.contact = contact
        self.password = password
        self.complaints = complaints or []
        self.forward_count = forward_count
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def to_dict(self):
        return {
            "station_name": self.station_name,
            "jurisdiction": self.jurisdiction,
            "area": self.area,
            "contact": self.contact,
            "password": self.password,
            "complaints": self.complaints,
            "forward_count": self.forward_count,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @staticmethod
    def from_dict(data):
        return PoliceStation(
            station_name=data.get("station_name"),
            jurisdiction=data.get("jurisdiction"),
            area=data.get("area"),
            contact=data.get("contact"),
            password=data.get("password"),
            complaints=data.get("complaints", [])
        )

