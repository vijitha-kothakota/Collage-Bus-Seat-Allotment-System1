from datetime import datetime
from . import db

class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    college_id = db.Column(db.String(30), unique=True, nullable=False, index=True)
    year_of_study = db.Column(db.Integer, nullable=False, default=1)  # 1 for 1st year, 2, 3, 4
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    allocations = db.relationship('SeatAllocation', backref='student', lazy=True, cascade='all, delete-orphan')

    def get_schedule(self):
        """
        College Transport Policy:
        - 1st Year: Morning 8:30 AM, Evening 5:00 PM
        - 2nd, 3rd, 4th Year: Morning 7:30 AM, Evening 4:00 PM
        """
        if self.year_of_study == 1:
            return {
                'year_label': '1st Year (Freshers)',
                'morning_time': '08:30 AM',
                'evening_time': '05:00 PM',
                'badge': '1st Year Shift (8:30 AM - 5:00 PM)'
            }
        else:
            suffix = 'nd' if self.year_of_study == 2 else ('rd' if self.year_of_study == 3 else 'th')
            return {
                'year_label': f'{self.year_of_study}{suffix} Year',
                'morning_time': '07:30 AM',
                'evening_time': '04:00 PM',
                'badge': f'{self.year_of_study}{suffix} Year Shift (7:30 AM - 4:00 PM)'
            }

    def get_confirmed_allocation(self, academic_year_id=None):
        query = [alloc for alloc in self.allocations if alloc.status == 'CONFIRMED']
        if academic_year_id:
            query = [alloc for alloc in query if alloc.academic_year_id == academic_year_id]
        return query[-1] if query else None

    def get_latest_allocation(self):
        return self.allocations[-1] if self.allocations else None

    def __repr__(self):
        return f'<Student {self.name} ({self.college_id}, Year {self.year_of_study})>'
