from . import db

class BoardingPoint(db.Model):
    __tablename__ = 'boarding_points'

    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id'), nullable=False)
    stop_name = db.Column(db.String(100), nullable=False)
    stop_order = db.Column(db.Integer, nullable=False, default=1)
    pickup_time = db.Column(db.String(20), nullable=True, default="07:30 AM")
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)

    allocations = db.relationship('SeatAllocation', backref='boarding_point', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'route_id': self.route_id,
            'stop_name': self.stop_name,
            'stop_order': self.stop_order,
            'pickup_time': self.pickup_time,
            'latitude': self.latitude,
            'longitude': self.longitude
        }

    def __repr__(self):
        return f'<BoardingPoint {self.stop_name} (Order: {self.stop_order})>'
