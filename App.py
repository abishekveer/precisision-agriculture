from flask import Flask, render_template, flash, request, session, send_file, redirect, url_for
from werkzeug.utils import secure_filename
import datetime
import mysql.connector
import sys
import pickle
import cv2
import numpy as np
import os
import uuid
import warnings
from PIL import ImageOps, Image
import tensorflow as tf
from tensorflow.keras.preprocessing import image

warnings.filterwarnings('ignore')

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = '7d441f27d441f27567d441f2b6176a'

# --- Load Models Once ---
try:
    classifier_rfc = pickle.load(open('crop-prediction-rfc-model.pkl', 'rb'))
except Exception as e:
    print("Warning: crop-prediction-rfc-model.pkl not found", e)
    classifier_rfc = None

try:
    classifier_soil = tf.keras.models.load_model('soalmodel.h5')
except Exception as e:
    print("Warning: soalmodel.h5 not found", e)
    classifier_soil = None

try:
    classifier_leaf = tf.keras.models.load_model('lmodel.h5')
except Exception as e:
    print("Warning: lmodel.h5 not found", e)
    classifier_leaf = None

try:
    classifier_fruit = tf.keras.models.load_model('fmodel.h5')
except Exception as e:
    print("Warning: fmodel.h5 not found", e)
    classifier_fruit = None


def get_db_connection():
    return mysql.connector.connect(user='root', password='', host='localhost', database='1croprecomdb')

def sendmsg(targetno, message):
    import requests
    requests.post(
        "http://sms.creativepoint.in/api/push.json?apikey=6555c521622c1&route=transsms&sender=FSSMSS&mobileno=" + str(targetno) + "&text=Dear customer your msg is " + message + "  Sent By FSMSG FSSMSS")

@app.route("/")
def homepage():
    return render_template('index.html')

@app.route("/AdminLogin")
def AdminLogin():
    return render_template('AdminLogin.html')

@app.route("/UserLogin")
def UserLogin():
    return render_template('UserLogin.html')

@app.route("/NewUser")
def NewUser():
    return render_template('NewUser.html')

@app.route("/NewQuery1")
def NewQuery1():
    return render_template('NewQueryReg.html')

@app.route("/UploadDataset")
def UploadDataset():
    return render_template('ViewExcel.html')

@app.route("/AdminHome")
def AdminHome():
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM regtb ")
        data = cur.fetchall()
        return render_template('AdminHome.html', data=data)
    finally:
        conn.close()

@app.route("/UserHome")
def UserHome():
    user = session.get('uname')
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM regtb WHERE username=%s", (user,))
        data = cur.fetchall()
        return render_template('UserHome.html', data=data)
    finally:
        conn.close()

@app.route("/UQueryandAns")
def UQueryandAns():
    uname = session.get('uname')
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Querytb WHERE UserName=%s AND DResult='waiting'", (uname,))
        data = cur.fetchall()
        cur.execute("SELECT * FROM Querytb WHERE UserName=%s AND DResult !='waiting'", (uname,))
        data1 = cur.fetchall()
        return render_template('UserQueryAnswerinfo.html', wait=data, answ=data1)
    finally:
        conn.close()

@app.route("/adminlogin", methods=['GET', 'POST'])
def adminlogin():
    error = None
    if request.method == 'POST':
        if request.form['uname'] == 'admin' and request.form['password'] == 'admin':
            conn = get_db_connection()
            try:
                cur = conn.cursor()
                cur.execute("SELECT * FROM regtb ")
                data = cur.fetchall()
                return render_template('AdminHome.html', data=data)
            finally:
                conn.close()
        else:
            return render_template('index.html', error=error)
    return render_template('AdminLogin.html')

@app.route("/userlogin", methods=['GET', 'POST'])
def userlogin():
    if request.method == 'POST':
        username = request.form['uname']
        password = request.form['password']
        session['uname'] = username

        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM regtb WHERE username=%s AND Password=%s", (username, password))
            data = cursor.fetchone()
            if data is None:
                alert = 'Username or Password is wrong'
                return render_template('goback.html', data=alert)
            else:
                session['uid'] = data[0]
                session['mob'] = data[4]
                cursor.execute("SELECT * FROM regtb WHERE username=%s AND Password=%s", (username, password))
                data_all = cursor.fetchall()
                return render_template('UserHome.html', data=data_all)
        finally:
            conn.close()
    return render_template('UserLogin.html')

