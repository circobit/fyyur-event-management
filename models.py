from database import db

# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = "venues"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String())
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)
    location_id = db.Column(db.Integer, db.ForeignKey("locations.id"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())
    shows = db.relationship("Show", back_populates="venue", cascade="all, delete-orphan")
    location = db.relationship("Location", backref="venues")
    venue_links = db.relationship(
        "VenueLink", back_populates="venue", cascade="all, delete-orphan"
    )
    genres = db.relationship(
        "Genre", 
        secondary="genres_venues",
		back_populates="venues"
	)

    __table_args__ = (
        db.Index("ix_venue_name", "name"),
        db.UniqueConstraint("name", "location_id", name="uq_name_locationid"),
    )

    def __repr__(self):
        return f"<Venue id={self.id} name={self.name!r}>"


class Artist(db.Model):
    __tablename__ = "artists"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    image_link = db.Column(db.String(500))
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship("Show", back_populates="artist", cascade="all, delete-orphan")
    social_link = db.Column(db.String(500))
    artist_links = db.relationship(
        "ArtistLink", back_populates="artist", cascade="all, delete-orphan"
    )
    genres = db.relationship(
        "Genre",
        secondary="genres_artists",
        back_populates="artists",
	)

    __table_args__ = (db.Index("ix_artist_name", "name"),)

    def __repr__(self):
        return f"<Artist id={self.id} name={self.name!r}>"


class Show(db.Model):
    __tablename__ = "shows"

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(
        db.Integer, db.ForeignKey("artists.id", ondelete="CASCADE"), nullable=False
    )
    venue_id = db.Column(
        db.Integer, db.ForeignKey("venues.id", ondelete="CASCADE"), nullable=False
    )
    start_time = db.Column(db.DateTime(timezone=True), nullable=False)
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())
    artist = db.relationship("Artist", back_populates="shows")
    venue = db.relationship("Venue", back_populates="shows")

    __table_args__ = (
        db.UniqueConstraint(
            "artist_id", "venue_id", "start_time", name="uq_artistid_venueid_starttime"
        ),
        db.Index("ix_show_start_time", "start_time"),
        db.Index("ix_show_artist_id", "artist_id"),
        db.Index("ix_show_venue_id", "venue_id"),
    )

    def __repr__(self):
        return f"<Show id={self.id} artist_id={self.artist_id} venue_id={self.venue_id} start_time={self.start_time}>"


class Location(db.Model):
    __tablename__ = "locations"

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(255), nullable=False)
    postal_code_id = db.Column(db.Integer, db.ForeignKey("postal_codes.id"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())
    postal_code = db.relationship("PostalCode", back_populates="locations")

    __table_args__ = (
        db.UniqueConstraint(
            "address", "postal_code_id", name="uq_address_postalcodeid"
        ),
    )


class PostalCode(db.Model):
    __tablename__ = "postal_codes"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), nullable=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    locations = db.relationship(
        "Location", back_populates="postal_code", cascade="all, delete-orphan"
    )

    __table_args__ = (
        db.UniqueConstraint("city", "state", name="uq_city_state"),
    )


class Genre(db.Model):
    __tablename__ = "genres"

    id = db.Column(db.Integer, primary_key=True)
    genre_name = db.Column(db.String(120), nullable=False, unique=True)
    venues = db.relationship(
        "Venue",
        secondary="genres_venues",
        back_populates="genres",
	)
    artists = db.relationship(
        "Artist",
        secondary="genres_artists",
        back_populates="genres"
	)


class GenreArtist(db.Model):
    __tablename__ = "genres_artists"

    artist_id = db.Column(
        db.Integer, db.ForeignKey("artists.id", ondelete="CASCADE"), primary_key=True
    )
    genre_id = db.Column(
        db.Integer, db.ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True
    )


class GenreVenue(db.Model):
    __tablename__ = "genres_venues"

    venue_id = db.Column(
        db.Integer, db.ForeignKey("venues.id", ondelete="CASCADE"), primary_key=True
    )
    genre_id = db.Column(
        db.Integer, db.ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True
    )


class LinkType(db.Model):
    __tablename__ = "link_types"

    id = db.Column(db.Integer, primary_key=True)
    type_name = db.Column(db.String(50), unique=True, nullable=False)
    links = db.relationship(
        "Link", back_populates="link_type", cascade="all, delete-orphan"
    )


class Link(db.Model):
    __tablename__ = "links"

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(255), nullable=False)
    link_type_id = db.Column(
        db.Integer, db.ForeignKey("link_types.id", ondelete="CASCADE"), nullable=False
    )
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=db.func.now())
    link_type = db.relationship("LinkType", back_populates="links")
    venue_links = db.relationship(
        "VenueLink", back_populates="link", cascade="all, delete-orphan"
    )
    artist_links = db.relationship(
        "ArtistLink", back_populates="link", cascade="all, delete-orphan"
    )


class VenueLink(db.Model):
    __tablename__ = "venue_links"

    venue_id = db.Column(
        db.Integer, db.ForeignKey("venues.id", ondelete="CASCADE"), primary_key=True
    )
    link_id = db.Column(
        db.Integer, db.ForeignKey("links.id", ondelete="CASCADE"), primary_key=True
    )
    is_primary = db.Column(db.Boolean, nullable=False, default=False)
    venue = db.relationship("Venue", back_populates="venue_links")
    link = db.relationship("Link", back_populates="venue_links")

    __table_args__ = (
        # Prevent duplicate exact link assignments
        db.UniqueConstraint("venue_id", "link_id", name="uq_venueid_linkid"),
        # Ensure only one primary link per venue
        db.Index(
            "ix_venue_primary_link",
            "venue_id",
            unique=True,
            postgresql_where=(db.text("is_primary = true")),
        ),
    )


class ArtistLink(db.Model):
    __tablename__ = "artist_links"

    artist_id = db.Column(
        db.Integer, db.ForeignKey("artists.id", ondelete="CASCADE"), primary_key=True
    )
    link_id = db.Column(
        db.Integer, db.ForeignKey("links.id", ondelete="CASCADE"), primary_key=True
    )
    is_primary = db.Column(db.Boolean, nullable=False, default=False)
    artist = db.relationship("Artist", back_populates="artist_links")
    link = db.relationship("Link", back_populates="artist_links")

    __table_args__ = (
        # Prevent duplicate exact link assignments
        db.UniqueConstraint("artist_id", "link_id", name="uq_artistid_linkid"),
        # Ensure only one primary link per artist
        db.Index(
            "ix_artist_primary_link",
            "artist_id",
            unique=True,
            postgresql_where=(db.text("is_primary = true")),
        ),
    )