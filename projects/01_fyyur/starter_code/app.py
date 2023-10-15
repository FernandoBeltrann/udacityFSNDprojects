#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, abort, render_template, request, Response, flash, redirect, url_for
from sqlalchemy import func, text
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from markupsafe import Markup
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# DONE TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    start_time = db.Column(db.DateTime)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    artist_image_link = db.Column(db.String(500))
    artist_name = db.Column(db.String, nullable=False)
    venue_name = db.Column(db.String, nullable=False)
    artist = db.relationship('Artist', foreign_keys=[artist_id], backref=db.backref('shows_artist', lazy=True))
    venue = db.relationship('Venue', foreign_keys=[venue_id], backref=db.backref('shows_venue', lazy=True))

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, autoincrement=True ,primary_key=True)
    #venues_id = db.Column(db.Integer)
    name = db.Column(db.String, unique=True)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500), unique=True)
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(200))
    

    @property
    def past_shows_count(self):
        current_time = datetime.now()
        return db.session.query(func.count(Show.id)).filter(Show.venue_id == self.id, Show.start_time < current_time).scalar()
    @property
    def past_shows(self):
      current_time = datetime.now()
      return db.session.query(Show).filter(Show.venue_id == self.id, Show.start_time < current_time).all()
    @property
    def upcoming_shows_count(self):
        current_time = datetime.now()
        return db.session.query(func.count(Show.id)).filter(Show.venue_id == self.id, Show.start_time > current_time).scalar()
    @property
    def upcoming_shows(self):
      current_time = datetime.now()
      return db.session.query(Show).filter(Show.venue_id == self.id, Show.start_time > current_time).all()

    #artists = db.relationship('Artist', secondary=shows, backref=db.backref('artists'), lazy=True)

    def __repr__(self):
      return f'<Venue {self.id} {self.name}>'

    #  DONE TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, unique=True)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500), unique=True)
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(500))   
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(200))

    @property
    def past_shows_count(self):
        current_time = datetime.now()
        return db.session.query(func.count(Show.id)).filter(Show.artist_id == self.id, Show.start_time < current_time).scalar()
    @property
    def past_shows(self):
      current_time = datetime.now()
      return db.session.query(Show).filter(Show.artist_id == self.id, Show.start_time < current_time).all()
    @property
    def upcoming_shows_count(self):
        current_time = datetime.now()
        return db.session.query(func.count(Show.id)).filter(Show.artist_id == self.id, Show.start_time > current_time).scalar()
    @property
    def upcoming_shows(self):
      current_time = datetime.now()
      return db.session.query(Show).filter(Show.artist_id == self.id, Show.start_time > current_time).all()


    def __repr__(self):
      return f'<Artist {self.id} {self.name}>'

    # Done TODO: implement any missing fields, as a database migration using Flask-Migrate


# Done TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
 


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
  # DONE -> TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

  return render_template('pages/venues.html',
                         result = db.session.query(Venue.city, Venue.state, func.array_agg(Venue.id).label('id'), func.array_agg(Venue.name).label('name')).group_by(Venue.city, Venue.state).all()
                         )

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }


  search_term=request.form.get('search_term', '')

  query_expression = text("SELECT * FROM venues WHERE name ILIKE :search_term")
  cnt_query_expression = text("SELECT count(*) FROM venues WHERE name ILIKE :search_term")

  results = db.session.execute(query_expression, {"search_term": f"%{search_term}%"}).fetchall()
  cnt_results = db.session.execute(cnt_query_expression, {"search_term": f"%{search_term}%"}).first()
  cnt = cnt_results[0]


  return render_template('pages/search_venues.html', results=results, cnt=cnt, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # DONE -> TODO: replace with real venue data from the venues table, using venue_id
  
  return render_template('pages/show_venue.html', 
                         venue=db.session.query(Venue).get(venue_id))


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # on successful db insert, flash success
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  address = request.form.get('address')
  phone = request.form.get('phone')
  genres = request.form.getlist('genres')  # For multi-select fields
  facebook_link = request.form.get('facebook_link')
  image_link = request.form.get('image_link')
  website = request.form.get('website_link')
  seeking_talent = bool(request.form.get('seeking_talent'))
  seeking_description = request.form.get('seeking_description')

  venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres,
                facebook_link=facebook_link, image_link=image_link, website=website,
                seeking_talent=seeking_talent, seeking_description=seeking_description)
  db.session.add(venue)
  db.session.commit()
  

  flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')


#  Delete Venue
#  ----------------------------------------------------------------

