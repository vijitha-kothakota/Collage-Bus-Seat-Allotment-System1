from models import (
    db, User, AcademicYear, Route, BoardingPoint, Bus, Driver,
    Student, Seat, SeatAllocation, Payment, BusPass, BusLocation
)

def seed_database():
    """Populates initial sample data if not already present."""
    # 1. Academic Year
    ay = AcademicYear.query.filter_by(year_label='2026–27').first()
    if not ay:
        ay = AcademicYear(year_label='2026–27', is_active=True)
        db.session.add(ay)
        db.session.commit()

    # 2. Routes & Boarding Points
    route1 = Route.query.filter_by(route_name="Dharmavaram → College").first()
    if not route1:
        route1 = Route(
            route_name="Dharmavaram → College",
            start_point="Dharmavaram",
            destination="Ananthalakshmi College (ALTS)",
            annual_fee=18000.0,
            total_distance_km=36.5
        )
        db.session.add(route1)
        db.session.commit()

        stops1 = [
            ("Dharmavaram Bus Stand", 1, "07:30 AM", 14.4137, 77.7126),
            ("Railway Station Junction", 2, "07:42 AM", 14.4250, 77.7190),
            ("Kethireddy Colony", 3, "07:55 AM", 14.4500, 77.7300),
            ("Marur Toll Plaza", 4, "08:10 AM", 14.5200, 77.7550),
            ("Rudrampeta Bypass", 5, "08:28 AM", 14.6500, 77.6000),
            ("ALTS College Campus", 6, "08:45 AM", 14.6819, 77.5540)
        ]
        for name, order, ptime, lat, lng in stops1:
            db.session.add(BoardingPoint(
                route_id=route1.id,
                stop_name=name,
                stop_order=order,
                pickup_time=ptime,
                latitude=lat,
                longitude=lng
            ))
        db.session.commit()

    route2 = Route.query.filter_by(route_name="Anantapur Clock Tower → College").first()
    if not route2:
        route2 = Route(
            route_name="Anantapur Clock Tower → College",
            start_point="Anantapur Clock Tower",
            destination="Ananthalakshmi College (ALTS)",
            annual_fee=22000.0,
            total_distance_km=18.0
        )
        db.session.add(route2)
        db.session.commit()

        stops2 = [
            ("Clock Tower Center", 1, "08:00 AM", 14.6819, 77.6006),
            ("Sapthagiri Circle", 2, "08:12 AM", 14.6750, 77.5950),
            ("Subash Nagar", 3, "08:22 AM", 14.6700, 77.5850),
            ("ALTS College Campus", 4, "08:40 AM", 14.6819, 77.5540)
        ]
        for name, order, ptime, lat, lng in stops2:
            db.session.add(BoardingPoint(
                route_id=route2.id,
                stop_name=name,
                stop_order=order,
                pickup_time=ptime,
                latitude=lat,
                longitude=lng
            ))
        db.session.commit()

    # 3. Buses & Seats
    bus1 = Bus.query.filter_by(bus_number="BUS-05").first()
    if not bus1:
        bus1 = Bus(bus_number="BUS-05", capacity=40, route_id=route1.id, is_active=True)
        db.session.add(bus1)
        db.session.commit()

        for i in range(1, 41):
            s_num = f"{i:02d}"
            s_type = 'Window' if (i % 4 in (1, 0)) else 'Aisle'
            db.session.add(Seat(bus_id=bus1.id, seat_number=s_num, seat_type=s_type))
        
        loc1 = BusLocation(
            bus_id=bus1.id,
            latitude=14.4137,
            longitude=77.7126,
            speed=0.0,
            heading=0.0,
            trip_status='IDLE'
        )
        db.session.add(loc1)
        db.session.commit()

    bus2 = Bus.query.filter_by(bus_number="BUS-02").first()
    if not bus2:
        bus2 = Bus(bus_number="BUS-02", capacity=40, route_id=route2.id, is_active=True)
        db.session.add(bus2)
        db.session.commit()

        for i in range(1, 41):
            s_num = f"{i:02d}"
            s_type = 'Window' if (i % 4 in (1, 0)) else 'Aisle'
            db.session.add(Seat(bus_id=bus2.id, seat_number=s_num, seat_type=s_type))

        loc2 = BusLocation(
            bus_id=bus2.id,
            latitude=14.6819,
            longitude=77.6006,
            speed=0.0,
            heading=0.0,
            trip_status='IDLE'
        )
        db.session.add(loc2)
        db.session.commit()

    # 4. Users: Admin
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(
            username='admin',
            email='admin@college.edu',
            role='admin'
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.commit()

    # 5. Users: Driver
    driver_user = User.query.filter_by(username='driver_ramesh').first()
    if not driver_user:
        driver_user = User(
            username='driver_ramesh',
            email='driver@college.edu',
            role='driver'
        )
        driver_user.set_password('driver123')
        db.session.add(driver_user)
        db.session.commit()

        driver_profile = Driver(
            user_id=driver_user.id,
            name='Ramesh Kumar',
            license_number='AP04-2018-009871',
            phone_number='9876543210',
            bus_id=bus1.id
        )
        db.session.add(driver_profile)
        db.session.commit()

    # 6. Users: Students
    # Student 1: Vijitha (1st Year: Morning 8:30 AM, Evening 5:00 PM)
    student1_user = User.query.filter_by(username='23B91A0501').first()
    if not student1_user:
        student1_user = User(
            username='23B91A0501',
            email='vijitha@college.edu',
            role='student'
        )
        student1_user.set_password('student123')
        db.session.add(student1_user)
        db.session.commit()

        student1 = Student(
            user_id=student1_user.id,
            name='Vijitha',
            college_id='23B91A0501',
            year_of_study=1,  # 1st Year: 8:30 AM - 5:00 PM
            email='vijitha@college.edu',
            phone_number='9123456789'
        )
        db.session.add(student1)
        db.session.commit()

    # Student 2: Rahul Sharma (3rd Year: Morning 7:30 AM, Evening 4:00 PM)
    student2_user = User.query.filter_by(username='23B91A0502').first()
    if not student2_user:
        student2_user = User(
            username='23B91A0502',
            email='rahul@college.edu',
            role='student'
        )
        student2_user.set_password('student123')
        db.session.add(student2_user)
        db.session.commit()

        student2 = Student(
            user_id=student2_user.id,
            name='Rahul Sharma',
            college_id='23B91A0502',
            year_of_study=3,  # 3rd Year: 7:30 AM - 4:00 PM
            email='rahul@college.edu',
            phone_number='9123456780'
        )
        db.session.add(student2)
        db.session.commit()

    print("Sample database seeded successfully!")
