import os
TEST_DB_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'database', 'test_bus.db')
os.environ['DATABASE_URL'] = f'sqlite:///{TEST_DB_PATH}'

import unittest
from app import create_app, db
from models import (
    User, Student, Driver, Bus, Seat, SeatAllocation, Payment, BusPass, BusLocation, AcademicYear
)
from seed import seed_database

class CollegeBusSystemTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()

        with self.app.app_context():
            db.drop_all()
            db.create_all()
            seed_database()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
        if os.path.exists(TEST_DB_PATH):
            try:
                os.remove(TEST_DB_PATH)
            except Exception:
                pass

    def test_01_seed_data_integrity(self):
        """Verify initial database seed data and shift timings."""
        with self.app.app_context():
            ay = AcademicYear.query.filter_by(year_label='2026–27').first()
            self.assertIsNotNone(ay)

            bus = Bus.query.filter_by(bus_number='BUS-05').first()
            self.assertIsNotNone(bus)
            self.assertEqual(bus.capacity, 40)
            self.assertEqual(len(bus.seats), 40)

            admin = User.query.filter_by(username='admin').first()
            self.assertIsNotNone(admin)
            self.assertTrue(admin.check_password('admin123'))

            driver = User.query.filter_by(username='driver_ramesh').first()
            self.assertIsNotNone(driver)
            self.assertTrue(driver.check_password('driver123'))

            student1 = Student.query.filter_by(college_id='23B91A0501').first()
            self.assertIsNotNone(student1)
            self.assertEqual(student1.name, 'Vijitha')
            # 1st Year: 8:30 AM - 5:00 PM
            self.assertEqual(student1.year_of_study, 1)
            sched1 = student1.get_schedule()
            self.assertEqual(sched1['morning_time'], '08:30 AM')
            self.assertEqual(sched1['evening_time'], '05:00 PM')

            student2 = Student.query.filter_by(college_id='23B91A0502').first()
            self.assertIsNotNone(student2)
            # 3rd Year: 7:30 AM - 4:00 PM
            self.assertEqual(student2.year_of_study, 3)
            sched2 = student2.get_schedule()
            self.assertEqual(sched2['morning_time'], '07:30 AM')
            self.assertEqual(sched2['evening_time'], '04:00 PM')

    def test_02_student_registration_validation(self):
        """Verify Student ID 10-char mixed rule and password freedom."""
        # 1. Invalid length (less than 10 chars)
        res = self.client.post('/register', data={
            'name': 'Test User',
            'college_id': '23B91A',
            'year_of_study': 1,
            'email': 'short@college.edu',
            'phone_number': '9876543210',
            'password': 'anypassword',
            'confirm_password': 'anypassword'
        }, follow_redirects=True)
        self.assertIn(b'Student ID must be exactly 10 characters', res.data)

        # 2. Invalid composition (all digits, no letters)
        res = self.client.post('/register', data={
            'name': 'Test User',
            'college_id': '1234567890',
            'year_of_study': 1,
            'email': 'allnum@college.edu',
            'phone_number': '9876543210',
            'password': 'mypassword',
            'confirm_password': 'mypassword'
        }, follow_redirects=True)
        self.assertIn(b'mixed with both letters and integers', res.data)

        # 3. Valid registration (10 characters alphanumeric, custom password)
        res = self.client.post('/register', data={
            'name': 'Sneha Reddy',
            'college_id': '23B91A0588',
            'year_of_study': 2,
            'email': 'sneha@college.edu',
            'phone_number': '9848012345',
            'password': 'mypassword@2026',
            'confirm_password': 'mypassword@2026'
        }, follow_redirects=True)
        self.assertIn(b'Registration successful', res.data)

    def test_03_login_and_roles(self):
        """Test authentication for student, driver, and admin."""
        # Student login
        res = self.client.post('/login', data={
            'identifier': '23B91A0501',
            'password': 'student123'
        }, follow_redirects=True)
        self.assertIn(b'Vijitha', res.data)
        self.client.get('/logout')

        # Driver login
        res = self.client.post('/login', data={
            'identifier': 'driver_ramesh',
            'password': 'driver123'
        }, follow_redirects=True)
        self.assertIn(b'Driver GPS Console', res.data)
        self.client.get('/logout')

        # Admin login
        res = self.client.post('/login', data={
            'identifier': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertIn(b'Transport Administration Console', res.data)
        self.client.get('/logout')

    def test_04_seat_selection_payment_locking_and_bus_pass(self):
        """Test full workflow: select seat 07, pay fee, lock seat, generate QR bus pass."""
        # Log in as Vijitha
        self.client.post('/login', data={'identifier': '23B91A0501', 'password': 'student123'})

        with self.app.app_context():
            bus = Bus.query.filter_by(bus_number='BUS-05').first()
            ay = AcademicYear.query.filter_by(is_active=True).first()
            bp = bus.route.boarding_points[0]

            # Confirm seat 07
            res = self.client.post('/student/confirm-seat', data={
                'bus_id': bus.id,
                'academic_year_id': ay.id,
                'boarding_point_id': bp.id,
                'seat_number': '07'
            }, follow_redirects=True)
            self.assertIn(b'College Bus Fee Portal', res.data)

            alloc = SeatAllocation.query.filter_by(
                bus_id=bus.id,
                seat_number='07',
                academic_year_id=ay.id
            ).first()
            self.assertIsNotNone(alloc)

            # Process Demo Payment
            res = self.client.post('/student/process-payment', data={
                'allocation_id': alloc.id,
                'payment_method': 'Instant UPI (Simulated)'
            }, follow_redirects=True)
            self.assertIn(b'Digital Bus Pass', res.data)

            # Check that allocation is CONFIRMED and QR code exists
            db.session.refresh(alloc)
            self.assertEqual(alloc.status, 'CONFIRMED')
            self.assertIsNotNone(alloc.bus_pass)
            self.assertTrue(os.path.exists(os.path.join(self.app.root_path, 'static', alloc.bus_pass.qr_code_path)))

        # Log out Vijitha
        self.client.get('/logout')

        # Log in as Student 2 (Rahul Sharma) and attempt to book the SAME seat 07 for the SAME bus and academic year!
        self.client.post('/login', data={'identifier': '23B91A0502', 'password': 'student123'})

        with self.app.app_context():
            res = self.client.post('/student/confirm-seat', data={
                'bus_id': bus.id,
                'academic_year_id': ay.id,
                'boarding_point_id': bp.id,
                'seat_number': '07'
            }, follow_redirects=True)
            # Must be BLOCKED and rejected!
            self.assertIn(b'already occupied and locked', res.data)

    def test_05_driver_gps_api_and_student_tracking(self):
        """Test POST /api/bus-location and GET /api/bus-location/<bus_id>."""
        with self.app.app_context():
            bus = Bus.query.filter_by(bus_number='BUS-05').first()
            bus_id = bus.id

        # Driver updates GPS coordinates
        payload = {
            'bus_id': bus_id,
            'latitude': 14.4500,
            'longitude': 77.7300,
            'speed': 32.5,
            'trip_status': 'RUNNING'
        }
        res = self.client.post('/api/bus-location', json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'success')

        # Student queries location
        res = self.client.get(f'/api/bus-location/{bus_id}')
        self.assertEqual(res.status_code, 200)
        loc_data = res.get_json()['location']
        self.assertEqual(loc_data['latitude'], 14.4500)
        self.assertEqual(loc_data['longitude'], 77.7300)
        self.assertEqual(loc_data['trip_status'], 'RUNNING')

if __name__ == '__main__':
    unittest.main()
