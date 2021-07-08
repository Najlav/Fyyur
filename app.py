#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import exc
from sqlalchemy import func
from forms import *
from Models import *
import dateutil.parser
import json
import babel
import logging
import sys
from flask import (
    Flask, 
    render_template, 
    request, 
    Response, 
    flash, 
    redirect, 
    url_for
)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues') 
def venues():
  
  locals = []
  venues = Venue.query.all()
  places = Venue.query.distinct(Venue.city, Venue.state).all()

  for place in places:
      locals.append({
        'city': place.city,
        'state': place.state,
        'venues': [{
            'id': venue.id,
            'name': venue.name,
        } for venue in venues if
            venue.city == place.city and venue.state == place.state]
    })
  return render_template('pages/venues.html', areas=locals);

@app.route('/venues/search', methods=['POST'])
def search_venues():

  search_term = request.form.get('search_term', '');
  results = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()
  response_data = []

  for result in results:
    response_data.append({
      "id": result.id,
      "name": result.name,
      })
  
  response={
    "count": len(results),
    "data":  response_data
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  
  genres =[]
  TheVenue= Venue.query.get(venue_id);  
  venues_geners=TheVenue.genres
  for genre in venues_geners:
     genres.append(genre);
  
  
  upcoming_shows =[]
  past_shows =[]
  current_time = datetime.utcnow()
  shows= Show.query.join(Artist).join(Venue).all()

  for s in shows:
    if ((s.Start_Time >= current_time) and (s.Venue_ID == venue_id)):  
     artists = Artist.query.get(s.Artist_ID)
     upcoming_shows.append({
        "artist_id": s.Artist_ID,
        "artist_name": artists.name,
        "artist_image_link":artists.image_link,
        "start_time": str( s.Start_Time)
      })

  for s in shows:
    if ((s.Start_Time < current_time) and (s.Venue_ID == venue_id)):  
     artists = Artist.query.get(s.Artist_ID)
     past_shows.append({
        "artist_id": s.Artist_ID,
        "artist_name": artists.name,
        "artist_image_link":artists.image_link,
        "start_time": str( s.Start_Time)
      })

  data = {
    "id": venue_id,
    "name": TheVenue.name ,
    "genres": genres,
    "address": TheVenue.address,
    "city": TheVenue.city,
    "state": TheVenue.state,
    "phone": TheVenue.phone,
    "website": TheVenue.website_link,
    "facebook_link": TheVenue.facebook_link ,
    "seeking_talent": TheVenue.seeking_talent,
    "seeking_description": TheVenue.seeking_description,
    "image_link": TheVenue.image_link,
    "past_shows": past_shows ,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  failed=False

  try: 
    Name = request.form.get('name' );
    city = request.form.get('city' );
    state = request.form.get('state' );
    Address = request.form.get('address');
    Phone = request.form.get('phone');
    Genres = request.form.getlist('genres')
    Facebook_Link = request.form.get('facebook_link');
    Image_Link = request.form.get('image_link' );
    Website_Link = request.form.get('website_link' );
    seeking_talent = request.form.get('seeking_talent' );
    seeking_description = request.form.get('seeking_description');

    if (seeking_talent=='y') :
        seeking_talent=True
    else:
       seeking_talent=False

    if (( not seeking_description ) and (seeking_talent==True)):
          flash(' Venue was not listed, please write a seeking Description')
          return render_template('pages/home.html')

    venue = Venue(name=Name , city=city , state=state , address=Address , phone=Phone , image_link=Image_Link ,facebook_link=Facebook_Link , website_link=Website_Link , seeking_talent=seeking_talent , seeking_description=seeking_description , genres=Genres)
    db.session.add(venue)
    db.session.commit()
  except exc.SQLAlchemyError:
    db.session.rollback()
    failed=True
    error_desc= sys.exc_info()
  finally:
    db.session.close()

  # on successful db insert, flash success
  if failed==False :
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  else:
     flash('An error occurred, Venue' + request.form['name'] + ' could not be listed. Error description:'+ error_desc)
  
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
 
  # delete the venue from all tables
  venue = Venue.query.get(venue_id)
  Show.filter_by(Venue_ID=venue_id).delete()
  Genre.query.filter_by(name=venue.name).delete()
  Venue.query.filter_by(id=venue_id).delete()

  try:
    db.session.commit()
  except exc.SQLAlchemyError:
    db.session.rollback()
  finally :
     db.session.close()
  
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  
  data=[]
  artists = Artist.query.all()
  
  for artist in artists:
   data.append({
    "id": artist.id,
    "name": artist.name
    })
  
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  
  search_term = request.form.get('search_term', '');
  results = db.session.query(Artist).filter(Artist.name.ilike(f'%{search_term}%')).all()
  response_data = []

  for result in results :
    response_data.append({
      "id": result.id,
      "name": result.name,
      })
    
  response={
    "count": len(results),
    "data":  response_data
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  
  artist = Artist.query.get(artist_id);  
  artist_generes=artist.genres
  genres =[]
  
  for genre in artist_generes:
     genres.append(genre);
  
  shows = Show.query.join(Artist).join(Venue).all()
  current_time = datetime.utcnow()
  upcoming_shows =[]
  past_shows =[]
 
  for s in shows:
    if ((s.Start_Time >= current_time) and (s.Artist_ID == artist_id)):  
     venue =db.session.query(Venue).filter(Venue.id == s.Venue_ID).first()
     upcoming_shows.append({
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link ,
      "start_time": str( s.Start_Time)
    
      })

  for s in shows:
    if (s.Start_Time < current_time) and (s.Artist_ID == artist_id):  
     venue =db.session.query(Venue).filter(Venue.id == s.Venue_ID).first()
     past_shows.append({
      "venue_id": venue.id,
      "venue_name": venue.name,
      "venue_image_link": venue.image_link ,
      "start_time": str( s.Start_Time)
    
      })

  data={
    "id": artist_id,
    "name": artist.name,
    "genres": genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description":artist.seeking_description ,
    "image_link": artist.image_link,
    "past_shows":past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),

  }


  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id);  
  artist_generes=artist.genres
  genres =[]
  
  for genre in artist_generes:
     genres.append(genre);
 
 
  artist={
    "id": artist_id,
    "name": artist.name,
    "genres": genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description":artist.seeking_description ,
    "image_link": artist.image_link
  }

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  
  try:
    artist = Artist.query.get(artist_id);  
    Name = request.form.get('name');
    city = request.form.get('city');
    state = request.form.get('state');
    Phone = request.form.get('phone');
    Genres = request.form.getlist('genres')
    Facebook_Link = request.form.get('facebook_link');
    Image_Link = request.form.get('image_link' );
    Website_Link = request.form.get('website_link');
    seeking_venue = request.form.get('seeking_venue');
    Seeking_description = request.form.get('seeking_description');

    if seeking_venue=='y':
       seeking_venue=True
    else:
        seeking_venue=False
 

    if Name :
       artist.name = Name
    if city :
       artist.city = city
    if state :
       artist.state = state 
    if Phone :
       artist.phone = Phone 
    if Facebook_Link :
       artist.facebook_link = Facebook_Link
    if Image_Link :
       artist.image_link = Image_Link
    if Website_Link :
       artist.website_link = Website_Link
    artist.seeking_venue = seeking_venue

    if ((Seeking_description ) and (seeking_venue == True)):
        artist.seeking_description = Seeking_description
    elif ((Seeking_description ) and (seeking_venue == False)):
         artist.seeking_description = None
    if (( not Seeking_description ) and (seeking_talent == True)):
           db.session.rollback()
           flash("Artist modificatiion was not listed because seeking description was required ")
           return render_template('pages/home.html')
  
    db.session.commit()
  except exc.SQLAlchemyError:
      db.session.rollback()
  finally:
      db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm() 
  selected_Venue = Venue.query.get(venue_id); 
  venue_genres= selected_Venue.genres
  genres =[]

  for genre in venue_genres:
     genres.append(genre);
 
 
  venue={
    "id": venue_id,
    "name":  selected_Venue.name,
    "genres": genres,
    "address":  selected_Venue.address ,
    "city":  selected_Venue.city,
    "state":  selected_Venue.state,
    "phone":  selected_Venue.phone,
    "website": selected_Venue.website_link,
    "facebook_link":  selected_Venue.facebook_link,
    "seeking_talent":  selected_Venue.seeking_talent,
    "seeking_description": selected_Venue.seeking_description ,
    "image_link":  selected_Venue.image_link
    }
 
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  
  try:
     Selected_Venue = Venue.query.get(venue_id);  
     Name = request.form.get('name');
     city = request.form.get('city');
     state = request.form.get('state');
     Address = request.form.get('address');
     Phone = request.form.get('phone' );
     Genres = request.form.getlist('genres')
     Facebook_Link = request.form.get('facebook_link');
     Image_Link = request.form.get('image_link' );
     Website_Link = request.form.get('website_link');
     seeking_talent = request.form.get('seeking_talent');
     Seeking_description = request.form.get('seeking_description');


     if seeking_talent=='y':
        seeking_talent=True
     else:
         seeking_talent=False
 

     if Name :
        Selected_Venue.name = Name
     if city :
        Selected_Venue.city = city
     if state :
        Selected_Venue.state = state
     if Phone :
        Selected_Venue.phone = Phone 
     if Facebook_Link :
        Selected_Venue.facebook_link = Facebook_Link
     if Image_Link :
        Selected_Venue.image_link = Image_Link
     if Website_Link :
        Selected_Venue.website_link = Website_Link
     if Address:
        Selected_Venue.address = Address
  
     Selected_Venue.seeking_talent = seeking_talent
  
    
     if ((Seeking_description ) and (seeking_talent == True)):
          Selected_Venue.seeking_description = Seeking_description
     elif ((Seeking_description ) and (seeking_talent == False)):
          Selected_Venue.seeking_description = None
     if (( not Seeking_description ) and (seeking_talent == True)):
           db.session.rollback()
           flash("Venue modificatiion was not listed because seeking description was required ")
           return render_template('pages/home.html')

     
     db.session.commit()
  except exc.SQLAlchemyError:
     db.session.rollback()
  db.session.close()
 

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

  try:
    failed=False
    Name = request.form.get('name' , '');
    city = request.form.get('city' , '');
    state = request.form.get('state' , '');
    Phone = request.form.get('phone' , '');
    Genres = request.form.getlist('genres')
    Facebook_Link = request.form.get('facebook_link' , '');
    Image_Link = request.form.get('image_link' , '');
    Website_Link = request.form.get('website_link' , '');
    seeking_venue = request.form.get('seeking_venue' , '');
    seeking_description = request.form.get('seeking_description' , '');

    if seeking_venue=='y':
       seeking_venue=True
    else:
       seeking_venue=False

    if (( not seeking_venue ) and (seeking_venue==True)):
          flash(' Venue was not listed, please write a seeking Description')
          return render_template('pages/home.html')

    artist= Artist(name=Name , city=city , state=state , phone=Phone , image_link=Image_Link ,facebook_link=Facebook_Link , website_link=Website_Link , seeking_venue=seeking_venue , seeking_description=seeking_description, genres=Genres )
    db.session.add(artist)
    db.session.commit()
  except exc.SQLAlchemyError:
    db.session.rollback()
    failed=True
    error_desc= sys.exc_info()
  finally:
    db.session.close()


  # on successful db insert, flash success
  if failed==False :
     flash('Artist ' + request.form['name'] + ' was successfully listed!')
  else:
     flash('An error occurred. Artist ' + Name + ' could not be listed. Error Description: ' + error_desc )

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

  data= []
  shows= Show.query.all()
  
  for show in shows:
    venue=Venue.query.get(show.Venue_ID)
    artist=Artist.query.get(show.Artist_ID)
    data.append({
        "venue_id": show.Venue_ID,
        "venue_name":venue.name ,
        "artist_id": show.Artist_ID,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": str(show.Start_Time)
      })

  
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  
  try:
     failed =False
     Artist_ID  = request.form.get('artist_id');
     Venue_ID  = request.form.get('venue_id');
     Start_Time = request.form.get('start_time');
     Artist_exists = db.session.query(Artist.id).filter_by(id=Artist_ID)
     Venue_exists = db.session.query(Venue.id).filter_by(id=Venue_ID)
  
     if ((Artist_exists is not None ) and (Venue_exists is not None)):
       try:
         show = Show(Artist_ID=Artist_exists ,Venue_ID=Venue_exists , Start_Time=Start_Time)
         db.session.add(show)
         db.session.commit()
       except exc.SQLAlchemyError:
         db.session.rollback()
         failed=True
         error_desc= sys.exc_info()
       finally:
         db.session.close()

       if failed == False:
          flash('Show was successfully listed!')
       else:
          flash('An error occurred. Show could not be listed. Error description: ' + str(error_desc))
     else:
        flash('Artist ID OR Venue ID does not exists')
  
  except exc.SQLAlchemyError:
         flash('please enter valid values')

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
