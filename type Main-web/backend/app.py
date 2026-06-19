from flask import Flask
from flask_cors import CORS
from database import db_init
from routes import register_routes
from flask_jwt_extended import JWTManager
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.config["JWT_SECRET_KEY"] = "supersecretkey"
jwt = JWTManager(app)

CORS(app)  # Enable CORS
db_init(app)  # Initialize Database
register_routes(app)  # Register API Routes

if __name__ == "__main__":
    app.run(debug=True)
