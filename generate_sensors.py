from random import randint, uniform
from sqlalchemy.orm import Session
from database import db_engine, Plant, Pot, SensorData
from datetime import datetime, timedelta
from config import API_KEY
import requests


URL = "http://api.openweathermap.org/data/2.5/weather?"

def generate_sensor_values(pot_id, action_taken):

    def new_random_values(plant : Plant, temperature, time):
        if plant.type == "Unutrašnja":
            light = randint(100, 2000)
        elif plant.type == "Unutrašnja/vanjska":
            light = randint(100, 20000)
        else:
            light = randint(100, 100000)
        soil_humidity = randint(0, 100)
        soil_ph = float(randint(4, 10)) + float(randint(0, 9))/10
        sensor_data = SensorData(temperature=temperature, soil_humidity=soil_humidity, light=light, soil_ph=soil_ph, time=time, after_action=False, pot_id=pot_id)
        return sensor_data
    
    def new_acceptable_values(plant : Plant, temperature, time):
        light = randint(plant.optimal_light_min, plant.optimal_light_max)
        soil_humidity = randint(plant.optimal_soil_humidity_min, plant.optimal_soil_humidity_max)
        soil_ph = round(uniform(plant.optimal_soil_ph_min, plant.optimal_soil_ph_max), 1)
        sensor_data = SensorData(temperature=temperature, soil_humidity=soil_humidity, light=light, soil_ph=soil_ph, time=time, after_action=True, pot_id=pot_id)
        return sensor_data

    with Session(db_engine) as session:

        pot = session.query(Pot).filter(Pot.id == pot_id).first()

        if pot.plant_id is not None and pot.status != 0:

            plant = session.query(Plant).filter(Plant.id == pot.plant_id).first()
            
            complete_url = URL + "appid=" + API_KEY + "&q=Zagreb"
            response = requests.get(complete_url)
            data = response.json()
            temperature = round(data['main']['temp'] - 273.15)

            time = datetime.now()

            last_measurement = session.query(SensorData).filter(SensorData.pot_id == pot_id).order_by(SensorData.time.desc()).first()

            if last_measurement is None:
                sensor_data = new_random_values(plant, temperature, time)
                session.add(sensor_data)
                session.commit()
                return
            
            delta = time - last_measurement.time

            if last_measurement.after_action and action_taken and delta >= timedelta(hours=12):
                after_action = True
                sensor_data = SensorData(temperature=temperature, soil_humidity=last_measurement.soil_humidity, light=last_measurement.light, soil_ph=last_measurement.soil_ph, time=time, after_action=after_action, pot_id=pot_id)
                session.add(sensor_data)
            elif last_measurement.after_action and not action_taken and delta >= timedelta(hours=12):
                sensor_data = new_random_values(plant, temperature, time)
                session.add(sensor_data)
            elif not last_measurement.after_action and action_taken and delta >= timedelta(hours=12):
                sensor_data = new_acceptable_values(plant, temperature, time)
                session.add(sensor_data)
            elif not last_measurement.after_action and not action_taken and delta >= timedelta(hours=12):
                sensor_data = new_random_values(plant, temperature, time)
                session.add(sensor_data)
            elif last_measurement.after_action and action_taken and delta < timedelta(hours=12):
                after_action = True
                sensor_data = SensorData(temperature=temperature, soil_humidity=last_measurement.soil_humidity, light=last_measurement.light, soil_ph=last_measurement.soil_ph, time=time, after_action=after_action, pot_id=pot_id)
                session.add(sensor_data)
            elif last_measurement.after_action and not action_taken and delta < timedelta(hours=12):
                after_action = False
                sensor_data = SensorData(temperature=temperature, soil_humidity=last_measurement.soil_humidity, light=last_measurement.light, soil_ph=last_measurement.soil_ph, time=time, after_action=after_action, pot_id=pot_id)
                session.add(sensor_data)
            elif not last_measurement.after_action and action_taken and delta < timedelta(hours=12):
                sensor_data = new_acceptable_values(plant, temperature, time)
                session.add(sensor_data)
            elif not last_measurement.after_action and not action_taken and delta < timedelta(hours=12):
                after_action = False
                sensor_data = SensorData(temperature=temperature, soil_humidity=last_measurement.soil_humidity, light=last_measurement.light, soil_ph=last_measurement.soil_ph, time=time, after_action=after_action, pot_id=pot_id)
                session.add(sensor_data)
            
            session.commit()