from . import db

class Bus(db.Model):
    __tablename__ = 'buses'

    id = db.Column(db.Integer, primary_key=True)
    bus_number = db.Column(db.String(20), unique=True, nullable=False)
    capacity = db.Column(db.Integer, nullable=False, default=40)
    route_id = db.Column(db.Integer, db.ForeignKey('routes.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    seats = db.relationship('Seat', backref='bus', lazy=True, cascade='all, delete-orphan')
    allocations = db.relationship('SeatAllocation', backref='bus', lazy=True)
    locations = db.relationship('BusLocation', backref='bus', lazy=True, cascade='all, delete-orphan', order_by='BusLocation.updated_at.desc()')

    def get_latest_location(self):
        from .bus_location import BusLocation
        return BusLocation.query.filter_by(bus_id=self.id).order_by(BusLocation.updated_at.desc()).first()

    def get_available_seats_count(self, academic_year_id):
        from .allocation import SeatAllocation
        confirmed_count = SeatAllocation.query.filter_by(
            bus_id=self.id,
            academic_year_id=academic_year_id,
            status='CONFIRMED'
        ).count()
        return max(0, self.capacity - confirmed_count)

    def __repr__(self):
        return f'<Bus {self.bus_number}>'
