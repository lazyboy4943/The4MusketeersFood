from flask import render_template, redirect, Flask, session, request
from flask_session import Session
from tempfile import mkdtemp
#from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
#from werkzeug.security import check_password_hash, generate_password_hash

from helpers import getConnection, executeWriteQuery, executeReadQuery, login_required

# configure application, use filesystem insted of cookies, make sure responses aren't cached
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

names = ['Prakamya Singh', 'Praneeth Suresh', 'Pratyush Bansal', 'Rahul Rajkumar']
sellers = {
    1: {"name": "Wong Lao", "cuisine": "Assorted", "foodavailable": True, "vegetarian": True},
    2: {"name": "Stan Lee", "cuisine": "Assorted", "foodavailable": True, "vegetarian": True},
    3: {"name": "Suresh Kumar", "cuisine": "Indian", "foodavailable": True, "vegetarian": True},
    4: {"name": "Adam Wong", "cuisine": "Chinese", "foodavailable": True, "vegetarian": True},
    5: {"name": "Chan Li", "cuisine": "Assorted", "foodavailable": True, "vegetarian": False},
    6: {"name": "Mohammed bin Yusuf", "cuisine": "Malay", "foodavailable": True, "vegetarian": True},
    7: {"name": "Abdul Rahman", "cuisine": "Malay", "foodavailable": True, "vegetarian": False},
    8: {"name": "Faadil Ahmed", "cuisine": "Indian", "foodavailable": True, "vegetarian": True},
}

@app.route("/")
def homepage():
    return render_template('home.html')

@app.route("/home")
def test():
    return render_template("home1.html")
    
@app.route("/about")
def about():
    return render_template('about.html', names = names)

@app.route("/preferences", methods=["GET", "POST"])
def preferences():
    if request.method == "GET":
        return render_template('preferences.html')

    preferences.veg = request.form.get("veg")
    preferences.cuisine = request.form.get("cuisine")   
    return redirect("/listings")
    

@app.route("/listings")
def listings(): 
    recommendedsellers = []
    if preferences.veg == "Vegetarian":
        for seller in sellers:
            if sellers[seller]["foodavailable"]:
                if sellers[seller]["cuisine"] == preferences.cuisine:
                    if sellers[seller]["vegetarian"]:
                        recommendedsellers.append(sellers[seller])
    else:
        for seller in sellers:
            if sellers[seller]["foodavailable"]:
                if sellers[seller]["cuisine"] == preferences.cuisine:
                    recommendedsellers.append(sellers[seller])

    recommendedsellers = tuple(recommendedsellers)
        
    return render_template('listings.html', listings = recommendedsellers)

@app.route('/signin')
def signinpage():
    return "signin"

@app.route('/signup')
def signuppage():
    return "signup"
