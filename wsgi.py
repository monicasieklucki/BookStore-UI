from flask import Flask

app = Flask(__name__)

import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskApp import app, db, bcrypt
from flaskApp.forms import RegistrationForm, LoginForm, UpdateAccountForm
from flaskApp.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
def entry():
    return render_template('home.html')


if __name__ == "__main__":
    app.run()
