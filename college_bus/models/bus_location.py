from datetime import datetime
from . import db

class BusLocation(db.Model):
    __tablename__ = 'bus_locations'

    id = db.Column(db.Integer, primary_key=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'), nullable=False, index=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    speed = db.Column(db.Float, default=0.0)
    heading = db.Column(db.Float, default=0.0)
    trip_status = db.Column(db.String(20), default='IDLE')  # 'IDLE', 'RUNNING', 'COMPLETED'
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'bus_id': self.bus_id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'speed': self.speed or 0.0,
            'heading': self.heading or 0.0,
            'trip_status': self.trip_status,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else ''
        }

    def __repr__(self):
        return f'<BusLocation Bus:{self.bus_id} ({self.latitude}, {self.longitude}) Status:{self.trip_status}>'
