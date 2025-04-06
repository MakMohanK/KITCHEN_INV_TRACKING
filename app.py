from flask import Flask, render_template, request, redirect, jsonify
import pymysql
import pytesseract
import cv2
import numpy as np
import base64
from datetime import datetime, timedelta
from utils.connect_db import get_db_connection
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add', methods=['POST'])
def add_item():
    item_name = request.form['item_name']
    description = request.form['description']
    weight = request.form['weight']
    price = request.form['price']
    mfg_date = request.form['mfg_date']
    exp_date = request.form['exp_date']
    nutritiants = request.form['nutritiants']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO inventory (Item_Name, Description, Weight, Price, Mfg_Date, Exp_Date, Nutritiants)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    ''', (item_name, description, weight, price, mfg_date, exp_date, nutritiants))
    conn.commit()
    conn.close()
    
    return redirect('/inventory')

# Function to process image and extract text
def extract_text(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)
    return text

@app.route('/ocr_page')
def ocr_page():
    return render_template('ocr_page.html')

@app.route('/inventory')
def show_inventory():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM inventory")
    items = cursor.fetchall()
    conn.close()
    return render_template('inventory.html', items=items)

@app.route('/edit/<int:item_id>')
def edit_item(item_id):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM inventory WHERE Id = %s", (item_id,))
    item = cursor.fetchone()
    conn.close()

    if not item:
        return "Item not found", 404

    return render_template('edit.html', item=item)

@app.route('/update/<int:item_id>', methods=['POST'])
def update_item(item_id):
    item_name = request.form['item_name']
    description = request.form['description']
    weight = request.form['weight']
    price = request.form['price']
    mfg_date = request.form['mfg_date']
    exp_date = request.form['exp_date']
    nutritiants = request.form['nutritiants']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE inventory
        SET Item_Name=%s, Description=%s, Weight=%s, Price=%s, Mfg_Date=%s, Exp_Date=%s, Nutritiants=%s
        WHERE Id=%s
    ''', (item_name, description, weight, price, mfg_date, exp_date, nutritiants, item_id))
    conn.commit()
    conn.close()
    
    return redirect('/inventory')

@app.route('/delete/<int:item_id>')
def delete_item(item_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventory WHERE Id = %s", (item_id,))
    conn.commit()
    conn.close()

    return redirect('/inventory')

def get_items():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM inventory")  # Adjust table name if different
    items = cursor.fetchall()
    conn.close()
    return items

@app.route('/expiring-items')
def expiring_items():
    today = datetime.today().date()
    
    # Categorizing items
    expired = []
    less_than_week = []
    less_than_month = []
    more_than_month = []
    
    for item in get_items():
        print(item)
        exp_date = item['Exp_Date']
        
        if exp_date < today:
            expired.append(item)
        elif today <= exp_date <= today + timedelta(days=7):
            less_than_week.append(item)
        elif today + timedelta(days=7) < exp_date <= today + timedelta(days=30):
            less_than_month.append(item)
        else:
            more_than_month.append(item)
        
    print(expired)
    print(less_than_week)
    print(less_than_month)
    print(more_than_month)
    
    return render_template(
        'expiring_items.html',
        expired=expired,
        less_than_week=less_than_week,
        less_than_month=less_than_month,
        more_than_month=more_than_month
    )

@app.route('/capture', methods=['POST'])
def capture():
    data = request.json['image']
    image_data = base64.b64decode(data.split(',')[1])
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'captured_image.jpg')
    with open(file_path, 'wb') as f:
        f.write(image_data)
    extracted_text = extract_text(file_path)
    return jsonify({'text': extracted_text})

@app.route('/save', methods=['POST'])
def save_data():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO inventory (Item_Name, Description, Weight, Price, Mfg_Date, Exp_Date, Nutritiants)
                 VALUES (%s, %s, %s, %s, %s, %s, %s)''', 
              (data['item_name'], data['description'], data['weight'], data['price'], data['mfg_date'], data['exp_date'], data['nutrients']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Data saved successfully'})

if __name__ == '__main__':
    app.run(debug=True)
