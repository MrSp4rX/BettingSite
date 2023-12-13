from flask import * b
import sqlite3, uuid, base64, random, requests
from urllib.parse import unquote
import datetime
from random import choice, randint

app = Flask(__name__)
api = "6320852128:AAF60s4Iyd-RKnan-xdLkzDZacBOG2gDj3Q"
admins = (6349757274, )
app.secret_key = "My Password"

@app.route("/", methods=["GET"])
def index():
    return "<script>window.alert ('Index Page Not Exist so Redirecting to Login'); window.location.href='/login';</script>"

def notify(msg):
    for admin in admins:
        r = requests.get(f"https://api.telegram.org/bot{api}/sendMessage?chat_id={admin}&text={msg}")

def get_bal(uuid):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute(f"""select balance from users where uuid = '{uuid}';""")
    balance = cur.fetchone()[0]
    return balance

def update_balance(uuid, amount, operator):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    balance = get_bal(uuid)
    if operator == "-":
        cur.execute(f"""Update users set balance = {balance - amount} where uuid = "{uuid}";""")
        conn.commit()
        return True
    elif operator == "+":
        cur.execute(f"""Update users set balance = {balance+amount} where uuid = "{uuid}";""")
        conn.commit()
        return True
    else:
        return False

@app.route("/andar_bahar", methods=["POST", "GET"])
def andar_bahar():
    if request.method == "GET":
        balance = get_bal(decode(str(session.get('token'))))
        return render_template("games/andar_bahar/index.html", balance=balance)
    elif request.method == "POST":
        choice = request.form.get("value")
        amount = int(request.form.get("amount"))
        balance = int(get_bal(decode(str(session.get('token')))))
        if amount <= int(get_bal(decode(str(session.get('token'))))):
            if amount >= 100:
                main = randint(0,10)
                if int(choice) == int(main):
                    if update_balance(decode(str(session.get('token'))), amount*0.98, "+"):
                        result = "success"
                    else:
                        return redirect(url_for("andar_bahar", type="danger", message="Something went Wrong!"))
                else:
                    if update_balance(decode(str(session.get('token'))), amount, "-"):
                        result = "failed"
                    else:
                        return redirect(url_for("andar_bahar", type="danger", message="Something went Wrong!"))
                return render_template("games/andar_bahar/result.html", choice=choice, main=main, result=result, balance=balance)
            else:
                return redirect(url_for("andar_bahar", type="warning", message="Bet can't be Less than 100 rs!"))
        else:
            return redirect(url_for("andar_bahar", type="danger", message="Insufficient Funds!"))
    else:
        return redirect(url_for("error", type="danger", message="Method not Allowed!"))


[
    {
        "ID":725100,
        "number":"AX-FLPKRT",
        "message":"Flipkart: Use OTP 477388 to log in to your account. DO NOT SHARE this code with anyone, including the delivery executive. @www.flipkart.com #477388",
        "deviceID":8803,
        "simSlot":0,
        "schedule":None,
        "userID":24372,
        "groupID":None,
        "status":"Received",
        "resultCode":None,
        "errorCode":None,
        "type":None,
        "attachments":None,
        "prioritize":None,
        "retries":None,
        "sentDate":"2023-10-20T13:55:11+0530",
        "deliveredDate":"2023-10-20T13:55:10+0530",
        "expiryDate":None
    }
]
@app.route("/recieve-payment", methods=["POST", "GET"])
def recSMS():
    messages = request.form.get("messages")
    print(messages)
    messages = messages[1:-1]
    message = json.loads(messages)
    message = message.get("message")
    if message.split()[1].lower() == "credited":
        data = {}
        by_index = message.split().index("by")
        avlbl_index = message.split().index("Avlbl")
        thru_index = message.split().index("thru")
        data['from'] = message.split()[by_index+1]
        data['date'] = message.split()[avlbl_index+1].split("(")[1]
        data['time'] = message.split()[avlbl_index+2].split(")")[0]
        data['amount'] = int(message.split()[0].split(".")[1])
        data['ref_number'] = int(message.split()[thru_index+1].split("/")[1])
        try:
            conn = sqlite3.connect("database.db")
            cur = conn.cursor()
            cur.execute(f"""insert into all_payments values ({data.get("amount")}, {data.get("ref_number")}, '{data.get("from")}', '{data.get("date")}', '{data.get("time")}');""")
            conn.commit()
            conn.close()
            notify(f"{data['from']} sent {data['amount']} rs from Ref No. {data['ref_number']} at Date - {data['date']} and Time - {data['time']}")
            return "success"
        except Exception as e:
            return str(e)
    else:
        return "failed"

@app.route("/recharge", methods=["GET"])
def recharge():
    if request.method == "GET":
        if session.get('token') != None:
            db = sqlite3.connect("database.db")
            cur = db.cursor()
            cur.execute(f"""
            select * from users where uuid = "{decode(str(session.get('token')))}";
            """)
            data = cur.fetchone()
            if data != None:
                db.close()
                notify(f"{request.remote_addr} is Requested Recharge Page.")
                
                return render_template("recharge.html", balance=get_bal(decode(str(session.get('token')))))
            else:
                notify(f"{request.remote_addr} is Trying to Access Recharge Page without Login.")
                return redirect(url_for("login", type="danger", message="Please Login First!"))
        
        elif session.get('token') != "":
            notify(f"{request.remote_addr} is Trying to Access Verify Payment Page with Invalid Token.")
            return redirect(url_for("error", type="danger", message="Invalid Token!"))

        elif session['token'] == None:
            notify(f"{request.remote_addr} is Trying to Access Profile Page without Login.")
            return redirect(url_for("login", type="danger", message="Please Login First!"))
        notify(f"{request.remote_addr} is Trying to Access Profile Page with Unknown Error.")
        return redirect(url_for("login", type="danger", message="Unknown Error Founded!"))
    else:
        return redirect(url_for("error", type="danger", message="Method not Allowed!"))

