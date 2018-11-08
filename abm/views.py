from datetime import datetime
from flask import request, render_template, redirect, url_for
import  forms , models
from __init__ import app
from flask_login import LoginManager, \
                        UserMixin, login_required,\
                        login_user, logout_user,\
                        current_user

app.secret_key = 'SecretKey'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def user_loader(user_id):
    return models.User.query.filter_by(username=user_id).first()


@app.route('/')
@app.route('/home', methods=['GET'])
def home():
    return render_template('home.html')


@app.route('/lista-tarea/crear', methods=['GET', 'POST'])
@login_required
def add_list():
    """
    Esta funcion crea las listas de tareas
    utilizando el formulario de listas
    y los modelos
    """
    form = forms.ListForm(request.form)
    user = models.User.get_by_name(current_user.username)

    if request.method == 'POST' and form.validate():
        new_task_list = models.TaskList(
            name=form.name.data,
            date=form.date.data,
            user_id=user.id)
        models.db.session.add(new_task_list)
        models.db.session.commit()
        return redirect(url_for('task_list'))

    return render_template('new_list.html', form=form)


@app.route('/menu-lista-tarea', methods=['GET', 'POST'])
@login_required
def task_list():
    """
    Con esta funcion muestro las listas de tareas
    haciendo una query a la tasklist filtrando por
    el estado de las finalizadas o no, para mostrar segun
    corresponda. Tambien uso un .choices para el forms
    para mostrar de forma dinamica los valores
    """
    user = models.User.query.filter_by(
        username=current_user.username
        ).first()

    tareas = models.TaskList.query.filter_by(
        user_id=user.id).filter(
        models.TaskList.finalize.is_(False)).all()

    tareasFinalizadas = models.TaskList.query.filter_by(
        user_id=user.id).filter(models.TaskList.finalize).all()

    form = forms.MenuListForm(request.form)

    form.task_list.choices = [
        (tarea.id, tarea.name)
        for tarea in tareas]

    form.task_list.choices.insert(0, (0, 'Seleccionar'))
    form.task_list.default = [(0, 'Seleccionar')]

    if request.method == 'POST':
        return redirect(url_for('tarea', list_id=form.task_list.data))
    return render_template(
        'task_list.html', form=form, tareasFinalizadas=tareasFinalizadas)


@app.route('/lista-tarea/<int:list_id>/eliminar', methods=['GET', 'POST'])
@login_required
def eliminar_lista(list_id):
    """
    Con esta funcion eliminamos la lista de tareas
    buscando la id de la lista de tareas
    """
    task_list = models.TaskList.query.get(list_id)
    models.db.session.delete(task_list)
    models.db.session.commit()
    return redirect(url_for('task_list'))


@app.route('/tarea/<int:list_id>')
def tarea(list_id):
    """
    Con esta funcion listamos las tarea individuales
    de cada lista
    """
    tarea = models.TaskList.query.filter_by(id=list_id).first()

    return render_template('tarea.html', tarea=tarea)

@app.route('/tarea/<int:id_tarea>/finalizar')
def finalizar_tarea(id_tarea):
    """
    Con esta funcion listamos las tarea individuales
    de cada lista
    """
    tarea = models.Task.query.filter_by(id=id_tarea).first()
    tarea.finalize = True
    tarea.date_finalize = datetime.now(models.time_argentina)
    models.db.session.commit()

    return redirect(url_for('tarea', list_id=tarea.list.id))


@app.route('/tarea/<int:list_id>/agregar', methods=['GET', 'POST'])
@login_required
def addtask(list_id):
    """
    Esta funcion nos permite agregar nuevas tareas a la lista
    mediante el models y con un if validando el forms
    y el metodo
    """
    form = forms.taskForm(request.form)
    task_list = models.TaskList.query.get(list_id)

    if request.method == 'POST' and form.validate():
        if task_list:
            new_task = models.Task(
                task=form.task.data,
                task_id=task_list.id
                )
            models.db.session.add(new_task)
            models.db.session.commit()
            return redirect(url_for('tarea', list_id=task_list.id))
        else:
            return 'La lista no existe, debe crearla para continuar.'
    return render_template('addtask.html', form=form)


@app.route('/tarea/<int:id_tarea>/editar', methods=['GET', 'POST'])
@login_required
def edittask(id_tarea):
    """
    Con esta funcion editamos las tareas, precargando el valor
    con el form.task.data para asi poder cambiarlo
    a uno nuevo
    """
    form = forms.taskForm(request.form)
    task = models.Task.query.get(id_tarea)

    if request.method == 'POST' and form.validate():
        task.task = form.task.data
        models.db.session.commit()
        return redirect(url_for('tarea', list_id=task.task_id))
    else:
        form.task.data = task.task
    return render_template('edittask.html', form=form)


