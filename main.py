import os
import sys
import json
import time
import secrets
import logging
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, redirect, render_template, flash, send_file
from dankware import cls, clr, align, blue, blue_dim, blue_normal, white, white_normal, err

os.chdir(os.path.dirname(__file__))

# custom banner

def print_banner():
    cls()
    banner = "\n\n                                      \n _____ ____  _____    _____ _         \n|  _  |    \\|   __|  |  _  |_|_ _ _ _ \n|   __|  |  |   __|  |   __| |_'_| | |\n|__|  |____/|__|     |__|  |_|_,_|_  |\n                                 |___|\n"
    print(clr(align(banner), 4, colours=[blue, blue_dim, blue_normal, white, white_normal]))
    print(clr(align("s i r . d a n k <3\n\n"), colour_two=blue))
    
print_banner()

# disable logging
#logging.captureWarnings(False)
#logging.getLogger('werkzeug').disabled = True
requests.packages.urllib3.disable_warnings()

# vars

local_host = False
one_hour = 3600
one_day = 86400
one_week = 604800
one_month = 2592000
one_year = 31536000
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# NOTE: hardcoded for simplicity. Ideally these should be stored in a db / google sheets ( but since these are using json format, its really fast to read and write to them )

registered_users = json.loads(open('assets/registered_users.json', 'r').read())
signed_in_users = json.loads(open('assets/signed_in_users.json', 'r').read())
shared_files = json.loads(open('assets/shared_files.json', 'r').read())
tokens = json.loads(open('assets/tokens.json', 'r').read())

if not os.path.isdir('user_files'):
    os.mkdir('user_files')
os.chdir('user_files')

# app routes

@app.route('/', methods=['GET'])
def index():
    return redirect('/dashboard')

# for uptime robot monitoring

@app.route('/uptime-robot', methods=['GET'])
def uptime_robot():
    return '<pre>Up!</pre>', 200

@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    
    if request.method == 'GET':

        ip = get_ip()
        if user_signed_in(ip):
            return redirect('/dashboard')
        else:
            return render_template('sign-up.html'), 200

    else:
        
        _redirect = False
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        ip = get_ip()
        
        # validity checks
        
        if len(name) < 3 or name.isdigit() or name.replace(' ', '') == '':
            flash('Invalid name!'); _redirect = True
        if not "@" in email or not "." in email or len(email) < 6:
            flash('Invalid email!'); _redirect = True  
        elif email in get_registered_emails():
            flash('Email already registered!'); _redirect = True
        if len(password) < 8:
            flash('Password must be at least 8 characters long!'); _redirect = True
        if _redirect:
            return redirect('/sign-up')
        else:

            registered_users[email] = {"name": name, "hash": generate_password_hash(password), "ips": [ip]}
            signed_in_users[ip] = {"valid_time": time.time() + one_day, "email": email}
            shared_files[email] = {}
            
            return redirect('/dashboard')

@app.route('/sign-in', methods=['GET', 'POST'])
def sign_in():

    if request.method == 'GET':

        ip = get_ip()
        if user_signed_in(ip):
            # log ip
            email = get_email(ip)
            add_ip_to_log(ip, email)
            return redirect('/dashboard')
        else:
            return render_template('sign-in.html'), 200

    else:
        
        ip = get_ip()
        _redirect = False
        email = request.form['email']
        password = request.form['password']
        
        # validity checks
        
        if not "@" in email or not "." in email or len(email) < 6:
            flash('Invalid email!'); _redirect = True
        elif not email in get_registered_emails():
            flash('Email not registered!'); _redirect = True 
        if len(password) < 8:
            flash('Invalid Password!'); _redirect = True
        if _redirect:
            return redirect('/sign-in')
        else:
            if check_password_hash(registered_users[email]["hash"], password):
                add_ip_to_log(ip, email)
                signed_in_users[ip] = {"valid_time": time.time() + one_day, "email": email}
                return redirect('/dashboard')
            else:
                flash('Wrong Password!')
                return redirect('/sign-in')

@app.route('/sign-out', methods=['GET'])
def sign_out():
    
    ip = get_ip()
    if ip in get_signed_in_ips():
        signed_in_users[ip]["valid_time"] = 0
    else:
        flash('Unauthorised!')
    return redirect('/sign-in')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    
    ip = get_ip()

    if user_signed_in(ip):
        
        email = get_email(ip)
        
        if request.method == 'GET':
            
            # show files and comments
            
            files, comments = [], []
            for file in get_user_files(email):
                if os.path.isfile(f"{email}/{file}") or os.path.isfile(tokens[get_token(email, file)]["path"]):
                    token = get_token(email, file)
                    files.append({"name": file, "url": "/download?token=" + token})
                    comments += tokens[token]["comments"]
            
            return render_template('dashboard.html', files=files, comments=comments), 200
    
        else:
            
            try:
                
                # save comment for specified file

                file = request.form['file']
                comment = request.form['comment']
                
                if file in get_user_files(email):

                    current_datetime = datetime.now()
                    day = current_datetime.day
                    month = current_datetime.strftime("%b")
                    year = current_datetime.year
                    token = get_token(email, file)
                    tokens[token]["comments"].append({"file": file, "text": comment, "user": email.split('@')[0], "date": f"{day}/{month}/{year}"})

                else:
                    flash('File not found!')

            except:
                flash('Failed to post comment!')
            
            return redirect('/dashboard')

    else:
        flash('Unauthorised!')
        return redirect('/sign-in')

