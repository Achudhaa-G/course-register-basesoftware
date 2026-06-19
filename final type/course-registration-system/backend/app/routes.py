from flask import Blueprint, jsonify
from flask import send_from_directory
import os


main = Blueprint('main', __name__)

@main.route("/")
def home():
    return jsonify({"message": "Welcome to the Course Registration System API"})

@main.route("/courses")
def get_courses():
    return jsonify({"courses": ["Math", "Science", "History"]})

@main.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(os.path.dirname(__file__), 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')
