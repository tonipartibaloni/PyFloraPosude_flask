import sqlalchemy as db
from sqlalchemy.orm import Session, relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "Users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True,)
    password = db.Column(db.String, nullable=False)
    name = db.Column(db.String)
    surname = db.Column(db.String)
    email = db.Column(db.String)

    # required for flask-login
    def is_authenticated(self):
        return True

    def is_active(self):   
        return True           

    def is_anonymous(self):
        return False          

    def get_id(self):         
        return str(self.id)

class Plant(Base):
    __tablename__ = "Plants"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    type = db.Column(db.String, nullable=False)
    optimal_soil_humidity_min = db.Column(db.Integer, nullable=False)
    optimal_soil_humidity_max = db.Column(db.Integer, nullable=False)
    optimal_light_min = db.Column(db.Integer, nullable=False)
    optimal_light_max = db.Column(db.Integer, nullable=False)
    optimal_soil_ph_min = db.Column(db.Float, nullable=False)
    optimal_soil_ph_max = db.Column(db.Float, nullable=False)
    image = db.Column(db.String, nullable=False)
    pots = relationship("Pot", backref=backref("plant"))

class Pot(Base):
    __tablename__ = "Pots"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    status = db.Column(db.Integer, nullable=False)
    plant_id = db.Column(db.Integer, db.ForeignKey("Plants.id"))
    sensor_data = relationship("SensorData", backref=backref("pot"))

class SensorData(Base):
    __tablename__ = "SensorData"
    id = db.Column(db.Integer, primary_key=True)
    temperature = db.Column(db.Integer, nullable=False)
    soil_humidity = db.Column(db.Integer, nullable=False)
    light = db.Column(db.Integer, nullable=False)
    soil_ph = db.Column(db.Float, nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    after_action = db.Column(db.Boolean, nullable=False) # True if after action, False if before action
    pot_id = db.Column(db.Integer, db.ForeignKey("Pots.id"), nullable=False)

db_engine = db.create_engine("sqlite:///PyFloraPosude.db")

Base.metadata.create_all(bind=db_engine)

if __name__ == "__main__":
    with Session(bind=db_engine) as session:
        # fill database with data
        user = User(username="admin", password="2myxFFhgGiUUmUm", name="Toni", surname="Pavlović", email="toni.pavl@gmail.com")
        session.add(user)
        user_test = User(username="test", password="12345", name="Test", surname="Test", email="")
        session.add(user_test)

        plant1 = Plant(name='Svekrvin jezik', type='Unutrašnja', optimal_soil_humidity_min=30, optimal_soil_humidity_max=50, optimal_light_min=800, optimal_light_max=1600, optimal_soil_ph_min=5.5, optimal_soil_ph_max=7.0, image='/static/svekrvin_jezik.jpg')
        session.add(plant1)
        plant2 = Plant(name='Zamija', type='Unutrašnja', optimal_soil_humidity_min=30, optimal_soil_humidity_max=50, optimal_light_min=800, optimal_light_max=1600, optimal_soil_ph_min=6.0, optimal_soil_ph_max=7.0, image='/static/zamija.jpg')
        session.add(plant2)
        plant3 = Plant(name='Puzavac', type='Unutrašnja', optimal_soil_humidity_min=30, optimal_soil_humidity_max=50, optimal_light_min=800, optimal_light_max=1600, optimal_soil_ph_min=6.0, optimal_soil_ph_max=7.0, image='/static/puzavac.jpg')
        session.add(plant3)
        plant4 = Plant(name='Monstera', type='Unutrašnja', optimal_soil_humidity_min=40, optimal_soil_humidity_max=60, optimal_light_min=1000, optimal_light_max=1600, optimal_soil_ph_min=6.0, optimal_soil_ph_max=7.0, image='/static/monstera.jpg')
        session.add(plant4)
        plant5 = Plant(name='Lavanda', type='Vanjska', optimal_soil_humidity_min=20, optimal_soil_humidity_max=40, optimal_light_min=10000, optimal_light_max=50000, optimal_soil_ph_min=6.7, optimal_soil_ph_max=7.3, image='/static/lavanda.jpg')
        session.add(plant5)
        plant6 = Plant(name='Rajčica', type='Vanjska', optimal_soil_humidity_min=60, optimal_soil_humidity_max=80, optimal_light_min=10000, optimal_light_max=50000, optimal_soil_ph_min=6.2, optimal_soil_ph_max=6.8, image='/static/rajcica.jpg')
        session.add(plant6)
        plant7 = Plant(name='Bosiljak', type='Unustrašnja/vanjska', optimal_soil_humidity_min=40, optimal_soil_humidity_max=60, optimal_light_min=1600, optimal_light_max=10000, optimal_soil_ph_min=4.3, optimal_soil_ph_max=8.2, image='/static/bosiljak.jpg')
        session.add(plant7)
        plant8 = Plant(name='Jedarce', type='Unutrašnja', optimal_soil_humidity_min=40, optimal_soil_humidity_max=60, optimal_light_min=270, optimal_light_max=800, optimal_soil_ph_min=6.0, optimal_soil_ph_max=7.20, image='/static/jedarce.jpg')
        session.add(plant8)
        plant9 = Plant(name='Sukulent', type='Unutrašnja/vanjska', optimal_soil_humidity_min=0, optimal_soil_humidity_max=20, optimal_light_min=800, optimal_light_max=1600, optimal_soil_ph_min=6.0, optimal_soil_ph_max=7.0, image='/static/sukulent.jpg')
        session.add(plant9)
        plant10 = Plant(name='Engleski bršljan', type='Unustrašnja/vanjska', optimal_soil_humidity_min=40, optimal_soil_humidity_max=60, optimal_light_min=800, optimal_light_max=1600, optimal_soil_ph_min=6.0, optimal_soil_ph_max=7.0, image='/static/engleski_brsljan.jpg')
        session.add(plant10)

        pot1 = Pot(name='Kuhinja_1', status=False, plant_id=None)
        session.add(pot1)
        pot2 = Pot(name='Dnevni_1', status=True, plant_id=9)
        session.add(pot2)
        pot3 = Pot(name='Kuhinja_2', status=True, plant_id=1)
        session.add(pot3)
        pot4 = Pot(name='Dnevni_2', status=True, plant_id=2)
        session.add(pot4)
        pot5 = Pot(name='Balkon_1', status=False, plant_id=5)
        session.add(pot5)
        pot6 = Pot(name='Balkon_2', status=True, plant_id=4)
        session.add(pot6)
        pot7 = Pot(name='Vrt_1', status=True, plant_id=6)
        session.add(pot7)
        pot8 = Pot(name='Vrt_2', status=True, plant_id=7)
        session.add(pot8)
        pot9 = Pot(name='Vrt_3', status=True, plant_id=7)
        session.add(pot9)

        session.commit()


