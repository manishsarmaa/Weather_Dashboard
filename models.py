from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class FavoriteLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100), unique=True, nullable=False)
