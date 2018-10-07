from wtforms import Form, validators, StringField, \
                    PasswordField, SubmitField,\
                    DateField, SelectField


class LoginForm(Form):
    username = StringField('Username', [
        validators.required(message='* requerido')])
    password = PasswordField('Contraseña', [
        validators.required(message='* requerido')])


class RegistryForm(Form):
    username = StringField('Username', [
        validators.required(message='* requerido')])
    email = StringField('Email', [
        validators.required(message='* requerido')])
    password = PasswordField('Contraseña', [
        validators.required(message='* requerido')])
    confirm = PasswordField('Contraseña', [
        validators.required(message='* requerido'),
        validators.equal_to('password', message='* No coincide')])


class taskForm(Form):
    task = StringField('Task', [
        validators.required(message='* requerido')])


class ListForm(Form):
    name = StringField('Task', [
        validators.required(message='* requerido')])
    date = DateField('Date', format='%d/%m/%Y', validators=[
        validators.required(message='* requerido')])


class MenuListForm(Form):
    task_list = SelectField('Selecciona la lista..', coerce=int)

class CargarProvedor(Form):
    nombre = StringField('Nombre', [
        validators.required(message='* requerido')])
    direccion = StringField('Direccion', [
        validators.required(message='* requerido')])
    telefono = StringField('Telefono', [
        validators.required(message='* requerido')])
    email = StringField('Email', [
        validators.required(message='* requerido')])

class CargarStock(Form):
    nombre = StringField('Nombre', [
        validators.required(message='* requerido')])
    cantidad = StringField('Cantidad', [
        validators.required(message='* requerido')])