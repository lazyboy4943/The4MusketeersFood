from flask import render_template, redirect, Flask, session, request, url_for, jsonify
from flask_session import Session
from tempfile import mkdtemp
import requests
from flask_simple_geoip import SimpleGeoIP
import mpu
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from authlib.integrations.flask_client import OAuth
#from werkzeug.security import check_password_hash, generate_password_hash

from helpers import getConnection, executeWriteQuery, executeReadQuery

# configure application, use filesystem insted of cookies, make sure responses aren't cached
app = Flask(__name__)
app.secret_key = '5yTuleqqRRdRwvCf'
app.config.update(GEOIPIFY_API_KEY='at_KIgYTxO7GSB26ukH0av9aCEC2IUCQ')
simple_geoip = SimpleGeoIP(app)
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
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id='400883400079-0mgfa8lv7qco8f9dj1elpg2huv70llcs.apps.googleusercontent.com',
    client_secret='YLdpERED0IZeD80ZPSZ59qIh',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',  # This is only needed if using openId to fetch user info
    client_kwargs={'scope': 'openid email profile'},
)

names = ["Akshaya Singh", "Prakamya Singh", "Praneeth Suresh", "Pratyush Bansal", "Rahul Rajkumar", "Vishnumaya Praveenraman"]
db = getConnection("/home/lazyboy4943/mysite/feelathomesg.db")
global item_choices
item_choices = []

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


@app.route('/sell', methods=["GET", "POST"])
def sell():
    email = dict(session).get("email", None)
    if email:
        if request.method == "GET":
            return render_template("sell.html")

        category = request.form.get("category")
        usage = request.form.get("usage")
        name = request.form.get("name")
        prodname = request.form.get("prodname")
        proddesc = request.form.get("proddesc")
        phone = request.form.get("phone")
        latitude = float(request.form.get("latitude"))
        longitude = float(request.form.get("longitude"))
        query = """
        INSERT INTO listings
        (seller, prodname, description, category, usage, phone_num, latitude, longitude, email, availability)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1);
        """
        values = tuple((name, prodname, proddesc, category, usage, phone, latitude, longitude, email))
        if executeWriteQuery(db, query, values):
            return render_template("sell.html", sold=True)

    else:
        return redirect("/")


@app.route('/signmentor', methods=["GET", "POST"])
def signmentor():
    email = dict(session).get("email", None)
    if email:
        if request.method == "GET":
            return render_template("signmentor.html")

        area = request.form.get("expertin")
        name = request.form.get("name")
        descr = request.form.get("descr")
        phone = request.form.get("phone")
        latitude = float(request.form.get("latitude"))
        longitude = float(request.form.get("longitude"))
        query = """
        INSERT INTO mentors
        (mentor, description, area, phone_num, latitude, longitude, email)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """
        values = tuple((name, descr, area, phone, latitude, longitude, email))
        if executeWriteQuery(db, query, values):
            return render_template("signmentor.html", registered=True)

    else:
        return redirect("/")


@app.route("/about")
def about():
    return render_template('about.html', names=names)

@app.route("/buy", methods=["GET", "POST"])
def choices():
    email = dict(session).get('email', None)
    if email:
        if request.method == "GET":
            return render_template('preferences.html')

        #global choice_usage
        choices.usage = (request.form.get("usage"))
        #global choice_category
        choices.category = (request.form.get("category"))
        #global choice_buyerLat
        choices.lat = (float(request.form.get("latitude")))
        #global choice_buyerLong
        choices.long = (float(request.form.get("longitude")))
        #print(item_choices)
        return redirect("/listings")

    else:
        return redirect("/")


@app.route("/mentorpreferences", methods=["GET", "POST"])
def mentorpreferences():
    email = dict(session).get('email', None)
    if email:
        if request.method == "GET":
            return render_template('mentorpreferences.html')

        mentorpreferences.area = request.form.get("expertin")
        mentorpreferences.menteeLat = float(request.form.get("latitude"))
        mentorpreferences.menteeLong = float(request.form.get("longitude"))
        return redirect("/mentorlistings")

    else:
        return redirect("/")


@app.route("/listings", methods=["GET", "POST"])
def findlistings():
    email = dict(session).get('email', None)
    if email:
        if request.method == "GET":
            query = "SELECT seller, prodname, description, phone_num, latitude, longitude FROM listings WHERE availability = 1 AND category = ? AND usage = ?"
            values = tuple((choices.category, choices.usage))
            listings = executeReadQuery(db, query, values)
            viableSellers = []
            lat1, long1 = choices.lat, choices.long
            for listing in listings:
                lat2, long2 = listing[4], listing[5]
                dist = mpu.haversine_distance((lat1, long1), (lat2, long2))
                if dist <= 40:
                    tmp = []
                    for i in range(4):
                        tmp.append(listing[i])
                    if dist >= 1:
                        tmp.append(f"{dist:.1f} km")
                    else:
                        tmp.append(f"{dist:.1f} meters")
                    viableSellers.append(tmp)
            return render_template('listings.html', listings=viableSellers, category=choices.category, usage=choices.usage)

        else:
            findlistings.listing_id = (int(request.form.get("ordernum")[3:]),)
            return redirect("/processing")

    else:
        return redirect("/")

@app.route("/mentorlistings")
def mentorlistings():
    email = dict(session).get('email', None)
    if email:
        query = "SELECT mentor, description, phone_num, area, latitude, longitude FROM mentors WHERE area = ?;"
        values = (mentorpreferences.area,)
        listings = executeReadQuery(db, query, values)
        viableMentors = []
        lat1, long1 = mentorpreferences.menteeLat, mentorpreferences.menteeLong
        for listing in listings:
            lat2, long2 = listing[4], listing[5]
            dist = mpu.haversine_distance((lat1, long1), (lat2, long2))
            tmp = []
            for i in range(2):
                tmp.append(listing[i])
            phone_num = listing[2].split()
            phone_num = "".join(phone_num)
            tmp.append(phone_num)
            if dist >= 1:
                tmp.append(f"{dist:.1f} km")
            else:
                tmp.append(f"{int(dist)} meters")
            viableMentors.append(tmp)

        return render_template('mentorlistings.html', listings=viableMentors, area=mentorpreferences.area)

    else:
        return redirect("/")


@app.route('/signin')
def signinpage():
    return "signin"

@app.route('/signup')
def signuppage():
    return "signup"

@app.route("/processing")
def processing():
    listing_id = findlistings.listing_id
    query = "UPDATE listings SET availability = 0 WHERE listing_id = ?;"
    if executeWriteQuery(db, query, listing_id):
        query = "SELECT phone_num FROM listings WHERE listing_id = ?;"
        phone_num = executeReadQuery(db, query, listing_id)[0][0]
        phone_num = phone_num.split()
        phone_num = "".join(phone_num)
        return redirect(f"http://wa.me/{phone_num}")

# error handling
def errorhandler(e):
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return render_template("error.html", name=e.name, code=e.code)

# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == "__main__":
    app.run(debug=False)
