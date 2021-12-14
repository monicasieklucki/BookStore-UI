import os
import secrets
import requests
import json
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort, session
from flaskApp import app, db, bcrypt
from flaskApp.forms import RegistrationForm, LoginForm, UpdateAccountForm, CustomerForm
from flaskApp.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required


'''@register.filter
def to_json(value):
    return mark_safe(simplejson.dumps(value))

@register.filter
def to_string(value):
    return mark_safe(simplejson.dumps(value))'''

hostname = "http://localhost:8080/"
#hostname = "http://book-store-luc.herokuapp.com/"
@app.route("/")
@app.route("/home")
def home():

    #entry point
    api_url = "http://book-store-luc.herokuapp.com/service/productservice/product"

    headers = {'content-type': 'application/json', 'Accept': 'application/json'}

    response = requests.get(api_url, headers=headers)
    json_response = json.loads(response.text)

    return render_template('home.html', products=json_response)

@app.route("/product", methods=['GET','POST'])
@app.route("/product/<path:Links>", methods=['GET','POST'])
def product(Links):
    print("in products")

    wrapped_string = (Links).replace("'", "\"")
    json_list = json.loads("[" + wrapped_string + "]")

    api_url = ""
    for obj in json_list:
        print(obj)

    #http://localhost:8080/productservice/product?productid=3
    #api_url = json_obj['url']
    #headers = {'content-type': 'application/' + json_obj['mediaType'], 'Accept': 'application/' + json_obj['mediaType']}

    #response = requests.get(api_url, headers=headers)

    #json_response = json.loads(response.text)
    #print(json_response)

    #print(json.loads(Links))
    #product = request.args.getlist('Links')
    #print(product)
    #api_url = "http://book-store-luc.herokuapp.com/service/productservice/product"

    return render_template('home.html')

@app.route("/product_detail")
def product_detail():
    #api_url = "http://book-store-luc.herokuapp.com/service/productservice/product"
    api_url = "http://book-store-luc.herokuapp.com/service/productservice/product"

    headers = {'content-type': 'application/json', 'Accept': 'application/json'}

    response = requests.get(api_url, headers=headers)
    #print(response)
    #print(response.text)

    json_response = json.loads(response.text)
    #print(json_response)

    return render_template('home.html', products=json_response)


@app.route("/about")
def about():
    print(session['customer'] )
    print(session['user'] )

    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        #entry point
        url = "http://book-store-luc.herokuapp.com/service/userservice/user"
        user = {'username': form.username.data, 'email': form.email.data, 'password': hashed_password}

        headers = {'content-type': 'application/json', 'Accept': 'application/json'}

        response = requests.post(url, data=json.dumps(user), headers=headers)
        json_response = json.loads(response.text)

        username = json_response['username']
        links = json_response['links']
        session['user'] = json_response
        print(session['user'])

        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        print("form validated")
        print(form.email.data)

        if len(session['user']) != 0:
            print(session['user'])
            print(session['user']['links'])
            for obj in session['user']['links']:
                mediatype = obj['mediaType']
                rel = obj['rel'] 
                url = obj['url']  
                if rel == "CreateCustomer":
                    headers = {'content-type': 'application/'+mediatype, 'Accept': 'application/'+mediatype}
                    print(url)
                    customer = {'username': session['user']['username']}
                    print(customer)                    #data=json.dumps(customer), 
                    response = requests.post(url, data=json.dumps(customer), headers=headers)

                    print(response)
                    print(response.text)
                    json_response = json.loads(response.text)
                    session['customer'] = json_response

                if rel == "GetUser":
                    headers = {'content-type': 'application/'+mediatype, 'Accept': 'application/'+mediatype}

                    response = requests.get(url, headers=headers)

                    json_response = json.loads(response.text)

                    user = User(id=json_response["id"],username=json_response["username"],email=json_response["email"],password=json_response["password"])
                    if user and bcrypt.check_password_hash(json_response["password"], form.password.data):
                        login_user(user, remember=form.remember.data)
                        next_page = request.args.get('next')
                        return redirect(next_page) if next_page else redirect(url_for('home'))
                    else:
                        flash('Login Unsuccessful. Please check email and password', 'danger')
        else: #not working I need to pass in username to retrieve correct response
            url = "http://book-store-luc.herokuapp.com/service/userservice/user/monica" #+form.email.data
            headers = {'content-type': 'application/json', 'Accept': 'application/json'}
            response = requests.get(url, headers=headers)

            json_response = json.loads(response.text)

            user = User(id=json_response["id"],username=json_response["username"],email=json_response["email"],password=json_response["password"])
            if user and bcrypt.check_password_hash(json_response["password"], form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('home'))
            else:
                flash('Login Unsuccessful. Please check email and password', 'danger')


    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)

@app.route("/customer", methods=['GET', 'POST'])
@login_required
def customer():
    form = CustomerForm()
    if form.validate_on_submit():

        links = session['customer']['links']
        for link in links:
            if link["rel"] == "UpdateCustomer":
                headers = {'content-type': 'application/'+link["mediatype"], 'Accept': 'application/'+link["mediatype"]}

                customer = {'firstname': form.firstname.data, 'lastname': form.lastname.data}

                response = requests.post(link["url"], data=json.dumps(customer), headers=headers)

        #current_user.username = form.username.data
        #current_user.email = form.email.data

        flash('Your account has been updated!', 'success')
        return redirect(url_for('customer'))
    elif request.method == 'GET':
        print("does nothing yet")
        #form.username.data = current_user.username
        #form.email.data = current_user.email
    return render_template('customer.html', title='Customer', form=form)

@app.route("/delete_customer", methods=['GET', 'POST'])
@login_required
def delete_customer():

    links = session['customer']['links']

    for link in links:
        if link['rel'] == "DeleteCustomer":
            url = link['url'] #+form.email.data
            headers = {'content-type': 'application/'+link["mediatype"], 'Accept': 'application/'+link["mediatype"]}
            response = requests.get(url, headers=headers)

    logout()
"""
@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')


@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))
"""