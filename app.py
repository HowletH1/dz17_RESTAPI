# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app)
movies_name = api.namespace("movies")
directors_name = api.namespace("directors")
genres_name = api.namespace("genres")


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.String()
    trailer = fields.String()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    genre = fields.String()
    director_id = fields.Int()
    director = fields.String()


class DirectorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


movies_schema = MovieSchema(many=True)
movie_schema = MovieSchema()

directors_schema = DirectorSchema(many=True)
director_schema = DirectorSchema()

genres_schema = GenreSchema(many=True)
genre_schema = GenreSchema()


@movies_name.route('/')
class MoviesView(Resource):
    def get(self):
        all_movies_query = db.session.query(Movie)

        director_id = request.args.get("director_id")
        if director_id:
            all_movies_query = all_movies_query.filter(Movie.director_id == director_id)

        genre_id = request.args.get("genre_id")
        if genre_id:
            all_movies_query = all_movies_query.filter(Movie.genre_id == genre_id)

        final_query = all_movies_query.all()

        return movies_schema.dump(final_query), 200

    def post(self):
        req = request.json
        new_movie = Movie(**req)
        with db.session.begin():
            db.session.add(new_movie)
        return 'Movie added', 201


@movies_name.route('/<int:mid>')
class MovieView(Resource):
    def get(self, mid):
        movie = Movie.query.get(mid)
        if not movie:
            return "", 404

        return movie_schema.dump(movie), 200


@genres_name.route("/")
class GenresView(Resource):
    def get(self):
        q_all = db.session.query(Genre)
        query = q_all.all()

        return genres_schema.dump(query), 200

    def post(self):
        new_post = request.json

        genre = genre_schema.load(new_post)
        new = Genre(**genre)
        with db.session.begin():
            db.session.add(new)

        return "", 201


@genres_name.route("/<int:gid>")
class GenreView(Resource):
    def get(self, gid):
        query_one = Genre.query.get(gid)
        if not query_one:
            return "", 404

        return genre_schema.dump(query_one), 200


@directors_name.route("/")
class DirectorsView(Resource):
    def get(self):
        query_all = db.session.query(Director)
        final_query = query_all.all()

        return directors_schema.dump(final_query), 200

    def post(self):
        new_d = request.json

        director = director_schema.load(new_d)
        new = Director(**director)
        with db.session.begin():
            db.session.add(new)

        return "", 201


@directors_name.route("/<int:did>")
class DirectorView(Resource):
    def get(self, did):
        query_one = Director.query.get(did)

        if not query_one:
            return "", 404

        return director_schema.dump(query_one), 200


if __name__ == '__main__':
    app.run(debug=True)
