#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
Migrate = Migrate(app , db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Show(db.Model):
   __tablename__ = 'Show'
   id = db.Column(db.Integer, primary_key=True )
   Artist_ID = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
   Venue_ID = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
   Start_Time = db.Column(db.DateTime, nullable=False ,default=datetime.utcnow())

class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String ,  nullable=False)
    city = db.Column(db.String(120) ,  nullable=False)
    state = db.Column(db.String(120) ,  nullable=False)
    address = db.Column(db.String(120) ,  nullable=False)
    phone = db.Column(db.String(120) ,  nullable=False)
    image_link = db.Column(db.String(500) ,  nullable=False)
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent =db.Column(db.Boolean, default=False)
    seeking_description =db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String))
    Shows = db.relationship('Show', backref="venue")


class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String , nullable=False)
    city = db.Column(db.String(120) , nullable=False)
    state = db.Column(db.String(120) , nullable=False)
    phone = db.Column(db.String(120) , nullable=False)
    image_link = db.Column(db.String(500) , nullable=False)
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description =db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String))
    Shows = db.relationship('Show', backref="artist")
    