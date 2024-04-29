from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import login_user, login_required, logout_user, current_user
from models import TeamMember,db, Contact, Listing, Resident, Service, Payment, Notification, Lease, ListingImage, Chatbot
from werkzeug.utils import secure_filename
import os
from flask_login import LoginManager
from datetime import datetime
from sqlalchemy import extract

from datetime import timedelta
from sqlalchemy import not_, or_


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:sai123@localhost:3306/Property_management'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'sai123'
    db.init_app(app)

    with app.app_context():
        db.create_all()

    # Initialize Flask-Login
    login_manager = LoginManager(app)
    login_manager.login_view = 'login'  # 'login' should be the endpoint for your login route

    @login_manager.user_loader
    def load_user(user_id):
        # Assuming the user_id is the user's ID as a string
        return Resident.query.get(int(user_id))

    return app

app = create_app()




@app.route('/')
def home():
    return render_template('index.html', listings = Listing.query.all(), chatbots=Chatbot.query.all() )

@app.route('/contact' , methods=['GET', 'POST'])
def contact():    
    if request.method == 'POST':

        first_name = request.form['firstName']
        last_name = request.form['lastName']
        email = request.form['email']
        subject = request.form['subject']
        message = request.form['message']
        try:
            contact = Contact(first_name=first_name, last_name=last_name, email=email, subject=subject, message=message)
            db.session.add(contact)
            db.session.commit()
            message = "Request succesfully submitted !"
        except Exception as e:
            message = "Error raising request. Please try Again."

        return render_template('contact.html', message = message)

    else:
        return render_template('contact.html')


@app.route('/team', methods=['GET', 'POST'])
def team():
    try:
        team_members = TeamMember.query.all()
        print("Team Members:", team_members) 
        return render_template('team.html', team_members=team_members)
    except Exception as e:
        print("Error fetching team members:", str(e))
        return "Error fetching team members"

@app.route('/about')
def about():    
    return render_template('about.html')

@app.route('/resident', methods=['GET', 'POST'])
def resident():
    if request.method == 'GET':
        return render_template('residents_login.html')
    elif request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        resident = Resident.query.filter_by(email=email, password=password).first()
        if resident:
            login_user(resident)  
            if resident.resident_type == 'employee':
                return render_template('admin_home.html', resident=resident)
            elif resident.resident_type == 'applicant':
                return render_template('applicant_home.html', resident=resident)
            else: 
                return render_template('residents_home.html', resident=resident)
        else:
            message = "Invalid email or password. Please try again."
            return render_template('residents_login.html', message=message)



    
@app.route('/registration', methods=['GET', 'POST'])
def registration():  
    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone_number = request.form['phone_number']
        address = request.form['address']
        resident_type = "applicant"

        existing_resident = Resident.query.filter_by(email=email).first()
        if existing_resident:
            message = "Email already exists. Please choose a different email."
            return render_template('applicant_register.html', message=message)
        

        # Create a new Resident object
        new_resident = Resident(email=email, password=password, first_name=first_name,
                                last_name=last_name, phone_number=phone_number,
                                address=address, resident_type=resident_type)
        print(new_resident)
        # Add the new resident to the database
        db.session.add(new_resident)
        db.session.commit()
        message = "Account created Succesfully !"
   
        # Redirect to a page after successful registration
        return render_template('applicant_register.html', message=message)  

    # Render the registration form template for GET requests
    return render_template('applicant_register.html')  

@app.route('/forgotpassword', methods=['GET', 'POST'])
def forgotpassword():    
    return render_template('forgotpassword.html')


@app.route('/resident_lease_details', methods=['GET', 'POST'])
@login_required
def resident_lease_details():
    query = Lease.query
    query = query.filter_by(email=current_user.email)
    leases = query.all()
    return render_template('resident_lease_details.html', leases=leases)


