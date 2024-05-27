from flask import Flask, render_template, request, session, redirect, url_for
import pandas as pd
import pickle
import numpy as np
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

conn = mysql.connector.connect(host="127.0.0.1", user="root", database="expenseapp")
cursor = conn.cursor()

# Load model and data
data = pd.read_csv('D:/Py.Files/Pune_housing_price/dataset/cleaned_data.csv')
pipe = pickle.load(open('D:/Py.Files/Pune_housing_price/models/LinearModel.pkl', 'rb'))

def predict_price(sqft, bath, balcony, location, bhk):
    input_data = pd.DataFrame([[sqft, bath, balcony, location, bhk]], columns=['total_sqft', 'bath', 'balcony', 'site_location', 'bhk'])
    prediction = pipe.predict(input_data)[0] * 1e5
    return np.round(prediction, 2)

@app.route('/')
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/register')
def register():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/home')
def home():
    if 'user_id' in session:
        return render_template('home.html')
    return redirect(url_for('login'))

@app.route('/login_validation', methods=['POST'])
def login_validation():
    email = request.form.get('email')
    password = request.form.get('password')

    cursor.execute("SELECT * FROM user WHERE email = %s AND password = %s", (email, password))
    user = cursor.fetchone()

    if user:
        session['user_id'] = user[0]
        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.form.get('uname')
    email = request.form.get('uemail')
    password = request.form.get('upassword')

    cursor.execute("INSERT INTO user (name, email, password) VALUES (%s, %s, %s)", (name, email, password))
    conn.commit()

    cursor.execute("SELECT * FROM user WHERE email = %s", (email,))
    myuser = cursor.fetchone()
    session['user_id'] = myuser[0]

    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'GET':
        locations = sorted(data['site_location'].unique())
        return render_template('index.html', locations=locations)
    
    if request.method == 'POST':
        location = request.form.get('location')
        bhk = request.form.get('bhk')
        bath = request.form.get('bath')
        sqft = request.form.get('total_sqft')
        balcony = request.form.get('balcony')

        prediction = predict_price(float(sqft), int(bath), int(balcony), location, int(bhk))
        return str(prediction * 2)

if __name__ == '__main__':
    app.run("0.0.0.0")
