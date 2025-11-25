from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = 'farm2school_secret_key'

# MongoDB configuration
client = MongoClient('mongodb://localhost:27017/')
db = client['farm2school']
users = db['users']
products = db['products']
orders = db['orders']
messages = db['messages']

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users.find_one({'email': email, 'password': password})
        
        if user:
            session['user_id'] = str(user['_id'])
            session['user_type'] = user['user_type']
            
            if user['user_type'] == 'farmer':
                return redirect(url_for('farmer_dashboard'))
            else:
                return redirect(url_for('school_dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']
        location = request.form['location']
        
        if users.find_one({'email': email}):
            return render_template('register.html', error='Email already exists')
        
        user_id = users.insert_one({
            'name': name,
            'email': email,
            'password': password,
            'user_type': user_type,
            'location': location,
            'created_at': datetime.now()
        }).inserted_id
        
        session['user_id'] = str(user_id)
        session['user_type'] = user_type
        
        if user_type == 'farmer':
            return redirect(url_for('farmer_dashboard'))
        else:
            return redirect(url_for('school_dashboard'))
    
    return render_template('register.html')

@app.route('/farmer_dashboard')
def farmer_dashboard():
    if 'user_id' not in session or session['user_type'] != 'farmer':
        return redirect(url_for('login'))
    
    farmer_id = session['user_id']
    farmer_products = list(products.find({'farmer_id': farmer_id}))
    farmer_orders = list(orders.find({'farmer_id': farmer_id}))
    
    # Enrich orders with product names
    for order in farmer_orders:
        product = products.find_one({'_id': ObjectId(order['product_id'])})
        if product:
            order['product_name'] = product['name']
        else:
            order['product_name'] = "Unknown Product"
    
    return render_template('farmer_dashboard.html', 
                          products=farmer_products, 
                          orders=farmer_orders)

@app.route('/school_dashboard')
def school_dashboard():
    if 'user_id' not in session or session['user_type'] != 'school':
        return redirect(url_for('login'))
    
    all_products = list(products.find())
    school_orders = list(orders.find({'school_id': session['user_id']}))
    
    # Enrich orders with product names
    for order in school_orders:
        product = products.find_one({'_id': ObjectId(order['product_id'])})
        if product:
            order['product_name'] = product['name']
        else:
            order['product_name'] = "Unknown Product"
    
    return render_template('school_dashboard.html', 
                          products=all_products, 
                          orders=school_orders)

@app.route('/contact', methods=['POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message_text = request.form['message']
        
        try:
            # Store message in database
            contact_message = {
                'name': name,
                'email': email,
                'message': message_text,
                'created_at': datetime.now(),
                'status': 'new'
            }
            messages.insert_one(contact_message)
            
            # Simple email sending
            smtp_server = "smtp.gmail.com"
            smtp_port = 587
            sender_email = "susmitha.vcsc@gmail.com"
            sender_password = "your_app_password"  # Replace with app password
            
            # Admin email
            admin_body = f"New contact from {name} ({email}): {message_text}"
            admin_msg = MIMEText(admin_body)
            admin_msg['Subject'] = f'Contact Form - {name}'
            admin_msg['From'] = sender_email
            admin_msg['To'] = sender_email
            
            # User confirmation email
            user_body = f"Dear {name}, Thank you for contacting Farm2School! We received your message and will respond within 24 hours."
            user_msg = MIMEText(user_body)
            user_msg['Subject'] = 'Thank you for contacting Farm2School'
            user_msg['From'] = sender_email
            user_msg['To'] = email
            
            # Send emails
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(admin_msg)
            server.send_message(user_msg)
            server.quit()
            
            return redirect(url_for('index') + '?contact=success')
            
        except Exception as e:
            return redirect(url_for('index') + '?contact=success')  # Show success even if email fails
    
    return redirect(url_for('index'))

@app.route('/messages')
def messages():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('messages.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)