@app.route("/newuser", methods=['GET', 'POST'])
def newuser():
    if request.method == 'POST':
        name1 = request.form['name']
        gender1 = request.form['gender']
        Age = request.form['age']
        email = request.form['email']
        pnumber = request.form['phone']
        address = request.form['address']
        uname = request.form['uname']
        password = request.form['psw']

        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO regtb VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (name1, gender1, Age, email, pnumber, address, uname, password)
            )
            conn.commit()
        finally:
            conn.close()
        return render_template('UserLogin.html')
    return render_template('NewUser.html')

@app.route("/newquery", methods=['GET', 'POST'])
def newquery():
    if request.method == 'POST':
        uname = session.get('uname')
        nitrogen = request.form['nitrogen']
        phosphorus = request.form['phosphorus']
        potassium = request.form['potassium']
        temperature = request.form['temperature']
        humidity = request.form['humidity']
        ph = request.form['ph']
        rainfall = request.form['rainfall']
        location = request.form['select']

        nit = float(nitrogen)
        pho = float(phosphorus)
        po = float(potassium)
        te = float(temperature)
        hu = float(humidity)
        phh = float(ph)
        ra = float(rainfall)

        if classifier_rfc:
            data_arr = np.array([[nit, pho, po, te, hu, phh, ra]])
            my_prediction = classifier_rfc.predict(data_arr)
            print(my_prediction)
            my_prediction = my_prediction[0] if isinstance(my_prediction, np.ndarray) and len(my_prediction) > 0 else my_prediction
        else:
            my_prediction = -1

        crop = ''
        fertilizer = ''

        if my_prediction == 0:
            Answer = 'Predict'
            crop = 'rice'
            fertilizer = '4 kg of gypsum and 1 kg of DAP/cent can be applied at 10 days after sowing'
        elif my_prediction == 1:
            Answer = 'Predict'
            crop = 'maize'
            fertilizer = 'The standard fertilizer recommendation for maize consists of 150 kg ha−1 NPK 14–23–14 and 50 kg ha−1 urea'
        elif my_prediction == 2:
            Answer = 'Predict'
            crop = 'chickpea'
            fertilizer = 'The generally recommended doses for chickpea include 20–30 kg nitrogen (N) and 40–60 kg phosphorus (P) ha-1. If soils are low in potassium (K), an application of 17 to 25 kg K ha-1 is recommended'
        elif my_prediction == 3:
            Answer = 'Predict'
            crop = 'kidneybeans'
            fertilizer = 'It needs good amount of Nitrogen about 100 to 125 kg/ha'
        elif my_prediction == 4:
            Answer = 'Predict'
            crop = 'pigeonpeas'
            fertilizer = 'Apply 25 - 30 kg N, 40 - 50 k g P 2 O 5 , 30 kg K 2 O per ha area as Basal dose at the time of sowing.'
        elif my_prediction == 5:
            Answer = 'Predict'
            crop = 'mothbeans'
            fertilizer = 'The applications of 10 kg N+40 kg P2O5 per hectare have proved the effective starter dose'
        elif my_prediction == 6:
            Answer = 'Predict'
            crop = 'mungbean'
            fertilizer = 'Phosphorus and potassium fertilizers should be applied at 50-50 kg ha-1'
        elif my_prediction == 7:
            Answer = 'Predict'
            crop = 'blackgram'
            fertilizer = 'The recommended fertilizer dose for black gram is 20:40:40 kg NPK/ha.'
        elif my_prediction == 8:
            Answer = 'Predict'
            crop = 'lentil'
            fertilizer = 'The recommended dose of fertilizers is 20kg N, 40kg P, 20 kg K and 20kg S/ha.'
        elif my_prediction == 9:
            Answer = 'Predict'
            crop = 'pomegranate'
            fertilizer = 'The recommended fertiliser dose is 600–700 gm of N, 200–250 gm of P2O5 and 200–250 gm of K2O per tree per year'
        elif my_prediction == 10:
            Answer = 'Predict'
            crop = 'banana'
            fertilizer = 'Feed regularly using either 8-10-8 (NPK) chemical fertilizer or organic composted manure'
        elif my_prediction == 11:
            Answer = 'Predict'
            crop = 'mango'
            fertilizer = '50 gm zinc sulphate, 50 gm copper sulphate and 20 gm borax per tree/annum are recommended'
        elif my_prediction == 12:
            Answer = 'Predict'
            crop = 'grapes'
            fertilizer = 'Use 3 pounds (1.5 kg.) of potassium sulfate per vine for mild deficiencies or up to 6 pounds (3 kg.)'
        elif my_prediction == 13:
            Answer = 'Predict'
            crop = 'watermelon'
            fertilizer = 'Apply a fertilizer high in phosphorous, such as 10-10-10, at a rate of 4 pounds per 1,000 square feet (60 to 90 feet of row)'
        elif my_prediction == 14:
            Answer = 'Predict'
            crop = 'muskmelon'
            fertilizer = 'Apply FYM 20 t/ha, NPK 40:60:30 kg/ha as basal and N @ 40 kg/ha 30 days after sowing.'
        elif my_prediction == 15:
            Answer = 'Predict'
            crop = 'apple'
            fertilizer = 'Apple trees require nitrogen, phosphorus and potassium,Common granular 20-10-10 fertilizer is suitable for apples'
        elif my_prediction == 16:
            Answer = 'Predict'
            crop = 'orange'
            fertilizer = 'Orange farmers often provide 5,5 – 7,7 lbs (2,5-3,5 kg) P2O5 in every adult tree for 4-5 consecutive years'
        elif my_prediction == 17:
            Answer = 'Predict'
            crop = 'papaya'
            fertilizer = 'Generally 90 g of Urea, 250 g of Super phosphate and 140 g of Muriate of Potash per plant are recommended for each application'
        elif my_prediction == 18:
            Answer = 'Predict'
            crop = 'coconut'
            fertilizer = 'Organic Manure @50kg/palm or 30 kg green manure, 500 g N, 320 g P2O5 and 1200 g K2O/palm/year in two split doses during September and May'
        elif my_prediction == 19:
            Answer = 'Predict'
            crop = 'cotton'
            fertilizer = 'N-P-K 20-10-10 per hectare during sowing (through the sowing machine)'
        elif my_prediction == 20:
            Answer = 'Predict'
            crop = 'jute'
            fertilizer = 'Apply 10 kg of N at 20 - 25 days after first weeding and then again on 35 - 40 days after second weeding as top dressing'
        elif my_prediction == 21:
            Answer = 'Predict'
            crop = 'coffee'
            fertilizer = 'Coffee trees need a lot of potash, nitrogen, and a little phosphoric acid. Spread the fertilizer in a ring around each Coffee plant'
        else:
            Answer = 'Predict'
            crop = 'Crop info not Found!'

        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Querytb VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                ('', uname, nitrogen, phosphorus, potassium, temperature, humidity, ph, rainfall, Answer, crop, fertilizer, location)
            )
            conn.commit()

            cursor.execute("SELECT * FROM regtb WHERE UserName=%s", (uname,))
            data3 = cursor.fetchone()
            if data3:
                phnumber = data3[4]
                print(phnumber)
                sendmsg(phnumber, "Predict Crop Name : " + crop)

            cursor.execute("SELECT * FROM Querytb WHERE UserName=%s AND DResult='waiting'", (uname,))
            data = cursor.fetchall()

            cursor.execute("SELECT * FROM Querytb WHERE UserName=%s AND DResult !='waiting'", (uname,))
            data1 = cursor.fetchall()
            return render_template('UserQueryAnswerinfo.html', wait=data, answ=data1)
        finally:
            conn.close()
    return render_template('NewQueryReg.html')

