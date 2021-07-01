from flask import render_template, redirect, Flask, session, request, url_for
from flask_session import Session
from tempfile import mkdtemp
import json
import os
import sqlite3
#from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
#from werkzeug.security import check_password_hash, generate_password_hash

from helpers import getConnection, executeWriteQuery, executeReadQuery, login_required


from authlib.integrations.flask_client import OAuth


app = Flask(__name__)
app.secret_key = '5yTuleqqRRdRwvCf'


oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id = '400883400079-0mgfa8lv7qco8f9dj1elpg2huv70llcs.apps.googleusercontent.com',
    client_secret = 'YLdpERED0IZeD80ZPSZ59qIh',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',  # This is only needed if using openId to fetch user info
    client_kwargs={'scope': 'openid email profile'},
)

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

# whatever that was

@app.route('/login')
def login():
    google = oauth.create_client('google')
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()
    user = oauth.google.userinfo()
    # do something with the token and profile
    session['email'] = user_info['email']
    return redirect('/')

@app.route("/")
def homepage():
    email = dict(session).get('email', None)
    if email:
        return redirect("/signedin")
    else:
        return redirect("/signedout")

@app.route('/signedin')
def signedin():
    email = dict(session).get('email', None)
    return render_template('homein.html', email = email)

@app.route("/signedout")
def signedout():
    return render_template('homeout.html')


@app.route('/logout')
def logout():
    for key in list(session.keys()):
        session.pop(key) 
    return redirect('/')


@app.route("/home")
def test():
    return redirect("/")

@app.route('/sell')
def sell():
    return 'this is the sell page'

    
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

#@app.route("/preferences1", methods=["GET", "POST"])
#def preferences1():
#    if request.method == "GET":
#        return render_template('pref1.html')

#    preferences.veg = request.form.get("veg")
#    preferences.cuisine = request.form.get("cuisine")   
#    return redirect("/listings")

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

    return render_template('listings.html', listings=recommendedsellers, cuisine=preferences.cuisine, veg=preferences.veg)

@app.route('/signin')
def signinpage():
    return "signin"

@app.route('/signup')
def signuppage():
    return "signup"


if __name__ == "__main__":
    app.run(ssl_context="adhoc")