import datetime
from sqlalchemy import Column, String, Integer, DateTime  
from sqlalchemy.ext.declarative import declarative_base  

base = declarative_base()

class Bookings(base):
    __tablename__ = 'bookings'

    booking_id = Column(Integer, primary_key=True, autoincrement=True)
    package_id = Column(String)
    booker_email = Column(String)
    booker_phone_number = Column(String)
    booker_surname = Column(String)
    booker_firstname = Column(String)
    booker_message = Column(String)
    booking_seen = Column(String)
    booking_replied = Column(String)
    time_stamp = Column(DateTime, default=datetime.datetime.utcnow)

class Destination(base):
    __tablename__ = 'destination'

    destination_id = Column(Integer, primary_key=True, autoincrement=True)
    destination_image = Column(String)
    destination_name = Column(String)
    destination_packages = Column(String)
    time_stamp = Column(DateTime, default=datetime.datetime.utcnow)

class Package(base):
    __tablename__ = 'package'

    package_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    duration = Column(String)
    from_date = Column(String)
    price = Column(String)
    deposit = Column(String)
    destination_id = Column(String)
    details = Column(String)
    photo = Column(String)
    itinerary = Column(String)
    active = Column(String)
    time_stamp = Column(DateTime, default=datetime.datetime.utcnow)

class Users(base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String)
    password = Column(String)