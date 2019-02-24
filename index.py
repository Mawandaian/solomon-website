from flask import Flask, session, g, request, redirect, url_for, render_template, json, jsonify
from functools import wraps
import datetime
from sqlalchemy import create_engine  
from sqlalchemy import Column, String, Integer, DateTime, JSON  
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import sessionmaker
import time
import os.path

db_string = "postgres://postgres:Kitekuma@localhost:5432/solomon_db"

db = create_engine(db_string)  
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
    destination_packages = Column(JSON)
    time_stamp = Column(DateTime, default=datetime.datetime.utcnow)

class Package(base):
    __tablename__ = 'package'

    package_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    duration = Column(String)
    expiry_date = Column(String)
    price = Column(String)
    deposit = Column(String)
    destination_id = Column(String)
    details = Column(String)
    photo = Column(JSON)
    itinerary = Column(JSON)
    active = Column(String)
    time_stamp = Column(DateTime, default=datetime.datetime.utcnow)

class Users(base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String)
    password = Column(String)


class Photos(base):
    __tablename__ = 'photos'

    photo_id = Column(Integer, primary_key=True, autoincrement=True)
    photo = Column(String)
    time_stamp = Column(DateTime, default=datetime.datetime.utcnow)


Session = sessionmaker(db)  
db_session = Session()

base.metadata.create_all(db)

# Create 
bookings = Bookings()  
#db_session.add(bookings)  

destination = Destination()
#db_session.add(destination)

package = Package()
#db_session.add(package)

# users = Users(username="mawazvol", password="1234")
users = Users()
#db_session.add(users)

photos = Photos()
#db_session.add(photos)

db_session.commit()

#################################################################################

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def root_dir():  # pragma: no cover
    return os.path.abspath(os.path.dirname(__file__))

def create_image_from_datauri(data_uri, image_name):
    from base64 import b64decode
    
    header, encoded = data_uri.split(",", 1)
    data = b64decode(encoded)
    
    with open("{}/static/real_images/{}.jpeg".format(root_dir(), image_name), "wb") as f:
        f.write(data)
    

def create_image_thumbnail(image_path, image_name):
    import glob
    from PIL import Image

    image_file = "{}real_images/{}.jpeg".format(image_path, image_name)
    # get all the jpg files from the current folder
    for infile in glob.glob("{}".format(image_file)):
        im = Image.open(infile)
        # convert to thumbnail image
        im.thumbnail((128, 128), Image.ANTIALIAS)
        # don't save if thumbnail already exists
        if infile[0:2] != "T_":
            # prefix thumbnail file with T_
            im.save("{}thumbnails/T_{}.jpeg".format(image_path, image_name), "JPEG")

def get_all_destinations():
    querys = db_session.query(Destination).all()
    destination_dictionary = {}

    for query in querys:
        destination_dictionary.update({query.destination_id : query.destination_name})
    
    return destination_dictionary


app = Flask(__name__)
# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        POST_USERNAME = str(request.form['username'])
        POST_PASSWORD = str(request.form['password'])

        query = db_session.query(Users).filter(Users.username.in_([POST_USERNAME]), Users.password.in_([POST_PASSWORD]) )
        result = query.first()
        if result:
            session['logged_in'] = True
            session['user_id'] = result.user_id
            return redirect(url_for('administrator_home'))
        else:
            error = 'Invalid Credentials. Please try again.'
        
    return render_template('administrator_login.html', error=error)

@app.route('/administrator_home')
@login_required
def administrator_home():
    error = None
    return render_template('administrator_home.html', error=error, post_package='post_package', destinations=get_all_destinations())

@app.route('/post_package', methods=['GET', 'POST'])
@login_required
def post_package():
    error = None
    
    if request.method == 'POST':
        package_name = str(request.form['package_name'])
        package_duration = str(request.form['duration'])
        package_price = str(request.form['price'])
        package_destination = str(request.form['destination'])
        package_details = str(request.form['details'])
        package_photo_counter = int(request.form['photo_counter'])

        photo_ids = []

        # for photo in range(0, package_photo_counter):
        #     package_photo_data_uri = request.form['photo_data_uri_1']
        #     photos = Photos(photo=package_photo_data_uri)
        #     db_session.add(photos)
        #     db_session.flush()
        #     db_session.refresh(photos)
        #     photo_ids.append(photos.photo_id)

        package = Package(name=package_name, duration=package_duration, price=package_price, destination_id=package_destination, details=package_details, photo=photo_ids)
        db_session.add(package)

        db_session.commit()
        
    return render_template('administrator_home.html', error=error, post_package='post_package', destinations=get_all_destinations())


