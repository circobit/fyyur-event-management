# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from forms import *
from database import db
from models import *
from datetime import datetime, timezone

# ----------------------------------------------------------------------------#
# App Config
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object("config")
db.init_app(app)
migrate = Migrate(app, db)

# ----------------------------------------------------------------------------#
# Filters
# ----------------------------------------------------------------------------#


def format_datetime(value, format="medium"):
    # Handle strings (For example: "2025-08-19T20:00:00") and datetime objects from SQLAlchemy
    if isinstance(value, str):
        # If it's a string, parse it into a datetime
        date = dateutil.parser.parse(value)
    else:
        # If it's already a datetime, use it as it is
        date = value
    # Pick formatting
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    # Render datetime as a human-readable string using Babel
    # Babel handles localization (e.g. language-specific month/day names, time formatting)
    return babel.dates.format_datetime(date, format, locale="en")


app.jinja_env.filters["datetime"] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers
# ----------------------------------------------------------------------------#

# These functions search for any existing primary link within ArtistLink and VenueLink,
# clears it out and set a new primary link. There can just be one primary link for those tables.

def set_primary_link_for_artist(artist_id, link_id):
    with db.session.begin():
        # Clear existing primary link
        db.session.query(ArtistLink).filter_by(artist_id=artist_id, is_primary=True).update({"is_primary": False})
        # Set new primary link
        db.session.query(ArtistLink).filter_by(artist_id=artist_id, link_id=link_id).update({"is_primary": True})

def set_primary_link_for_venue(venue_id, link_id):
    with db.session.begin():
        # Clear existing primary link
        db.session.query(VenueLink).filter_by(venue_id=venue_id, is_primary=True).update({"is_primary": False})
        # Set new primary link
        db.session.query(VenueLink).filter_by(venue_id=venue_id, link_id=link_id).update({"is_primary": True})


@app.route("/")
def index():
    return render_template("pages/home.html")

@app.route("/artists/<int:artist_id>/links/<int:link_id>/make-primary", methods=["POST"])
def make_primary_link(artist_id, link_id):
    set_primary_link_for_artist(artist_id, link_id)
    flash("Primary link updated")
    return redirect(url_for("show_artist", artist_id=artist_id))

@app.route("/venues/<int:venue_id>/links/<int:link_id>/make-primary", methods=["POST"])
def make_primary_venue_link(venue_id, link_id):
    set_primary_link_for_venue(venue_id, link_id)
    flash("Primary link updated for venue")
    return redirect(url_for("show_venue", venue_id=venue_id))


# ----------------------------------------------------------------------------#
#  Venues
# ----------------------------------------------------------------------------#


@app.route("/venues")
def venues():
    # Empty list to be replaced with real data
    data = []
    
    city_state_map = {}

    for venue in Venue.query.all():
        # City and state for the current venue
        city = venue.location.postal_code.city
        state = venue.location.postal_code.state

        # Check if the entry for the combination of city/state exists
        if (city, state) in city_state_map:
            index = city_state_map[(city, state)]

            # Append current venue to the venues list
            data[index]["venues"].append(venue)

        else:
            # Create a new entry for this city/state
            new_area = {
                "city": city,
                "state": state,
                "venues": [venue]
            }

            data.append(new_area)
            # Index of the recently created dictionary
            city_state_map[(city, state)] = len(data) - 1

    return render_template("pages/venues.html", areas=data)


