from flask import Flask, render_template, request, jsonify
import pytesseract
import cv2
import numpy as np
import base64
import sqlite3
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Initialize database
def init_db():
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS product_data (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 item_name TEXT,
                 quantity TEXT,
                 mfg_date TEXT,
                 exp_date TEXT,
                 nutrients TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Function to process image and extract text
def extract_text(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)
    return text

@app.route('/')
def index():
    return render_template('index.html')

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
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute('''INSERT INTO product_data (item_name, quantity, mfg_date, exp_date, nutrients)
                 VALUES (?, ?, ?, ?, ?)''', 
              (data['item_name'], data['quantity'], data['mfg_date'], data['exp_date'], data['nutrients']))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Data saved successfully'})

if __name__ == '__main__':
    app.run(debug=True)


