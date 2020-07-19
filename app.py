import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for, flash, send_file
from flask_session import Session
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class #possible notUsed
import datetime
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import api_handler
import pillow_filter
import requests

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
photos = UploadSet('photos', IMAGES)
app.config['UPLOADED_PHOTOS_DEST'] = "static/uploads"
app.config['MAX_CONTENT_LENGTH'] = 1920 * 1920
configure_uploads(app, photos)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

#Methods called by routes
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF"]
UPLOAD_FOLDER = "/static/uploads" #possible notUsed
app.config['IMAGE_UPLOADS'] = UPLOAD_FOLDER #possible notUsed
currentImage = ""

def fixImage(image):
    return image.replace("i.imgur", "imgur")

def fixCurrentImage():
    global currentImage
    currentImage = fixImage(currentImage)

def allowed_image(filename):
    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("postgres://ldrthfhaqyelpx:3350e790b7910d24ff94ec98eb5633d54b50e00d1864c7c162209e063676d04b@ec2-52-22-216-69.compute-1.amazonaws.com:5432/d96punflgs6a2d")

@app.route("/")
@login_required
def index():
    fixCurrentImage()
    return render_template("index.html", currentImage=currentImage)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        if "'" in request.form.get("username") or ";" in request.form.get("username") or "'" in request.form.get("password") or ";" in request.form.get("password"):
            return apology("No SQL injection, please!")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    #Make sure the user's input was a POST method.
    if request.method != "POST":
        return render_template("register.html") #This shouldn't happen regardless of user input!

    #Make sure the username is not blankher and does not already exist.
    if not request.form.get("username"):
        return apology("Must provide username")
    if "'" in request.form.get("username") or ";" in request.form.get("username"):
        return apology("No SQL injection, please!")
    #Query database for the username
    rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))
    if rows:
        return apology("Username already exists") #I think this way will work!


    #Make sure the password is not blank and that the password and confirmation match.
    if not request.form.get("password"):
        return apology("Must provide password")
    if request.form.get("password") != request.form.get("confirmation"):
        return apology("Username and password must match!")

    #Insert the new row into users, storing a hash of the user's password, not the password itself.
    db.execute("INSERT INTO users (username, hash) VALUES (:username, :myHash)",
        username=request.form.get("username"), myHash=generate_password_hash(request.form.get("password")))


    return redirect("/")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    global currentImage
    currentImage = ""

    # Redirect user to login form
    return redirect("/")


