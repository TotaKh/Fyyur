#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

from flask_migrate import Migrate
from datetime import datetime
import sys
 

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app , db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
  __tablename__ = 'venue'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  address = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  genres = db.Column(db.String(120))
  website = db.Column(db.String(120))
  seeking_talent = db.Column(db.Boolean , default = False)
  seeking_description = db.Column(db.String(120))
  artist = db.relationship('Show', backref='venue' , lazy='joined')

  def __repr__(self):
    return f'<Venue ID: {self.id}, name: {self.name} ,city: {self.city}>'


class Artist(db.Model):
  __tablename__ = 'artist'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String)
  city = db.Column(db.String(120))
  state = db.Column(db.String(120))
  phone = db.Column(db.String(120))
  genres = db.Column(db.String(120))
  image_link = db.Column(db.String(500))
  facebook_link = db.Column(db.String(120))
  website = db.Column(db.String(120))
  seeking_venue = db.Column(db.Boolean, default = False  )
  seeking_description = db.Column(db.String(120))
  venues = db.relationship('Show', backref='artist' , lazy='joined')
  
  def __repr__(self):
    return f'<Artist ID: {self.id}, name: {self.name}>'  


class Show(db.Model):
  __tablename__ = 'show'
  venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), primary_key=True)
  start_time = db.Column(db.DateTime, nullable = False )
  venues = db.relationship('Venue', backref='show_artist', lazy='joined')
  artists = db.relationship('Artist', backref='show_venue' , lazy='joined')

  def __repr__(self):
    return f'<Show venue_id: {self.venue_id}, artist_id: {self.artist_id}>'


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  if isinstance(value, str):
    date = dateutil.parser.parse(value)
  else:
    date = value
  #date = dateutil.parser.parse(value)
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

#  -------
#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # num_shows should be aggregated based on number of upcoming shows per venue.
  
  all_cites = Venue.query.group_by(Venue.city, Venue.state).with_entities(Venue.city, Venue.state).all()
  data = []

  for city in all_cites:
    venues = Venue.query.filter(Venue.state == city.state ,Venue.city == city.city).all()
    add_data = []
    add = []
    for venue in venues:
      add = {
        "id": venue.id,
        "name": venue.name, 
        "num_upcoming_shows":Show.query.filter(Show.venue_id == venue.id , Show.start_time > datetime.now()).count()
      }
      add_data.append(add)

    data.append({
      "city": city.city,
      "state": city.state, 
      "venues": add_data
    })

  return render_template('pages/venues.html', areas=data)

#  Search Venues
#  ----------------------------------------------------------------
@app.route('/venues/search', methods=['POST'])
def search_venues():
  # search on venues with partial string search. Ensure it is case-insensitive.
  search_term=request.form.get('search_term', '')
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  response={
    "count": len(venues),
    "data": []
    }

  for venue in venues:
    data = {
      "id" : venue.id ,
      "name" : venue.name,
      "num_upcoming_shows":Show.query.filter(Show.venue_id == venue.id , Show.start_time > datetime.now()).count()
    }
    response["data"].append(data)
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

#  Shows Venue Details 
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id   
  venue = Venue.query.get(venue_id)
  all_shows= Show.query.filter(Show.venue_id == venue_id).all()
  past_shows = []
  upcoming_shows = []
  
  for show in all_shows:
    if show.start_time < datetime.now():
      add =[{
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time
      }]
      past_shows.append(show)

    else:
      add =[{
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": show.start_time
      }]
      upcoming_shows.append(show)

  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres.split(','),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
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
  # insert form data as a new Venue record in the db

  error = False
  try:
    venue = Venue()
    venue.name = request.form.get('name')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.address = request.form.get('address')
    venue.phone = request.form.get('phone')
    venue.genres = request.form.getlist('genres')
    venue.facebook_link = request.form.get('facebook_link')
    
    db.session.add(venue)
    db.session.commit()
  except:
    db.session.rollback()
    error=True
    print(sys.exc_info())
  finally:
    db.session.close()

  if error:
    # on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')

