from flask import Flask, render_template, redirect, abort, request
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = '150708'

def main():
    app.run(port=8080, host='127.0.0.1')

@app.route('/')
def mainstr():
    return render_template('main_str.html')


@app.route('/AboutUs')
def AboutUs():
    return render_template('about_us.html')


@app.route('/logging')
def logging():
    return render_template('log_in.html')


@app.route('/registering')
def registering():
    return render_template('register.html')


@app.route('/CreatePost')
def CreatePost():
    return render_template('create_post.html')





if __name__ == '__main__':
    main()