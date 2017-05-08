# main.py
# Main Python Flask application

#===================#
#===== MODULES =====#
#===================#

from flask import Flask, flash, redirect, render_template, request, session, abort, g, url_for, escape
from hashlib import sha512
import string
import sqlite3
import os

#=================#
#===== MAIN ======#
#=================#

app = Flask(__name__)

#generates pseudorandom secret key
app.secret_key = os.urandom(32)

# Database set up
DATABASE = "main.db"

# initial connect
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# function to simplify querries
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()

    #returns a TUPLE, NOT DICT
    return (rv[0] if rv else None) if one else rv

#==================#
#===== ROUTES =====#
#==================#

# index
@app.route('/')
def index():
    return render_template("index.html")

# login
# route limits access to POST
@app.route("/login", methods=["POST","GET"])
def login():

    #if POST, i.e. form has been submitted with login information
    if request.method == "POST":

        # remove non alphanumeric characters from form, after convverting unicode --> ascii
        #sha512 hash for password
        username = filter(str.isalnum,request.form["username"].encode("ascii","replace"))
        password = sha512(filter(str.isalnum,request.form["password"].encode("ascii","replace"))).hexdigest()

        # parameterized query
        query = "select * from users where password = ? and email = ?;"
        args = [password, username]

        response = query_db(query,args,one=True)

        if response is None:
            # don't tell user which one is incorrect
            # otherwise, user can discern info on users in database
            flash("Wrong username/password combination!")
            return redirect(url_for("login"))

        else:
            #set session variables
            session['username'] = response[1]
            session['firstName'] = response[4]
            session['lastName'] = response[5]

            return redirect(url_for("index"))

    #if GET, i.e. user is trying to get to login page
    else:
        return render_template("login.html")

# logout
@app.route("/logout")
def logout():
    session.pop('username', None)
    flash("You have been succesfully logged out.")
    return redirect(url_for('index'))

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":

        # remove non alphanumeric characters from form, after convverting unicode --> ascii
        #sha512 hash (hex) for password
        username = filter(str.isalnum,request.form["username"].encode("ascii","replace"))
        password = sha512(filter(str.isalnum,request.form["password"].encode("ascii","replace"))).hexdigest()
        lastName = filter(str.isalnum,request.form["lastName"].encode("ascii","replace"))
        firstName = filter(str.isalnum,request.form["firstName"].encode("ascii","replace"))

        # parameterized query
        query = "insert into users values (?,?,?,?,?)"
        args = [username,password,lastName,firstName,0.00]

        response = query_db(query,args,one=True)

    else:
        return render_template("register.html")

# tear down
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

#=====================================#
#===== CONDITIONAL RUN VARIABLES =====#
#=====================================#

# we probably won't need this, so it's commented out for now

# this will only run if the applicaiotn is being run as an applicaiton
# (versus being imported as a moedule)
# if __name__ == "__main__":
#     app.run(debug=True,host='0.0.0.0', port=5000)