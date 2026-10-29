from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .academic_year import AcademicYear
from .route import Route
from .boarding_point import BoardingPoint
from .bus import Bus
from .driver import Driver
from .student import Student
from .seat import Seat
from .allocation import SeatAllocation
from .payment import Payment
from .bus_pass import BusPass
from .bus_location import BusLocation
