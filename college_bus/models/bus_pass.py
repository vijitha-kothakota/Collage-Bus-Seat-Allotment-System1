from datetime import datetime
from . import db

class BusPass(db.Model):
    __tablename__ = 'bus_passes'

    id = db.Column(db.Integer, primary_key=True)
    pass_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    allocation_id = db.Column(db.Integer, db.ForeignKey('seat_allocations.id'), nullable=False, unique=True)
    qr_code_path = db.Column(db.String(255), nullable=True)
    issue_date = db.Column(db.DateTime, default=datetime.utcnow)
    valid_until = db.Column(db.String(50), default='May 2027')
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<BusPass {self.pass_id}>'
