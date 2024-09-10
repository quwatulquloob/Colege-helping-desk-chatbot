import pyrebase
from flask import Flask, redirect, render_template, request, url_for
import pickle
import json
import random

app = Flask(__name__)

# Add your own Firebase configuration details
config = {
    'apiKey': "AIzaSyDM9hliIUZ1a1ukwLlAtQ4BOr1sNuRnULA",
    'authDomain': "flask-f123e.firebaseapp.com",
    'projectId': "flask-f123e",
    'storageBucket': "flask-f123e.appspot.com",
    'messagingSenderId': "486663157988",
    'appId': "1:486663157988:web:8dac88b9eb9cb683d2d4f1",
    'measurementId': "G-1R1H3CW7N1",
    'databaseURL': "https://flask-f123e-default-rtdb.firebaseio.com/"
}

# Initialize Firebase
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

# Initialize person as dictionary
person = {"is_logged_in": False, "name": "", "email": "", "uid": ""}

# Login
@app.route("/")
def login():
    return render_template("login.html")

# Sign up / Register
@app.route("/signup")
def signup():
    return render_template("signup.html")

# Handle login form submission
@app.route("/result", methods=["POST"])
def result():
    if request.method == "POST":
        result = request.form
        email = result["email"]
        password = result["pass"]
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["uid"] = user["localId"]
            data = db.child("users").get()
            person["name"] = data.val()[person["uid"]]["name"]
            return redirect(url_for('home'))
        except:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

# Handle signup form submission
@app.route("/register", methods=["POST"])
def register():
    if request.method == "POST":
        result = request.form
        email = result["email"]
        password = result["pass"]
        name = result["name"]
        try:
            auth.create_user_with_email_and_password(email, password)
            user = auth.sign_in_with_email_and_password(email, password)
            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["uid"] = user["localId"]
            person["name"] = name
            data = {"name": name, "email": email}
            db.child("users").child(person["uid"]).set(data)
            return redirect(url_for('home'))
        except:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('signup'))
# Load the trained model and vectorizer
with open('model.pkl', 'rb') as f:
    best_model = pickle.load(f)

with open('vectorizer.pkl', 'rb') as f:
    vectorizer = pickle.load(f)

# Load the intents data
with open('sentences.json', 'r') as f:
    intents = json.load(f)

def chatbot_response(user_input):
    input_text = vectorizer.transform([user_input])
    predicted_intent = best_model.predict(input_text)[0]

    for intent in intents['intents']:
        if intent['tag'] == predicted_intent:
            response = random.choice(intent['responses'])
            break

    return response

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.form['user_input']
    response = chatbot_response(user_input)
    return response

if __name__ == '__main__':
    app.run(debug=True)