@app.route('/receive_destination', methods=['GET', 'POST'])
@login_required
def receive_destination():
    error = None
    
    if request.method == 'POST':
        new_destination_name = str(request.form['new_destination'])
        photo_data_uri = str(request.form['photo_data_uri'])
        
        timestamp = time.time()

        create_image_from_datauri(photo_data_uri, timestamp)
        create_image_thumbnail("{}/static/".format(root_dir()), timestamp)

        destination = Destination(destination_name=new_destination_name, destination_image=timestamp)
        db_session.add(destination)
        db_session.commit()
        
    return render_template('administrator_home.html', error=error, post_package='post_package', destinations=get_all_destinations())

@app.route('/receive_blob', methods=['GET', 'POST'])
def receive_blob():
    if request.method == 'POST':
        package_name = str(request.form['package_name'])
        package_duration = str(request.form['duration'])
        package_price = str(request.form['price'])
        package_destination = str(request.form['destination'])
        package_expiry_date = str(request.form['expiry_date'])
        package_details = str(request.form['details'])
        package_photo_counter = int(request.form['photo_counter'])

        photo_data = {}  
        photo_data['photos'] = [] 

        package_itinerary = {}
        package_itinerary['itinerary'] = [] 
        

        itinerary_package_photo_counter = int(request.form['itinerary_counter'])

        photo = request.form.getlist('photos[]')

        dict = request.form
        for key in dict:
            range_limit = package_photo_counter + 1
            for x in range(1, range_limit):
                if key == 'photo{}'.format(x):
                    data_uri = dict[key]
                    #Assuming server does not return same timestamp
                    timestamp = time.time()

                    create_image_from_datauri(data_uri, timestamp)
                    create_image_thumbnail("{}/static/".format(root_dir()), timestamp)

                    photo_data['photos'].append({  
                        'photo_name': '{}'.format(timestamp)
                    })

            # Itinerary section
            itinerary_range_limit = itinerary_package_photo_counter + 1
            for x in range(1, itinerary_range_limit):
                if key == 'itinerary_photo{}'.format(x):
                    itinerary_data_uri = dict['itinerary_photo{}'.format(x)]
                    itinerary_title = str(dict['itinerary_title{}'.format(x)])
                    itinerary_details = str(dict['itinerary_details{}'.format(x)])

                    timestamp = time.time()

                    create_image_from_datauri(itinerary_data_uri, timestamp)
                    create_image_thumbnail("{}/static/".format(root_dir()), timestamp)

                    package_itinerary['itinerary'].append({
                        'itinerary_title': itinerary_title,
                        'itinerary_details': itinerary_details,
                        'itinerary_photo' : '{}'.format(timestamp)
                    })

        package = Package(name=package_name, duration=package_duration, expiry_date=package_expiry_date, price=package_price, destination_id=package_destination, details=package_details, photo=photo_data, itinerary=package_itinerary, active="True")
        db_session.add(package)

        db_session.commit()

        return 'blob received'
    print('blob not received')
    return 'blob not received'


@app.route('/get_packages')
def get_packages():
    # package_query = db_session.query(Package).order_by(Package.name).all();
    package_query = db_session.query(Package).order_by(Package.package_id).all();
    packages_array = [];
    for package in package_query:
        x = {
            "package_id": package.package_id,
            "name": package.name,
            "duration": package.duration,
            "expiry_date": package.expiry_date,
            "price": package.price,
            "deposit": package.deposit,
            "destination_id": package.destination_id,
            "details": package.details,
            "photo": package.photo,
            "itinerary": package.itinerary,
            "active": package.active,
            "time_stamp": package.time_stamp
            }
        packages_array.append(x)
    
    print(packages_array)

    return jsonify(packages_array);

@app.route('/')
def home():
    error = None
    return render_template('home.html', error=error, post_package='post_package', destinations=get_all_destinations())

@app.route('/modal')
def modal():
    error = None
    return render_template('modal.html', error=error, post_package='post_package', destinations=get_all_destinations())


@app.route('/pop')
def popit():
    session.pop('user_id', None)
    return 'Session popped';

if __name__=='__main__':
    app.debug = True
    app.run(host='0.0.0.0')
