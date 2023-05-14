from wtforms import Form, StringField, SelectField, PasswordField, BooleanField, SubmitField, IntegerField, FloatField, FileField, validators
from database import Plant, db_engine
from sqlalchemy.orm import Session

session = Session(bind=db_engine)

class LoginForm(Form):
    username = StringField('Username', [validators.DataRequired(), validators.Length(min=4, max=25)])
    password = StringField('Email Address', [validators.DataRequired(), validators.Length(min=5, max=35)])
    remember_me = BooleanField('Keep me logged in')

class UserForm(Form):
    user = IntegerField('User', validators=[validators.DataRequired()])
    username = StringField('Username', validators=[validators.DataRequired()])
    password = PasswordField('Password', validators=[validators.DataRequired()])
    name = StringField('Name', validators=[validators.DataRequired()])
    surname = StringField('Surname', validators=[validators.DataRequired()])
    email = StringField('Email', validators=[validators.Email()])
    save_changes = SubmitField('Spremi promjene')
    delete_user = SubmitField('Obriši korisnika')
    refresh_page = SubmitField('Osvježi')

class PlantForm(Form):
    name = StringField('Naziv', validators=[validators.DataRequired()])
    type = StringField('Tip', validators=[validators.DataRequired()])
    optimal_soil_humidity_min = IntegerField('Optimalna vlažnost tla (min)', validators=[validators.DataRequired(), validators.NumberRange(min=0)])
    optimal_soil_humidity_max = IntegerField('Optimalna vlažnost tla (max)', validators=[validators.DataRequired(), validators.NumberRange(min=0)])
    optimal_light_min = IntegerField('Optimalno osvjetljenje (min)', validators=[validators.DataRequired(), validators.NumberRange(min=0)])
    optimal_light_max = IntegerField('Optimalno osvjetljenje (max)', validators=[validators.DataRequired(), validators.NumberRange(min=0)])
    optimal_soil_ph_min = FloatField('Optimalan pH tla (min)', validators=[validators.DataRequired(), validators.NumberRange(min=0)])
    optimal_soil_ph_max = FloatField('Optimalan pH tla (max)', validators=[validators.DataRequired(), validators.NumberRange(min=0)])
    save_changes = SubmitField('Spremi promjene')
    delete = SubmitField('Obriši biljku')
    return_page = SubmitField('Povratak')

class NewPlantForm(Form):
    name = StringField('Naziv', validators=[validators.DataRequired()])
    type = StringField('Tip', validators=[validators.DataRequired()])
    optimal_soil_humidity_min = IntegerField('Optimalna vlažnost tla (min)', validators=[validators.DataRequired(), validators.NumberRange(min=0)])
    optimal_soil_humidity_max = IntegerField('Optimalna vlažnost tla (max)', validators=[validators.DataRequired(), validators.NumberRange(min=0)])
    optimal_light_min = IntegerField('Optimalno osvjetljenje (min)', validators=[validators.DataRequired(), validators.NumberRange(min=0)])
    optimal_light_max = IntegerField('Optimalno osvjetljenje (max)', validators=[validators.DataRequired(), validators.NumberRange(min=0)])
    optimal_soil_ph_min = FloatField('Optimalan pH tla (min)', validators=[validators.DataRequired(), validators.NumberRange(min=0)])
    optimal_soil_ph_max = FloatField('Optimalan pH tla (max)', validators=[validators.DataRequired(), validators.NumberRange(min=0)])
    image = FileField('Slika biljke')
    save_plant = SubmitField('Spremi biljku')
    return_page = SubmitField('Povratak')

class NewPotForm(Form):
    name = StringField('Naziv', validators=[validators.DataRequired()])
    plant = SelectField('Biljka', choices=[], validators=[validators.DataRequired()], coerce=int)
    save_pot = SubmitField('Spremi posudu')
    return_page = SubmitField('Povratak')

    def __init__(self, *args, **kwargs):
        super(NewPotForm, self).__init__(*args, **kwargs)

        self.plant.choices = [(p.id, p.name) for p in session.query(Plant).all()]