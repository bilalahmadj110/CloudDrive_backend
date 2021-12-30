import pathlib
import re
import secrets
import configparser
import shutil
import os
import sys

from flask import Flask, request, jsonify, url_for, send_file
from sqlalchemy.sql.operators import exists
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm
from wtforms import HiddenField, SubmitField, StringField
from wtforms.validators import Required
from datetime import datetime
from .helper import *
from quantiphy import Quantity
import mimetypes
from werkzeug.utils import secure_filename
import contextlib



# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()
config = configparser.ConfigParser(interpolation=None)
root = pathlib.Path(__file__).parent
config.read(root/"config.ini")
conf = config["DEFAULT"]

# Class email and person name validator
class Validator():
    
    def email(self, field):
        if re.match(r"[^@]+@[^@]+\.[^@]+", field):
            return True
        return False
    
    def name(self, field):
        if re.match(r"^[a-zA-Z ]+$", field):
            return True
        return False

class ProtoForm(FlaskForm):
    hidden = HiddenField("Hidden")
    name = StringField("Name", validators=[Required()])
    submit = SubmitField("Submit")


def create_app():
    app = Flask(__name__)

    dbroot = pathlib.Path(conf["localeDatabase"]).expanduser()
    dbpath = dbroot / "db.sqlite"
    dbpath.parent.mkdir(parents=True, exist_ok=True)

    app.config["SECRET_KEY"] = secrets.token_urlsafe(16)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{dbpath}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    csrf = CSRFProtect()
    csrf.init_app(app)

    
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table,
        # use it in the query for the user
        return User.query.get(int(user_id))
    
    from .explorer import explorer as explorer_blueprint
    from .auth import new_directory, auth as auth_blueprint
    from .explorer import validate_node, get_breadcrumbs, path_to_url, mimeicon
    
    def auth_required_api(func):
        def wrapper(*args, **kwargs):
            token = request.headers.get("Authorization") or request.headers.get("authorization")
            email = request.headers.get("email")
            if not email or not token:
                return jsonify({"message": "Please fill out all fields"}), 400
            email = email.lower().strip()
            user = User.query.filter_by(email=email).first()
            if not user:
                return jsonify({"message": "user doesn't exists"}), 401
            print (eval(user.token), token)
            if token not in eval(user.token):
                return jsonify({"message": "Invalid Token"}), 401    
            return func(*args, **kwargs)
        wrapper.__name__ = func.__name__
        return wrapper
    
    @app.route("/android/api/create", methods=["POST"])
    @csrf.exempt
    def create_user():
        """Create a user account"""
        print ("Create a use account")
        email = request.form.get("email") or request.form.get("username")
        password = request.form.get("password")
        name = request.form.get("name")
        if not email or not password or not name:
            return jsonify({"message": "Please fill out all fields"}), 400
        # validate the data
        if not (Validator().email(email) and len(name) > 2 and len(password) > 5):
            return jsonify({"message": "Invalid data"}), 400
        # check if the user already exists
        email = email.lower().strip()
        exists = User.query.filter_by(email=email).first()
        if exists:
            return jsonify({"message": "That email already exists"}), 400
         # create a new user with the form data. Hash the password so the plaintext version isn't saved.
        try:
            print (dir(auth_blueprint))
            new_user = User(
                email=email,
                name=name,
                password=generate_password_hash(password, method="sha256"),
                directory=new_directory(name, email),
                regdate=datetime.utcnow().date(),
            )

            # add the new user to the database
            db.session.add(new_user)
            db.session.commit()
            return jsonify({"message": "Account created"}), 200
        except Exception as e:
            print (e)
            return jsonify({"message": str(e)}), 500
       
    
    @app.route("/android/api/login", methods=["POST"])
    @csrf.exempt
    def login():
        """Log in a user"""
        email = request.form.get("email")
        password = request.form.get("password")
        if not email or not password:
            return jsonify({"message": "Please fill out all fields"}), 400
        # validate the data
        if not (Validator().email(email) and len(password) > 5):
            return jsonify({"message": "Invalid data"}), 400
        email = email.lower().strip()
        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"message": "User doesn't exists"}), 401
        if not check_password_hash(user.password, password):
            return jsonify({"message": "Please check your login details and try again."}), 401
        if not (root := pathlib.Path(user.directory)).exists():
            root.mkdir()
        # push token as a list
        random_token = secrets.token_urlsafe(16)
        if not user.token:
            user.token = str([random_token])
        else:
            user.token = str(eval(user.token) + [random_token])
        regData = user.regdate
        node = validate_node(None, (root := user.directory), True)
        print (node, root)
        
        list_dir = Helper().iterate(node, root)
               
        db.session.commit()
        
        # format regData
        regData = regData.strftime("%Y/%m/%d")
        return jsonify({"message": "Login successful", "token": random_token, 
                        "name": user.name, "email": user.email, "regdate": regData, "node": list_dir}), 200

        
    
    @app.route("/android/api/explorer/<path:node>", endpoint="sub")
    @app.route("/android/api/explorer/", defaults={"node": None})
    @app.route("/android/api/explorer", defaults={"node": None})
    @csrf.exempt
    @auth_required_api
    def explorer(node):
        """Get the explorer"""
        print (node)
        email = request.headers.get("email")
        email = email.lower().strip()
        user = User.query.filter_by(email=email).first() 
        node = validate_node(node, (root := user.directory), True) 
        
        print (email, user, node)
        if not node.exists():
            return jsonify({"message": "Node doesn't exists"}), 404   
        # this is a folder
        if node.is_dir():
            list_dir = Helper().iterate(node, root)
            print ('GET THIS', node, root)
            return jsonify({"message": "Success", "node": list_dir}), 200
        # if it's a file send the content to the user
        elif node.is_file():
            print ('send THIS', node, root)
            return send_file(node, as_attachment=True)
        else: # unknown
            return jsonify({"message": "Unknown"}), 404
        
    @app.route("/android/api/delete/<path:node>", endpoint="delete")
    @csrf.exempt
    @auth_required_api
    def delete(node):
        """Delete a file or folder"""
        email = request.headers.get("email")
        email = email.lower().strip()
        user = User.query.filter_by(email=email).first() 
        node = validate_node(node, (root := user.directory), True) 
        
        if not node.exists():
            return jsonify({"message": "Node doesn't exists"}), 404
        if node == pathlib.Path(root):
            return jsonify({"message": "Unknown"}), 404
        # this is a folder
        if node.is_dir():
            shutil.rmtree(node)
            return jsonify({"message": "Success"}), 200
        # if it's a file send the content to the user
        elif node.is_file():
            node.unlink()
            return jsonify({"message": "Success"}), 200
        else: # unknown
            return jsonify({"message": "Unknown"}), 404
    
    @app.post("/android/api/upload/<path:node>")
    @app.post("/android/api/upload/", defaults={"node": None})
    @app.post("/android/api/upload", defaults={"node": None})
    @csrf.exempt
    @auth_required_api
    def upload(node):
        """Upload a file"""
        print ("Uploading file...")
        email = request.headers.get("email")
        email = email.lower().strip()
        user = User.query.filter_by(email=email).first() 
        node = validate_node(node, (root := user.directory), True) 
        if not node.exists():
            return jsonify({"message": "Node doesn't exists"}), 404
        # this is a folder
        if node.is_dir():
            file = request.files.get("file")
            print (file)
            if not file:
                return jsonify({"message": "No file"}), 400
            
            filename = secure_filename(file.filename)
            new = validate_node(filename, node)
            print ('filename', new)
            print ("Saved:", os.path.join(node, filename))
            print ("root", root)
            print ('node', node)
            file.save(os.path.join(node, filename))
            # return filename to the user
            ret = Helper().get_info(new, root)
            ret["message"] = "Success"
            return jsonify(ret), 200
        
    @app.route("/android/api/mkdir/<path:node>")
    @app.route("/android/api/mkdir/", defaults={"node": None})
    @csrf.exempt
    @auth_required_api
    def mkdir(node):
        try:
            """Create a folder"""
            email = request.headers.get("email")
            email = email.lower().strip()
            user = User.query.filter_by(email=email).first() 
                    
            node = validate_node(node, (root := user.directory), True) 
            
            
            print (email, node, root)
            
            name = request.headers.get("name").rstrip(". ")
            if "./" in name or ".\\" in name:
                return jsonify({"message": "Relative path is not allowed in the directory name."}), 400
        
        
            new = validate_node(name, node)
            # check if new string is valid directory name
            print ("directory name", new)
            
            with contextlib.suppress(FileNotFoundError):
                new.mkdir(exist_ok=True)
                ret = Helper().get_info(new, root)
                ret["message"] = "Success"
                return jsonify(ret), 200
            return jsonify({"message": "Unknown"}), 404
        except Exception as e:
            # get exception line number
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            print (e)
            return jsonify({"message": "Something bad happend on our end, please try again with valid directory name"}), 400


    # blueprint for auth routes in our app
    # from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
 

    # blueprint for explorer routes in our app
    # from .explorer import explorer as explorer_blueprint
    app.register_blueprint(explorer_blueprint)

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
