from flask import Flask,render_template,request,redirect,url_for,flash,session
import mysql.connector #Import the MySQL connector library for interacting with MySQL database
from datetime import datetime, timedelta

app = Flask(__name__) #Creating a Flask web application instance
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://localhost:3306/hotel_reservations' 
app.secret_key = 'alakazam' ## Set the application's secret key for session management and security

db = mysql.connector.connect( #Create a connection to the MySQL database using the provided credentials
    host="localhost", #Specifying the database host
    username="root", #Specifying the database username
    password="", #specifying the database password
)
cursor = db.cursor() #Cursor for database

database_name = 'hotel_reservations'

# Create the hotel_reservations database
try:
    cursor.execute(f"CREATE DATABASE {database_name}")
    print(f"Database '{database_name}' created successfully.")

except mysql.connector.Error as err:
    print(f"Error: {err}")

# Switch to the hotel_reservations database
cursor.execute(f"USE {database_name}")

# Table: bookings
try:
    cursor.execute("""
        CREATE TABLE bookings (
            roomid INT AUTO_INCREMENT PRIMARY KEY,
            num_rooms INT,
            checkin_date DATE,
            checkout_date DATE,
            num_guests INT,
            room_type VARCHAR(255),
            price INT,
            room_number INT
        )
    """)
    print("Table 'bookings' created successfully.")

except mysql.connector.Error as err:
    print(f"Error: {err}")

# Table: booking_confirm
try:
    cursor.execute("""
        CREATE TABLE booking_confirm (
            customer_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            surname VARCHAR(255),
            email VARCHAR(255),
            phone VARCHAR(20)
        )
    """)
    print("Table 'booking_confirm' created successfully.")

except mysql.connector.Error as err:
    print(f"Error: {err}")

# Table: users
try:
    cursor.execute("""
        CREATE TABLE users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            surname VARCHAR(255),
            telephone VARCHAR(20),
            username VARCHAR(255),
            password VARCHAR(255)
        )
    """)
    print("Table 'users' created successfully.")

except mysql.connector.Error as err:
    print(f"Error: {err}")
    
try:
    cursor.execute("""
        CREATE TABLE customer_services (
            customer_id INT AUTO_INCREMENT PRIMARY KEY,
            service VARCHAR(255)
        )                  
    """)
    print("Table 'customer_services' created successfully")
    
except mysql.connector.Error as err:
    print(f"Error: {err}")
    
