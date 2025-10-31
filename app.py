from api.routes.employee import employee_bp
from api.routes.salary import salary_bp

from flask import Flask


app = Flask(__name__)

app.register_blueprint(employee_bp)
app.register_blueprint(salary_bp)
