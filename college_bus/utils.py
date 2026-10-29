import os
import math
import qrcode
from functools import wraps
from flask import abort, flash, redirect, url_for, current_app
from flask_login import current_user

def role_required(*allowed_roles):
    """Decorator to enforce role-based access control."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('login'))
            if current_user.role not in allowed_roles:
                flash('You do not have permission to access that page.', 'danger')
                return abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def generate_bus_pass_qr(pass_id, student_name, college_id, bus_number, seat_number):
    """
    Generates a high-quality QR code for the bus pass and saves it as PNG in static/qr_codes.
    Returns the relative path suitable for <img> tags.
    """
    qr_dir = os.path.join(current_app.root_path, 'static', 'qr_codes')
    os.makedirs(qr_dir, exist_ok=True)
    
    filename = f"{pass_id}.png"
    filepath = os.path.join(qr_dir, filename)

    payload = (
        f"COLLEGE BUS PASS\n"
        f"Pass ID: {pass_id}\n"
        f"Student: {student_name}\n"
        f"College ID: {college_id}\n"
        f"Bus: {bus_number}\n"
        f"Seat: {seat_number}\n"
        f"Status: VALID / VERIFIED"
    )

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=3,
    )
    qr.add_data(payload)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#0d47a1", back_color="white")
    img.save(filepath)

    return f"qr_codes/{filename}"

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate approximate distance in kilometers between two GPS coordinates."""
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return 0.0
    R = 6371.0 # Earth's radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2.0) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)
