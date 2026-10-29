from . import db

class Seat(db.Model):
    __tablename__ = 'seats'

    id = db.Column(db.Integer, primary_key=True)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'), nullable=False)
    seat_number = db.Column(db.String(10), nullable=False)  # e.g., '01', '02', '40'
    seat_type = db.Column(db.String(20), default='Standard')  # 'Window', 'Aisle', 'Standard'
    is_active = db.Column(db.Boolean, default=True)

    __table_args__ = (
        db.UniqueConstraint('bus_id', 'seat_number', name='uq_bus_seat_number'),
    )

    def is_occupied(self, academic_year_id):
        from .allocation import SeatAllocation
        return SeatAllocation.query.filter_by(
            bus_id=self.bus_id,
            seat_number=self.seat_number,
            academic_year_id=academic_year_id,
            status='CONFIRMED'
        ).first() is not None

    def __repr__(self):
        return f'<Seat {self.seat_number} on Bus {self.bus_id}>'
