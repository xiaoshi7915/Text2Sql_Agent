from app import create_app
from flask_jwt_extended import create_access_token

app = create_app()
with app.app_context():
    token = create_access_token(identity=1)
    print(token) 