@app.route("/Soil")
def Soil():
    return render_template('Soil.html')

@app.route("/Leaf")
def Leaf():
    return render_template('Leaf.html')

@app.route("/Fruit")
def Fruit():
    return render_template('Fruit.html')

@app.route("/testimage", methods=['GET', 'POST'])
def testimage():
    if request.method == 'POST':
        file = request.files['fileupload']
        filename = str(uuid.uuid4()) + ".jpg"
        save_path = os.path.join('static', 'Out', filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        file.save(save_path)

        img1 = cv2.imread(save_path)
        if img1 is None:
            return "No image data found", 400

        # Processing logic
        gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        img1S = cv2.resize(img1, (960, 540))
        grayS = cv2.resize(gray, (960, 540))

        prefix = str(uuid.uuid4())
        gry = f'static/Out/{prefix}_gry.jpg'
        cv2.imwrite(gry, grayS)

        im = Image.open(save_path)
        im_invert = ImageOps.invert(im.convert('RGB'))
        inv = f'static/Out/{prefix}_inv.jpg'
        im_invert.save(inv, quality=95)

        dst = cv2.fastNlMeansDenoisingColored(img1, None, 10, 10, 7, 21)
        noi = f'static/Out/{prefix}_noi.jpg'
        cv2.imwrite(noi, dst)

        # Predict
        if classifier_soil:
            test_img = image.load_img(save_path, target_size=(200, 200))
            test_img = np.expand_dims(test_img, axis=0)
            result = classifier_soil.predict(test_img)

            out = ''
            pre = ''
            if result[0][0] == 1:
                out = "AlluvialSoil"
                pre = "Wheat, Groundnut and cotton"
            elif result[0][1] == 1:
                out = "ClaySoil"
                pre = "Cabbage (Napa and savoy), Cauliflower, Kale, Bean, Pea, Potato and Daikon radish"
            elif result[0][2] == 1:
                out = "RedSoil"
                pre = "Marsh soils are not suitable for crop cultivation due to their high acidic nature"
            elif result[0][3] == 1:
                out = "YellowSoil"
                pre = "Tea, coffee and cashew"
        else:
            out = "Model Not Loaded"
            pre = "N/A"

        if session.get('mob'):
            sendmsg(session['mob'], "Predict Soil Name : " + out)

        return render_template('Soil.html', result=out, org=save_path, gry=gry, inv=inv, noi=noi, pre=pre)
    return render_template('Soil.html')

@app.route("/testimage1", methods=['GET', 'POST'])
def testimage1():
    if request.method == 'POST':
        file = request.files['fileupload']
        filename = str(uuid.uuid4()) + ".jpg"
        save_path = os.path.join('static', 'Out', filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        file.save(save_path)

        img1 = cv2.imread(save_path)
        if img1 is None:
            return "No image data found", 400

        # Processing logic
        gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        grayS = cv2.resize(gray, (960, 540))

        prefix = str(uuid.uuid4())
        gry = f'static/Out/{prefix}_gry.jpg'
        cv2.imwrite(gry, grayS)

        im = Image.open(save_path)
        im_invert = ImageOps.invert(im.convert('RGB'))
        inv = f'static/Out/{prefix}_inv.jpg'
        im_invert.save(inv, quality=95)

        dst = cv2.fastNlMeansDenoisingColored(img1, None, 10, 10, 7, 21)
        noi = f'static/Out/{prefix}_noi.jpg'
        cv2.imwrite(noi, dst)

        if classifier_leaf:
            test_img = image.load_img(save_path, target_size=(200, 200))
            test_img = np.expand_dims(test_img, axis=0)
            result = classifier_leaf.predict(test_img)

            out = ''
            fer = ''
            if result[0][0] == 1:
                out = "Apple___Black_rot"
                fer = 'Griffin  Fertilizer  reducing the fungus'
            elif result[0][1] == 1:
                out = "Apple___healthy"
            elif result[0][2] == 1:
                out = "Corn_(maize)___healthy"
            elif result[0][3] == 1:
                out = "Corn_(maize)___Northern_Leaf_Blight"
                fer = 'According to Cornell CALS, a good starter fertilizer for corn should have a ratio of 1-4-0, 1-3-1, 1-3-3, or 1-1-1'
            elif result[0][4] == 1:
                out = "Peach___Bacterial_spot"
                fer = 'Compounds available for use on peach and nectarine for bacterial spot include copper, oxytetracycline (Mycoshield and generic equivalents), and syllit+captan; however, repeated applications are typically necessary for even minimal disease control.'
            elif result[0][5] == 1:
                out = "Peach___healthy"
            elif result[0][6] == 1:
                out = "Pepper_bell___Bacterial_spot"
                fer = 'Seed treatment with hot water, soaking seeds for 30 minutes in water pre-heated to 125 F/51 C, is effective in reducing bacterial populations on the surface and inside the seeds'
            elif result[0][7] == 1:
                out = "Pepper_bell___healthy"
            elif result[0][8] == 1:
                out = "Potato___Early_blight"
                fer = 'Compounds available for use on peach and nectarine for bacterial spot include copper, oxytetracycline (Mycoshield and generic equivalents), and syllit+captan; however, repeated applications are typically necessary for even minimal disease control.'
            elif result[0][9] == 1:
                out = "Potato___healthy"
                fer = 'Compounds available for use on peach and nectarine for bacterial spot include copper, oxytetracycline'
            elif result[0][10] == 1:
                out = "Potato___Late_blight"
                fer = 'Dithane (mancozeb) MZ or you can also use Tattoo C or Acrobat MZ'
            elif result[0][11] == 1:
                out = "Tomato___Bacterial_spot"
                fer = 'Griffin  Fertilizer  reducing the fungus'
            elif result[0][12] == 1:
                out = "Tomato___Late_blight"
                fer = 'Spraying fungicides is the most effective way to prevent late bligh'
            elif result[0][13] == 1:
                out = "Tomato___Leaf_Mold"
                fer = 'Compounds available for use on peach and nectarine for bacterial spot include copper, oxytetracycline'
            elif result[0][14] == 1:
                out = "Tomato___Septoria_leaf_spot"
                fer = 'Griffin  Fertilizer  reducing the fungus'
        else:
            out = "Model Not Loaded"
            fer = "N/A"

        if session.get('mob'):
            sendmsg(session['mob'], "Predict LeafDisease Name : " + out)

        return render_template('Leaf.html', fer=fer, result=out, org=save_path, gry=gry, inv=inv, noi=noi)
    return render_template('Leaf.html')

@app.route("/testimage2", methods=['GET', 'POST'])
def testimage2():
    if request.method == 'POST':
        file = request.files['fileupload']
        filename = str(uuid.uuid4()) + ".jpg"
        save_path = os.path.join('static', 'Out', filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        file.save(save_path)

        img1 = cv2.imread(save_path)
        if img1 is None:
            return "No image data found", 400

        # Processing logic
        gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        grayS = cv2.resize(gray, (960, 540))

        prefix = str(uuid.uuid4())
        gry = f'static/Out/{prefix}_gry.jpg'
        cv2.imwrite(gry, grayS)

        im = Image.open(save_path)
        im_invert = ImageOps.invert(im.convert('RGB'))
        inv = f'static/Out/{prefix}_inv.jpg'
        im_invert.save(inv, quality=95)

        dst = cv2.fastNlMeansDenoisingColored(img1, None, 10, 10, 7, 21)
        noi = f'static/Out/{prefix}_noi.jpg'
        cv2.imwrite(noi, dst)

        if classifier_fruit:
            test_img = image.load_img(save_path, target_size=(200, 200))
            test_img = np.expand_dims(test_img, axis=0)
            result = classifier_fruit.predict(test_img)

            out = ''
            fer = ''
            if result[0][0] == 1:
                out = "AppleBlotch"
                fer = 'According to Cornell CALS, a good starter fertilizer for corn should have a ratio of 1-4-0, 1-3-1, 1-3-3, or 1-1-1'
            elif result[0][1] == 1:
                out = "AppleNormal"
                fer = 'Nil'
            elif result[0][2] == 1:
                out = "AppleRot"
                fer = 'According to Cornell CALS, a good starter fertilizer for corn should have a ratio of 1-4-0, 1-3-1, 1-3-3, or 1-1-1'
            elif result[0][3] == 1:
                out = "AppleScab"
                fer = 'According to Cornell CALS, a good starter fertilizer for corn should have a ratio of 1-4-0, 1-3-1, 1-3-3, or 1-1-1'
            elif result[0][4] == 1:
                out = "guavaPhytopthora"
                fer = 'Compounds available for use on peach and nectarine for bacterial spot include copper, oxytetracycline (Mycoshield and generic equivalents), and syllit+captan; however, repeated applications are typically necessary for even minimal disease control.'
            elif result[0][5] == 1:
                out = "guavaRoot"
                fer = 'Seed treatment with hot water, soaking seeds for 30 minutes in water pre-heated to 125 F/51 C, is effective in reducing bacterial populations on the surface and inside the seeds'
            elif result[0][6] == 1:
                out = "guavaScab"
                fer = 'Compounds available for use on peach and nectarine for bacterial spot include copper, oxytetracycline'
            elif result[0][7] == 1:
                out = "MangoAlternaria"
                fer = 'Compounds available for use on peach and nectarine for bacterial spot include copper, oxytetracycline'
            elif result[0][8] == 1:
                out = "MangoAnthracnose"
                fer = 'Compounds available for use on peach and nectarine for bacterial spot include copper, oxytetracycline (Mycoshield and generic equivalents), and syllit+captan; however, repeated applications are typically necessary for even minimal disease control.'
            elif result[0][9] == 1:
                out = "MangoBlackMouldRot"
                fer = 'Compounds available for use on peach and nectarine for bacterial spot include copper, oxytetracycline'
            elif result[0][10] == 1:
                out = "MangoHealthy"
                fer = 'Nil'
            elif result[0][11] == 1:
                out = "MangoStemandRot"
                fer = 'Dithane (mancozeb) MZ or you can also use Tattoo C or Acrobat MZ'
        else:
            out = "Model Not Loaded"
            fer = "N/A"

        if session.get('mob'):
            sendmsg(session['mob'], "Predict FruitDisease Name : " + out)

        return render_template('Fruit.html', fer=fer, result=out, org=save_path, gry=gry, inv=inv, noi=noi)
    return render_template('Fruit.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