@app.route('/download', methods=['GET'])
def download_pdf():
    
    ip = get_ip()
    
    if user_signed_in(ip):
        
        email = get_email(ip)
        
        # check if token is valid and then send file
        
        try: 
            token = request.args.get('token')
            file = tokens[token]["path"].split('/')[-1] # watch out for path error!
            if token in tokens.keys() and (tokens[token]["path"].startswith(email) or token == get_token(email, file)):
                return send_file(("user_files/" + tokens[token]["path"]), mimetype='application/pdf') # watch out for path error!
            else:
                flash('Invalid Token!')
        except:
            flash('Missing Token!')
        
        return redirect('/dashboard')
            
    else:
        flash('Unauthorised!')
        return redirect('/sign-in')

@app.route('/upload', methods=['GET', 'POST'])
def upload_pdf():

    ip = get_ip()
    if user_signed_in(ip):
        
        if request.method == 'POST':

            email = get_email(ip)
            
            # save file and generate token
            
            try:
                file = request.files['file']
                
                if file.filename == '':
                    flash('No file selected!')
                elif not file.filename.endswith('.pdf'):
                    flash('Invalid file type!')
                elif len(file.filename) > 100:
                    flash('File name too long!')
                elif len(file.read()) > 10000000:
                    flash('File size too large!')
                else:

                    path = f"{email}/{file.filename}"
                    if os.path.isfile(path):
                        os.remove(path)
                    if not os.path.isdir(email):
                        os.mkdir(email)
                    file.save(path)

                    if not file.filename in get_user_files(email):
                        token = generate_token()
                        shared_files[email][file.filename] = token
                        tokens[token] = {"path": path, "comments": []} # watch out for path error!

            except:
                flash('Failed to upload file!')
        
        return redirect('/dashboard')
            
                
    else:
        flash('Unauthorised!')
        redirect('/sign-in')

@app.route('/share', methods=['GET', 'POST'])
def share_pdf():
    
    ip = get_ip()
    if user_signed_in(ip):
        
        email = get_email(ip)
        
        if request.method == 'GET':

            # show files

            files = []
            for file in get_user_files(email):
                if os.path.isfile(f"{email}/{file}"):
                    files.append({"name": file})
            
            return render_template('share.html', files=files), 200
            
        else:
            
            try:

                file = request.form['file']
                receiver_email = request.form['email']
                
                if file in get_user_files(email):
                    if not "@" in email or not "." in email or len(email) < 6:
                        flash('Invalid email!')
                    elif receiver_email in get_registered_emails():
                        if file not in shared_files[receiver_email].keys():
                            token = get_token(email, file)
                            shared_files[receiver_email][file] = token
                        else:
                            flash('File already shared! Please rename it!')
                    else:
                        flash('Receiver email not registered!')
                else:
                    flash('File not found!')   

            except:
                flash('Failed to share file!')
                
            return redirect('/share')

    else:
        flash('Unauthorised!')
        return redirect('/sign-in')

# logic

def save_dicts():
    
    path = os.path.dirname(__file__) + '/assets/' # watch out for path error!
    while True:
        time.sleep(600)
        open(path + 'registered_users.json', 'w+').write(json.dumps(registered_users, indent=4))
        open(path + 'signed_in_users.json', 'w+').write(json.dumps(signed_in_users, indent=4))
        open(path + 'shared_files.json', 'w+').write(json.dumps(shared_files, indent=4))
        open(path + 'tokens.json', 'w+').write(json.dumps(tokens, indent=4))

def generate_token():
    
    while True:
        token = ''.join(secrets.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(16))
        if token not in tokens.keys():
            break
    return token

# shortcuts for better readability

def user_signed_in(ip):
    
    if ip in get_signed_in_ips() and signed_in_users[ip]["valid_time"] > time.time():
        return True
    else:
        return False

def get_ip():
    
    if not local_host:
        ip = request.headers['X-Forwarded-For'].split(', ')[0]
    else:
        ip = request.remote_addr
    return ip

def get_signed_in_ips():
    
    return signed_in_users.keys()
        
def get_registered_emails():
        
    return registered_users.keys()

def get_email(ip):
    
    return signed_in_users[ip]["email"]

def add_ip_to_log(ip, email):
    
    if ip not in registered_users[email]["ips"]:
        registered_users[email]["ips"].append(ip)
     
def get_user_files(email):
    
    return shared_files[email].keys()

def get_token(email, file):
    
    return shared_files[email][file]

if __name__ == "__main__":
    executor = ThreadPoolExecutor(max_workers=100)
    executor.submit(save_dicts)
    port = int(os.environ.get("PORT", 443))
    app.run(host='0.0.0.0', port=port, threaded=True)