#  Delete Venue  
#  ----------------------------------------------------------------
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # clicking that button delete it from the db then redirect the user to the homepage
  # taking a venue_id, and delete a record.
  error = False
  try:
    Show.query.filter(Show.venue_id == venue_id).delete()
    Venue.query.filter(Venue.id == venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    # on unsuccessful db delete, flash an error instead.
    flash('An error occurred. Venue could not be deleted.')
  else:
    # on successful db delete, flash success
    flash('Venue was successfully deleted!')

  return redirect(url_for('index'))

#  Update Venue  
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = Venue.query.get(venue_id)
  #populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  
  venue = Venue.query.get(venue_id)
  error = False
  try:
    venue.name = request.form.get('name')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.address = request.form.get('address')
    venue.phone = request.form.get('phone')
    venue.genres = request.form.getlist('genres')
    venue.facebook_link = request.form.get('facebook_link')
    
    db.session.commit()
  except:
    db.session.rollback()
    error=True
    print(sys.exc_info())
  finally:
    db.session.close()

  if error:
    # on unsuccessful db update, flash an error instead.
    flash('An error occurred. Venue ' + data.name + ' could not be updated.')
  else:
    # on successful db update, flash success
    flash('Venue ' + request.form['name'] + ' was successfully updated!')
  
  return redirect(url_for('show_venue', venue_id=venue_id))


#  -------
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # data returned from querying the database 
  data = Artist.query.all()
  return render_template('pages/artists.html', artists=data)

#  Search Artists
#  ----------------------------------------------------------------
@app.route('/artists/search', methods=['POST'])
def search_artists():
  # implement search on artists with partial string search. Ensure it is case-insensitive.
  search_term=request.form.get('search_term', '')
  artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  
  response={
    "count": len(artists),
    "data": []
    }

  for artist in artists:
    data = {
      "id" : artist.id ,
      "name" : artist.name,
      "num_upcoming_shows": Show.query.filter(Show.artist_id == artist.id , Show.start_time > datetime.now()).count()
    }
    response["data"].append(data)
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

#  Shows Artist Details
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id 
  
  artist = Artist.query.get(artist_id)
  all_shows= Show.query.filter(Show.artist_id == artist_id).all()
  past_shows = []
  upcoming_shows = []
  
  for show in all_shows:
    if show.start_time < datetime.now():
      add =[{
        "artist_id": artist.id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": show.start_time
      }]
      past_shows.append(show)

    else:
      add =[{
        "artist_id": artist.id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": show.start_time
      }]
      upcoming_shows.append(show)

  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.split(','),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update Artist 
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)

  # populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.get(artist_id)
  error=False
  try:
    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.genres = request.form.getlist('genres')
    artist.facebook_link = request.form.get('facebook_link')

    db.session.commit()
  except:
    db.session.rollback()
    error=True
    print(sys.exc_info())
  finally:
    db.session.close()

  if error:
    # on unsuccessful db update, flash an error instead.. done
    flash('An error occurred. Artist ' + data.name + ' could not be updated.')
  else:
    # on successful db update, flash success
    flash('Artist ' + request.form['name'] + ' was successfully updated!')

  return redirect(url_for('show_artist', artist_id=artist_id))

#  Create Artist
#  ----------------------------------------------------------------
@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # insert form data as a new Artist record in the db, 
  error=False
  try:
    artist = Artist()
    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.genres = request.form.getlist('genres')
    artist.facebook_link = request.form.get('facebook_link')

    db.session.add(artist)
    db.session.commit()
  except:
    db.session.rollback()
    error=True
    print(sys.exc_info())
  finally:
    db.session.close()

  if error:
    # on unsuccessful db insert, flash an error instead 
    flash('An error occurred. Artist could not be listed.')
  else:
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  
  return render_template('pages/home.html')

#  Delete Artist  
#  ----------------------------------------------------------------
@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  # taking a artist_id, and delete a record.
  error = False
  try:
    Show.query.filter(Show.artist_id == artist_id).delete()
    Artist.query.filter(Artist.id == artist_id).delete()
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    # on unsuccessful db delete, flash an error instead.
    flash('An error occurred. Artist could not be deleted.')
  else:
    # on successful db delete, flash success
    flash('Artist was successfully deleted!')

  return redirect(url_for('index'))


#  -------
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows  
  all_shows = db.session.query(Show).join(Venue).join(Artist).all()
  data = []
  for show in all_shows:
    details = {
      "venue_id": show.venue_id ,
      "venue_name": show.venue.name ,
      "artist_id": show.artist_id ,
      "artist_name": show.artist.name ,
      "artist_image_link": show.artist.image_link ,
      "start_time": show.start_time
    }
    data.append(details)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  error = False
  try:
    show = Show()
    show.artist_id = request.form.get('artist_id')
    show.venue_id = request.form.get('venue_id')
    show.start_time = request.form.get('start_time')

    db.session.add(show)
    db.session.commit()
  except:
    db.session.rollback()
    error=True
    print(sys.exc_info())
  finally:
    db.session.close()

  if error:
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    flash('An error occurred. Show could not be listed.')
  else:
    # on successful db insert, flash success
     flash('Show was successfully listed!')
  
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

#----------------------------------------------------------------------------#

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
