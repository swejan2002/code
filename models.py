from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class Contact(db.Model):
    __tablename__ = 'contacts'  # Custom table name
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), primary_key=True)
    subject = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)

class TeamMember(db.Model):
    __tablename__ = 'team_members'  # Custom table name
    name = db.Column(db.String(255), primary_key=True)
    designation = db.Column(db.String(255), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)


class Listing(db.Model):
    __tablename__ = 'listings'  # Custom table name
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    property_address = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    long_description = db.Column(db.Text, nullable=False)
    amenities = db.Column(db.String(255), nullable=False)
    lease_length = db.Column(db.String(50), nullable=False)
    utilities = db.Column(db.String(255), nullable=False)
    appliances = db.Column(db.String(255), nullable=False)
    pet_policies = db.Column(db.String(255), nullable=False)
    year_built = db.Column(db.Integer)
    images = db.relationship('ListingImage', backref='listing', lazy=True)
    status = db.Column(db.String(50), nullable=False)
    property_type = db.Column(db.String(50), nullable=False)
    available_date = db.Column(db.Date)
    map_location = db.Column(db.String(255), nullable=False)
    country = db.Column(db.String(50), nullable=False)  # Add country field
    state = db.Column(db.String(50), nullable=False)  # Add state field
    county = db.Column(db.String(50), nullable=False)  # Add county field
    price = db.Column(db.Integer)

class ListingImage(db.Model):
    __tablename__ = 'listing_images'  # Custom table name
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('listings.id'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)

class Resident(db.Model, UserMixin):
    __tablename__ = 'residents'  # Custom table name
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    application_id = db.Column(db.Integer, unique=True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    resident_type = db.Column(db.String(50), nullable=False)
    print("In")
    def is_active(self):
        # For simplicity, assuming all residents are active.
        return True

    def get_id(self):
        # Return the unique identifier for the user (e.g., user's email).
        return str(self.id)

class Service(db.Model):
    __tablename__ = 'services'  # Custom table name
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    application_id = db.Column(db.Integer, unique=True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    resident_type = db.Column(db.String(50), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending') 


class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    amount = db.Column(db.Float, nullable=False)
    card_token = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('residents.application_id'), nullable=False)
    user_address = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    resident_email = db.Column(db.String(20), nullable=False, default='all') 
    sent_email = db.Column(db.String(120))  
    subject = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)


# Define your Lease model
class Lease(db.Model):
    __tablename__ = 'leases'

    id = db.Column(db.Integer, primary_key=True)
    property_type = db.Column(db.String(50), nullable=False)
    property_address = db.Column(db.String(255), nullable=False)
    beds = db.Column(db.String(255), nullable=False)
    baths = db.Column(db.String(255), nullable=False)
    long_description = db.Column(db.Text, nullable=False)
    lease_type = db.Column(db.String(50), nullable=False)
    lease_start_date = db.Column(db.Date, nullable=False)
    lease_end_date = db.Column(db.Date, nullable=False)
    appliances = db.Column(db.String(255), nullable=False)
    amenities = db.Column(db.String(255), nullable=False)
    monthly_rent =  db.Column(db.Integer)
    application_fee = db.Column(db.Float, nullable=False)
    applicant_full_name = db.Column(db.String(100), nullable=False)
    ssn = db.Column(db.String(11), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    phone_numbers = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    photo_id = db.Column(db.String(50), nullable=False)
    id_number = db.Column(db.String(50), nullable=False)
    additional_occupants = db.Column(db.Integer, nullable=False)
    signature = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')  # Status of lease (pending/approved/rejected)
    lease_document = db.Column(db.String(255), nullable=True) 

class Chatbot(db.Model):
    __tablename__ = 'chatbot'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.String(255), nullable=False)