@app.route("/venues/search", methods=["POST"])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_terms = request.form.get("search_term", "")
    
    # Use .options(joinedload(Venue.shows)) to load the data from the shows in the same query
    # and to avoid running further queries per each artist (N+1 problem)
    venues_list = Venue.query.options(joinedload(Venue.shows)).filter(Venue.name.ilike(f"%{search_terms}%")).all()
    
    # Get current datetime in UTC format (timezone aware)
    current_datetime = datetime.now(timezone.utc)
    
    response = {
        "count": len(venues_list),
        "data": [],
    }
    
    for venue in venues_list:
        # Define the dictionary to insert in response["data"]
        new_venue= {
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": 0
        }

        # Check upcoming shows based on current datetime
        # and sum up the number
        for show in venue.shows:
            if show.start_time > current_datetime:
                new_venue["num_upcoming_shows"] += 1
        
        # Append the dictionary to the list in response["data"]
        response["data"].append(new_venue)

    return render_template(
        "pages/search_venues.html",
        results=response,
        search_term=search_terms,
    )


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    data1 = {
        "id": 1,
        "name": "The Musical Hop",
        "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
        "address": "1015 Folsom Street",
        "city": "San Francisco",
        "state": "CA",
        "phone": "123-123-1234",
        "website": "https://www.themusicalhop.com",
        "facebook_link": "https://www.facebook.com/TheMusicalHop",
        "seeking_talent": True,
        "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
        "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
        "past_shows": [
            {
                "artist_id": 4,
                "artist_name": "Guns N Petals",
                "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
                "start_time": "2019-05-21T21:30:00.000Z",
            }
        ],
        "upcoming_shows": [],
        "past_shows_count": 1,
        "upcoming_shows_count": 0,
    }
    data2 = {
        "id": 2,
        "name": "The Dueling Pianos Bar",
        "genres": ["Classical", "R&B", "Hip-Hop"],
        "address": "335 Delancey Street",
        "city": "New York",
        "state": "NY",
        "phone": "914-003-1132",
        "website": "https://www.theduelingpianos.com",
        "facebook_link": "https://www.facebook.com/theduelingpianos",
        "seeking_talent": False,
        "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
        "past_shows": [],
        "upcoming_shows": [],
        "past_shows_count": 0,
        "upcoming_shows_count": 0,
    }
    data3 = {
        "id": 3,
        "name": "Park Square Live Music & Coffee",
        "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
        "address": "34 Whiskey Moore Ave",
        "city": "San Francisco",
        "state": "CA",
        "phone": "415-000-1234",
        "website": "https://www.parksquarelivemusicandcoffee.com",
        "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
        "seeking_talent": False,
        "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
        "past_shows": [
            {
                "artist_id": 5,
                "artist_name": "Matt Quevedo",
                "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
                "start_time": "2019-06-15T23:00:00.000Z",
            }
        ],
        "upcoming_shows": [
            {
                "artist_id": 6,
                "artist_name": "The Wild Sax Band",
                "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
                "start_time": "2035-04-01T20:00:00.000Z",
            },
            {
                "artist_id": 6,
                "artist_name": "The Wild Sax Band",
                "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
                "start_time": "2035-04-08T20:00:00.000Z",
            },
            {
                "artist_id": 6,
                "artist_name": "The Wild Sax Band",
                "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
                "start_time": "2035-04-15T20:00:00.000Z",
            },
        ],
        "past_shows_count": 1,
        "upcoming_shows_count": 1,
    }
    data = list(filter(lambda d: d["id"] == venue_id, [data1, data2, data3]))[0]
    return render_template("pages/show_venue.html", venue=data)


#  ----------------------------------------------------------------
#  Create Venue
#  ----------------------------------------------------------------


