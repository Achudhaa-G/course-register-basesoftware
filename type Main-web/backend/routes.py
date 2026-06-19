from flask import request, jsonify
from database import db, User, Course, Enrollment, bcrypt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import check_password_hash

def register_routes(app):

    # Register User
    @app.route("/register", methods=["POST"])
    def register():
        data = request.json
        hashed_password = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
        new_user = User(username=data["username"], password=hashed_password, role=data["role"])
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201

    # Login User and Generate Token
    @app.route("/login", methods=["POST"])
    def login():
        data = request.json
        user = User.query.filter_by(username=data["username"]).first()
        if user and check_password_hash(user.password, data["password"]):  # Ensure password is hashed
            access_token = create_access_token(identity={"id": user.id, "role": user.role})
            return jsonify({"access_token": access_token, "role": user.role})
        return jsonify({"message": "Invalid credentials"}), 401

    # Admin-Only: Add Course
    @app.route("/add_course", methods=["POST"])
    @jwt_required()
    def add_course():
        current_user = get_jwt_identity()
        if current_user["role"] != "admin":
            return jsonify({"message": "Access Denied: Admins Only"}), 403

        data = request.json
        new_course = Course(name=data["name"], instructor=data["instructor"])
        db.session.add(new_course)
        db.session.commit()
        return jsonify({"message": "Course added successfully"}), 201

    # Student-Only: Enroll in Course
    @app.route("/enroll", methods=["POST"])
    @jwt_required()
    def enroll():
        current_user = get_jwt_identity()
        if current_user["role"] != "student":
            return jsonify({"message": "Access Denied: Students Only"}), 403

        data = request.json
        new_enrollment = Enrollment(student_id=current_user["id"], course_id=data["course_id"])
        db.session.add(new_enrollment)
        db.session.commit()
        return jsonify({"message": "Enrolled successfully"}), 201
