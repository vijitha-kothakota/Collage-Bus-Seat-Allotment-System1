from datetime import datetime
from . import db

class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    allocation_id = db.Column(db.Integer, db.ForeignKey('seat_allocations.id'), nullable=False, unique=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), default='UPI (Simulated)')
    transaction_id = db.Column(db.String(64), unique=True, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Pending')  # 'Pending', 'Successful', 'Failed'
    payment_date = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship('Student', backref='payments')

    def __repr__(self):
        return f'<Payment {self.transaction_id} Amount:₹{self.amount} ({self.status})>'