@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
    # Instantiate VenueForm from forms.py
    form = VenueForm()
    
    # Use the validate_on_submit() method to check if it's a POST
    # request and if the data is valid according to the form's rules
    if form.validate_on_submit():
        try:
            # Check if postal code exists filtering by city and state
            # I use .first() to get the first result or to get None if no match is found
            postal_code = PostalCode.query.filter_by(city=form.city.data, state=form.state.data).first()

            # If postal code doesn't exist, create the record
            if not postal_code:
                postal_code = PostalCode(city=form.city.data, state=form.state.data)
                db.session.add(postal_code)
            
            # Check if location exists filtering by postal code id and the address from the form
            location = Location.query.filter_by(postal_code_id=postal_code.id, address=form.address.data).first()
            # If location doesn't exist, create the record
            if not location:
                location = Location(address=form.address.data, postal_code_id=postal_code.id)
                db.session.add(location)
            
            # Instatiate venue
            new_venue = Venue(
                name=form.name.data, 
                phone=form.phone.data, 
                image_link=form.image_link.data,
                seeking_talent=form.seeking_talent.data,
                seeking_description=form.seeking_description.data,
                location=location
            )

            # Handle genres (Many-to-Many relationship)
            genre_names = form.genres.data

            for name in genre_names:
                genre = Genre.query.filter_by(genre_name=name).first()

                if not genre:
                    genre = Genre(genre_name=name)
                    db.session.add(genre)
            
                # Create the GenreVenue link by appending the genre to the Venue
                new_venue.genres.append(genre)

            # Handle social link
            social_url = form.social_link.data
            if social_url:
                # Determine the link type by checking the URL
                link_type_name = "Website"  # Default
                if "instagram.com" in social_url:
                    link_type_name = "Instagram"
                elif "tiktok.com" in social_url:
                    link_type_name = "TikTok"
                elif "x.com" in social_url or "twitter.com" in social_url:
                    link_type_name = "X"
                elif "facebook.com" in social_url:
                    link_type_name = "Facebook"
                elif "youtube.com" in social_url:
                    link_type_name = "YouTube"
                
                # Get or create the LinkType object
                link_type = LinkType.query.filter_by(type_name=link_type_name).first()
                if not link_type:
                    link_type = LinkType(type_name=link_type_name)
                    db.session.add(link_type)
                
                # Create Link object
                link_obj = Link(url=social_url, link_type=link_type)
                db.session.add(link_obj)

                # Create VenueLink
                venue_link = VenueLink(venue=new_venue, link=link_obj)
                db.session.add(venue_link)

            # Add venue
            db.session.add(new_venue)
            # If the operations succeed, commit changes and show message.
            db.session.commit()
            flash("Venue " + request.form["name"] + " was successfully listed!")
            # On success, redirect to the homepage
            return redirect(url_for('index'))
        
        except Exception as e:
            # Rollback changes in case of failure. Show message and the error itself.
            db.session.rollback()
            flash("An error ocurred. Venue " + form.name.data + " could not be listed.")
            print(e)
        finally:
            # Regardless of the result, close the db connection.
            db.session.close()

    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None


#  ----------------------------------------------------------------
#  Artists
#  ----------------------------------------------------------------

@app.route("/artists")
def artists():
    data = Artist.query.all()
    return render_template("pages/artists.html", artists=data)


@app.route("/artists/search", methods=["POST"])
def search_artists():
    # Search on artists with partial string search. It must be case-insensitive.
    # Seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # Search for "band" should return "The Wild Sax Band".
    search_terms = request.form.get("search_term", "")
    
    # Use .options(joinedload(Artist.shows)) to load the data from the shows in the same query
    # and to avoid running further queries per each artist (N+1 problem)
    artists_list = Artist.query.options(joinedload(Artist.shows)).filter(Artist.name.ilike(f"%{search_terms}%")).all()

    # Get current datetime in UTC format (timezone aware)
    current_datetime = datetime.now(timezone.utc)
    
    response = {
        "count": len(artists_list),
        "data": [],
    }

    for artist in artists_list:
        # Define the dictionary to insert in response["data"]
        new_artist = {
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": 0
        }

        # Check upcoming shows based on current datetime
        # and sum up the number
        for show in artist.shows:
            if show.start_time > current_datetime:
                new_artist["num_upcoming_shows"] += 1
        
        # Append the dictionary to the list in response["data"]
        response["data"].append(new_artist)

    return render_template(
        "pages/search_artists.html",
        results=response,
        search_term=search_terms,
    )


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    artist = Artist.query.get(artist_id)
    
    # TODO: Add a check here for a 404 error if artist is None
    if not artist:
        return render_template("errors/404.html")

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": [ genre.genre_name for genre in artist.genres ],
        "social_link": artist.artist_links[0].link.url if artist.artist_links else None,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link
    }

    # Get the current time in a timezone-aware format (UTC)
    current_datetime = datetime.now(timezone.utc)

    # Initiate the lists that will hold the upcoming and past shows
    upcoming_shows = []
    past_shows = []

    # Check all the shows from the artist and add the upcoming and past
    # shows to the correponding list
    for show in artist.shows:
        # Build the dictionary that the template expects
        show_details = {
            "venue_id": show.venue.id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": show.start_time.isoformat() # Convert datetime to string for the template
        }
        if show.start_time > current_datetime:
            upcoming_shows.append(show_details)
        else:
            past_shows.append(show_details)
    
    data["upcoming_shows"] = upcoming_shows
    data["past_shows"] = past_shows
    data["past_shows_count"] = len(past_shows)
    data["upcoming_shows_count"] = len(upcoming_shows)
    
    return render_template("pages/show_artist.html", artist=data)