@app.route('/resident_lease', methods=['GET', 'POST'])
@login_required
def resident_lease():
    if request.method == 'POST':
        property_address = request.form['propertyAddress']
        lease_type = request.form['leaseType']
        lease_start_date = request.form['leaseStartDate']
        application_fee = request.form['applicationFee']
        applicant_full_name = request.form['applicantFullName']
        ssn = request.form['ssn']
        dob = request.form['dob']
        phone_numbers = request.form['phoneNumbers']
        email = request.form['email']
        photo_id = request.form['photoID']
        id_number = request.form['idNumber']
        additional_occupants = request.form['additionalOccupants']
        signature = request.form['signature']


        listing = Listing.query.filter_by(property_address=property_address).first()
        property_type = listing.property_type
        description_parts = listing.description.split(',')
        beds = description_parts[0]
        baths = description_parts[1]
        long_description = listing.long_description
        appliances = listing.appliances
        amenities = listing.amenities 
        monthly_rent = listing.price


        # File upload handling for lease document
        lease_start_date = datetime.strptime(lease_start_date, '%Y-%m-%d')
        if lease_type == "halfyear":
            lease_end_date = lease_start_date + timedelta(days=6*30)
        elif lease_type == "fullyear":
            lease_end_date = lease_start_date + timedelta(days=12*30)

        if 'leaseDocument' in request.files:
                        # Get the current directory where the app.py file resides
            current_directory = os.path.dirname(os.path.abspath(__file__))

            # Define the uploads folder path
            uploads_folder = os.path.join(current_directory, 'uploads')

            # Create the uploads folder if it doesn't exist
            if not os.path.exists(uploads_folder):
                os.makedirs(uploads_folder)

            # Update the UPLOAD_FOLDER configuration variable
            app.config['UPLOAD_FOLDER'] = uploads_folder

            lease_document = request.files['leaseDocument']
            filename = secure_filename(current_user.email + '_' + property_address + '_' + lease_document.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            # Save the file to the defined path
            lease_document.save(file_path)

        else:
            lease_document = None
        
        new_lease = Lease(
            property_type=property_type,
            property_address=property_address,
            beds=beds,
            baths=baths,
            long_description=long_description,
            lease_type=lease_type,
            lease_start_date=lease_start_date,
            lease_end_date=lease_end_date,
            appliances=appliances,
            amenities=amenities,
            monthly_rent=monthly_rent,
            application_fee=application_fee,
            applicant_full_name=applicant_full_name,
            ssn=ssn,
            dob=dob,
            phone_numbers=phone_numbers,
            email=email,
            photo_id=photo_id,
            id_number=id_number,
            additional_occupants=additional_occupants,
            signature=signature,
            lease_document=file_path
        )

        # Add the new lease to the database
        db.session.add(new_lease)
        db.session.commit()
        listings = Listing.query.all()
        return render_template('resident_lease.html',listings=listings, message="Lease Agreement submitted Successfully !")
    else:
        listings = Listing.query.all()

        return render_template('resident_lease.html', listings=listings)



@app.route('/resident_lease_extend', methods=['GET', 'POST'])
@login_required
def resident_lease_extend():
    lease = Lease.query.filter_by(email=current_user.email).order_by(Lease.id.desc()).first()

    if request.method == 'POST':
        if lease.lease_end_date > (datetime.now() + timedelta(days=30)).date():
            return render_template('resident_lease_extend.html', listing=lease, message=f"Please submit your extension one month before the end date!")
        property_address = request.form['propertyAddress']
        lease_type = request.form['leaseType']
        lease_start_date = request.form['leaseStartDate']

        listing = Listing.query.filter_by(property_address=property_address).first()
        property_type = listing.property_type
        description_parts = listing.description.split(',')
        beds = description_parts[0]
        baths = description_parts[1]
        long_description = listing.long_description
        appliances = listing.appliances
        amenities = listing.amenities 
        monthly_rent = listing.price

        application_fee = request.form['applicationFee']
        applicant_full_name = request.form['applicantFullName']
        ssn = request.form['ssn']
        dob = request.form['dob']
        phone_numbers = request.form['phoneNumbers']
        email = request.form['email']
        photo_id = request.form['photoID']
        id_number = request.form['idNumber']
        additional_occupants = request.form['additionalOccupants']
        signature = request.form['signature']


        # File upload handling for lease document
        lease_start_date = datetime.strptime(lease_start_date, '%Y-%m-%d')
        if lease_type == "halfyear":
            lease_end_date = lease_start_date + timedelta(days=6*30)
        elif lease_type == "fullyear":
            lease_end_date = lease_start_date + timedelta(days=12*30)

        if 'leaseDocument' in request.files:
                        # Get the current directory where the app.py file resides
            current_directory = os.path.dirname(os.path.abspath(__file__))

            # Define the uploads folder path
            uploads_folder = os.path.join(current_directory, 'uploads')

            # Create the uploads folder if it doesn't exist
            if not os.path.exists(uploads_folder):
                os.makedirs(uploads_folder)

            # Update the UPLOAD_FOLDER configuration variable
            app.config['UPLOAD_FOLDER'] = uploads_folder

            lease_document = request.files['leaseDocument']
            filename = secure_filename(current_user.email + '_' + property_address + '_' + 'extension' + '_' + lease_document.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            # Save the file to the defined path
            lease_document.save(file_path)

        else:
            lease_document = None

        new_lease = Lease(
            property_type=property_type,
            property_address=property_address,
            beds=beds,
            baths=baths,
            long_description=long_description,
            lease_type=lease_type,
            lease_start_date=lease_start_date,
            lease_end_date=lease_end_date,
            appliances=appliances,
            amenities=amenities,
            monthly_rent=monthly_rent,
            application_fee=application_fee,
            applicant_full_name=applicant_full_name,
            ssn=ssn,
            dob=dob,
            phone_numbers=phone_numbers,
            email=email,
            photo_id=photo_id,
            id_number=id_number,
            additional_occupants=additional_occupants,
            signature=signature,
            status="extend",
            lease_document=file_path
        )

        # Add the new lease to the database
        db.session.add(new_lease)

        db.session.commit()
        return render_template('resident_lease_extend.html',listing=lease, message="Lease Agreement submitted Successfully !")
    else:
        return render_template('resident_lease_extend.html', listing=lease)




@app.route('/resident_service_requests', methods=['GET', 'POST'])
@login_required
def resident_service_requests():
    if request.method == 'POST':
        email = current_user.email
        resident = Resident.query.filter_by(email=email).first()
        subject = request.form['subject']
        message = request.form['message']

        service_request = Service(
                    first_name=resident.first_name,
                    last_name=resident.last_name,
                    email=resident.email,
                    address=resident.address,
                    phone_number=resident.phone_number,
                    resident_type=resident.resident_type,
                    subject=subject,
                    message=message,
                    application_id=current_user.application_id,
                    status="pending"
                )

        db.session.add(service_request)
        db.session.commit()
        message = "Request successfully submitted!"

        return render_template('resident_service_request.html', message=message)
    else:
        return render_template('resident_service_request.html')



@app.route('/resident_service_requests_details', methods=['GET', 'POST'])
@login_required
def resident_service_requests_details():
    email = current_user.email
    service_requests = Service.query.filter_by(email=email)
    return render_template('resident_service_request_details.html', service_requests=service_requests)


from datetime import datetime
from sqlalchemy import extract

@app.route('/resident_pay_bill', methods=['GET', 'POST'])
@login_required
def resident_pay_bill():
    listing = Listing.query.filter_by(property_address=current_user.address).first()

    if listing is None:
        return render_template('resident_pay_bill.html', message="No listing found for the specified address.")

    amount = listing.price

    if request.method == 'POST':
        # Check if there is already a payment for the current month
        current_month_payments = Payment.query.filter(
            extract('year', Payment.timestamp) == datetime.utcnow().year,
            extract('month', Payment.timestamp) == datetime.utcnow().month,
            Payment.user_id == current_user.application_id
        ).all()

        if current_month_payments:
            # Payment for this month has already been placed
            return render_template('resident_pay_bill.html', message="Payment for this month's rent has already been placed. This payment will not process.")


        card_number = request.form['card_number']
        expiry_date = request.form['expiry_date']
        cvv = request.form['cvv']

        
        # Save payment details to your database
        payment = Payment(amount=amount, user_id=current_user.application_id, user_address=current_user.address, 
                          card_token = card_number, 
                          timestamp=datetime.utcnow())
        db.session.add(payment)
        db.session.commit()

        return render_template('resident_pay_bill.html', message="Payment have been successfully placed.")

    return render_template('resident_pay_bill.html', amount=amount)




@app.route('/resident_pay_bill_details', methods=['GET', 'POST'])
@login_required
def resident_pay_bill_details():
 
    payment_details = Payment.query.filter_by(user_id=current_user.application_id)
    return render_template('resident_pay_bill_details.html', payment_details=payment_details)



@app.route('/resident_notifications', methods=['GET', 'POST'])
@login_required
def resident_notifications():
    email = current_user.email
    notifications = Notification.query.filter(or_(Notification.resident_email == email, Notification.resident_email == "all")).all()
    return render_template('resident_notifications.html', notifications=notifications)

@app.route('/resident_notification_details/<int:notification_id>', methods=['GET', 'POST'])
@login_required
def resident_notification_details(notification_id):
    notifications = Notification.query.get_or_404(notification_id)
    return render_template('resident_notifications_details.html', notifications=notifications)

@app.route('/lease')
def lease():    
    return render_template('lease.html')

@app.route('/show_property')
def show_property():    
    return render_template('show_property.html')

@app.route('/listings', methods=['GET', 'POST'])
def listings():
    # Get all available listings
    all_listings = Listing.query.all()

    # Get unique counties, states, and countries for filter options
    counties = set(listing.county for listing in all_listings)
    states = set(listing.state for listing in all_listings)
    countries = set(listing.country for listing in all_listings)

    if request.method == 'POST':
        # If it's a POST request, retrieve filter values from the form
        filter_county = request.form.get('county-filter', '')
        filter_state = request.form.get('state-filter', '')
        filter_country = request.form.get('country-filter', '')

        # Filter listings based on the selected filters
        filtered_listings = [
            listing for listing in all_listings
            if (not filter_county or listing.county == filter_county) and
               (not filter_state or listing.state == filter_state) and
               (not filter_country or listing.country == filter_country)
        ]
    else:
        # If it's a GET request, display all listings
        filtered_listings = all_listings
        filter_county = ''
        filter_state = ''
        filter_country = ''

    return render_template('listings.html', listings=filtered_listings,
                           counties=counties, states=states, countries=countries,
                           filter_county=filter_county, filter_state=filter_state,
                           filter_country=filter_country)

@app.route('/listing_details/<int:listing_id>')
def listing_details(listing_id):
    
    listing = Listing.query.get(listing_id)
    
    if listing:
        return render_template('listings_details.html', listing=listing)
    else:
        return render_template('listings.html', message="Listing not found.")

@app.route('/login_home', methods=['GET', 'POST'])
@login_required
def login_home():
    resident = Resident.query.filter_by(email=current_user.email).first()
    if resident.resident_type == 'employee':
         return render_template('admin_home.html', resident=resident)
    elif resident.resident_type == 'resident':

        return render_template('residents_home.html', resident=resident)
    elif resident.resident_type == 'applicant':
        return render_template('applicant_home.html', resident=resident)

from sqlalchemy import not_
@app.route('/applicant_lease_details', methods=['GET', 'POST'])
@login_required
def applicant_lease_details():
    query = Lease.query
    query = query.filter_by(email=current_user.email, status="pending")
    leases = query.all()

    return render_template('applicant_lease_details.html', leases=leases)


@app.route('/applicant_lease', methods=['GET', 'POST'])
@login_required
def applicant_lease():
    if request.method == 'POST':

        property_address = request.form['propertyAddress']
        lease_type = request.form['leaseType']
        lease_start_date = request.form['leaseStartDate']
        application_fee = request.form['applicationFee']
        applicant_full_name = request.form['applicantFullName']
        ssn = request.form['ssn']
        dob = request.form['dob']
        phone_numbers = request.form['phoneNumbers']
        email = request.form['email']
        photo_id = request.form['photoID']
        id_number = request.form['idNumber']
        additional_occupants = request.form['additionalOccupants']
        signature = request.form['signature']


        listing = Listing.query.filter_by(property_address=property_address).first()
        property_type = listing.property_type
        description_parts = listing.description.split(',')
        beds = description_parts[0]
        baths = description_parts[1]
        long_description = listing.long_description
        appliances = listing.appliances
        amenities = listing.amenities 
        monthly_rent = listing.price


        # File upload handling for lease document
        lease_start_date = datetime.strptime(lease_start_date, '%Y-%m-%d')
        if lease_type == "halfyear":
            lease_end_date = lease_start_date + timedelta(days=6*30)
        elif lease_type == "fullyear":
            lease_end_date = lease_start_date + timedelta(days=12*30)

        if 'leaseDocument' in request.files:
                        # Get the current directory where the app.py file resides
            current_directory = os.path.dirname(os.path.abspath(__file__))

            # Define the uploads folder path
            uploads_folder = os.path.join(current_directory, 'uploads')

            # Create the uploads folder if it doesn't exist
            if not os.path.exists(uploads_folder):
                os.makedirs(uploads_folder)

            # Update the UPLOAD_FOLDER configuration variable
            app.config['UPLOAD_FOLDER'] = uploads_folder

            lease_document = request.files['leaseDocument']
            filename = secure_filename(current_user.email + '_' + property_address + '_' + lease_document.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            # Save the file to the defined path
            lease_document.save(file_path)

        else:
            lease_document = None
        
        new_lease = Lease(
            property_type=property_type,
            property_address=property_address,
            beds=beds,
            baths=baths,
            long_description=long_description,
            lease_type=lease_type,
            lease_start_date=lease_start_date,
            lease_end_date=lease_end_date,
            appliances=appliances,
            amenities=amenities,
            monthly_rent=monthly_rent,
            application_fee=application_fee,
            applicant_full_name=applicant_full_name,
            ssn=ssn,
            dob=dob,
            phone_numbers=phone_numbers,
            email=email,
            photo_id=photo_id,
            id_number=id_number,
            additional_occupants=additional_occupants,
            signature=signature,
            lease_document=file_path
        )

        # Add the new lease to the database
        db.session.add(new_lease)
        db.session.commit()
        listings = Listing.query.all()
        return render_template('applicant_lease.html',listings=listings, message="Lease Agreement submitted Successfully !")
    else:
        listings = Listing.query.all()

        return render_template('applicant_lease.html', listings=listings)


@app.route('/admin_payments', methods=['GET', 'POST'])
@login_required
def admin_payments():
    if request.method == 'POST':
        user_id_filter = request.form['user_id']
        user_address_filter = request.form['user_address']

        # Apply filters if provided
        query = Payment.query
        if user_id_filter:
            query = query.filter_by(user_id=user_id_filter)
        if user_address_filter:
            query = query.filter_by(user_address=user_address_filter)

        payment_details = query.all()
        
    else:
        payment_details = Payment.query.all()
        
    return render_template('admin_payments.html', payment_details=payment_details)
    
@app.route('/admin_service_requests', methods=['GET', 'POST'])
@login_required
def admin_service_requests():
    if request.method == 'POST':
        user_id_filter = request.form['user_id']
        user_address_filter = request.form['user_address']

        # Apply filters if provided
        query = Service.query
        if user_id_filter:
            query = query.filter_by(application_id=user_id_filter)
        if user_address_filter:
            query = query.filter_by(address=user_address_filter)

        service_requests = query.all()
        old_service_requests = Service.query.filter(not_(or_(Service.status == "in-progress", Service.status == "pending"))).all() 
    else:
        service_requests = Service.query.filter(or_(Service.status == "in-progress", Service.status == "pending")).all()
        old_service_requests = Service.query.filter(not_(or_(Service.status == "in-progress", Service.status == "pending"))).all() 

    return render_template('admin_service_request.html', service_requests=service_requests, old_service_requests=old_service_requests)

@app.route('/progress_service/<int:request_id>', methods=['POST'])
@login_required
def progress_service(request_id):
    service = Service.query.get_or_404(request_id)
    service.status = 'in-progress'
    db.session.commit()
   
    service_requests = Service.query.filter(or_(Service.status == "in-progress", Service.status == "pending")).all()
    old_service_requests = Service.query.filter(not_(or_(Service.status == "in-progress", Service.status == "pending"))).all() 

    return render_template('admin_service_request.html', service_requests=service_requests, old_service_requests=old_service_requests)
   

@app.route('/close_service/<int:request_id>', methods=['POST'])
@login_required
def close_service(request_id):
    service = Service.query.get_or_404(request_id)
    service.status = 'closed'
    db.session.commit()
    service_requests = Service.query.filter(or_(Service.status == "in-progress", Service.status == "pending")).all()
    old_service_requests = Service.query.filter(not_(or_(Service.status == "in-progress", Service.status == "pending"))).all() 

    return render_template('admin_service_request.html', service_requests=service_requests, old_service_requests=old_service_requests)




@app.route('/admin_notifications', methods=['GET', 'POST'])
@login_required
def admin_notifications():
    if request.method == 'POST':
        subject = request.form['subject']
        message = request.form['message']
        send_to = request.form['send_to']

        if send_to == "all":
            new_notification = Notification(
                    resident_email=send_to,  # Set email from resident
                    sent_email = current_user.email,
                    subject=subject,
                    message=message
            )

        else:
            new_notification = Notification(
                    resident_email=send_to,  # Set email from resident
                    sent_email = current_user.email,
                    subject=subject,
                    message=message,
            )       

        db.session.add(new_notification)
        db.session.commit()
        message = "Notification sent succesfully !"
        return render_template('admin_notifications.html', message=message)

    residents = Resident.query.all()
    return render_template('admin_notifications.html',residents=residents)


@app.route('/admin_notifications_display', methods=['GET', 'POST'])
@login_required
def admin_notifications_display():
    notifications = Notification.query.filter_by(sent_email=current_user.email)
    return render_template('admin_notifications_display.html', notifications=notifications)


@app.route('/admin_notification_page/<int:notification_id>', methods=['POST'])
@login_required
def admin_notification_page(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    return render_template('admin_notification_page.html', notification=notification)

@app.route('/admin_queries')
@login_required
def admin_queries():
    contacts = Contact.query.all()
    return render_template('admin_queries.html', contacts=contacts)

@app.route('/admin_lease_details', methods=['GET', 'POST'])
@login_required
def admin_lease_details():
    if request.method == 'POST':
        user_id_filter = request.form['user_id']
        user_address_filter = request.form['user_address']

        # Apply filters if provided
        query = Lease.query
        if user_id_filter:
            query = query.filter_by(id=user_id_filter)
        if user_address_filter:
            query = query.filter_by(property_address=user_address_filter)

        leases = query.all()

        leases1 = Lease.query.filter(not_(or_(Lease.status == "pending", Lease.status == "extend"))).all()

    else:
       # All leases with status pending or extend
        leases = Lease.query.filter(or_(Lease.status == "pending", Lease.status == "extend")).all()
 
        leases1 = Lease.query.filter(not_(or_(Lease.status == "pending", Lease.status == "extend"))).all()
    
    return render_template('admin_lease.html', leases=leases, all_leases=leases1)

from flask import send_file

@app.route('/download_lease_document/<int:lease_id>',  methods=['GET', 'POST'])
@login_required  # Optional: Protect the download route if needed
def download_lease_document(lease_id):
    if lease_id == 0:
        current_directory = os.path.dirname(os.path.abspath(__file__)) +  '\lease.pdf'
        return send_file(current_directory, as_attachment=True)
    else:
        lease = Lease.query.get_or_404(lease_id)
        if lease.lease_document:
            return send_file(lease.lease_document, as_attachment=True)
        else:
            return redirect(url_for('admin_lease_details'))


@app.route('/approve_lease/<int:lease_id>', methods=['POST'])
@login_required
def approve_lease(lease_id):
    lease = Lease.query.get_or_404(lease_id)
    if lease.status == "pending":
        lease.status = 'approved'
        db.session.commit()

        resident = Resident.query.filter_by(email=lease.email).first()
        if resident:
            resident.application_id = lease.id
            resident.phone_number = lease.phone_numbers
            resident.address = lease.property_address
            resident.resident_type = 'resident'
            db.session.commit()

        listing = Listing.query.filter_by(property_address=lease.property_address).first()
        if listing:
            listing.status = 'Occupied'
            db.session.commit()
    elif lease.status == "extend":
        lease.status = 'approved'
        db.session.commit()

        old_lease = Lease.query.filter_by(email=current_user.email).filter(not_(Lease.id == lease_id)).first()
        old_lease.status = 'end lease'
        db.session.commit()
    
    return redirect(url_for('admin_lease_details'))

@app.route('/reject_lease/<int:lease_id>', methods=['POST'])
@login_required
def reject_lease(lease_id):
    lease = Lease.query.get_or_404(lease_id)
    lease.status = 'rejected'
    db.session.commit()

    resident = Resident.query.filter_by(email=lease.email).first()
    if resident:
        resident.application_id = None
        resident.phone_number = lease.phone_numbers
        resident.address = lease.property_address
        resident.resident_type = 'applicant'
        db.session.commit()

    listing = Listing.query.filter_by(property_address=lease.property_address).first()
    if listing:
        listing.status = 'Available'
        db.session.commit()

    return redirect(url_for('admin_lease_details'))


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


from us import states
@app.route('/admin_listings', methods=['GET', 'POST'])
@login_required
def admin_listings():
    if request.method == 'POST':
        # Extract form data
        property_address = request.form['property_address']
        description = request.form['description']
        long_description = request.form['long_description']
        amenities = request.form['amenities']
        lease_length = request.form['lease_length']
        utilities = request.form['utilities']
        appliances = request.form['appliances']
        pet_policies = request.form['pet_policies']
        year_built = request.form['year_built']
        status = request.form['status']
        property_type = request.form['property_type']
        available_date = request.form['available_date']
        map_location = request.form['map_location']
        country = request.form['country']
        state = request.form['state']
        county = request.form['county']
        price = request.form['price']

        # Create a new listing object
        new_listing = Listing(
            property_address=property_address,
            description=description,
            long_description=long_description,
            amenities=amenities,
            lease_length=lease_length,
            utilities=utilities,
            appliances=appliances,
            pet_policies=pet_policies,
            year_built=year_built,
            status=status,
            property_type=property_type,
            available_date=available_date,
            map_location=map_location,
            country=country,
            state=state,
            county=county,
            price=price
        )
        UPLOAD_FOLDER = 'static'  # Define the folder where uploaded images will be stored

        # Save images
        images = request.files.getlist('images')
        image_urls = []
        for image in images:
            if image and allowed_file(image.filename):
                filename = secure_filename(image.filename)
                image.save(os.path.join(UPLOAD_FOLDER, filename))
                image_urls.append(os.path.join(UPLOAD_FOLDER, filename))
            else:
                return redirect(request.url)

                # Add the new listing to the database
        db.session.add(new_listing)
        db.session.commit()

        for url in image_urls:
            new_image = ListingImage(listing_id=new_listing.id, image_url=url)
            db.session.add(new_image)
        db.session.commit()




        countries = ['United States']
        us_states = [state.name for state in states.STATES]

        listings = Listing.query.all()
        return render_template('admin_listings.html', listings=listings, countries=countries, us_states=us_states, message="Listing Added Successfully!")
    else: 

        # countries = [country.name for country in pycountry.countries]
        countries = ['United States']
        us_states = [state.name for state in states.STATES]

        listings = Listing.query.all()
        return render_template('admin_listings.html', listings=listings, countries=countries, us_states=us_states)


@app.route('/admin_listings_details', methods=['GET', 'POST'])
@login_required
def admin_listings_details():
    if request.method == 'POST':
        user_id_filter = request.form['user_id']
        user_address_filter = request.form['user_address']

        # Apply filters if provided
        query = Listing.query
        if user_id_filter:
            query = query.filter_by(id=user_id_filter)
        if user_address_filter:
            query = query.filter_by(property_address=user_address_filter)

    listings = Listing.query.all()

    return render_template('admin_listings_details.html',  listings=listings)


@app.route('/delete_listing/<int:listing_id>', methods=['POST'])
@login_required
def delete_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)

    if listing.status == "Occupied":
        message= "Listing is assigned a Resident, it cannot be deleted."
    else:
        # Delete listing images
        listing_images = ListingImage.query.filter_by(listing_id=listing_id).all()
        for image in listing_images:
            db.session.delete(image)
        db.session.commit()

        # Delete the listing
        db.session.delete(listing)
        db.session.commit()
        message = "Listing has been successfully deleted."


    listings = Listing.query.all()
    return render_template('admin_listings_details.html', listings=listings, message=message)

@app.route('/daily_job', methods=['GET', 'POST'])
@login_required
def daily_job(): 
    return render_template('daily_job.html') 
    

@app.route('/daily_job_listings', methods=['GET', 'POST'])
@login_required
def daily_job_listings(): 
        # Get all leases
    leases = Lease.query.all()
    
    # Iterate through leases and update status if end date is less than today
    for lease in leases:
        if lease.lease_end_date < (datetime.now() + timedelta(days=30)).date():
            # Update lease status to "Closed"
            lease.status = "Closed"
            
            # Update associated listing status to "Available"
            listing = Listing.query.filter_by(id=lease.listing_id).first()
            if listing:
                listing.status = "Available"
                
    # Commit changes to the database
    db.session.commit()
    
    return render_template('daily_job.html', message="Listings Updated Successfully!")
  

@app.route('/daily_job_notifications', methods=['GET', 'POST'])
@login_required
def daily_job_notifications(): 

    new_notification = Notification(
                    resident_email="all",
                    sent_email = current_user.email,
                    subject="Remainder Residents!! Its time to pay the bill !",
                    message="Hi Residents,\t\n Hope you are doing well \n This is small remainder to remind you to pay the rent! \n Thanks, \nProperty Management",
    )       

    db.session.add(new_notification)
    db.session.commit()

    return render_template('daily_job.html', message="Notifications Sent Successfully!") 

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return render_template('index.html', listings = Listing.query.all())


if __name__ == '__main__':
    app.run(debug=True)
