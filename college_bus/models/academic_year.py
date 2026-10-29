from . import db

class AcademicYear(db.Model):
    __tablename__ = 'academic_years'

    id = db.Column(db.Integer, primary_key=True)
    year_label = db.Column(db.String(20), unique=True, nullable=False)  # e.g., '2026–27'
    is_active = db.Column(db.Boolean, default=True)

    allocations = db.relationship('SeatAllocation', backref='academic_year', lazy=True)

    def __repr__(self):
        return f'<AcademicYear {self.year_label}>'
