from flask import render_template, redirect, Flask, session, request, url_for, jsonify
from flask_session import Session
from tempfile import mkdtemp
import requests
from flask_simple_geoip import SimpleGeoIP
import mpu
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
#from werkzeug.security import check_password_hash, generate_password_hash

from helpers import getConnection, executeWriteQuery, executeReadQuery


from authlib.integrations.flask_client import OAuth


app = Flask(__name__)
app.secret_key = ''

app.config.update(GEOIPIFY_API_KEY='')
simple_geoip = SimpleGeoIP(app)


oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id = '',
    client_secret = '',
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
db = getConnection("feelathomesg.db")

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

    if email:
        return render_template('homein.html', email = email)
    else:
        return redirect("/signedout")

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

@app.route('/sell', methods=["GET", "POST"])
def sell():
    email = dict(session).get("email", None)
    if email: 
        if request.method == "GET":
            return render_template("sell.html", sold=False)

        cuisine = request.form.get("cuisine")
        if request.form.get("veg") == "Vegetarian":
            veg = 1
        else:
            veg = 0
        name = request.form.get("name")
        dishname = request.form.get("dishname")
        phone = request.form.get("phone")
        latitude = float(request.form.get("latitude"))
        longitude = float(request.form.get("longitude"))
        query = """
        INSERT INTO listings 
        (seller, description, cuisine, veg, phone_num, availability, latitude, longitude, email)
        VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?);
        """
        print(email)
        values = tuple((name, dishname, cuisine, veg, phone, latitude, longitude, email))
        if executeWriteQuery(db, query, values):
            return render_template("sell.html", sold=True)
    
    else:
        return redirect("/")
    

@app.route("/about")
def about():
    return render_template('about.html', names = names)

@app.route("/preferences", methods=["GET", "POST"])
def preferences():
    email = dict(session).get('email', None)

    if email:

        if request.method == "GET":
            return render_template('preferences.html')

        preferences.veg = request.form.get("veg")
        preferences.cuisine = request.form.get("cuisine")   
        preferences.buyerLat = float(request.form.get("latitude"))
        preferences.buyerLong = float(request.form.get("longitude"))
        return redirect("/listings")
    
    else:
        return redirect("/")

# @app.route("/preferences1", methods=["GET", "POST"])
# def preferences1():
#    if request.method == "GET":
#        return render_template('pref1.html')

#    preferences.veg = request.form.get("veg")
#    preferences.cuisine = request.form.get("cuisine")   
#    return redirect("/listings")

@app.route("/listings")
def listings(): 
    email = dict(session).get('email', None)
    if email:
        if preferences.veg == "Vegetarian":
            veg = 1
        else:
            veg = 0
        query = "SELECT seller, description, phone_num, latitude, longitude FROM listings WHERE availability = 1 AND cuisine = ? AND veg = ?"
        values = tuple((preferences.cuisine, veg))
        listings = executeReadQuery(db, query, values)
        print(listings)
        viableSellers = []
        lat1, long1 = preferences.buyerLat, preferences.buyerLong
        for listing in listings:
            lat2, long2 = listing[3], listing[4]
            dist = mpu.haversine_distance((lat1, long1), (lat2, long2))
            if dist <= 40:
                tmp = []
                for i in range(3):
                    tmp.append(listing[i])
                if dist >= 1:
                    tmp.append(f"{dist:.1f} km")
                else:
                    tmp.append(f"{dist:.1f} meters")
                viableSellers.append(tmp)

        return render_template('listings.html', listings=viableSellers, cuisine=preferences.cuisine, veg=preferences.veg)

    else:
        return redirect("/")



@app.route('/signin')
def signinpage():
    return "signin"

@app.route('/signup')
def signuppage():
    return "signup"

# error handling
def errorhandler(e):
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return render_template("error.html", name=e.name, code=e.code)

# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == "__main__":
    app.run(ssl_context="adhoc")