@app.route("/upload", methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'GET':
        return render_template("upload.html")
    elif request.files:
        #The POST request came through with an image file.
        image = request.files['image']

        if image.filename == "":
            print("No filename")
            return redirect("/upload")
        if image and allowed_image(image.filename):
            filename = secure_filename(image.filename)
            #image.save(filename)
            newFilename = "image." + filename.rsplit(".", 1)[1]
            image.save(newFilename)
            print("Image saved.")
            #Now it's on the filesystem, but because I use image.{extension}, the filesystem won't get clogged up with a million uploads. That's imgur's job.
            x = api_handler.uploadToImgur(newFilename)
            #flash("Image saved.")
            if x == "-1":
                flash("failed to upload!")
            else:
                flash("Image uploaded successfully. Permanent link at " + x)
                global currentImage
                currentImage = x
                db.execute("INSERT INTO pics (user_id, path, filter) VALUES (:user_id, :path, 'None')", user_id=session["user_id"], path=x)
            #This should mean that we have the link uploaded.
            return redirect("/")
        else:
            print("That file extension is not allowed")
            flash("That file extension is not allowed")
            return redirect("/upload")
    else:
        print("Not request.files")
        flash("Please select a file to upload")
        return render_template("upload.html")
    

@app.route('/filter', methods=['GET', 'POST'])
@login_required
def filter():
    if request.method == 'GET':

        filterSelection = pillow_filter.filterTypes

        rows = db.execute("SELECT path FROM pics WHERE user_id = :user_id", user_id = session['user_id'])

        imgSelection = []

        for item in rows:
            item['path]'] = fixImage(item['path'])
            imgSelection.append(item['path'])

        return render_template("filter.html", filterSelection=filterSelection, imgSelection=imgSelection)
    #else, it's a post, which means we're taking the URL of a particular image from imgur, and a desired filter.
    print("Got post request.")
    print("Have filter and image")
    url = request.form['image']
    print("url: " + url)
    filter = request.form['filter']
    print("filter: " + filter)
    print("Applying filter...")
    img = pillow_filter.applyFilter(url, filter)
    print("Filter applied.")

    print("Finding parent...")
    rows = db.execute("SELECT id FROM pics WHERE path = :path", path=url)
    parent = rows[0]["id"]

    print("Saving to filesystem...")
    ext = url.rsplit(".", 1)[1]
    newFilename = "image." + ext
    img.save(newFilename)

    #Then, we re-post that image to imgur, with the filter applied.
    print("Posting to imgur...")
    x = api_handler.uploadToImgur(newFilename)
    if x == "-1":
        flash("Failed to upload.")
        print("Failed to upload.")
    else:
        flash("Filter applied and new image hosted. Permanent link at " + x)
        global currentImage
        currentImage = x
        print("Saving to database...")
        db.execute("INSERT INTO pics (user_id, path, filter, parent) VALUES (:user_id, :path, :filter, :parent)", user_id=session["user_id"], path=x, filter=filter, parent=parent)
        print("Done.")
    return redirect("/")

@app.route("/library", methods=['GET', 'POST'])
@login_required
def library():
    if request.method == 'POST':
        print("Got post request...")
        #Add the currentImage from the table pics to the table library
        global currentImage
        size = api_handler.getImageSize(currentImage)
        #db.execute("INSERT INTO library SELECT * FROM pics WHERE path=:path", path=currentImage)
        db.execute("INSERT INTO library (user_id, path, filter, id, parent, size) SELECT user_id, path, filter, id, parent, :size FROM pics WHERE path=:path", path=currentImage, size=size)
        print("Added current image to library...")
        currentImage = ""
    #FilterSelection
    filterSelection = pillow_filter.filterTypes
    rows = db.execute("SELECT path FROM library WHERE user_id=:id", id=session['user_id'])
    #Turn rows into a list of links which will be loaded on the library page (imageLibrary)
    imageLibrary = []
    for item in rows:
        imageLibrary.append(item['path'])
    return render_template("library.html", filterSelection=filterSelection, imageLibrary=imageLibrary)

@app.route("/profile")
@login_required
def profile():
    rows = db.execute("SELECT filter FROM pics WHERE user_id = :id", id=session['user_id'])
    rows2 = rows.copy()
    for item in rows:
        if item['filter'] != "None":
            rows.remove(item)
    imgsUploaded = len(rows) #Images Uploaded
    for item in rows2:
        if item['filter'] == "None":
            rows2.remove(item)
    filtersApplied = len(rows2) #Filters Applied
    rows = db.execute("SELECT path, size FROM library WHERE user_id = :id", id=session['user_id'])
    
    numImgs = len(rows)
    sizeBytes = 0
    for item in rows:
        sizeBytes += item['size']


    filterFavDict = {}
    for item in pillow_filter.filterTypes:
        filterFavDict[item] = 0 #Initializing all values to 0
    filterFavDict["None"] = 0
    for item in rows2:
        if item['filter'] != "None":
            filterFavDict[item['filter']] += 1

    


    #the following is the old way of doing things?
    #favFilterNum = filterFavDict[max(filterFavDict, key=filterFavDict.get)]
    #for key, value in filterFavDict.items():
        #if value == favFilterNum:
            #favFilter.append(key)

    filterLeastDict = {} #this one will exclude those with zero uses.
    for key, value in filterFavDict.items():
            if value != 0:
                filterLeastDict[key] = value
    favFilter = [] #favorite filters
    lstFav = [] #least favorite filters
    if len(filterLeastDict) == 0:
        lstFavNum = 0
        favFilterNum = 0
    else:
        lstFavNum = filterLeastDict[min(filterLeastDict, key=filterLeastDict.get)]
        favFilterNum = filterLeastDict[max(filterLeastDict, key=filterLeastDict.get)]
        for key, value in filterLeastDict.items():
            if value == lstFavNum and key != "None":
                lstFav.append(key)
            if value == favFilterNum and key != "None":
                favFilter.append(key)
    if len(favFilter) == 1:
        favFilter = favFilter[0]
    if len(lstFav) == 1:
        lstFav = lstFav[0]
    return render_template("profile.html", uploads=imgsUploaded, filters=filtersApplied, sizeImgs=numImgs, sizeBytes=sizeBytes, favFilter=favFilter, lstFav=lstFav, favNum=favFilterNum, lstNum=lstFavNum)

@app.route("/docs")
@login_required
def docs():
    return render_template("docs.html")

if __name__ == "main":
    app.run()