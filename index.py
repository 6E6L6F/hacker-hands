from flask import *
import subprocess
from database import Database
from datetime import *
import os
from flask import *
from flask_jwt_extended import *

app = Flask(__name__ , template_folder='template/' , static_folder='static/')
app.config["JWT_COOKIE_SECURE"] = False
app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
app.config["JWT_SECRET_KEY"] = "27211f4d1658c3603865c7d98327a11f35a96b24352732c58adc4679569cdffc175f2fdad248e6fa5d7426fdc4cf0b37"  # Change this in your code!
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)

jwt = JWTManager(app)

database = Database()

path_tools = database.read_tools()
tools_id = None
format_tools = {'go':'go run' , 'py':'python3'}

def get_logs():
    return os.listdir("logs/")

def get_cmd(data):
    cmd = ""
    if "&" in data:
        for i in data.split('&'):
            cmd += i.split('=')[1] + " "
    else:
        cmd = data.split("=")[1]
    return cmd
    
def write_logs(data , start_time , date):
    file_log = open(f'logs/{date}_{start_time}.txt' ,'a+')
    file_log.write(data)
    file_log.close()
    
def list_tools() -> list:
    global path_tools
    path_tools , info_tools = database.read_tools()
    return info_tools
    
@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(hours=24))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        return response
    
@app.route('/' , methods=['GET'])
def index():
    photos = database.get_photos()
    return render_template('index.html' , result=list_tools() , photo_list=photos)

@app.route("/tools/<id_>" , methods=['GET' , "POST"])
def tools(id_):
    global tools_name
    global path_tools
    global format_tools
    global tools_id
    if request.method == 'GET':
        tools_id = id_
        inputs , desc = database.get_tools(id_)
        return render_template("tools.html" , result=inputs , desc=desc)
    else:
        list_tools()
        args = get_cmd(request.get_data().decode())
        for path in path_tools:
            if path['id'] == tools_id:
                cmd = format_tools.get(path['path'].split('.')[1])
                dt = datetime.now()
                logs = subprocess.getoutput(f"{cmd} {path['path']} {args}")
                date = str(dt.today().year) + "-" + str(dt.today().month) + "-" + str(dt.today().day) 
                time = str(dt.today().hour) + ":" + str(dt.today().minute) + ":" + str(dt.today().second)
                database.write_logs(data=logs , start_time=time , date=date)
                write_logs(date=date , start_time=time , data=logs)
                return render_template("tools.html" 
                    ,info=[{'head':'the tools was end process','body':'process was end you can download log file in your panel'}] ,
                    logs=[{"result":logs}])
        return redirect('/')

    
@app.route("/login" , methods=["POST" , "GET"])
def login_page():
    if request.method != "POST":
        return render_template("login.html")
    else:
        dt = datetime.now()
        logs = "The User Try Login Ip : " + request.remote_addr
        date = str(dt.today().year) + "-" + str(dt.today().month) + "-" + str(dt.today().day) 
        time = str(dt.today().hour) + ":" + str(dt.today().minute) + ":" + str(dt.today().second)
        database.write_logs(data=logs , start_time=time , date=date)
        username = request.form["username"]
        password = request.form["password"]
        result = database.check_user(username=username , password=password)
        if result == True:
            response = redirect("/admin")
            access_token = create_access_token(identity="admin_user")
            set_access_cookies(response, access_token)
            return response
        else:
            return jsonify(msg="Unauthorized access"), 401

@app.route('/admin' , methods=["GET"])
@jwt_required()
def admin_panel():
    if request.args:
        dt = datetime.now()
        logs = f"The User Downlaod Log {request.args['log']} Ip : " + request.remote_addr
        date = str(dt.today().year) + "-" + str(dt.today().month) + "-" + str(dt.today().day) 
        time = str(dt.today().hour) + ":" + str(dt.today().minute) + ":" + str(dt.today().second)
        database.write_logs(data=logs , start_time=time , date=date)
        return send_file("logs/"+request.args['log'] , as_attachment="log.txt")
    
    return render_template("admin.html" , logs=get_logs() , tools_logs=database.get_logs())


if __name__ == "__main__":
    app.run("0.0.0.0" , 8080 , debug=True)