#  ----------------------------------------------------------------
#  Update
#  ----------------------------------------------------------------

@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = {
        "id": 4,
        "name": "Guns N Petals",
        "genres": ["Rock n Roll"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "326-123-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    }
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template("forms/edit_artist.html", form=form, artist=artist)


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    return redirect(url_for("show_artist", artist_id=artist_id))


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    # Get the venue to edit
    venue_to_edit = Venue.query.options(
            joinedload(Venue.location).joinedload(Location.postal_code),
            joinedload(Venue.genres),
            joinedload(Venue.venue_links).joinedload(VenueLink.link)
        ).filter_by(id=venue_id).first()
    
    # Handle case where venue doesn't exist
    if not venue_to_edit:
        return render_template('errors/404.html')

    # Populate form with values
    form = VenueForm()

    form.name.data = venue_to_edit.name
    form.city.data = venue_to_edit.location.postal_code.city
    form.state.data = venue_to_edit.location.postal_code.state
    form.address.data = venue_to_edit.location.address
    form.phone.data = venue_to_edit.phone
    form.image_link.data = venue_to_edit.image_link
    form.genres.data = [genre.genre_name for genre in venue_to_edit.genres]
    form.seeking_talent.data = venue_to_edit.seeking_talent
    form.seeking_description.data = venue_to_edit.seeking_description
    
    # Check if there are any links before trying to access them
    if venue_to_edit.venue_links:
        form.social_link.data = venue_to_edit.venue_links[0].link.url

    return render_template("forms/edit_venue.html", form=form, venue=venue_to_edit)


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    venue_to_edit = Venue.query.get(venue_id)
    
    form = VenueForm()

    if form.validate_on_submit():
        try:
            # Update the simple fields on the venue object
            venue_to_edit.name = form.name.data
            venue_to_edit.phone = form.phone.data
            venue_to_edit.image_link = form.image_link.data
            venue_to_edit.seeking_talent = form.seeking_talent.data
            venue_to_edit.seeking_description = form.seeking_description.data

            # Check if postal code exists filtering by city and state
            # I use .first() to get the first result or to get None if no match is found
            postal_code = PostalCode.query.filter_by(city=form.city.data, state=form.state.data).first()

            # If postal code doesn't exist, create the record
            if not postal_code:
                postal_code = PostalCode(city=form.city.data, state=form.state.data)
                db.session.add(postal_code)
            
            # Check if location exists filtering by postal code id and the address from the form
            location = Location.query.filter_by(postal_code_id=postal_code.id, address=form.address.data).first()
            # If location doesn't exist, create the record
            if not location:
                location = Location(address=form.address.data, postal_code_id=postal_code.id)
                db.session.add(location)
            # Add location to Venue
            venue_to_edit.location = location

            # For many-to-many fields, a reliable way to update is to
            # clear the existing list and re-populate it with the new selections
            # from the form. This ensures removed items are handled correctly.
            venue_to_edit.genres.clear()
            # Handle genres (Many-to-Many relationship)
            genre_names = form.genres.data

            for name in genre_names:
                genre = Genre.query.filter_by(genre_name=name).first()

                if not genre:
                    genre = Genre(genre_name=name)
                    db.session.add(genre)
            
                # Create the GenreVenue link by appending the genre to the Venue
                venue_to_edit.genres.append(genre)

            # Clear venue_links list
            venue_to_edit.venue_links.clear()
            # Handle social link
            social_url = form.social_link.data
            if social_url:
                # Determine the link type by checking the URL
                link_type_name = "Website"  # Default
                if "instagram.com" in social_url:
                    link_type_name = "Instagram"
                elif "tiktok.com" in social_url:
                    link_type_name = "TikTok"
                elif "x.com" in social_url or "twitter.com" in social_url:
                    link_type_name = "X"
                elif "facebook.com" in social_url:
                    link_type_name = "Facebook"
                elif "youtube.com" in social_url:
                    link_type_name = "YouTube"
                
                # Get or create the LinkType object
                link_type = LinkType.query.filter_by(type_name=link_type_name).first()
                if not link_type:
                    link_type = LinkType(type_name=link_type_name)
                    db.session.add(link_type)
                
                # Create Link object
                link_obj = Link(url=social_url, link_type=link_type)
                db.session.add(link_obj)

                # Create VenueLink
                venue_link = VenueLink(venue=venue_to_edit, link=link_obj)
                db.session.add(venue_link)
            
            # If the operations succeed, commit changes and show message.
            db.session.commit()
            flash('Venue ' + form.name.data + ' was successfully updated!')
        except Exception as e:
            # In case of error, rollback changes
            db.session.rollback()
            flash('An error occurred. Venue could not be updated.')
            flash(e)
        finally:
            # Close the db session
            db.session.close()
        
        # On successful submission, redirect
        return redirect(url_for("show_venue", venue_id=venue_id))

    # If form.validate_on_submit() is False, re-render the page
    return render_template("forms/edit_venue.html", form=form, venue=venue_to_edit)


#  ----------------------------------------------------------------
#  Create Artist
#  ----------------------------------------------------------------


@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    # called upon submitting the new artist listing form
    form = ArtistForm()
    
    if form.validate_on_submit():
        try:
            # Create new artist object
            new_artist = Artist(
                name=form.name.data,
                image_link=form.image_link.data,
                seeking_venue=form.seeking_venue.data,
                seeking_description=form.seeking_description.data
            )

            # Handle the genres
            genres = form.genres.data
            for name in genres:
                # Search for genre in the database
                genre = Genre.query.filter_by(genre_name=name).first()
                # If the genre is not found, create it
                if not genre:
                    genre = Genre(genre_name=name)
                    db.session.add(genre)
                # Append the genre to the genres list of the artist
                new_artist.genres.append(genre)
            
            # Handle social link
            social_url = form.social_link.data
            if social_url:
                # Determine the link type by checking the URL
                link_type_name = "Website"  # Default
                if "instagram.com" in social_url:
                    link_type_name = "Instagram"
                elif "tiktok.com" in social_url:
                    link_type_name = "TikTok"
                elif "x.com" in social_url or "twitter.com" in social_url:
                    link_type_name = "X"
                elif "facebook.com" in social_url:
                    link_type_name = "Facebook"
                elif "youtube.com" in social_url:
                    link_type_name = "YouTube"
                
                # Get or create the LinkType object
                link_type = LinkType.query.filter_by(type_name=link_type_name).first()
                if not link_type:
                    link_type = LinkType(type_name=link_type_name)
                    db.session.add(link_type)
                
                # Create Link object
                link_obj = Link(url=social_url, link_type=link_type)
                db.session.add(link_obj)

                # Create ArtistLink
                artist_link = ArtistLink(artist=new_artist, link=link_obj)
                db.session.add(artist_link)
            
            # Add artist 
            db.session.add(new_artist)
            db.session.commit()

            # On successful db insert, flash success
            flash("Artist " + request.form["name"] + " was successfully listed!")

        except Exception as e:
            # On unsuccessful db insert, flash an error instead.
            db.session.rollback()
            flash('An error occurred. Artist ' + form.name.data + ' could not be created.')

        finally:
            # Close the connection
            db.session.close()

    return render_template("pages/home.html")


#  ----------------------------------------------------------------
#  Shows
#  ----------------------------------------------------------------


@app.route("/shows")
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    data = [
        {
            "venue_id": 1,
            "venue_name": "The Musical Hop",
            "artist_id": 4,
            "artist_name": "Guns N Petals",
            "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
            "start_time": "2019-05-21T21:30:00.000Z",
        },
        {
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "artist_id": 5,
            "artist_name": "Matt Quevedo",
            "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
            "start_time": "2019-06-15T23:00:00.000Z",
        },
        {
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "artist_id": 6,
            "artist_name": "The Wild Sax Band",
            "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
            "start_time": "2035-04-01T20:00:00.000Z",
        },
        {
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "artist_id": 6,
            "artist_name": "The Wild Sax Band",
            "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
            "start_time": "2035-04-08T20:00:00.000Z",
        },
        {
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "artist_id": 6,
            "artist_name": "The Wild Sax Band",
            "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
            "start_time": "2035-04-15T20:00:00.000Z",
        },
    ]
    return render_template("pages/shows.html", shows=data)


@app.route("/shows/create")
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    # on successful db insert, flash success
    flash("Show was successfully listed!")
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template("pages/home.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == "__main__":
    app.run()

# Or specify port manually:
"""
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
"""
