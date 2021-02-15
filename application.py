import os
from datetime import datetime
from flask import Flask, render_template, flash, redirect, url_for, session, request, jsonify
from flask_socketio import SocketIO, emit
from flask_bcrypt import Bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextField
from wtforms.validators import Required, Length, EqualTo


app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)
bcrypt = Bcrypt(app)
users = {}
messages = {}
channels = ['General']
counter = 0

# create a form to register user 
class RegistrationForm(FlaskForm):
    username = StringField("username", validators=[Required(), Length(min=2, max=20)])
    password = PasswordField("password", validators=[Required()])
    confirm_password = PasswordField("confirm password", validators=[Required(), EqualTo("password")])
    submit = SubmitField('Register')

# create a form to log in user 
class LoginForm(FlaskForm):
    username = StringField("username", validators=[Required(), Length(min=2, max=20)])
    password = PasswordField("password", validators=[Required()])
    submit = SubmitField('sign in')

#a form for creating a channel 
class ChannelForm(FlaskForm):
    channel = StringField('Channel name', validators=[Required(), Length(min=2, max=20)])
    submit = SubmitField('Create channel')

# the home route 
@app.route("/")
def index():
    form = RegistrationForm()
    return render_template("index.html", form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    """ Login the user in """
    form = LoginForm()
    if form.validate_on_submit():
        # make sure the credinationl are valide 
        if form.username.data in users and bcrypt.check_password_hash(users[form.username.data], form.password.data):
            session['username'] = form.username.data
            return redirect(url_for('home'))
        flash(" invalid username or password please try again", "danger")
    return render_template("login.html", form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    """ Login the user in """
    form = RegistrationForm()
    if form.validate_on_submit():
        # register the user if the user name is valide 
        if form.username.data not in users:
            users[form.username.data] = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
            flash('Username created you can now log in ', "success")
            return redirect(url_for('login'))
        flash("username taken please choose another one", "info")
    return render_template("index.html", form=form)

 # home route    
@app.route("/home")
def home():
    return render_template("home.html", channels=channels, users=users.keys())

# log the user out 
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))



@app.route("/channel", methods=['POST'])
def channel():
    """ Return all msgs send to a specific channel """
    channel = request.form.get('channel')
    if channel not in messages:
        return jsonify([])
    else:
        channel_msgs = messages[channel]
    return jsonify(channel_msgs)


@socketio.on('create channel')
def create(data):
    # create a chnannel if it's not alredy created 
    name = data['name']
    if name not in channels and len(name):
        channels.append(name)
        emit('channel name', {'name': name}, broadcast=True)
        

@socketio.on('new message')
def message(data):
    # recivieng messages and storing them in the app memory 
    global counter
    message = data['message']
    message_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    user = session['username']
    channel = data['channel']
    counter += 1
    if channel  not in messages.keys():
        messages[channel] = []
        messages[channel].append({'messages':message, 'user':user, 'message_time':message_time, 'message_id':counter})
        
    else:
        messages[channel].append(
            {'messages': message, 'user': user, 'message_time': message_time, 'message_id':counter})
        
        if len(messages[channel]) > 100:
            messages[channel].pop(0)
    
    emit('annonce message', {
         'message': message, 'message_time': message_time, 'user': user, 'message_id':counter}, broadcast=True)


@socketio.on('delete message')
def delete(data):
    """ delete user messages """
    channel = data['channel']
    message_id = data['message_id']
    print(channel)
    for msg in messages[channel]:
        if int(msg['message_id']) == int(message_id):
            messages[channel].remove(msg)




