from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150))
    name = db.Column(db.String(150))
    picture = db.Column(db.String(300))
    token = db.Column(db.String(500))