@app.route('/') #Defines a route
def home(): #Function home
    countdown_time = (datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
    return render_template('home.html', countdown_time=countdown_time) #Renders to home.html template 

extra_services = [ #A list of extra services that can be selected by a user
    "Extra Pillows",
    "Extra Blankets",
    "Room Service",
    "Airport Shuttle",
    "Spa Services",
    "Dining Reservations",
]


@app.route('/dashboard', methods=['GET', 'POST']) #Defines a route that can handle GET and POST requests
def dashboard(): #Function executed when method is POST
    countdown_time = (datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
    if request.method == 'POST': 
        selected_services = request.form.getlist('selected_services') #This retrieves all the extra services selected by the customer
        customer_id = 2
    
        save_selected_services(customer_id, selected_services) #A function is called which will save the customer_id and the selected_services in the database
        
        return redirect(url_for('confirmation')) #Redirects to the confirmation url
    return render_template('dashboard.html', extra_services=extra_services, countdown_time=countdown_time) #Renders template dashboard.html

def save_selected_services(customer_id, selected_services):
        for service in selected_services:
            cursor.execute = ("INSERT INTO customer_services (customer_id, service) VALUES (%s, %s)", (customer_id, service))
        db.commit() #Commit the changes to the database

@app.route('/confirm_booking', methods=['POST'])
def confirm_booking():
    try:
        name = request.form['name'] #Get the name field from the form
        surname = request.form['surname'] #Get the surname field from the form
        email = request.form['email'] #Get the email field from the form
        phone = request.form['phone'] #Get the phone field from the form

        # Insert the form data into the 'booking_confirm' table in the database
        cursor.execute("INSERT INTO booking_confirm (name, surname, email, phone) VALUES (%s, %s, %s, %s)", (name, surname, email, phone))
        db.commit()

        # Process and save the booking details and personal information to your database

        flash('Booking confirmed!')
        return redirect(url_for('confirmation'))

    except Exception as e:
        db.rollback()
        flash(f'Error: {e}')
        return redirect(url_for('confirmation'))
    
@app.route('/confirmation') #Defines a route for handling GET requests
def confirmation(): #Function is executed when a GET request is made
    countdown_time = (datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
    return render_template('/booking_confirmed.html', countdown_time=countdown_time) #Render the booking_confirmed template


@app.route('/booking_details/<int:customer_id>/<int:roomid>')
def booking_details(customer_id, roomid):
    countdown_time = (datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
    try:
        # Retrieve customer data from the 'booking_confirm' table based on customer_id
        cursor.execute("SELECT name, surname, email, phone FROM booking_confirm WHERE customer_id = %s", (customer_id,))
        customer_data = cursor.fetchone()

        # Retrieve booking data from the 'bookings' table based on roomid
        cursor.execute("SELECT num_rooms, checkin_date, checkout_date, num_guests, room_type, price, room_number FROM bookings WHERE roomid = %s", (roomid,))
        booking_data = cursor.fetchone()

        if customer_data and booking_data:
            # Checking if both customer and booking data are found
            name, surname, email, phone = customer_data
            num_rooms, checkin_date, checkout_date, num_guests, room_type, price, room_number = booking_data

            return render_template('booking_details.html', name=name, surname=surname, email=email, phone=phone, num_rooms=num_rooms, checkin_date=checkin_date, checkout_date=checkout_date, num_guests=num_guests, room_type=room_type, price=price, room_number=room_number, countdown_time=countdown_time)
        else:
            # If data is not found then show an error message
            return "No booking data found for this customer or room."
    except mysql.connector.Error as err:
        # Handle database errors
        return f"Database error: {err}"

@app.route('/cancel_booking/<int:room_id>', methods=['GET', 'POST'])
def cancel_booking(room_id):
    countdown_time = (datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
    if request.method == 'POST':
        # Perform a database operation to cancel the booking based on booking_id
        if cancel_booking_in_database(room_id):
            flash("Booking canceled successfully.")
        else:
            flash("Failed to cancel booking. Please try again.")

        return redirect(url_for('dashboard'))

    return render_template('booking_cancel.html', countdown_time=countdown_time)

def cancel_booking_in_database(room_id):
    try:
        # Perform the database operation to cancel the booking
        query = "DELETE FROM bookings WHERE room_id = %s"
        cursor.execute(query, (room_id,))
        db.commit()
        return True
    except mysql.connector.Error as err:
        # Handle database errors 
        db.rollback()
        return False

@app.route('/booking', methods=['GET','POST']) #This line defines a route for the '/booking' URL
def booking(): #This function will be executed when a request to booking will be made
    countdown_time = (datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
    flash('Logged in successfully') #This will add a flash message indicating login successful
    
    if request.method == 'POST': #Check if the request method is POST
        
        #Get data from the submitted form for the user needs
        num_rooms = request.form['num_rooms'] 
        if not num_rooms.isdigit():
            flash("Please enter a valid number for the number of rooms.")
        else:
            num_rooms = int(num_rooms)
            if num_rooms <= 0:
                flash("Number of rooms must be greater than 0.")
            elif num_rooms > 5:
                flash("You can book up to 5 rooms maximum.")
        
        checkin_date = datetime.strptime(request.form['checkin_date'], '%Y-%m-%d')
        checkout_date = datetime.strptime(request.form['checkout_date'], '%Y-%m-%d')
        num_guests = request.form['num_guests']
        room_type = request.form['room_type']
        room_number = request.form['room_number']
            
        if checkout_date <= checkin_date:
             flash("Checkout date must be later than checkin date")
             return render_template('booking_form.html')
            
        if room_type == "Standard":
            price =  50 * num_rooms * (checkout_date - checkin_date).days
        elif room_type == "Premium":
            price =  100 * num_rooms * (checkout_date - checkin_date).days
        elif room_type == "VIP":
                price = 250 * num_rooms * (checkout_date - checkin_date).days
        
        #Print the form data for login purposes
        print(f"Number of Rooms: {num_rooms}")
        print(f"Check-In Date: {checkin_date}")
        print(f"Check-Out Date: {checkout_date}")
        print(f"Number of Guests: {num_guests}")
        print(f"Room Type: {room_type}")
        print(f"Room Price: {price}")
        print(f"Room Number: {room_number}")
        
        #Insert the form data into a database table
        cursor.execute("INSERT INTO bookings (num_rooms, checkin_date, checkout_date, num_guests, room_type, price, room_number) VALUES (%s, %s, %s, %s, %s, %s, %s)", (num_rooms, checkin_date, checkout_date, num_guests, room_type, price, room_number))
        
        db.commit() #Commit the changes to the database
        
        flash("Your booking is being proceeded") #Flash message to inform the user that the booking is in progress
        return redirect(url_for('dashboard'))
    return render_template('booking_form.html', countdown_time=countdown_time) #If the request method is GET, render the 'booking_form.html' template


@app.route('/login', methods=['GET','POST']) #This line defines a route for the '/login' URL 
def login(): #This function will be executed when a request to '/login' will be made
    countdown_time = (datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
    if request.method =='POST': #check if the request is POST
        username = request.form['username'] #check username
        password = request.form['password'] #check password of the user  
        try:
            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            #Execute SQL query to check if the username and password already exists
            user = cursor.fetchone() #Fetch result of SQL query
                
            if user:
                return redirect(url_for('booking')) #If the user is recognized then they will be redirected to the '/booking' URL 
            else:
                return "Login failed. Please check your credentials." #If the user is not recognized then they will be shown an error message
        
        except Exception as e:
            # Handle database errors
            return f"An error occurred: {e}"
        
    return render_template('login.html', countdown_time=countdown_time) #If the request method is GET then render login template

@app.route('/register', methods=['GET', 'POST']) #This line defines a route for the '/register' URL
def register(): #This function will be executed when a request to register will be made
    countdown_time = (datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
    if request.method == 'POST': #Check if request is POST
        name = request.form['name'] #check name of the user
        surname = request.form['surname'] #check surname of the user
        telephone = request.form['telephone'] #check the telephone number of the user
        username = request.form['username'] #check username of the user
        password = request.form['password'] #check password of the user
        cursor.execute("INSERT INTO users (name, surname, telephone, username, password) VALUES (%s, %s, %s, %s, %s)", (name, surname, telephone, username, password))
        #Carry an SQL query to check if any of the details already exist in the database
        db.commit()

        return redirect(url_for('login')) #If user is recognized then they will be reditrected to the login form
    return render_template('register.html', countdown_time=countdown_time) #If the request mathod is GET then render register template
        
if __name__ == '__main__':
    app.run(debug=True)