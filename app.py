import os

from api.routes.auth import auth_bp
from api.routes.csv_data import csv_data_bp
from api.routes.employee import employee_bp
from api.routes.pdf_data import pdf_data_bp
from api.routes.salary import salary_bp
from api.routes.idempotency import idempotency_bp

from flask import Flask
from flask_jwt_extended import JWTManager


app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")

jwt = JWTManager(app)

app.register_blueprint(employee_bp)
app.register_blueprint(salary_bp)
app.register_blueprint(csv_data_bp)
app.register_blueprint(pdf_data_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(idempotency_bp)
