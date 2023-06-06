from flask import Flask, render_template,request
from flask_pymongo import PyMongo
from geopy.geocoders import Nominatim
import pandas as pd
import numpy as np
import pickle
import requests

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb+srv://12210071gcit:12210071gcit@cluster0.g4tmhsh.mongodb.net/your_database_name?retryWrites=true&w=majority'
mongo = PyMongo(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add')
def indexs():
    return render_template('upload.html')

@app.route('/predict',methods=['POST'])
def prediction():
    if request.method == 'POST':
        A1 = float(request.form.get('temp'))
        A2 = float(request.form.get('humi'))
        A3 = float(request.form.get('ph'))
        A4 = float(request.form.get('rain'))

        model = pickle.load(open("crop_recommendation_model.pkl", 'rb'))
        data = [[A1, A2, A3, A4]]

        x_sample = pd.DataFrame(data)

        res = model.predict_proba(x_sample)
        mean_probs = np.mean(res, axis=0)
        sorted_labels = np.argsort(mean_probs)[::-1]
        
        predicted_labels = []
        for i in range(5):
            label_idx = sorted_labels[i]
            label_name = model.classes_[label_idx]
            predicted_labels.append(label_name)
            print(label_name)
        return display(predicted_labels)
@app.route('/autopredict', methods=['POST'])
def autopredict():
    dzong = {'Thimphu':72.39,'Paro dzongkhag':71.39,'Haa dzongkhag':74,'wang dzongkhag':72,'Samdrup dzongkhag':150,'Gasa dzongkhag':70,'dagana dzongkhag':72,'Chukha dzongkhag':71.39,'samtse dzongkhag':185.42,'Tsirang dzongkhag':181,'Sarpang dzongkhag':180.8,'pemagatsel dzongkhag':180.8,'Tashigang dzongkhag':147.85,'Tashi dzongkhag':34.86,'Lhuentse dzongkhag':34.86,'Bumthang dzongkhag':70,'Zhemgang dzongkhag':180.8,'trongsa dzongkhag':23,'Mongar':71.45}

    if request.method == 'POST':
        val = request.form.get('place')
        geolocator = Nominatim(user_agent="my-app-name")
        location = geolocator.geocode(val)
        latitude = location.latitude
        longitude = location.longitude
        api_key = '63746ddd3e46493328fd256f0846aa87'

        url = f'https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}'

        response = requests.get(url)

        weather_data = response.json()

        A1 = weather_data['main']['temp']
        A2 = weather_data['main']['humidity']
        A3 = 5.56
        A4 = 0

        key_to_match = val

        for key, value in dzong.items():
            if key == key_to_match:
                A4 = value
                break
        print('hhhghg')
        model = pickle.load(open("crop_recommendation_model.pkl", 'rb'))
        data = [[A1, A2, A3, A4]]

        x_sample = pd.DataFrame(data)

        res = model.predict_proba(x_sample)
        mean_probs = np.mean(res, axis=0)
        sorted_labels = np.argsort(mean_probs)[::-1]
        
        predicted_labels = []
        for i in range(5):
            label_idx = sorted_labels[i]
            label_name = model.classes_[label_idx]
            predicted_labels.append(label_name)
            print(label_name)

        return display(predicted_labels)

@app.route('/display')
def display(name):
    names_list = name  # Split the names string into a list
    
    query = {
        'name': {'$in': names_list}  # Use the $in operator to match the names in the list
    }
    
    data = mongo.db.images.find(query, {'_id': 0})
    return render_template('search.html', data=data)

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/upload',methods=['POST'])
def upload():
    name = request.form['name']
    image = request.files['image']
    descript = request.form['descript']
    image.save('static/uploads/' + image.filename)

    image_data = {
        'name': name,
        'filename': image.filename,
        'description': descript
    }
    mongo.db.images.insert_one(image_data)

    return 'Image uploaded successfully!'

if __name__ == '__main__':
    app.run(debug=True)