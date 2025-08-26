from flask import Flask, render_template, url_for, flash, redirect, request
from form import LoginForm
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import socket
import logging
from waitress import serve
import xml.etree.ElementTree as ET

app = Flask(__name__)
limiter = Limiter(get_remote_address, app=app)

app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config["RECAPTCHA_PUBLIC_KEY"] = "6LcpqOIjAAAAAI6SaP0MFgG5drQihqqCHTkXXZJe"
app.config["RECAPTCHA_PRIVATE_KEY"] = "6LcpqOIjAAAAAHN5yf8zfeatZacB2aXI0ztR3Rrb"


logging.basicConfig(filename='log.log', level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')

failed_login = {}
blacklist=[]

@app.route("/admin", methods=['GET', 'POST'])
def admin():
    return "Welcome to admin account"

@app.route("/error", methods=['GET', 'POST'])
def error():
    return render_template('403.html')

@app.route("/", methods=['GET', 'POST'])
# @limiter.limit('3/minute')
def login():
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)

    form = LoginForm()

    if request.method == 'GET':
        if ip in blacklist:
            return redirect(url_for("error"))
        else:
            logging.info(f'Get Request. IP Address: {ip}')

    else:
        if ip in blacklist:
            return redirect(url_for("error"))

        if form.email.data == "admin@gmail.com" and form.password.data == "P@ssw0rd":
            # return redirect(url_for("admin"))
            return "Welcome to admin account"

        else:
            flash(f"Invalid login attempt", "danger")
            logging.info(f'Unsuccessful login attempt. IP Address: {ip} | Email: {form.email.data}')

            if ip not in failed_login:
                failed_login[ip] = 1
            else:
                failed_login[ip] += 1
                if failed_login[ip] >= 10:
                    logging.critical(f'10 consecutive Unsuccessful login attempt. Potential Brute Force attack. IP Address: {ip} | Email: {form.email.data}')
                    failed_login[ip] = 0
                    blacklist.append(ip)
                    return redirect(url_for("error"))

    return render_template('login.html', form=form)

#Development or Production
mode = "prod"

if __name__ == '__main__':
    if mode == "dev":
        app.run(debug=True, port=7000)
    else:
        serve(app, port=7000, url_prefix="/myapp", threads=2)