from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import update
from sqlalchemy.orm import Session
import flask_session as fs
from flask_login import login_manager, login_required, login_user, logout_user
from database import User, Plant, Pot, SensorData, db_engine
from forms import LoginForm, UserForm, PlantForm, NewPlantForm, NewPotForm
from generate_sensors import generate_sensor_values
from werkzeug.utils import secure_filename
import datetime
import json
import os
from html import escape

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///PyFloraPosude.db'
app.config['SECRET_KEY'] = "H3g2L4nyNqN8yNQeC9yhtTyov7mkvbQg"
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = "static/"
fs.Session(app)
login_manager = login_manager.LoginManager()
login_manager.init_app(app)


db_session = Session(bind=db_engine)

def user_to_json(users):
    users_json = []
    for user in users:
        users_json.append(
            {
        'id': user.id,
        'username': escape(user.username),
        'password': escape(user.password),
        'name': escape(user.name),
        'surname': escape(user.surname),
        'email': escape(user.email)
            }
        )
    return json.dumps(users_json, indent=4, default=str, separators=(',', ': '))

def sensors_to_json(sensors):
    sensors_json = []

    for sensor in sensors:
        formatted_time = sensor.time.strftime('%Y-%m-%d %H:%M:%S')

        data_dict = {
            'time': formatted_time,
            'temperature': sensor.temperature,
            'soil_humidity': sensor.soil_humidity,
            'light': sensor.light,
            'soil_ph': sensor.soil_ph
        }

        sensors_json.append(data_dict)

    json_data = json.dumps(sensors_json)

    return json_data


def pot_status_update(pot : Pot, last_sensor : SensorData):
    if pot.status != 0 and pot.plant_id is not None:
        plant = db_session.query(Plant).filter_by(id=pot.plant_id).first()
        if last_sensor.soil_humidity not in range(plant.optimal_soil_humidity_min, plant.optimal_soil_humidity_max):
            pot.status = 2
        elif last_sensor.light not in range(plant.optimal_light_min, plant.optimal_light_max):
            pot.status = 2
        elif last_sensor.soil_ph < plant.optimal_soil_ph_min or last_sensor.soil_ph > plant.optimal_soil_ph_max:
            pot.status = 2
        else:
            pot.status = 1
        
        db_session.commit()

@login_manager.user_loader
def load_user(user_id):
    return db_session.query(User).get(user_id)

