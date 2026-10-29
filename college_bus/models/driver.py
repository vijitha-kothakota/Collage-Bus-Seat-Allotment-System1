from . import db

class Driver(db.Model):
    __tablename__ = 'drivers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    license_number = db.Column(db.String(50), nullable=True)
    phone_number = db.Column(db.String(20), nullable=False)
    bus_id = db.Column(db.Integer, db.ForeignKey('buses.id'), nullable=True)

    bus = db.relationship('Bus', backref=db.backref('driver', uselist=False))

    def __repr__(self):
        return f'<Driver {self.name} (Bus: {self.bus.bus_number if self.bus else "Unassigned"})>'