@app.route('/venues/<venue_id>', methods=['POST','DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

    if request.method == 'POST' or request.form.get('_method') == 'DELETE':
        try:
            venue = Venue.query.get(venue_id)
            if not venue:
                flash('Venue not found', 'error')
                return render_template('pages/home.html')

            db.session.delete(venue)
            db.session.commit()
            flash('Venue deleted successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while deleting the venue', 'error')
        finally:
            db.session.close()
    return render_template('pages/home.html')


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  return render_template('pages/artists.html',
                          artists=Artist.query.all()
                          )

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }

  search_term=request.form.get('search_term', '')

  query_expression = text("SELECT * FROM artists WHERE name ILIKE :search_term")
  cnt_query_expression = text("SELECT count(*) FROM artists WHERE name ILIKE :search_term")

  results = db.session.execute(query_expression, {"search_term": f"%{search_term}%"}).fetchall()
  cnt_results = db.session.execute(cnt_query_expression, {"search_term": f"%{search_term}%"}).first()
  cnt = cnt_results[0]


  return render_template('pages/search_artists.html', results=results, cnt=cnt, search_term=search_term )

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  
  return render_template('pages/show_artist.html', 
                         artist=db.session.query(Artist).get(artist_id))

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  form.name.data = db.session.query(Artist).get(artist_id).name
  form.city.data = db.session.query(Artist).get(artist_id).city
  form.state.data = db.session.query(Artist).get(artist_id).state
  form.phone.data = db.session.query(Artist).get(artist_id).phone
  form.genres.data = db.session.query(Artist).get(artist_id).genres
  form.facebook_link.data = db.session.query(Artist).get(artist_id).facebook_link
  form.image_link.data = db.session.query(Artist).get(artist_id).image_link
  form.website_link.data = db.session.query(Artist).get(artist_id).website
  form.seeking_venue.data = db.session.query(Artist).get(artist_id).seeking_venue
  form.seeking_description.data = db.session.query(Artist).get(artist_id).seeking_description


  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist = db.session.query(Artist).get(artist_id))

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  artist = db.session.query(Artist).get(artist_id)

  if artist:
    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.genres = request.form.getlist('genres')
    artist.facebook_link = request.form.get('facebook_link')
    artist.website = request.form.get('website_link')
    artist.seeking_venue = bool(request.form.get('seeking_venue'))
    artist.seeking_description = request.form.get('seeking_description')

    for show in artist.shows_artist:
       show.artist_image_link = request.form.get('image_link')
    artist.image_link = request.form.get('image_link')

    db.session.commit()

  else:
    flash('Artist not found', 'error')

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  form.name.data = db.session.query(Venue).get(venue_id).name
  form.city.data = db.session.query(Venue).get(venue_id).city
  form.state.data = db.session.query(Venue).get(venue_id).state
  form.address.data = db.session.query(Venue).get(venue_id).address
  form.phone.data = db.session.query(Venue).get(venue_id).phone
  form.genres.data = db.session.query(Venue).get(venue_id).genres
  form.facebook_link.data = db.session.query(Venue).get(venue_id).facebook_link
  form.image_link.data = db.session.query(Venue).get(venue_id).image_link
  form.website_link.data = db.session.query(Venue).get(venue_id).website
  form.seeking_talent.data = db.session.query(Venue).get(venue_id).seeking_talent
  form.seeking_description.data = db.session.query(Venue).get(venue_id).seeking_description
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue = db.session.query(Venue).get(venue_id))

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  venue = db.session.query(Venue).get(venue_id)

  if venue:
    venue.name = request.form.get('name')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.address = request.form.get('address')
    venue.phone = request.form.get('phone')
    venue.genres = request.form.getlist('genres')
    venue.facebook_link = request.form.get('facebook_link')
    venue.image_link = request.form.get('image_link')
    venue.website = request.form.get('website_link')
    venue.seeking_venue = bool(request.form.get('seeking_venue'))
    venue.seeking_description = request.form.get('seeking_description')

    db.session.commit()

  else:
    flash('Venue not found', 'error')


  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  name = request.form.get('name')
  city = request.form.get('city')
  state = request.form.get('state')
  phone = request.form.get('phone')
  genres = request.form.getlist('genres')  # For multi-select fields
  facebook_link = request.form.get('facebook_link')
  image_link = request.form.get('image_link')
  website = request.form.get('website_link')
  seeking_venue = bool(request.form.get('seeking_venue'))
  seeking_description = request.form.get('seeking_description')

  artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres,
                facebook_link=facebook_link, image_link=image_link, website=website,
                seeking_venue=seeking_venue, seeking_description=seeking_description)
  db.session.add(artist)
  db.session.commit()


  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  

  return render_template('pages/home.html')


#  Delete Artist
#  ----------------------------------------------------------------

@app.route('/artist/<artist_id>', methods=['POST','DELETE'])
def delete_artist(artist_id):
  # TODO: Complete this endpoint for taking a artist_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Artist on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

    if request.method == 'POST' or request.form.get('_method') == 'DELETE':
        try:
            artist = Artist.query.get(artist_id)
            if not artist:
                flash('Artist not found', 'error')
                return render_template('pages/home.html')

            db.session.delete(artist)
            db.session.commit()
            flash('Artist deleted successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while deleting the artist', 'error')
        finally:
            db.session.close()
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.

  return render_template('pages/shows.html', 
                         shows1 = Show.query.all())

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  artist_id = request.form.get('artist_id')
  venue_id = request.form.get('venue_id')
  start_time = request.form.get('start_time')

  artist_name = db.session.query(Artist).get(artist_id).name
  artist_image_link = db.session.query(Artist).get(artist_id).image_link
  venue_name = db.session.query(Venue).get(venue_id).name


  show = Show(artist_id=artist_id, venue_id= venue_id, start_time=start_time, artist_image_link=artist_image_link, artist_name=artist_name, venue_name=venue_name )
  db.session.add(show)
  db.session.commit()


  # on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