@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        user = db_session.query(User).filter_by(username=form.username.data).first()
        if user is not None and user.password == form.password.data:
            if form.remember_me:
                login_user(user, remember=True, duration=datetime.timedelta(days=1))
                flash('Uspješno ste se prijavili!', 'success')
            else:
                login_user(user, remember=False)
                flash('Uspješno ste se prijavili!', 'success')
            return redirect('pots')
        else:
            flash('Pogrešno korisničko ime ili lozinka!', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route('/pots')
@login_required
def pots():
    pots = db_session.query(Pot).all()
    plants = db_session.query(Plant).all()
    for pot in pots:
        last_sensor = db_session.query(SensorData).filter_by(pot_id=pot.id).order_by(SensorData.time.desc()).first()
        if last_sensor is not None:
            pot_status_update(pot, last_sensor)
    return render_template('pots.html', pots=pots, plants=plants)

@app.route('/generate_sensors_all/<int:action_taken>')
@login_required
def generate_sensors_all(action_taken):
    pots = db_session.query(Pot).all()
    for pot in pots:
        generate_sensor_values(pot.id, action_taken)
    return redirect(url_for('pots'))

@app.route('/pot/<int:pot_id>')
@login_required
def pot(pot_id):
    pot = db_session.query(Pot).filter_by(id=pot_id).first()
    plant = db_session.query(Plant).filter_by(id=pot.plant_id).first()
    sensor_data = db_session.query(SensorData).filter_by(pot_id=pot_id).all()
    return render_template('pot.html', pot=pot, plant=plant, sensor_data=sensors_to_json(sensor_data))

@app.route('/generate_sensors/<int:pot_id>/<int:action_taken>')
@login_required
def generate_sensors(pot_id, action_taken):
    generate_sensor_values(pot_id, action_taken)
    return redirect(url_for('pot', pot_id=pot_id))

@app.route('/pot/new', methods=['GET', 'POST'])
@login_required
def new_pot():
    form = NewPotForm(request.form)
    if request.method == 'POST' and form.validate() and form.save_pot.data:
        pot = Pot(
            name=form.name.data,
            plant_id=form.plant.data,
            status=1
        )
        db_session.add(pot)
        db_session.commit()
        flash('Posuda uspješno dodana!', 'success')
        return redirect(url_for('pots'))

    if request.method == 'POST' and form.return_page.data:
        return redirect(url_for('pots'))
        
    return render_template('new_pot.html', form=form)

@app.route('/plants')
@login_required
def plants():
    plants = db_session.query(Plant).all()
    return render_template('plants.html', plants=plants)

@app.route('/plant/<int:plant_id>', methods=['GET', 'POST'])
@login_required
def plant(plant_id):
    plant = db_session.query(Plant).filter_by(id=plant_id).first()
    
    form = PlantForm(request.form, obj=plant)

    if request.method == "POST" and form.validate() and form.save_changes.data:
        plant = update(Plant).where(Plant.id == plant_id).values(
            name = form.name.data,
            type = form.type.data,
            optimal_soil_humidity_min = form.optimal_soil_humidity_min.data,
            optimal_soil_humidity_max = form.optimal_soil_humidity_max.data,
            optimal_light_min = form.optimal_light_min.data,
            optimal_light_max = form.optimal_light_max.data,
            optimal_soil_ph_min = form.optimal_soil_ph_min.data,
            optimal_soil_ph_max = form.optimal_soil_ph_max.data
        )
        db_session.execute(plant)
        db_session.commit()
        flash('Promjene spremljene!', 'success')
        return redirect(url_for('plant', plant_id=plant_id))
    
    if request.method == "POST" and form.validate() and form.delete.data:
        plant = db_session.query(Plant).filter_by(id=plant_id).first()
        db_session.delete(plant)
        db_session.commit()
        flash('Biljka obrisana!', 'success')
        return redirect(url_for('plants'))
    
    if request.method == "POST" and form.validate() and form.return_page.data:
        return redirect(url_for('plants'))

    return render_template('plant.html', form=form, plant=plant)

@app.route('/plant/new', methods=['GET', 'POST'])
@login_required
def new_plant():

    form = NewPlantForm(request.form)

    if request.method == "POST" and form.validate() and form.save_plant.data:

        image_data = request.files["image"]
        image_data.save(os.path.join(APP_ROOT, app.config['UPLOAD_FOLDER'], secure_filename(image_data.filename)))

        plant = Plant(
            name = form.name.data,
            type = form.type.data,
            optimal_soil_humidity_min = form.optimal_soil_humidity_min.data,
            optimal_soil_humidity_max = form.optimal_soil_humidity_max.data,
            optimal_light_min = form.optimal_light_min.data,
            optimal_light_max = form.optimal_light_max.data,
            optimal_soil_ph_min = form.optimal_soil_ph_min.data,
            optimal_soil_ph_max = form.optimal_soil_ph_max.data,
            image = os.path.join("/", app.config['UPLOAD_FOLDER'], secure_filename(image_data.filename))
        )
        db_session.add(plant)
        db_session.commit()
        flash('Biljka spremljena!', 'success')
        
        return redirect(url_for('plants'))
    
    if request.method == "POST" and form.return_page.data:
        return redirect(url_for('plants'))

    return render_template('new_plant.html', form=form)

@app.route('/users', methods=['GET', 'POST'])
@login_required
def users():
    users = db_session.query(User).all()
    users_json = user_to_json(users)
    form = UserForm(request.form)
    form.user.choices = [(user.id, user.username) for user in users]
    print(form.validate())
    print(form.save_changes)
    if request.method == "POST" and form.validate() and form.save_changes.data:
        if form.user.data not in [user.id for user in users]:
            user = User(
                id = form.user.data,
                username = form.username.data,
                password = form.password.data,
                name = form.name.data,
                surname = form.surname.data,
                email = form.email.data
            )
            db_session.add(user)
            db_session.commit()
            flash('Korisnik uspješno dodan!', 'success')
            return redirect(url_for('users'))
        else:
            user_id = form.user.data
            user = db_session.query(User).filter_by(id=user_id).first()
            user.username = form.username.data
            user.password = form.password.data
            user.name = form.name.data
            user.surname = form.surname.data
            user.email = form.email.data
            db_session.commit()
            flash('Promjene spremljene!', 'success')
            return redirect(url_for('users'))
    if request.method == "POST" and form.validate() and form.delete_user.data:
        user_id = form.user.data
        user = db_session.query(User).filter_by(id=user_id).first()
        db_session.delete(user)
        db_session.commit()
        flash('Korisnik obrisan!', 'success')
        return redirect(url_for('users'))
    if request.method == "POST" and form.refresh_page.data:
        return redirect(url_for('users'))
    return render_template('users.html', users=users, users_json=users_json, form=form)