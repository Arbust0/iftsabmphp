from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from __init__ import app  #Comentar para migrar
import pytz
from flask import Flask
from sqlalchemy import or_ , ForeignKey
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

#app = Flask(__name__) # Descomentar para migrar
config = 'postgresql://postgres:sebast@localhost/cerveceria'

app.config['SQLALCHEMY_DATABASE_URI'] = config

db = SQLAlchemy(app)

migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


time_argentina = pytz.timezone('America/Argentina/Buenos_Aires')


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String)
    password = db.Column(db.String)
    email = db.Column(db.String)
    authenticated = db.Column(db.Boolean, default=False)

    profile = db.relationship('Profile', back_populates='user')
    task_list = db.relationship('TaskList', back_populates='user')

    def is_active(self):
        return True

    def get_id(self):
        return self.username

    def is_authenticated(self):
        return self.authenticated

    def anonymous(self):
        return False

    def get_by_name(name):
        user = User.query.filter_by(username=name).first()
        return user

    def get_by_username_or_email(username, email):
        user = User.query.filter(
                                or_(
                                    User.username == username,
                                    User.email == email)
                                ).first()
        return user

    def get_by_id(id_usuario):
        user = User.query.get(id_usuario)
        return user


class Profile(db.Model):
    __tablename__ = 'profile'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    last_name = db.Column(db.String)
    mail = db.Column(db.String)
    birthdate = db.Column(db.DateTime)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    user = db.relationship('User', back_populates='profile')


class TaskList(db.Model):
    __tablename__ = 'tasklist'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    date = db.Column(db.DateTime, default=datetime.now(time_argentina))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    finalize = db.Column(db.Boolean, default=False)
    date_finalize = db.Column(db.DateTime)

    tasks = db.relationship('Task', back_populates='list')

    user = db.relationship('User', back_populates='task_list')

    def get_by_user_id(user_id):
        task_list = TaskList.query.filter_by(user_id=user_id)
        return task_list

    def get_by_name(name):
        task_list = TaskList.query.filter_by(name=name)
        return task_list


class Task(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    task = db.Column(db.String)
    task_id = db.Column(db.Integer, db.ForeignKey('tasklist.id'))
    date = db.Column(db.DateTime, default=datetime.now(time_argentina))
    finalize = db.Column(db.Boolean, default=False)
    date_finalize = db.Column(db.DateTime)

    list = db.relationship('TaskList', back_populates='tasks')

class Provedor(db.Model):
    __tablename__ = 'provedor'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String)
    direccion = db.Column(db.String)
    telefono = db.Column(db.String)
    email = db.Column(db.String)

class ProductoElaborado(db.Model):
    __tablename__ = 'productoelaborado'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String)
    precio = db.Column(db.Integer)

class Receta(db.Model):
    __tablename__ = 'receta'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    productoelaborado = db.Column(db.Integer,ForeignKey('productoelaborado.id'))
    materiaprima = db.Column(db.Integer,ForeignKey('materiaprima.id'))
    cantidad = db.Column(db.Integer)
class MateriaPrima(db.Model):
    __tablename__ = 'materiaprima'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String)
    cantidad = db.Column(db.Integer)

if __name__ == '__main__':
    manager.run()
