from flask import Flask, render_template, flash, redirect, url_for, request,abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user, logout_user
from datetime import timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from json import loads
from pywebpush import webpush, WebPushException
import traceback
from flask_mail import Mail, Message

app=Flask(__name__)
app.secret_key="narayan"
app.permanent_session_lifetime=timedelta(days=7)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///User.sqlite3'

app.config.update(dict(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USE_SSL = False,
    MAIL_USERNAME = 'pb.server.errors@gmail.com',
    MAIL_PASSWORD = 'Hffmf4Ip28eamRIxzqAc',
))

mail = Mail(app)
db=SQLAlchemy(app)
login_manager=LoginManager()
login_manager.init_app(app)

# Functions

def arrTable(arr):
    title_row=arr.pop(0)
    table="<table class='table'><tr>"
    for i in range(len(title_row)):
        table+="<th onclick='sortTable("+str(i)+")'>"+title_row[i]+"</th>"
    table+="</tr>"
    for row in arr:
        table+="<tr><td>"+"</td><td>".join(map(str,row))+"</td></tr>"
    return table+"</table>"

def sendPush(sub,message):
    aud=sub["endpoint"].split(".com")[0]+".com"
    try:
        claims={
            "aud": aud,
            "sub": "mailto:info@plantingbuddy.com"
        }
        webpush(sub,message,vapid_private_key="/var/www/plant_buddy/plantingbuddy/private_key.pem",vapid_claims=claims)
    except WebPushException as ex:
        print(repr(ex))
    return "Sent"

# Classes

class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String)
    password=db.Column(db.String)
    data=db.Column(db.String)
    crew=db.Column(db.String)
    subscription=db.Column(db.String)

    def __init__(self,name,password):
        self.name=name
        self.password=password
        self.data="{}"
        self.crew=""
        self.subscription=""

# Login

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login?next=' + request.path)

# PWA

@app.route('/sw.js', methods=['GET'])
def sw():
    return app.send_static_file('sw.js')

@app.route("/.well-known/assetlinks.json")
def assetlinks():
    return app.send_static_file(filename="assetlinks.json")

# Errors

@app.errorhandler(500)
def server_error(e):
    message=Message("error",body=traceback.format_exc(), recipients=["info@plantingbuddy.com"], sender="pb.server.errors@gmail.com")
    mail.send(message)
    return render_template("500.html")

# Views

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method=="GET":
        if current_user.is_authenticated:
            logout_user()
            flash("Logged Out")
        return render_template("login.html")
    else:
        user=User.query.filter_by(name=request.form["username"]).first()
        if user:
            if check_password_hash(user.password,request.form["password"]):
                login_user(user, remember=True)
                flash("Welcome "+user.name)
                return redirect(request.args.get('next') or url_for("home"))
            else:
                flash("Incorrect Password")
                return redirect(url_for("login"))
        else:
            flash("Account Does Not Exist")
            return redirect(url_for("login"))

@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method=="GET":
        return render_template("create.html")
    else:
        if User.query.filter_by(name=request.form["username"]).first():
            flash("Account Already Exists")
            return redirect(url_for("login"))
        else:
            if request.form["username"] and request.form["password"]:
                user=User(request.form["username"],generate_password_hash(request.form["password"]))
                db.session.add(user)
                db.session.commit()
                flash("Account Created")
                return redirect(url_for("login"))
            else:
                flash("Invalid Entry")
                return redirect(url_for("create"))

@app.route("/",methods=["GET"])
def home():
    if current_user.is_authenticated:
        return render_template("home.html",login_status="Logged in as " + current_user.name + " <a href='/login'>Logout</a>",data=current_user.data)
    else:
        return render_template("home.html",login_status="<a href='/login'>Login</a>",data="not_logged")

@app.route("/leaderboard")
@login_required
def Leaderboard():
    users=list(User.query.filter_by(crew=current_user.crew))
    names={}
    trees={}
    n_days={}
    for user in users:
        names[user.id]=user.name
        user_data=loads(user.data)
        trees[user.id]=sum(map(int, user_data.values()))
        n_days[user.id]=len(user_data.keys())

    sorted_IDs=sorted(trees,key=trees.__getitem__,reverse=True)
    leaderboard_arr=[["Rank","Username","Days","Trees"]]
    rank=1
    for ID in sorted_IDs:
        leaderboard_arr.append([rank,names[ID],n_days[ID],trees[ID]])
        rank+=1
    return render_template("leaderboard.html", login_status="Logged in as "+current_user.name+" <a href='/login'>Logout</a>", table=arrTable(leaderboard_arr), crew=current_user.crew)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin():
    if current_user.name=="admin":
        if request.method=="GET":
            all_users=list(User.query.all())
            table=[["Username","Crew","Total","Days","Options"]]
            for user in all_users:
                data=loads(user.data)
                n_days=len(data.keys())
                total=sum(map(int, data.values()))
                table.append([user.name,user.crew,total,n_days,"<form action='#' method='post'><input name='user_id' value='"+str(user.id)+"' hidden><input type='submit' value='Login' class='btn btn-success'></form>"])
            return render_template("admin.html", display=arrTable(table))
        else:
            logout_user()
            login_user(User.query.get(int(request.form["user_id"])))
            flash("Access Granted")
            return redirect(url_for("home"))
    else:
        flash("Permission Denied")
        return redirect(url_for("home"))

# Redirect Views

@app.route("/upload",methods=["POST","GET"])
@login_required
def upload():
    if request.method == "GET":
        return redirect(url_for("home"))
    else:
        try:
            crew_members=list(User.query.filter_by(crew=current_user.crew))
            for user in crew_members:
                if user.id!=current_user.id:
                    sendPush(loads(user.subscription),"Your crew member just updated their numbers!")
        except:
            print("Could not push notifications")

        current_user.data=request.form["data"]
        db.session.commit()
        flash("Data Uploaded")
        return redirect(url_for("Leaderboard"))


@app.route("/change_crew",methods=["POST"])
@login_required
def change_crew():
    current_user.crew=request.form["crew"]
    db.session.commit()
    flash("Crew Updated")
    return redirect(url_for("Leaderboard"))


@app.route("/updateSubscription", methods=["POST"])
@login_required
def updateSubscription():
    current_user.subscription=request.form["data"]
    db.session.commit()
    return redirect(url_for("home"))

@app.route("/delete")
@login_required
def delete():
    db.session.delete(current_user)
    db.session.commit()
    flash("Account Deleted")
    return redirect(url_for("login"))

if __name__=="__main__":
    db.create_all()
    app.run()