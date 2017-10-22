# An application about recording favorite movies & info

import os
from flask import Flask, render_template, session, redirect, url_for, flash
from flask_script import Manager, Shell
from flask_moment import Moment # needs pip/pip3 install flask_moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask_sqlalchemy import SQLAlchemy
## maybe not next two
# from flask_sqlalchemy import Table, Column, Integer, ForeignKey, String, DateTime, Date, Time
# from flask_sqlalchemy import relationship, backref

# from flask_migrate import Migrate, MigrateCommand # Later

# Configure base directory of app
basedir = os.path.abspath(os.path.dirname(__file__))

# Application configurations
app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'hardtoguessstringfromsi364thisisnotsupersecurebutitsok'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set up Flask debug stuff
manager = Manager(app)
moment = Moment(app) # For time
db = SQLAlchemy(app) # For database use
# migrate = Migrate(app, db) # For database use # later

#########
######### Everything above this line is important setup, not problem-solving.
#########

##### Set up Models #####

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64),unique=True) # Only unique title movies
    #person = db.relationship('Person',backref='person')

    def __repr__(self):
        return "{} | {}".format(self.title, self.genre)

class Person(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    # favMovie = db.relation(db.Integer, db.ForeignKey('movie.id')) # should this be a db.relationship to propagate to Movie?



##### Set up Forms #####

class NameMovieForm(FlaskForm):
    name = StringField("What is the person's name?", validators=[Required()])
    favMovie = StringField("What is the title of their favorite movie?", validators=[Required()])
    submit = SubmitField('Submit')

##### Helper functions
# def get_or_create_instrument(session, serial_number):
#     instrument = session.query(Instrument).filter_by(serial_number=serial_number).first()
#     if instrument:
#         return instrument
#     else:
#         instrument = Instrument(serial_number)
#         session.add(instrument)
#         return instrument

def get_or_create_person(db_session, person_name):#, fav_movie_title):
    person = db_session.query(Person).filter_by(name=person_name).first()
    if person:
        return person
    else:
        person = Person(name=person_name)
        db_session.add(person)
        db_session.commit()
        return person


##### Set up Controllers (view functions) #####

## Error handling routes
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

## Main route

@app.route('/', methods=['GET', 'POST'])
def index():
    # curr_people = Person.query.all()
    # num_people = len(curr_people)
    num_people = 0
    form = NameMovieForm()
    if form.validate_on_submit():
        get_or_create_person(db.session,form.name.data)
        # New person:
            # Add person and their fav movie

        # Extant person:
            # Change person's fav movie

        ## Q: What happens with a uniqueness error for movies -- does it update or not do anything, or is it gonna be a problem? May as well try the conservative way.



        # people_with_name = Person.query.filter_by(name=form.name.data)
        # if len(people_with_name) < 1:
        #     movie = Movie(title=form.favMovie.data)
        #     db.session.add(movie)
        #     db.session.commit()
        #     mv = Movie.query.filter_by(title=form.favMovie.data)
        #     id_new = mv.first().id
        #     person = Person(name=form.name.data,favMovie=id_new)
        #     db.session.add(person)
        #     db.session.commit()
        # else:
        #     # Just change their fav movie
        #     movies_like = Movie.query.filter_by(title=form.favMovie.data)
        #     if not movies_like: 
        #         movie = Movie(title=form.favMovie.data)
        #         db.session.add(movie)
        #         db.session.commit()
        #     movie = Movie.query.filter_by(title=form.favMovie.data)
        #     id_new = movie.first().id
        #     person = Person(name=form.name.data,favMovie=id_new)
        #     db.session.add(person)
        #     db.session.commit()
        #     flash("Movie changed!")
        return redirect(url_for('index')) # tpl
    return render_template('index.html', form=form,num_people=num_people) # Template should show e.g. "There are currently <NUM> ppl whose fav movies are stored!"

@app.route('/all_movies')
def see_all():
    ppl_n_movies = [] # to be list of tuples
    ppl = Person.query.all()
    for person in ppl:
        movie = Movie.query.filter_by(id=person.favMovie)
        ppl_n_movies.append((person,movie)) # list of tuples
    return render_template('all_movies.html',people_and_movies=ppl_n_movies)


if __name__ == '__main__':
    db.drop_all() # to start over FOR NOW
    db.create_all() # create tables 
    # if want to change data, have to drop tables
    manager.run()