@app.route("/verify-payment", methods=["POST", "GET"])
def verify_payment():
    if request.method == "POST":
        if session.get('token') != None:
            if request.form['ref_number'] == "" or ";" in request.form['ref_number'] or "'" in request.form['ref_number'] or '"' in request.form['ref_number'] or "{" in request.form['ref_number'] or "}" in request.form['ref_number']:
                return redirect(url_for("error", type="danger", message="Reference ID should not contain Symbols or Special Characters."))
            db = sqlite3.connect("database.db")
            cur = db.cursor()
            cur.execute(f"""select * from users where uuid = "{decode(str(session.get('token')))}";""")
            data = cur.fetchone()
            if data != None:
                cur.execute(f"""select amount from all_payments where ref_number = {request.form['ref_number']};""")
                amount = cur.fetchone()
                if amount != None:
                    amount = amount[0]
                    cur.execute(f"""select balance from users where uuid = "{decode(str(session.get('token')))}";""")
                    balance = cur.fetchone()[0]
                    cur.execute(f"""Update users set balance = {amount+balance} where uuid = "{decode(str(session.get('token')))}";""")
                    db.commit()
                    cur.execute(f"""DELETE FROM all_payments WHERE ref_number = {request.form['ref_number']};""")
                    db.commit()
                    cur.execute(f"""insert into success_payments values ({amount}, {request.form['ref_number']}, '{str(datetime.datetime.now()).split()[0]}', '{str(datetime.datetime.now()).split()[1]}');""")
                    db.commit()
                    db.close()
                    return redirect(url_for("recharge", type="success", message="Balance has been Updated in your Account."))
                else:
                    return redirect(url_for("verify_payment", type="danger", message="Payment not Found. Enter Correct UTR or Reference Number!"))
            else:
                notify(f"{request.remote_addr} is Trying to Access Profile Page without Login.")
                return redirect(url_for("login", type="danger", message="Please Login First!"))
        
        elif session.get('token') != "":
            notify(f"{request.remote_addr} is Trying to Access Verify Payment Page with Invalid Token.")
            return redirect(url_for("error", type="danger", message="Invalid Token!"))

        elif session['token'] == None:
            notify(f"{request.remote_addr} is Trying to Access Profile Page without Login.")
            return redirect(url_for("login", type="danger", message="Please Login First!"))
        notify(f"{request.remote_addr} is Trying to Access Profile Page with Unknown Error.")
        return redirect(url_for("login", type="danger", message="Unknown Error Founded!"))
    elif request.method == "GET":
        if session.get('token') != None:
            db = sqlite3.connect("database.db")
            cur = db.cursor()
            cur.execute(f"""
            select * from users where uuid = "{decode(str(session.get('token')))}";
            """)
            data = cur.fetchone()
            if data != None:
                db.close()
                notify(f"{request.remote_addr} is Requested Verify Payment Page.")
                return render_template("get-payment.html", balance=get_bal(decode(str(session.get('token')))))
            else:
                notify(f"{request.remote_addr} is Trying to Access Profile Page without Login.")
                return redirect(url_for("login", type="danger", message="Please Login First!"))
        
        elif session.get('token') != "":
            notify(f"{request.remote_addr} is Trying to Access Verify Payment Page with Invalid Token.")
            return redirect(url_for("error", type="danger", message="Invalid Token!"))

        elif session['token'] == None:
            notify(f"{request.remote_addr} is Trying to Access Profile Page without Login.")
            return redirect(url_for("login", type="danger", message="Please Login First!"))
        notify(f"{request.remote_addr} is Trying to Access Profile Page with Unknown Error.")
        return redirect(url_for("login", type="danger", message="Unknown Error Founded!"))
    else:
        return redirect(url_for("error", type="danger", message="Method not Allowed!"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        data = unquote(request.get_data().decode())
        data = data.split("&")
        temp = {}
        for parameter in data:
            temp[parameter.split("=")[0]] = parameter.split("=")[1]
        required = ["username", "password", "confpassword", "email", "number"]
        for parameter in temp.keys():
            if parameter in required:
                pass
            else:
                notify(f"{request.remote_addr} is Trying to Register with Invalid Parameters.")
                return redirect(url_for("signup", type="alert", message="Invalid Parameters!"))
        
        if "." not in str(temp.get("email")) or "@" not in str(temp.get("email")):
            notify(f"{request.remote_addr} is Trying to Register with Invalid/Fake Mail ID.")
            return redirect(url_for("signup", type="danger", message="Invalid Mail ID!"))
        if str(temp.get("password")) != str(temp.get("confpassword")):
            return redirect(url_for("signup", type="alert", message="Passwords Mismatched!"))
        if len(str(temp.get("number"))) != 10:
            notify(f"{request.remote_addr} is Trying to Register with Invalid/Fake Mobile Number.")
            return redirect(url_for("signup", type="danger", message="Incorrect Mobile Number!"))
        
        try:
            db = sqlite3.connect("database.db")
            cur = db.cursor()
            cur.execute("""
            CREATE TABLE if not exists users (
                username VARCHAR(20) NOT NULL PRIMARY KEY,
                password VARCHAR(50) NOT NULL,
                email VARCHAR(50) NOT NULL,
                number INTEGER(10) NOT NULL,
                uuid VARCHAR NOT NULL
            );
            """)
            db.commit()
            cur.execute(f"""insert into users values ('{temp.get("username")}', '{temp.get("password")}', '{temp.get("email")}', {temp.get("number")}, '{str(uuid.uuid4())}', 0);""")
            cur.execute(f"""insert into payment_methods  ("username") VALUES ('{temp.get("username")}');""")
            db.commit()
            db.close()
            return redirect(url_for("login", type="success", message="Account Created! You can Login Now."))

        except Exception as e:
            if "unique" in str(e).lower():
                return redirect(url_for("signup", type="warning", message="Account Already Exist!"))
            else:
                return redirect(url_for("error", type="alert", message=str(e)))

    elif request.method == "GET":
        if "token" in session.keys():
            notify(f"{request.remote_addr} is Requested SignUp Page.")
            return redirect(url_for("dashboard", type="success", message="Already Logged in!"))
        notify(f"{request.remote_addr} is Requested SignUp Page.")
        return render_template("signup.html")

    else:
        notify(f"{request.remote_addr} is Trying to Request SignUp Page with Invalid Method Type.")
        return redirect(url_for("error", type="alert", message="Method Not Allowed!"))

@app.route("/dashboard", methods=["GET"])
def dashboard():
    if "token" in session.keys():
        token = session['token']
        data = decode(token)
        db = sqlite3.connect("database.db")
        cur = db.cursor()
        cur.execute(f"""select * from users where uuid = '{data}';""")
        new_data = cur.fetchone()
        balance = get_bal(decode(str(session.get('token'))))
        cur.execute(f"""select * from games;""")
        games = cur.fetchall()
        if new_data != None:
            if request.args.get("type") != None and request.args.get("message") != None:
                notify(f"{request.remote_addr} is Requested Dashboard Page.")
                return render_template("dashboard.html", type=request.args.get("type"), message=request.args.get("message"), games=games, balance=balance)
            notify(f"{request.remote_addr} is Requested Dashboard Page.")
            return render_template("dashboard.html", games=games, balance=balance)
        else:
            notify(f"{request.remote_addr} is Requested Dashboard Page with Invalid Token.")
            return redirect(url_for("error", type="danger", message="Invalid Token!"))
    else:
        notify(f"{request.remote_addr} is Trying to Access Dashboard without Being Logged In.")
        return redirect(url_for("login", type="danger", message="Please Login First!"))

@app.route("/logout", methods=["GET"])
def logout():
    if "token" in session.keys():
        session.clear()
        notify(f"{request.remote_addr} is Logged Out Successfully.")
        return redirect(url_for("login", type="success", message="Logged Out Successfully!"))

    else:
        return redirect(url_for("login", type="alert", message="Please Login First!"))

def encode(data):
    py_string = str(data)
    byte_msg = py_string.encode('ascii')
    base64_val = base64.b64encode(byte_msg)
    base64_string = base64_val.decode('ascii')
    return base64_string

def decode(data):
    py_string = data
    byte_msg = py_string.encode('ascii')
    base64_val = base64.b64decode(byte_msg)
    base64_string = base64_val.decode('ascii')
    return base64_string

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = unquote(request.get_data().decode())
        data = data.split("&")
        temp = {}
        for parameter in data:
            temp[parameter.split("=")[0]] = parameter.split("=")[1]
        if "username" in temp.keys() and "password" in temp.keys():
            db = sqlite3.connect("database.db")
            cur = db.cursor()
            cur.execute(f"""
            select * from users where username = '{temp["username"]}' and password = '{temp["password"]}';
            """)
            data = cur.fetchone()
            if data == None:
                db.close()
                notify(f"{request.remote_addr} is Trying to get Logged In with Invalid Credentials.")
                return redirect(url_for("login", type="danger", message="Incorrect Username or Password!!"))
            db.close()
            a = encode(data[-2])
            session['token'] = a
            notify(f"{request.remote_addr} is Logged In Successfully as {temp.get('username')}.")
            return redirect(url_for("dashboard", type="success", message=f"Logged in Successfully!",))
        else:
            notify(f"{request.remote_addr} is Trying to get Logged In Without all Required Credentials.")
            return redirect(url_for("login", type="alert", message="Please Provide All Credentials!"))

    elif request.method == "GET":
        if "token" in session.keys():
            notify(f"{request.remote_addr} is Tring to Access Login Page Again After getting Logged In.")
            return redirect(url_for("dashboard", type="success", message="Already Logged in!"))
        else:
            if request.args.get("type") != None and request.args.get("message") != None:
                notify(f"{request.remote_addr} is Trying to Login.")
                return render_template("login.html", type=request.args.get("type"), message=request.args.get("message"))
            notify(f"{request.remote_addr} is Trying to Login.")
            return render_template("login.html", )

    else:
        notify(f"{request.remote_addr} is Trying to Login with Invalid Method.")
        return redirect(url_for("error", type="alert", message="Method not Allowed"))

otp_dict = {}

def sendotp(number):
    otp = random.randint(100000, 999999)
    print("\n\n",otp, "\n\n")
    otp_dict[number] = otp
    return True 

@app.route("/forgetPassword", methods=["GET", "POST"])
def forgetPassword():
    if request.method == "POST":
        data = unquote(request.get_data().decode())
        data = data.split("&")
        temp = {}
        for parameter in data:
            temp[parameter.split("=")[0]] = parameter.split("=")[1]
        db = sqlite3.connect("database.db")
        cur = db.cursor()
        cur.execute(f"""
        select number from users where username = '{temp["username"]}';
        """)
        data = cur.fetchone()
        if data != None:
            number = data[0]
            res = sendotp(number)
            if res:
                session['number'] = number
                notify(f"{request.remote_addr} is Requested OTP for Password Reset as {temp.get('username')}.")
                return redirect(url_for("checkOtp", type="success", message="OTP sent Successfully!"))

            else:
                notify(f"{request.remote_addr} is Requesting OTP for Password Reset as {temp.get('username')} but Not Fullfil.")
                return redirect(url_for("forgetPassword", type="warning", message="Something Went Wrong!"))

        else:
            notify(f"{request.remote_addr} is Requesting OTP for Password Reset as {temp.get('username')} but Username does not Exist.")
            return redirect(url_for("forgetPassword", type="danger", message="Username not Exist!"))

    elif request.method == "GET":
        notify(f"{request.remote_addr} is Requested Password Reset Page.")
        return render_template("forget_password.html")

    else:
        notify(f"{request.remote_addr} is Requested Password Reset Page with Invalid Method Type.")
        return redirect(url_for("error", type="alert", message="Method not Allowed"))

@app.route("/checkOtp", methods=["GET", "POST"])
def checkOtp():
    if request.method == "POST":
        data = unquote(request.get_data().decode())
        data = data.split("&")
        temp = {}
        for parameter in data:
            temp[parameter.split("=")[0]] = parameter.split("=")[1]
        if "number" in session.keys():
            if temp.get("otp") == str(otp_dict[session['number']]):
                temp.get("otp") == str(otp_dict[session['number']])
                notify(f"{request.remote_addr} is Setting Up a New Password.")
                return render_template("set_password.html", type="success", message="Set New PAssword.")
            else:
                notify(f"{request.remote_addr} is Setting Up a New Password with Invalid OTP.")
                return redirect(url_for("checkOtp", type="danger", message="Invalid OTP!"))
        else:
            notify(f"{request.remote_addr} is Trying to Check OTP without Requesting.")
            return redirect(url_for("forgetPassword", type="warning", message="Generate OTP First!"))

    elif request.method == "GET":
        if "number" not in session.keys():
            notify(f"{request.remote_addr} is Trying to Check OTP without Requesting.")
            return redirect(url_for("forgetPassword", type="warning", message="Generate OTP First!"))
        notify(f"{request.remote_addr} is Entering OTP for Password Reset.")
        return render_template("check_otp.html", type=request.args.get("type"), message=request.args.get("message"))

    else:
        notify(f"{request.remote_addr} is Trying to Access Check OTP Page with Invalid Method Type.")
        return redirect(url_for("error", type="alert", message="Method not Allowed"))

@app.route("/setPassword", methods=["POST"])
def set_password():
    data = unquote(request.get_data().decode())
    data = data.split("&")
    temp = {}
    for parameter in data:
        temp[parameter.split("=")[0]] = parameter.split("=")[1]
    
    if temp['password'] == temp['confpassword']:
        if int(session['number']) in otp_dict.keys():
            try:
                db = sqlite3.connect("database.db")
                cur = db.cursor()
                cur.execute(f"""
                Update users set password = '{temp["password"]}' where number = {int(session["number"])};
                """)
                db.commit()
                db.close()
                notify(f"{request.remote_addr} has Changed Password of user Unknown and Number -  {session['number']}.")
                return redirect(url_for("login", type="success", message="Password Changed Successfully. You can Login Now"))
            except Exception as e:
                return str(e)
        else:
            notify(f"{request.remote_addr} is Trying to Set Password Before Entering OTP.")
            return redirect(url_for("forgetPassword", type="warning", message="Generate OTP First!"))

    else:
        notify(f"{request.remote_addr} is Trying to Set Password with Unmatched Passwords.")
        return redirect(url_for("forgetPassword", type="warning", message="Both Passwords are not Same!"))

@app.route("/error")
def error():
    if request.args.get("type") != None and request.args.get("message") != None:
        notify(f"{request.remote_addr} has got an Error and Redirected to /error.")
        return render_template("error.html", type=request.args.get("type"), message=request.args.get("message"))
    
    else:
        notify(f"{request.remote_addr} Accessed Error Page without Automatically Redirection.")
        return render_template("error.html", type="warning", message="Parameters Missing!")

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if request.method == "POST":
        data = unquote(request.get_data().decode())
        data = data.split("&")
        temp = {}
        for parameter in data:
            temp[parameter.split("=")[0]] = parameter.split("=")[1]
        try:
            a = int(temp['number'])
            if len(str(a)) != 10:
                notify(f"{request.remote_addr} is Trying to Update Invalid Mobile Number as {temp.get('username')}.")
                return redirect(url_for("profile", type="danger", message="Mobile Number is Incorrect!"))
        except:
            notify(f"{request.remote_addr} is Trying to Update Non Integer Mobile Number as {temp.get('username')}.")
            return redirect(url_for("profile", type="danger", message="Mobile Number should be Number not Text!"))
        if "." not in str(temp.get("email")) or "@" not in str(temp.get("email")):
            notify(f"{request.remote_addr} is Trying to Update Invalid Mail ID as {temp.get('username')}.")
            return redirect(url_for("profile", type="warning", message="Invalid Mail ID!"))
        if "username" in temp.keys() and "email" in temp.keys() and "number" in temp.keys():
            if temp['username'] == "":
                return redirect(url_for("profile", type="warning", message="Invalid Username!"))
            if session.get('token') != None:
                db = sqlite3.connect("database.db")
                cur = db.cursor()
                cur.execute(f"""
                select * from users where uuid = "{decode(str(session.get('token')))}";
                """)
                data = cur.fetchone()
                if data == None:
                    notify(f"{request.remote_addr} is Trying to Access Profile Page without Login.")
                    return redirect(url_for("login", type="danger", message="Please Login First!"))
                dataa = []
                for i in data:
                    dataa.append(i)
                del dataa[1]
                del dataa[-1]
                if temp.get("username") != dataa[0] or temp.get("email") != dataa[1] or str(temp.get("number")) != str(dataa[2]):
                    try:
                        if temp.get("username") != dataa[0]:
                            try:
                                cur.execute(f"""
                                Update users set username = '{temp["username"]}' where uuid = '{decode(str(session["token"]))}';
                                """)
                                db.commit()
                            except Exception as e:
                                return redirect(url_for("profile", type="danger", message=str(e)))

                        if temp.get("email") != dataa[1]:
                            try:
                                cur.execute(f"""
                                Update users set email = '{temp["email"]}' where uuid = '{decode(str(session["token"]))}';
                                """)
                                db.commit()
                            except Exception as e:
                                return redirect(url_for("profile", type="danger", message=str(e)))
                        if int(temp.get("number")) != dataa[2]:
                            try:
                                cur.execute(f"""
                                Update users set number = {int(temp["number"])} where uuid = '{decode(str(session["token"]))}';
                                """)
                                db.commit()
                            except Exception as e:
                                return redirect(url_for("profile", type="danger", message=str(e)))
                        
                        notify(f"{request.remote_addr} has Updated Profile Data as {temp.get('username')}.")
                        return redirect(url_for("profile", type="success", message="Changes Saved!"))
                    except Exception as e:
                        return redirect(url_for("profile", type="danger", message=f"Error Found - {str(e)}"))
                elif temp.get("username") == dataa[0] and temp.get("email") == dataa[1] and int(temp.get("number")) == dataa[2]:
                    notify(f"{request.remote_addr} is Trying to Update Same Values in Profile Data as {temp.get('username')}.")
                    return redirect(url_for("profile", type="danger", message="Same Values can't be Updated!"))
                else:
                    return redirect(url_for("profile", type="danger", message="Something went Wrong!"))
        else:
            notify(f"{request.remote_addr} is Trying to Update Profile Data with Invalid Parameters.")
            return redirect(url_for("profile", type="warning", message="Parameters are Missing!"))

    elif request.method == "GET":
        if session.get('token') != None:
            db = sqlite3.connect("database.db")
            cur = db.cursor()
            cur.execute(f"""
            select * from users where uuid = "{decode(str(session.get('token')))}";
            """)
            data = cur.fetchone()
            if data != None:
                dataa = []
                for i in data:
                    dataa.append(i)
                del dataa[1]
                del dataa[-1]
                db.close()
                notify(f"{request.remote_addr} is Requested Profile Page.")
                return render_template("profile.html", data=dataa, balance=get_bal(decode(str(session.get('token')))))
            else:
                notify(f"{request.remote_addr} is Trying to Access Profile Page without Login.")
                return redirect(url_for("login", type="danger", message="Please Login First!"))
        
        elif session.get('token') != "":
            notify(f"{request.remote_addr} is Trying to Access Profile Page with Invalid Token.")
            return redirect(url_for("error", type="danger", message="Invalid Token!"))

        elif session['token'] == None:
            notify(f"{request.remote_addr} is Trying to Access Profile Page without Login.")
            return redirect(url_for("login", type="danger", message="Please Login First!"))
        notify(f"{request.remote_addr} is Trying to Access Profile Page with Unknown Error.")

        return redirect(url_for("login", type="danger", message="Unknown Error Founded!"))

    else:
        notify(f"{request.remote_addr} is Trying to Access Profile Page with Invalid Method Type.")
        return redirect(url_for("error", type="alert", message="Method not Allowed")) 

@app.route("/delete", methods=["GET", "POST"])
def delete():
    if request.method == "POST":
        data = unquote(request.get_data().decode())
        data = data.split("&")
        temp = {}
        for parameter in data:
            temp[parameter.split("=")[0]] = parameter.split("=")[1]
        if "@" not in temp.get('email') and "." not in temp.get('email'):
            return render_template("delete_temp.html", type="warning", message="Invalid E-Mail ID Found!")
        if len(temp.get("number")) != 10:
            return render_template("delete_temp.html", type="warning", message="Invalid Mobile Number Found!")
        db = sqlite3.connect("database.db")
        cur = db.cursor()
        cur.execute(f"""select * from users where uuid = "{decode(str(session.get('token')))}" and username = "{temp.get('username')}" and password = "{temp.get('password')}" and email = "{temp.get('email')}" and number = "{temp.get('number')}";""")
        data = cur.fetchone()
        if data != None:
            cur.execute(f"""DELETE from users where username = '{temp.get("username")}' and password = '{temp.get("password")}' and email = '{temp.get("email")}' and number = '{temp.get("number")}' and uuid = '{decode(str(session["token"]))}';""")
            db.commit()
            cur.execute(f"""insert into deleted_users values ('{temp.get("username")}', '{temp.get("password")}', '{temp.get("email")}', {temp.get("number")}, '{str(session["token"])}');""")
            db.commit()
            db.close()
            session.clear()
            return redirect(url_for("login", type="success", message="Account has been Deleted Successfully!"))
        else:
            return render_template("delete_temp.html", type="warning", message="Invalid Credentials Found!")

    elif request.method == "GET":
        if session.get('token') != None:
            db = sqlite3.connect("database.db")
            cur = db.cursor()
            cur.execute(f"""
            select * from users where uuid = "{decode(str(session.get('token')))}";
            """)
            data = cur.fetchone()
            if data != None:
                return render_template("delete_temp.html", balance=get_bal(decode(str(session.get('token')))))
            else:
                notify(f"{request.remote_addr} is Trying to Access Delete Page with Incorrect Token.")
                return redirect(url_for("login", type="danger", message="Please Login First!"))
        
        elif session.get('token') != "":
            notify(f"{request.remote_addr} is Trying to Access Profile Page with Invalid Token.")
            return redirect(url_for("error", type="danger", message="Invalid Token!"))

        elif session['token'] == None:
            notify(f"{request.remote_addr} is Trying to Access Profile Page without Login.")
            return redirect(url_for("login", type="danger", message="Please Login First!"))
        notify(f"{request.remote_addr} is Trying to Access Profile Page with Unknown Error.")
        
        return redirect(url_for("login", type="danger", message="Unknown Error Founded!"))

    else:
        return redirect(url_for("error", type="danger", message="Method not Allowed!"))

def get_wallets(username):
    db = sqlite3.connect("database.db")
    cur = db.cursor()
    cur.execute(f"""select payment_methods from payment_methods where username = "{username}";""")
    data = cur.fetchone()
    data = json.loads(data[0])
    w = []
    for wallet in data['wallet']:
        for service in wallet:
            w.append(service)
    return set(w)

def get_twithdrawl(username):
    db = sqlite3.connect("database.db")
    cur = db.cursor()
    cur.execute(f"""select payment_methods from payment_methods where username = "{username}";""")
    data = cur.fetchone()
    data = json.loads(data[0])
    return data['total_withdrawls']

def notifyWithdrawl(**kwargs):
    try:
        if str(type(kwargs.get('payment_method'))) == "<class 'str'>":
            notify(f"User - {kwargs.get('username')} want to Withdraw {kwargs.get('amount')} INR in {kwargs.get('payment_method')}  with {kwargs.get('ip_address')} IP Address.")
        else:
            account_details = ""
            for key, value in kwargs.get('payment_method').items():
                if key == "ifsc_code":
                    account_details = account_details + "IFSC Code - " + value + ", "
                    continue
                account_details = account_details + key.replace("_", " ").title() + " - " + value + ", "
            notify(f"User - {kwargs.get('username')} wants to Withdraw {kwargs.get('amount')} INR in {account_details[0:-2]}  with {kwargs.get('ip_address')} IP Address.")
        return True
    except Exception as e:
        return False

def create_withdrawl(username, amount, payment_method, ip_address):
    try:
        db = sqlite3.connect("database.db")
        cur = db.cursor()
        cur.execute(f"""select withdrawls from payment_methods where username = "{username}";""")
        data = cur.fetchone()
        data = data[0].replace("'", '"')
        data = json.loads(data)
        data['total_withdrawls'] = data['total_withdrawls'] + 1
        data['withdrawl_history'].append({"1231231230":{"date":str(datetime.datetime.now()).split()[0], "time":str(datetime.datetime.now()).split()[1], "amount":amount, "payment_method":payment_method, "ip_address":ip_address}})
        data = str(data).replace('"', "'").strip()
        cur.execute(f'''update payment_methods set withdrawls = "{data}" where username = "{username}";''')
        db.commit()
        db.close()
        return True
    except Exception as e:
        print("Sqlite3 Error -", e)
        return False

def minus_balance(uuid, amount):
    try:
        conn = sqlite3.connect("database.db")
        cur = conn.cursor()
        cur.execute(f"""select balance from users where uuid = '{uuid}';""")
        balance = cur.fetchone()[0]
        balance = balance - amount
        cur.execute(f"""update users set balance = {balance} where uuid = '{uuid}';""")
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        return False

@app.route("/withdrawl", methods=["POST", "GET"])
def withdrawl():
    if request.method == "POST":
        if len(list(request.form.keys())) != 2 or "amount" not in request.form.keys():
            return redirect(url_for("withdrawl", type="warning", message="Please Choose 1 Payment Method and Enter Correct Amount."))
        form_data = {}
        form_data[str(list(request.form.keys())[0])] = str(list(request.form.values())[0])
        form_data[str(list(request.form.keys())[1])] = str(list(request.form.values())[1])
        bal = get_bal(decode(str(session.get('token'))))
        if int(form_data['amount']) <= bal:
            if session.get('token') != None:
                db = sqlite3.connect("database.db")
                cur = db.cursor()
                cur.execute(f"""select * from users where uuid = "{decode(str(session.get('token')))}";""")
                dataa = cur.fetchone()
                payment_methods = ""
                if dataa != None:
                    cur.execute(f"""select payment_methods from payment_methods where username = '{dataa[0]}';""")
                    data = str(cur.fetchone())[2:-3]
                    payment_methods = json.loads(data)
                    if int(form_data['amount']) < 50:
                        return redirect(url_for("withdrawl", type="warning", message="Minimum Withdraw value is 50 INR."))


                    elif list(form_data.keys())[0] == "upi":
                        for upi in payment_methods['upi']:
                            if str(form_data['upi'].split("@")[0][0:4]+"****@"+form_data['upi'].split("@")[1]) == upi.split("@")[0][0:4]+"****@"+upi.split("@")[1]:
                                if create_withdrawl(dataa[0], form_data['amount'], upi, request.remote_addr) and minus_balance(decode(str(session.get('token'))), int(form_data['amount'])):
                                    notifyWithdrawl(username=dataa[0], amount=form_data['amount'], payment_method=upi, ip_address=request.remote_addr)
                                    return redirect(url_for("withdrawl", type="success", message="Withdrawl has been Done! It will Credited within 24 to 36 Hours."))
                                return redirect(url_for("withdrawl", type="danger", message="Something Went Wrong."))


                    elif list(form_data.keys())[0] == "bank":
                        for bank in payment_methods['bank']:
                            if str(form_data['bank']) == bank['ifsc_code'][0:2] + "******" + bank['ifsc_code'][-3:] + " ****" + bank['account_number'][-4:]:
                                if create_withdrawl(dataa[0], form_data['amount'], bank, request.remote_addr) and minus_balance(decode(str(session.get('token'))), int(form_data['amount'])):
                                    notifyWithdrawl(username=dataa[0], amount=form_data['amount'], payment_method=bank, ip_address=request.remote_addr)
                                    return redirect(url_for("withdrawl", type="success", message="Withdrawl has been Done! It will Credited within 24 to 36 Hours."))
                                return redirect(url_for("withdrawl", type="danger", message="Something Went Wrong."))


                    elif list(form_data.keys())[0] in get_wallets(dataa[0]):
                        for wallet in payment_methods['wallet']:
                            wallet_name, wallet_number = list(wallet.keys())[0], list(wallet.values())[0]
                            if form_data[list(form_data.keys())[0]] == f"{wallet_name.capitalize()} - *******{wallet_number[7:]}":
                                if create_withdrawl(dataa[0], form_data['amount'], form_data[list(form_data.keys())[0]], request.remote_addr) and minus_balance(decode(str(session.get('token'))), int(form_data['amount'])):
                                    notifyWithdrawl(username=dataa[0], amount=form_data['amount'], payment_method=wallet, ip_address=request.remote_addr)
                                    return redirect(url_for("withdrawl", type="success", message="Withdrawl has been Done! It will Credited within 24 to 36 Hours."))
                                return redirect(url_for("withdrawl", type="danger", message="Something Went Wrong."))
                    return redirect(url_for("withdrawl", type="warning", message="Please Choose Correct Payment method."))
                else:
                    notify(f"{request.remote_addr} is Trying to Access Delete Page with Incorrect Token.")
                    return redirect(url_for("login", type="danger", message="Please Login First!"))
        else:
            return redirect(url_for("withdrawl", type="warning", message="Not having Enough Balance to Withdraw."))
    elif request.method == "GET":
        if session.get('token') != None:
            db = sqlite3.connect("database.db")
            cur = db.cursor()
            cur.execute(f"""
            select * from users where uuid = "{decode(str(session.get('token')))}";
            """)
            data = cur.fetchone()
            payment_methods = ""
            if data != None:
                cur.execute(f"""select payment_methods from payment_methods where username = '{data[0]}';""")
                data = str(cur.fetchone())[2:-3]
                payment_methods = json.loads(data)
                return render_template("withdrawl.html", payment_methods=payment_methods, balance=get_bal(decode(str(session.get('token')))))
            else:
                notify(f"{request.remote_addr} is Trying to Access Delete Page with Incorrect Token.")
                return redirect(url_for("login", type="danger", message="Please Login First!"))
        elif session.get('token') != "":
            notify(f"{request.remote_addr} is Trying to Access Profile Page with Invalid Token.")
            return redirect(url_for("error", type="danger", message="Invalid Token!"))

        elif session['token'] == None:
            notify(f"{request.remote_addr} is Trying to Access Profile Page without Login.")
            return redirect(url_for("login", type="danger", message="Please Login First!"))
        notify(f"{request.remote_addr} is Trying to Access Profile Page with Unknown Error.")
        return redirect(url_for("login", type="danger", message="Unknown Error Founded!"))

    else:
        return redirect(url_for("error", type="danger", message="Method not Allowed!"))

@app.route("/add_payment_method", methods=["POST", "GET"])
def add_payment_method():
    if request.method == "POST":
        if session.get('token') != None:
            db = sqlite3.connect("database.db")
            cur = db.cursor()
            cur.execute(f"""select * from users where uuid = "{decode(str(session.get('token')))}";""")
            dataa = cur.fetchone()
            if dataa != None:
                cur.execute(f"""select payment_methods from payment_methods where username = '{dataa[0]}';""")
                data = str(cur.fetchone())[2:-3]
                payment_methods = json.loads(data)
                data = request.form
                data = data.to_dict(flat=True)
                if (data.get("acc_name") == "" and data.get("acc_no") == "" and data.get("conf_acc_no") == "" and data.get("acc_ifsc") == "" and (data.get("wallet") == "paytm" or data.get("wallet") == "amazon_pay") and data.get("upi_id") != "" and data.get("number") == ""):
                    upi_id = data.get("upi_id")
                    if "@" in upi_id:
                        payment_methods['upi'].append(upi_id)
                        cur.execute(f'''update payment_methods set payment_methods = '{str(payment_methods).strip().replace("'", '"')}' where username = '{dataa[0]}';''')
                        db.commit()
                        return redirect(url_for("add_payment_method", type="success", message="UPI ID for Payments has been Added."))
                    else:
                        return redirect(url_for("add_payment_method", type="warning", message="Invalid UPI ID Provided!"))
                elif (data.get("acc_name") != "" and data.get("acc_no") != "" and data.get("conf_acc_no") != "" and data.get("acc_ifsc") != "" and (data.get("wallet") == "paytm" or data.get("wallet") == "amazon_pay") and data.get("upi_id") == "" and data.get("number") == ""):
                    acc_name = data.get("acc_name")
                    acc_no = data.get("acc_no")
                    conf_acc_no = data.get("conf_acc_no")
                    acc_ifsc = data.get("acc_ifsc").upper()
                    if conf_acc_no == acc_no and len(acc_no) > 7 and len(acc_ifsc) == 11:
                        bank_details = {
                            "acc_name":acc_name,
                            "account_number":acc_no,
                             "ifsc_code":acc_ifsc
                        }
                        payment_methods['bank'].append(bank_details)
                        cur.execute(f'''update payment_methods set payment_methods = '{str(payment_methods).strip().replace("'", '"')}' where username = '{dataa[0]}';''')
                        db.commit()
                        return redirect(url_for("add_payment_method", type="success", message="Bank Account for Payments has been Added."))
                    else:
                        return redirect(url_for("add_payment_method", type="warning", message=f"Please Enter Correct Bank Details."))
                elif (data.get("acc_name") == "" and data.get("acc_no") == "" and data.get("conf_acc_no") == "" and data.get("acc_ifsc") == "" and ((data.get("wallet") == "paytm"  or data.get("wallet") == "amazon_pay") and data.get("number") != "") and data.get("upi_id") == ""):
                    wallet = data.get("wallet")
                    number = data.get("number")
                    if len(number) == 10:
                        wallet_dict = {wallet : number}
                        payment_methods['wallet'].append(wallet_dict)
                        cur.execute(f'''update payment_methods set payment_methods = '{str(payment_methods).strip().replace("'", '"')}' where username = '{dataa[0]}';''')
                        db.commit()
                        return redirect(url_for("add_payment_method", type="success", message=f"{wallet} - {number} Wallet for Payments has been Added."))
                    else:
                        return redirect(url_for("add_payment_method", type="warning", message=f"Enter Correct Mobile Number for Wallet."))
                else:
                    return redirect(url_for("add_payment_method", type="warning", message="Please Continue with Correct Payment Method."))
            else:
                notify(f"{request.remote_addr} is Trying to Access Delete Page with Incorrect Token.")
                return redirect(url_for("login", type="danger", message="Please Login First!"))
        elif session.get('token') == None:
            notify(f"{request.remote_addr} is Trying to Access Profile Page without Logged in.")
            return redirect(url_for("login", type="danger", message="Please Login First!"))
        else:
            notify(f"{request.remote_addr} is Trying to Access Profile Page with Invalid Token.")
            return redirect(url_for("login", type="danger", message="Invalid Token!"))
    elif request.method == "GET":
        if session.get('token') != None:
            db = sqlite3.connect("database.db")
            cur = db.cursor()
            cur.execute(f"""
            select * from users where uuid = "{decode(str(session.get('token')))}";
            """)
            data = cur.fetchone()
            if data != None:
                cur.execute(f"""select payment_methods from payment_methods where username = '{data[0]}';""")
                data = str(cur.fetchone())[2:-3]
                payment_methods = json.loads(data)
                return render_template("payment_methods.html", payment_methods=payment_methods)
            else:
                notify(f"{request.remote_addr} is Trying to Access Delete Page with Incorrect Token.")
                return redirect(url_for("login", type="danger", message="Please Login First!"))
        elif session.get('token') != "":
            notify(f"{request.remote_addr} is Trying to Access Profile Page with Invalid Token.")
            return redirect(url_for("error", type="danger", message="Invalid Token!"))

        elif session['token'] == None:
            notify(f"{request.remote_addr} is Trying to Access Profile Page without Login.")
            return redirect(url_for("login", type="danger", message="Please Login First!"))
        
        else:
            notify(f"{request.remote_addr} is Trying to Access Profile Page with Unknown Error.")
            return redirect(url_for("login", type="danger", message="Unknown Error Founded!"))

    else:
        return redirect(url_for("error", type="danger", message="Method not Allowed!"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)