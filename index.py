from flask import Flask, session, g, request, redirect, url_for, render_template
from functools import wraps
import datetime
from sqlalchemy import create_engine  
from sqlalchemy import Column, String, Integer, DateTime  
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import sessionmaker
import time

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

def create_image_from_datauri(data_uri, image_name):
    from base64 import b64decode
    
    header, encoded = data_uri.split(",", 1)
    data = b64decode(encoded)
    
    with open("{}.jpeg".format(image_name), "wb") as f:
        f.write(data)


def create_image_thumbnail(image_name):
    import glob
    from PIL import Image
    # get all the jpg files from the current folder
    for infile in glob.glob("{}.jpeg".format(image_name)):
        im = Image.open(infile)
        # convert to thumbnail image
        im.thumbnail((128, 128), Image.ANTIALIAS)
        # don't save if thumbnail already exists
        if infile[0:2] != "T_":
            # prefix thumbnail file with T_
            im.save("T_" + infile, "JPEG")


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
    return render_template('administrator_home.html', error=error, post_package='post_package')

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
        
    return render_template('administrator_home.html', error=error, post_package='post_package')


@app.route('/receive_blob', methods=['GET', 'POST'])
def receive_blob():
    if request.method == 'POST':
        package_name = str(request.form['package_name'])
        package_duration = str(request.form['duration'])
        package_price = str(request.form['price'])
        package_destination = str(request.form['destination'])
        package_details = str(request.form['details'])
        package_photo_counter = int(request.form['photo_counter'])

        package_photo_list = []
        package_itinerary = []

        itinerary_package_photo_counter = int(request.form['itinerary_counter'])

        photo = request.form.getlist('photos[]')
        #app.logger.debug(request.files['photos']) 

        dict = request.form
        for key in dict:
            range_limit = package_photo_counter + 1
            for x in range(1, range_limit):
                if key == 'photo{}'.format(x):
                    data_uri = dict[key]
                    #Assuming server does not return same timestamp
                    timestamp = time.time()

                    create_image_from_datauri(data_uri, timestamp)
                    create_image_thumbnail(timestamp)
                    package_photo_list.append('{}'.format(timestamp))

            # Itinerary section
            itinerary_range_limit = itinerary_package_photo_counter + 1
            for x in range(1, itinerary_range_limit):
                if key == 'itinerary_photo{}'.format(x):
                    itinerary_data_uri = dict['itinerary_photo{}'.format(x)]
                    itinerary_title = str(dict['itinerary_title{}'.format(x)])
                    itinerary_details = str(dict['itinerary_details{}'.format(x)])

                    timestamp = time.time()

                    create_image_from_datauri(itinerary_data_uri, timestamp)
                    create_image_thumbnail(timestamp)
                    package_itinerary.append([itinerary_title, itinerary_details, '{}'.format(timestamp)])

        package = Package(name=package_name, duration=package_duration, from_date="", price=package_price, destination_id=package_destination, details=package_details, photo=package_photo_list, itinerary=package_itinerary, active="True")
        db_session.add(package)
        db_session.commit()

        return 'blob received'
    print('blob not received')
    return 'blob not received'


@app.route('/pop')
def popit():
    session.pop('user_id', None)
    return 'Session popped';

if __name__=='__main__':
    app.debug = True
    app.run()
