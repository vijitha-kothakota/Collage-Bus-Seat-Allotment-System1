from datetime import datetime
from . import db

class SeatAllocation(db.Model):
    __tablename__ = 'seat_allocations'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'), nullable=False)
    seat_id = db.Column(db.Integer, db.ForeignKey('seats.id'), nullable=True)
    seat_number = db.Column(db.String(10), nullable=False)
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_years.id'), nullable=False)
    boarding_point_id = db.Column(db.Integer, db.ForeignKey('boarding_points.id'), nullable=False)
    allocation_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='PENDING')  # 'PENDING', 'CONFIRMED', 'CANCELLED'

    # Database-level constraint to prevent duplicate seat allocation for the same bus, seat, and academic year
    __table_args__ = (
        db.UniqueConstraint('bus_id', 'seat_number', 'academic_year_id', name='uq_bus_seat_academic_year'),
    )

    # Relationships
    payment = db.relationship('Payment', backref='allocation', uselist=False, cascade='all, delete-orphan')
    bus_pass = db.relationship('BusPass', backref='allocation', uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<SeatAllocation Student:{self.student_id} Bus:{self.bus_id} Seat:{self.seat_number} ({self.status})>'