@app.route('/tarea/<int:id_tarea>/eliminar', methods=['GET', 'POST'])
@login_required
def deletetask(id_tarea):
    """
    Con esta funcion eliminamos las tareas haciendo una query
    filtrando por id_tarea y luego eliminamos con el delete
    y aplicamos los cambios con el commit
    """
    task = models.Task.query.get(id_tarea)
    models.db.session.delete(task)
    models.db.session.commit()
    return redirect(url_for('tarea',  list_id=task.task_id))


@app.route('/tarea/<int:list_id>/finalizar', methods=['GET', 'POST'])
@login_required
def finalizetask(list_id):
    """
    Con esta funcion finalizamos la lista de tareas
    pasando el finalize a True y aplicando al date_finalize
    un datetime.now
    """
    taskList = models.TaskList.query.get(list_id)
    taskList.finalize = True
    taskList.date_finalize = datetime.now(models.time_argentina)
    models.db.session.commit()
    return redirect(url_for('task_list'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Esta es la funcion del login, donde validamos con el form
    chequeamos si el usuario existe, y logeamos,
    de lo contrario devolvemos "usuario incorrecto" o
    "no existe el usuario"
    """
    form = forms.LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        user = models.User.get_by_name(form.username.data)

        if user:
            if user.username == form.username.data:
                if user.password == form.password.data:
                    login_user(user, remember=True)
                    models.db.session.commit()
                    return redirect(url_for('task_list'))
                else:
                    return render_template(
                        'registry.html',
                        form=form,
                        wrong_username='El usuario ya existe.')
            else:
                return 'usuario incorrecto'
        else:
            return 'No existe el usuario'

    return render_template('login.html',
                           form=form,
                           wrong_password=None)


@app.route('/registro', methods=['GET', 'POST'])
def registry():
    """
    La funcion de registro, aca cargamos el registryform
    chequeando si existe el usuario, y si no existe
    creamos uno nuevo cargando el objeto con la funcion

    """
    form = forms.RegistryForm(request.form)

    if request.method == 'POST' and form.validate():
        user = models.User.get_by_username_or_email(
            form.username.data, form.email.data)

        if not user:
            new_user = models.User(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
                )
            models.db.session.add(new_user)
            models.db.session.commit()
            login_user(new_user, remember=True)
            return redirect(url_for('task_list'))
        else:
            return render_template(
                'registry.html',
                form=form,
                wrong_username='El usuario ya existe.')
    return render_template('registry.html', form=form)


@app.route('/<username>/perfil', methods=['GET', 'POST'])
@login_required
def profile(username):
    """
    Esta funcion es para generar el perfil del usuario
    obteniendo el currentuser y la ultima tarea creada
    filtrada por id
    """
    user = models.User.get_by_name(current_user.username)
    tarea = models.TaskList.query.order_by(
                models.TaskList.id.desc()
                ).filter(models.TaskList.finalize.is_(False)).filter_by(
                user_id=user.id).first()
    return render_template('profile.html', tarea=tarea)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))
#-------PROVEDORES----------------
@app.route('/cargar-provedor', methods=['GET', 'POST'])
def cargar_provedor():
    """
        carga provedores
        No es posible cargar el mismo provedor 
        falta obligar a que se ponga el nombre con la priemra en mayuscula
        y todo en minuscula
    """
    form = forms.CargarProvedor(request.form)
    
    if request.method == 'POST' and form.validate():
        res=models.db.session.query(models.Provedor).filter_by(nombre=str(form.nombre.data).capitalize()).count()
        if not res==0:
            return redirect(url_for('cargar_provedor'))
        nuevo_provedor=models.Provedor(
            nombre = str(form.nombre.data).capitalize(),
            direccion = form.direccion.data,
            telefono = form.telefono.data,
            email = form.email.data)
        models.db.session.add(nuevo_provedor)
        models.db.session.commit()
        return redirect(url_for('cargar_provedor'))
    return render_template("cargar_provedor.html",form=form)

@app.route('/provedores',methods=['GET','POST'])
def ver_provedores():
    """
        lista todos los provedores
    """
    provedores=models.Provedor.query.order_by(models.Provedor.id.asc()).all()
    return render_template("provedores.html",provedores=provedores)

@app.route('/provedor/<int:id_provedor>/editar',methods=['GET','POST'])
def modificar_provedor(id_provedor):
    """
        Modifica los provedores
    """
    form = forms.CargarProvedor(request.form)
    provedor = models.Provedor.query.get(id_provedor)
    if request.method == 'POST' and form.validate():
        provedor.nombre = form.nombre.data
        provedor.telefono = form.telefono.data
        provedor.direccion = form.direccion.data
        provedor.email = form.email.data
        models.db.session.commit()
        return redirect(url_for('ver_provedores'))
    else:
        form.nombre.data = provedor.nombre
        form.telefono.data = provedor.telefono
        form.direccion.data = provedor.direccion
        form.email.data = provedor.email
    return render_template('cargar_provedor.html',form=form,provedor=id_provedor)
    

#-----------FIN PROVEDORES---------------

@app.route('/cargar-stock/<int:id_materia>', methods=['GET', 'POST'])
def cargar_stock(id_materia):
    """
        carga stock
        el stock se suma al que ya habia
       
    """
    materia=models.MateriaPrima.query.get(id_materia)
    form = forms.CargarStock(request.form)
  

    if request.method == 'POST' and form.validate():
        #res=models.db.session.query(models.Producto.nombre,models.Producto.provedor,models.Producto.cantidad,models.Provedor.id).join(models.Provedor,models.Provedor.id=models.Producto.provedor).filter(
         
         #   models.Producto.nombre==form.nombre.data).count()
        #res=models.MateriaPrima.query.filter_by(id=form.nombre.data).first()
       
        materia.cantidad=materia.cantidad+form.cantidad.data
        models.db.session.commit()
        return redirect(url_for('ver_stock'))
       
    return render_template("cargar_stock.html",form=form,materia=materia)

@app.route('/stock', methods=['GET', 'POST'])
def ver_stock():
    materiaprima = models.MateriaPrima.listar()
    return render_template('stock.html',materiaprima=materiaprima)

# @app.route('/productos',methods=['POST','GET'])
# def descontar():
#     form = forms.productoListForm(request.form)
#     productos = models.ProductoElaborado.query.all()

#     form.productos_list.choices = [
#         (producto.id, producto.nombre)
#         for producto in productos]

#     if request.method =='POST':
#         productoelaborado=form.productos_list.data
#         receta = models.db.session.query(models.Receta).filter(productoelaborado==productoelaborado).all()
#         for materia in receta:
#             mat=models.db.session.query(models.MateriaPrima).filter_by(id=materia.materiaprima).first()
#             mat.cantidad = mat.cantidad - materia.cantidad
#             models.db.session.commit()
#         return redirect(url_for('descontar'))
#     return render_template('productos.html',form=form)

@app.route('/carta',methods=['POST','GET'])
def carta():
    productos=''
    unidad=''
    carta = models.ProductoElaborado.query.order_by(models.ProductoElaborado.id.asc()).all()
    if request.method == "POST":
        for producto in carta:
            unidades='unidad'+str(producto.id)
            if int(request.form[unidades]) > 0:
                productos=productos+str(producto.id)+","
                unidad=unidad+str(producto.id)+":"+request.form[unidades]+";"
        if len(productos) > 0:
            return redirect(url_for('facturar',productos=productos,unidades=unidad))               
    return render_template('carta.html',productos=carta)

@app.route('/carta/<int:id_carta>/editar',methods=['GET','POST'])
def modificar_carta(id_carta):
    """
        Modifica la Carta
    """
    form = forms.CargarCarta(request.form)
    producto = models.ProductoElaborado.query.get(id_carta)
    if request.method == 'POST' and form.validate():
        producto.nombre = form.producto.data
        producto.precio = form.precio.data
        producto.cant_ingrediente = form.cantingredientes.data
        models.db.session.commit()
        return redirect(url_for('carta'))
    else:
        form.producto.data = producto.nombre
        form.precio.data = producto.precio
        form.cantingredientes.data = producto.cant_ingrediente

    return render_template('cargar_carta.html',form=form,producto=str(id_carta))

@app.route('/carta/agregar',methods=["POST","GET"])
def agregar_carta():
    form = forms.CargarCarta(request.form)
    
    if request.method == 'POST' and form.validate():
        res=models.db.session.query(models.ProductoElaborado).filter_by(nombre=str(form.producto.data).capitalize()).count()
        if not res==0:
            return redirect(url_for('cargar_provedor'))
        nuevo_producto=models.ProductoElaborado(
            nombre = str(form.producto.data).capitalize(),
            precio = form.precio.data,
            cant_ingrediente = form.cantingredientes.data,)
        models.db.session.add(nuevo_producto)
        models.db.session.commit()
        return redirect(url_for('carta'))
    return render_template("cargar_carta.html",form=form)

@app.route('/receta/<int:id>/agregar',methods=["POST","GET"])
def agregar_receta(id):
    form = forms.CargarReceta(request.form)
    productoelaborado = models.ProductoElaborado.query.get(id)
    materiaprima=models.MateriaPrima.query.all()
    form.materiaprima.choices = [
        (producto.id, producto.nombre)
        for producto in materiaprima]
    if request.method == 'POST' and form.validate():
        res = models.Receta.query.filter_by(productoelaborado=id,materiaprima=form.materiaprima.data).count()
        if res > 0:
            return  render_template('cargar_receta.html',form=form,productoelaborado=productoelaborado,mensaje2=True)
        nueva_receta = models.Receta(
            productoelaborado = id,
            materiaprima = form.materiaprima.data,
            cantidad = form.cantidad.data
            ) 
        models.db.session.add(nueva_receta)
        models.db.session.commit()
        
        return render_template('cargar_receta.html',form=form,productoelaborado=productoelaborado,mensaje=True)

    return render_template('cargar_receta.html',form=form,productoelaborado=productoelaborado)

@app.route('/materia_prima/agregar',methods=["POST","GET"])
def agregar_materia_prima():
    
    form = forms.CargarMateriaPrima(request.form)
    if request.method == 'POST' and form.validate():
        res=models.db.session.query(models.MateriaPrima).filter_by(nombre=str(form.materiaprima.data).capitalize()).count()
        if not res==0:
            return "<script> alert('Ya existe el producto');location.href ='/stock';</script>"
        nueva_materia = models.MateriaPrima(
            nombre = str(form.materiaprima.data).capitalize(),
            cantidad = 0,
            unidad = str(form.unidad.data).capitalize()
        )
        models.db.session.add(nueva_materia)
        models.db.session.commit()
        return redirect(url_for('ver_stock'))
    return render_template('cargar_materiaprima.html',form=form)




@app.route('/carta/facturar',methods=["POST","GET"])
def facturar():
    total=0
    uni=dict()
    productos = request.args.get("productos").split(',')
    unidades = request.args.get("unidades").split(";")
    unidades.remove('')
    productos.remove('')
    for i in unidades:
        key , val = i.split(":")
        uni[int(key)] = int(val)

    productos_a_facturar=models.ProductoElaborado.query.filter(models.ProductoElaborado.id.in_(productos)).all()
    for i in productos_a_facturar:
        total=total+(i.precio * uni[i.id])
    fecha = datetime.now()
    if request.method=="POST":
        factura = models.Factura(
            fecha=fecha
        )
        models.db.session.add(factura)
        models.db.session.commit()
        factura=models.Factura.query.order_by(models.Factura.id.desc()).first()
   
        for producto in productos_a_facturar:
            receta = models.db.session.query(models.Receta).filter(models.Receta.productoelaborado==producto.id).all()
            if len(receta) == 0:
                return  "<script> alert('el producto no tiene receta');location.href ='/carta';</script>"
            for materia in receta:
                mat=models.db.session.query(models.MateriaPrima).filter_by(id=materia.materiaprima).first()
                mat.cantidad = mat.cantidad - (materia.cantidad*uni[producto.id])
                models.db.session.commit()
            detalle_factura = models.DetalleFactura(
                factura=factura.id,
                producto = producto.id,
                cantidad = uni[producto.id],
                precio   = producto.precio
            )
            models.db.session.add(detalle_factura)
            models.db.session.commit()
        return "<script> alert('Se Facturo correctamente');location.href ='/carta';</script>"
    return render_template("facturar2.html",productos_a_facturar=productos_a_facturar,unidad=uni,total=total,fecha=fecha)

# @app.route('/receta/<int:id_producto>/ver',methods=["POST","GET"])
# def ver_receta(id_producto):
#     receta=models.db.session.query(models.MateriaPrima.nombre,
#         models.MateriaPrima.unidad,
#         models.Receta.cantidad,
#         models.Receta.productoelaborado,
#         models.Receta.materiaprima,
#         models.ProductoElaborado.nombre,
#         models.ProductoElaborado.id).join(
#             models.Receta, models.Receta.productoelaborado==models.ProductoElaborado.id).filter(
#             models.Receta.productoelaborado==id_producto)
#     for i in receta:
#         print(i.materiaprima_nombre)
#     return("hola mundo")

@app.errorhandler(401)
def custom_401(error):
    
    return redirect(url_for('login'))


@app.errorhandler(404)
def custom_404(error):
    return render_template('404.html')
