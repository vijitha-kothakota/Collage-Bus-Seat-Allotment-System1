from . import db

class Route(db.Model):
    __tablename__ = 'routes'

    id = db.Column(db.Integer, primary_key=True)
    route_name = db.Column(db.String(100), nullable=False)
    start_point = db.Column(db.String(80), nullable=False)
    destination = db.Column(db.String(80), nullable=False)
    annual_fee = db.Column(db.Float, nullable=False, default=18000.0)
    total_distance_km = db.Column(db.Float, default=35.0)

    # Relationships
    buses = db.relationship('Bus', backref='route', lazy=True)
    boarding_points = db.relationship('BoardingPoint', backref='route', lazy=True, order_by='BoardingPoint.stop_order')

    def __repr__(self):
        return f'<Route {self.route_name}>'
