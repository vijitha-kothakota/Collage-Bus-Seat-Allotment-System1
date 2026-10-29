import os
import uuid
import json
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect, url_for, flash, jsonify, abort
)
from flask_login import (
    LoginManager, login_user, logout_user, login_required, current_user
)

from config import Config
from models import (
    db, User, Student, Driver, AcademicYear, Route, BoardingPoint,
    Bus, Seat, SeatAllocation, Payment, BusPass, BusLocation
)
from utils import role_required, generate_bus_pass_qr, haversine_distance
from seed import seed_database

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Create tables and seed default data
    with app.app_context():
        db.create_all()
        seed_database()

    # -------------------------------------------------------------
    # Context Processor
    # -------------------------------------------------------------
    @app.context_processor
    def inject_global_data():
        active_year = AcademicYear.query.filter_by(is_active=True).first()
        return dict(active_year=active_year)

    # -------------------------------------------------------------
    # General / Authentication Routes
    # -------------------------------------------------------------
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            if current_user.is_student():
                return redirect(url_for('student_dashboard'))
            elif current_user.is_driver():
                return redirect(url_for('driver_dashboard'))
            elif current_user.is_admin():
                return redirect(url_for('admin_dashboard'))
        return redirect(url_for('login'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('index'))

        if request.method == 'POST':
            identifier = request.form.get('identifier', '').strip()
            password = request.form.get('password', '')

            if not identifier or not password:
                flash('Please enter both identifier and password.', 'danger')
                return render_template('login.html')

            # 1. Check if it's an Admin or Driver account
            admin_driver_user = User.query.filter(
                ((User.username == identifier) | (User.email == identifier.lower())) &
                (User.role.in_(['admin', 'driver']))
            ).first()

            if admin_driver_user:
                if admin_driver_user.check_password(password):
                    login_user(admin_driver_user)
                    flash(f'Welcome back, {admin_driver_user.username}!', 'success')
                    return redirect(url_for('index'))
                else:
                    flash('Invalid password for administrative/driver account.', 'danger')
                    return render_template('login.html')

            # 2. Check Student: Accept any student ID and password
            clean_id = identifier.upper()
            student_profile = Student.query.filter(
                (Student.college_id == clean_id) | (Student.email == identifier.lower())
            ).first()

            if student_profile:
                user = student_profile.user
                if user:
                    if user.check_password(password) or len(password) > 0:
                        login_user(user)
                        flash(f'Welcome back, {student_profile.name} ({student_profile.college_id})!', 'success')
                        return redirect(url_for('student_dashboard'))
            
            # Check user table for existing student username
            existing_user = User.query.filter_by(username=clean_id).first()
            if existing_user and existing_user.is_student():
                login_user(existing_user)
                flash(f'Welcome back, {existing_user.username}!', 'success')
                return redirect(url_for('student_dashboard'))

            # Auto-register and accept ANY new student ID and password on the fly
            email_handle = clean_id.lower().replace(' ', '')
            new_email = f"{email_handle}@college.edu"
            counter = 1
            while User.query.filter_by(email=new_email).first():
                new_email = f"{email_handle}{counter}@college.edu"
                counter += 1

            new_user = User(
                username=clean_id,
                email=new_email,
                role='student'
            )
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.flush()

            new_student = Student(
                user_id=new_user.id,
                name=f"Student {clean_id}",
                college_id=clean_id,
                year_of_study=1,
                email=new_email,
                phone_number="9876543210"
            )
            db.session.add(new_student)
            db.session.commit()

            login_user(new_user)
            flash(f'Student ID {clean_id} verified & logged in! Please select your year of study below.', 'success')
            return redirect(url_for('student_dashboard'))

        return render_template('login.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('index'))

        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            college_id = request.form.get('college_id', '').strip().upper()
            email = request.form.get('email', '').strip().lower()
            phone_number = request.form.get('phone_number', '').strip()
            password = request.form.get('password', '')
            confirm_password = request.form.get('confirm_password', '')

            # Validation: Student ID must be exactly 10 characters mixed with letters and numbers
            if len(college_id) != 10:
                flash('Student ID must be exactly 10 characters long (e.g. 23B91A0501).', 'danger')
                return render_template('register.html')

            has_letter = any(c.isalpha() for c in college_id)
            has_digit = any(c.isdigit() for c in college_id)
            if not (has_letter and has_digit and college_id.isalnum()):
                flash('Student ID must be 10 characters mixed with both letters and integers (e.g. 23B91A0501).', 'danger')
                return render_template('register.html')

            if password != confirm_password:
                flash('Passwords do not match.', 'danger')
                return render_template('register.html')

            if len(password) < 1:
                flash('Password cannot be empty.', 'danger')
                return render_template('register.html')

            # Check duplicate email, college_id, username
            if User.query.filter_by(email=email).first():
                flash('An account with that email already exists.', 'danger')
                return render_template('register.html')

            if Student.query.filter_by(college_id=college_id).first():
                flash(f'Student ID {college_id} is already registered.', 'danger')
                return render_template('register.html')

            if User.query.filter_by(username=college_id).first():
                flash(f'An account with username {college_id} already exists.', 'danger')
                return render_template('register.html')

            # Create User and Student profile
            new_user = User(
                username=college_id,
                email=email,
                role='student'
            )
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.flush()

            year_of_study = request.form.get('year_of_study', type=int) or 1

            new_student = Student(
                user_id=new_user.id,
                name=name,
                college_id=college_id,
                year_of_study=year_of_study,
                email=email,
                phone_number=phone_number
            )
            db.session.add(new_student)
            db.session.commit()

            login_user(new_user)
            flash(f'Registration successful! Welcome to ALTS Bus Portal, {name}.', 'success')
            return redirect(url_for('student_dashboard'))

        return render_template('register.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out successfully.', 'info')
        return redirect(url_for('login'))

    # -------------------------------------------------------------
    # Student Routes
    # -------------------------------------------------------------
    @app.route('/student/dashboard')
    @role_required('student')
    def student_dashboard():
        student = current_user.student_profile
        active_year = AcademicYear.query.filter_by(is_active=True).first()
        allocation = student.get_confirmed_allocation(active_year.id if active_year else None)
        if not allocation:
            allocation = student.get_latest_allocation()

        bus_location = None
        if allocation and allocation.bus:
            bus_location = allocation.bus.get_latest_location()

        return render_template(
            'student/dashboard.html',
            student=student,
            allocation=allocation,
            bus_location=bus_location,
            active_year=active_year
        )

    @app.route('/student/update-year', methods=['POST'])
    @role_required('student')
    def student_update_year():
        student = current_user.student_profile
        year_of_study = request.form.get('year_of_study', type=int)

        if year_of_study in [1, 2, 3, 4]:
            student.year_of_study = year_of_study
            db.session.commit()
            sched = student.get_schedule()
            flash(f"Year of study updated to {sched['year_label']}! Bus shift timing: {sched['morning_time']} - {sched['evening_time']}.", 'success')
        else:
            flash('Invalid year of study selected.', 'danger')

        return redirect(url_for('student_dashboard'))

    @app.route('/student/buses', methods=['GET', 'POST'])
    @role_required('student')
    def student_buses():
        student = current_user.student_profile
        active_year = AcademicYear.query.filter_by(is_active=True).first()

        if request.method == 'POST':
            bus_id = request.form.get('bus_id', type=int)
            academic_year_id = request.form.get('academic_year_id', type=int)
            boarding_point_id = request.form.get('boarding_point_id', type=int)

            if not bus_id or not academic_year_id or not boarding_point_id:
                flash('Please select academic year, bus, and your boarding stop.', 'warning')
                return redirect(url_for('student_buses'))

            return redirect(url_for(
                'student_seats',
                bus_id=bus_id,
                academic_year_id=academic_year_id,
                boarding_point_id=boarding_point_id
            ))

        academic_years = AcademicYear.query.filter_by(is_active=True).all()
        buses = Bus.query.filter_by(is_active=True).all()

        bus_list = []
        for b in buses:
            avail = b.get_available_seats_count(active_year.id if active_year else 1)
            bus_list.append({
                'bus': b,
                'available_seats': avail
            })

        return render_template(
            'student/buses.html',
            student=student,
            academic_years=academic_years,
            bus_list=bus_list
        )

    @app.route('/student/seats')
    @role_required('student')
    def student_seats():
        bus_id = request.args.get('bus_id', type=int)
        academic_year_id = request.args.get('academic_year_id', type=int)
        boarding_point_id = request.args.get('boarding_point_id', type=int)

        if not bus_id or not academic_year_id:
            bus = Bus.query.first()
            ay = AcademicYear.query.filter_by(is_active=True).first()
            if not bus or not ay:
                flash('No bus or academic year available.', 'danger')
                return redirect(url_for('student_dashboard'))
            bus_id = bus.id
            academic_year_id = ay.id
            boarding_point_id = bus.route.boarding_points[0].id if bus.route.boarding_points else None

        bus = Bus.query.get_or_404(bus_id)
        academic_year = AcademicYear.query.get_or_404(academic_year_id)
        boarding_point = BoardingPoint.query.get(boarding_point_id) if boarding_point_id else (bus.route.boarding_points[0] if bus.route.boarding_points else None)

        # Retrieve all confirmed allocations for this bus + academic year
        confirmed_allocations = SeatAllocation.query.filter_by(
            bus_id=bus.id,
            academic_year_id=academic_year.id,
            status='CONFIRMED'
        ).all()
        occupied_seats_set = {alloc.seat_number for alloc in confirmed_allocations}

        # Build list of 40 seats in rows of 4 (left 2, right 2)
        total_capacity = bus.capacity or 40
        all_seats = []
        for i in range(1, total_capacity + 1):
            s_num = f"{i:02d}"
            all_seats.append({
                'seat_number': s_num,
                'is_occupied': (s_num in occupied_seats_set)
            })

        seat_rows = [all_seats[i:i + 4] for i in range(0, len(all_seats), 4)]

        return render_template(
            'student/seats.html',
            bus=bus,
            academic_year=academic_year,
            boarding_point=boarding_point,
            seat_rows=seat_rows
        )

    @app.route('/student/confirm-seat', methods=['POST'])
    @role_required('student')
    def student_confirm_seat():
        student = current_user.student_profile
        bus_id = request.form.get('bus_id', type=int)
        academic_year_id = request.form.get('academic_year_id', type=int)
        boarding_point_id = request.form.get('boarding_point_id', type=int)
        seat_number = request.form.get('seat_number', '').strip()

        if not bus_id or not academic_year_id or not seat_number or not boarding_point_id:
            flash('Invalid seat selection. Please choose an available seat.', 'danger')
            return redirect(url_for('student_buses'))

        # Database Check: Ensure seat is not already confirmed by someone else in this academic year
        existing_confirmed = SeatAllocation.query.filter_by(
            bus_id=bus_id,
            seat_number=seat_number,
            academic_year_id=academic_year_id,
            status='CONFIRMED'
        ).first()

        if existing_confirmed and existing_confirmed.student_id != student.id:
            flash(f'Seat {seat_number} is already occupied and locked by another student for Academic Year!', 'danger')
            return redirect(url_for('student_seats', bus_id=bus_id, academic_year_id=academic_year_id, boarding_point_id=boarding_point_id))

        # Check if student already has a pending allocation; update it, or create new
        existing_alloc = SeatAllocation.query.filter_by(
            student_id=student.id,
            academic_year_id=academic_year_id
        ).first()

        if existing_alloc:
            # If already confirmed, prevent overwriting confirmed seat
            if existing_alloc.status == 'CONFIRMED' and existing_alloc.seat_number != seat_number:
                flash(f'You already have confirmed Seat {existing_alloc.seat_number}. Contact transport admin to transfer seats.', 'info')
                return redirect(url_for('student_dashboard'))
            
            existing_alloc.bus_id = bus_id
            existing_alloc.boarding_point_id = boarding_point_id
            existing_alloc.seat_number = seat_number
            db.session.commit()
            allocation = existing_alloc
        else:
            allocation = SeatAllocation(
                student_id=student.id,
                bus_id=bus_id,
                boarding_point_id=boarding_point_id,
                seat_number=seat_number,
                academic_year_id=academic_year_id,
                status='PENDING'
            )
            db.session.add(allocation)
            db.session.commit()

        flash(f'Seat {seat_number} selected! Please complete the fee payment to confirm.', 'info')
        return redirect(url_for('student_payment'))

    @app.route('/student/payment')
    @role_required('student')
    def student_payment():
        student = current_user.student_profile
        active_year = AcademicYear.query.filter_by(is_active=True).first()
        allocation = student.get_confirmed_allocation(active_year.id if active_year else None)
        if not allocation:
            allocation = student.get_latest_allocation()

        if not allocation:
            flash('Please select a bus and seat first before proceeding to payment.', 'warning')
            return redirect(url_for('student_buses'))

        return render_template(
            'student/payment.html',
            student=student,
            allocation=allocation
        )

    @app.route('/student/process-payment', methods=['POST'])
    @role_required('student')
    def student_process_payment():
        student = current_user.student_profile
        allocation_id = request.form.get('allocation_id', type=int)
        payment_method = request.form.get('payment_method', 'UPI / QR (Demo)')

        allocation = SeatAllocation.query.get_or_404(allocation_id)
        if allocation.student_id != student.id:
            abort(403)

        # Database Check: Verify no other student has confirmed this seat in the meantime
        other_confirmed = SeatAllocation.query.filter(
            SeatAllocation.bus_id == allocation.bus_id,
            SeatAllocation.seat_number == allocation.seat_number,
            SeatAllocation.academic_year_id == allocation.academic_year_id,
            SeatAllocation.status == 'CONFIRMED',
            SeatAllocation.id != allocation.id
        ).first()

        if other_confirmed:
            flash(f'Sorry, Seat {allocation.seat_number} was just booked by another student. Please select another seat.', 'danger')
            return redirect(url_for('student_buses'))

        # 1. Update Allocation to CONFIRMED
        allocation.status = 'CONFIRMED'

        # 2. Record Payment
        amount = allocation.bus.route.annual_fee
        txn_id = f"ALTS-{datetime.utcnow().strftime('%y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        payment = Payment.query.filter_by(allocation_id=allocation.id).first()
        if not payment:
            payment = Payment(
                allocation_id=allocation.id,
                student_id=student.id,
                amount=amount,
                payment_method=payment_method,
                transaction_id=txn_id,
                status='Successful'
            )
            db.session.add(payment)
        else:
            payment.status = 'Successful'
            payment.payment_method = payment_method

        # 3. Generate Digital Bus Pass with QR Code
        pass_id = f"PASS-{datetime.utcnow().strftime('%y')}-{allocation.id:04d}"
        qr_rel_path = generate_bus_pass_qr(
            pass_id=pass_id,
            student_name=student.name,
            college_id=student.college_id,
            bus_number=allocation.bus.bus_number,
            seat_number=allocation.seat_number
        )

        bus_pass = BusPass.query.filter_by(allocation_id=allocation.id).first()
        if not bus_pass:
            bus_pass = BusPass(
                pass_id=pass_id,
                allocation_id=allocation.id,
                qr_code_path=qr_rel_path,
                valid_until='May 2027',
                is_active=True
            )
            db.session.add(bus_pass)
        else:
            bus_pass.qr_code_path = qr_rel_path
            bus_pass.is_active = True

        db.session.commit()

        flash(f'Payment of ₹{int(amount)} successful! Seat {allocation.seat_number} is locked for Academic Year {allocation.academic_year.year_label}. Digital Bus Pass generated!', 'success')
        return redirect(url_for('student_bus_pass'))

    @app.route('/student/bus-pass')
    @role_required('student')
    def student_bus_pass():
        student = current_user.student_profile
        active_year = AcademicYear.query.filter_by(is_active=True).first()
        allocation = student.get_confirmed_allocation(active_year.id if active_year else None)
        if not allocation:
            allocation = student.get_latest_allocation()

        bus_pass = allocation.bus_pass if allocation else None

        return render_template(
            'student/bus_pass.html',
            student=student,
            allocation=allocation,
            bus_pass=bus_pass
        )

    @app.route('/track-bus')
    @app.route('/student/track-bus')
    def student_track_bus():
        bus_id = request.args.get('bus_id', type=int)
        student = None
        student_stop = None

        if current_user.is_authenticated and current_user.is_student():
            student = current_user.student_profile
            active_year = AcademicYear.query.filter_by(is_active=True).first()
            alloc = student.get_confirmed_allocation(active_year.id if active_year else None) or student.get_latest_allocation()
            if alloc:
                if not bus_id:
                    bus_id = alloc.bus_id
                student_stop = alloc.boarding_point

        if not bus_id:
            bus = Bus.query.first()
            if not bus:
                flash('No buses configured in system.', 'warning')
                return redirect(url_for('index'))
            bus_id = bus.id

        bus = Bus.query.get_or_404(bus_id)
        bus_location = bus.get_latest_location()

        # Serialize stops for Leaflet JS
        all_stops = bus.route.boarding_points
        all_stops_data = [s.to_dict() for s in all_stops]
        student_stop_data = student_stop.to_dict() if student_stop else (all_stops_data[0] if all_stops_data else None)
        location_data = bus_location.to_dict() if bus_location else None

        return render_template(
            'student/track_bus.html',
            bus=bus,
            bus_location=bus_location,
            all_stops=all_stops,
            student_stop=student_stop,
            all_stops_json=json.dumps(all_stops_data),
            student_stop_json=json.dumps(student_stop_data),
            bus_location_json=json.dumps(location_data)
        )

    # -------------------------------------------------------------
    # Driver Console & GPS Endpoints
    # -------------------------------------------------------------
    @app.route('/driver/dashboard')
    @role_required('driver')
    def driver_dashboard():
        driver = current_user.driver_profile
        route_stops_data = []
        if driver.bus and driver.bus.route:
            route_stops_data = [s.to_dict() for s in driver.bus.route.boarding_points]

        return render_template(
            'driver/dashboard.html',
            driver=driver,
            route_stops_json=json.dumps(route_stops_data)
        )

    # -------------------------------------------------------------
    # REST API for GPS Telemetry
    # -------------------------------------------------------------
    @app.route('/api/bus-location', methods=['POST'])
    def api_update_bus_location():
        """
        Receives real GPS coordinates from driver's mobile phone:
        POST { "bus_id": 1, "latitude": 14.4137, "longitude": 77.7126, "speed": 28.5, "trip_status": "RUNNING" }
        """
        data = request.get_json() or {}
        bus_id = data.get('bus_id')
        if not bus_id:
            return jsonify({'status': 'error', 'message': 'Missing bus_id'}), 400

        bus = Bus.query.get(bus_id)
        if not bus:
            return jsonify({'status': 'error', 'message': 'Bus not found'}), 404

        lat = data.get('latitude')
        lng = data.get('longitude')
        speed = data.get('speed', 0.0)
        heading = data.get('heading', 0.0)
        trip_status = data.get('trip_status', 'RUNNING')

        loc = BusLocation.query.filter_by(bus_id=bus.id).first()
        if not loc:
            loc = BusLocation(
                bus_id=bus.id,
                latitude=lat if lat is not None else 14.4137,
                longitude=lng if lng is not None else 77.7126,
                speed=speed,
                heading=heading,
                trip_status=trip_status
            )
            db.session.add(loc)
        else:
            if lat is not None:
                loc.latitude = lat
            if lng is not None:
                loc.longitude = lng
            loc.speed = speed
            loc.heading = heading
            loc.trip_status = trip_status
            loc.updated_at = datetime.utcnow()

        db.session.commit()
        return jsonify({'status': 'success', 'location': loc.to_dict()})

    @app.route('/api/bus-location/<int:bus_id>', methods=['GET'])
    def api_get_bus_location(bus_id):
        """
        Returns latest GPS coordinates of the bus for student Leaflet map polling.
        """
        bus = Bus.query.get_or_404(bus_id)
        loc = bus.get_latest_location()
        if not loc:
            return jsonify({'status': 'error', 'message': 'Location not found'}), 404

        return jsonify({'status': 'success', 'location': loc.to_dict()})

    # -------------------------------------------------------------
    # Admin Panel Routes
    # -------------------------------------------------------------
    @app.route('/admin/dashboard')
    @role_required('admin')
    def admin_dashboard():
        active_year = AcademicYear.query.filter_by(is_active=True).first()
        ay_id = active_year.id if active_year else 1

        total_students = Student.query.count()
        buses = Bus.query.all()
        total_buses = len(buses)
        total_seats = sum(b.capacity for b in buses)

        confirmed_allocations = SeatAllocation.query.filter_by(
            academic_year_id=ay_id,
            status='CONFIRMED'
        ).all()
        allocated_seats = len(confirmed_allocations)
        available_seats = max(0, total_seats - allocated_seats)

        # Fee statistics
        successful_payments = Payment.query.filter_by(status='Successful').all()
        paid_fees = sum(p.amount for p in successful_payments)

        pending_allocs = SeatAllocation.query.filter_by(
            academic_year_id=ay_id,
            status='PENDING'
        ).all()
        pending_fees = sum(a.bus.route.annual_fee for a in pending_allocs if a.bus and a.bus.route)

        active_trips = BusLocation.query.filter_by(trip_status='RUNNING').count()

        return render_template(
            'admin/dashboard.html',
            total_students=total_students,
            total_buses=total_buses,
            total_seats=total_seats,
            allocated_seats=allocated_seats,
            available_seats=available_seats,
            paid_fees=paid_fees,
            pending_fees=pending_fees,
            active_trips=active_trips,
            buses=buses,
            active_year=active_year
        )

    @app.route('/admin/buses')
    @role_required('admin')
    def admin_buses():
        buses = Bus.query.all()
        routes = Route.query.all()
        active_year = AcademicYear.query.filter_by(is_active=True).first()
        return render_template('admin/buses.html', buses=buses, routes=routes, active_year=active_year)

    @app.route('/admin/add-bus', methods=['POST'])
    @role_required('admin')
    def admin_add_bus():
        bus_number = request.form.get('bus_number', '').strip().upper()
        capacity = request.form.get('capacity', type=int) or 40
        route_id = request.form.get('route_id', type=int)

        if not bus_number or not route_id:
            flash('Bus number and route are required.', 'danger')
            return redirect(url_for('admin_buses'))

        if Bus.query.filter_by(bus_number=bus_number).first():
            flash(f'Bus {bus_number} already exists.', 'danger')
            return redirect(url_for('admin_buses'))

        bus = Bus(bus_number=bus_number, capacity=capacity, route_id=route_id, is_active=True)
        db.session.add(bus)
        db.session.commit()

        # Generate seats for the bus
        for i in range(1, capacity + 1):
            s_num = f"{i:02d}"
            s_type = 'Window' if (i % 4 in (1, 0)) else 'Aisle'
            db.session.add(Seat(bus_id=bus.id, seat_number=s_num, seat_type=s_type))

        # Initial location
        start_stop = bus.route.boarding_points[0] if bus.route.boarding_points else None
        loc = BusLocation(
            bus_id=bus.id,
            latitude=start_stop.latitude if start_stop else 14.4137,
            longitude=start_stop.longitude if start_stop else 77.7126,
            trip_status='IDLE'
        )
        db.session.add(loc)
        db.session.commit()

        flash(f'Bus {bus_number} with {capacity} seats created successfully!', 'success')
        return redirect(url_for('admin_buses'))

    @app.route('/admin/delete-bus/<int:bus_id>', methods=['POST'])
    @role_required('admin')
    def admin_delete_bus(bus_id):
        bus = Bus.query.get_or_404(bus_id)
        db.session.delete(bus)
        db.session.commit()
        flash(f'Bus {bus.bus_number} deleted successfully.', 'info')
        return redirect(url_for('admin_buses'))

    @app.route('/admin/routes')
    @role_required('admin')
    def admin_routes():
        routes = Route.query.all()
        return render_template('admin/routes.html', routes=routes)

    @app.route('/admin/add-route', methods=['POST'])
    @role_required('admin')
    def admin_add_route():
        route_name = request.form.get('route_name', '').strip()
        start_point = request.form.get('start_point', '').strip()
        destination = request.form.get('destination', '').strip()
        annual_fee = request.form.get('annual_fee', type=float) or 18000.0
        total_distance_km = request.form.get('total_distance_km', type=float) or 30.0

        route = Route(
            route_name=route_name,
            start_point=start_point,
            destination=destination,
            annual_fee=annual_fee,
            total_distance_km=total_distance_km
        )
        db.session.add(route)
        db.session.commit()

        flash(f'Route "{route_name}" created successfully.', 'success')
        return redirect(url_for('admin_routes'))

    @app.route('/admin/add-boarding-point', methods=['POST'])
    @role_required('admin')
    def admin_add_boarding_point():
        route_id = request.form.get('route_id', type=int)
        stop_name = request.form.get('stop_name', '').strip()
        stop_order = request.form.get('stop_order', type=int) or 1
        pickup_time = request.form.get('pickup_time', '07:30 AM').strip()
        lat = request.form.get('latitude', type=float)
        lng = request.form.get('longitude', type=float)

        bp = BoardingPoint(
            route_id=route_id,
            stop_name=stop_name,
            stop_order=stop_order,
            pickup_time=pickup_time,
            latitude=lat,
            longitude=lng
        )
        db.session.add(bp)
        db.session.commit()

        flash(f'Boarding point "{stop_name}" added to route.', 'success')
        return redirect(url_for('admin_routes'))

    @app.route('/admin/students')
    @role_required('admin')
    def admin_students():
        students = Student.query.order_by(Student.created_at.desc()).all()
        active_year = AcademicYear.query.filter_by(is_active=True).first()
        return render_template('admin/students.html', students=students, active_year=active_year)

    @app.route('/admin/add-student', methods=['POST'])
    @role_required('admin')
    def admin_add_student():
        name = request.form.get('name', '').strip()
        college_id = request.form.get('college_id', '').strip().upper()
        year_of_study = request.form.get('year_of_study', type=int) or 1
        email = request.form.get('email', '').strip().lower()
        phone_number = request.form.get('phone_number', '').strip()
        password = request.form.get('password', 'student123')

        if len(college_id) != 10 or not (any(c.isalpha() for c in college_id) and any(c.isdigit() for c in college_id)):
            flash('Student ID must be exactly 10 characters mixed with letters and numbers (e.g. 23B91A0501).', 'danger')
            return redirect(url_for('admin_students'))

        if Student.query.filter_by(college_id=college_id).first():
            flash(f'Student ID {college_id} already exists in database.', 'danger')
            return redirect(url_for('admin_students'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered for another account.', 'danger')
            return redirect(url_for('admin_students'))

        user = User(username=college_id, email=email, role='student')
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        student = Student(
            user_id=user.id,
            name=name,
            college_id=college_id,
            year_of_study=year_of_study,
            email=email,
            phone_number=phone_number
        )
        db.session.add(student)
        db.session.commit()

        flash(f'Student {name} ({college_id}) added to database successfully!', 'success')
        return redirect(url_for('admin_students'))

    @app.route('/admin/delete-student/<int:student_id>', methods=['POST'])
    @role_required('admin')
    def admin_delete_student(student_id):
        student = Student.query.get_or_404(student_id)
        user = student.user
        student_name = student.name
        student_id_str = student.college_id
        db.session.delete(student)
        if user:
            db.session.delete(user)
        db.session.commit()
        flash(f'Student {student_name} ({student_id_str}) deleted from database.', 'info')
        return redirect(url_for('admin_students'))

    @app.route('/admin/allocations')
    @role_required('admin')
    def admin_allocations():
        allocations = SeatAllocation.query.order_by(SeatAllocation.allocation_date.desc()).all()
        return render_template('admin/allocations.html', allocations=allocations)

    @app.route('/admin/cancel-allocation/<int:allocation_id>', methods=['POST'])
    @role_required('admin')
    def admin_cancel_allocation(allocation_id):
        alloc = SeatAllocation.query.get_or_404(allocation_id)
        seat_num = alloc.seat_number
        db.session.delete(alloc)
        db.session.commit()
        flash(f'Allocation for Seat {seat_num} cancelled. Seat is now unlocked and available.', 'info')
        return redirect(url_for('admin_allocations'))

    @app.route('/admin/payments')
    @role_required('admin')
    def admin_payments():
        payments = Payment.query.order_by(Payment.payment_date.desc()).all()
        total_collected = sum(p.amount for p in payments if p.status == 'Successful')
        return render_template('admin/payments.html', payments=payments, total_collected=total_collected)

    return app

app = create_app()

if __name__ == '__main__':
    # Listen on all interfaces (0.0.0.0) so driver Android phone on the same Wi-Fi can connect!
    app.run(host='0.0.0.0', port=5000, debug=True)
