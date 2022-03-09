from flask import Flask, render_template, url_for, redirect, flash, request
from flask_wtf import FlaskForm
from datetime import datetime
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField, IntegerField
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
import random


#Inicialitzem Flask

app = Flask(__name__)

#Creem la clau secreta pels formularis de flask

app.config['SECRET_KEY']='holaquetalcomoteva'

# Afegim la base de dades
#SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuaris.db'
# MySQL
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:password@localhost/usuaris'

# Inicialitzem la base de dades

db = SQLAlchemy(app)

#Per permetre "migrar" la base de dades (cambiar l'estructura, p.e. afegir un camp que no estava d'inici)

migrate = Migrate(app, db)

#Per migrar: a la terminal, dins de l'entorn virtual:
		## 1 - flask db init
		## 2 - flask db migrate -m 'missatge' (p.e. 'migració inicial')
		## 3 - flask db upgrade

# Configuració flask login

login_manager = LoginManager()
login_manager.init_app(app)	
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
	return Users.query.get(int(user_id))

# Creem el model d'usuari

class Users(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), nullable=False, unique=True)
	nom = db.Column(db.String(200), nullable=False)
	email = db.Column(db.String(120), nullable=False, unique=True)
	date_Added = db.Column(db.DateTime, default=datetime.utcnow)
	# Afegim un camp que no estava d'inici
	pelicula_preferida = db.Column(db.String(250))

	# Gestions relacionades amb el password (tampoc estava d'inici!)
	password_hash = db.Column(db.String(128))

	@property
	def password(self):
		raise AttributeError('Password no és un atribut que es pugui llegir!')
	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)

	# Creem un tostring
	def __repr__(self):
		return 'Id: {}, Nom: {}, email: {}, username: {}'.format(self.id, self.nom, self.email, self.username)

# Creem el model de post

class Posts(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	titol = db.Column(db.String(200), nullable=False)
	autor = db.Column(db.String(120), nullable=False)
	data_publicacio = db.Column(db.DateTime, default=datetime.utcnow)
	contingut = db.Column(db.Text, nullable=False)

# Creem un formulari senzill

class FormulariNom(FlaskForm):
	nom = StringField("Nom: ", validators=[DataRequired()])
	submit = SubmitField()

# Creem un formulari senzill pel joc de càlculs

class FormulariCalculs(FlaskForm):
	resultat = IntegerField("Resultat: ", validators=[DataRequired()])
	submit = SubmitField()

# Creem un formulari per omplir els usuaris de la base de dades

class FormulariUsuari(FlaskForm):
	nom = StringField('Nom: ', validators=[DataRequired()])
	username = StringField('Username: ', validators=[DataRequired()])
	email = StringField('Email: ', validators=[DataRequired()])
	pelicula_preferida = StringField()
	password = PasswordField('Password', validators=[DataRequired(), EqualTo('password2')])
	password2 = PasswordField('Confirm Password', validators=[DataRequired()])
	submit = SubmitField()

 # Creem un formulari per fer login

class FormulariLogin(FlaskForm):
	username = StringField('Username: ', validators=[DataRequired()])
	password = PasswordField('Password: ', validators=[DataRequired()])
	submit = SubmitField()

 # Creem un formulari per omplir els posts de la base de dades

class FormulariPost(FlaskForm):
	titol = StringField('Titol: ', validators=[DataRequired()])
	autor = StringField('Autor: ', validators=[DataRequired()])
	contingut = TextAreaField()
	submit = SubmitField()

@app.route('/')
def index():
	if current_user.is_authenticated:
		nom = current_user.nom
	else:
		nom = 'foraster'
	return render_template ('index.html', title='Home', nom=nom)

@app.route('/about')
def about():
	return render_template ('about.html', title='About')

@app.route('/usuaris')
def usuaris():
	usuaris = Users.query.all()
	return render_template('usuaris.html', title='Usuaris', usuaris=usuaris)

@app.route('/usuaris/nou', methods=['GET', 'POST'])
def usuari_nou():
	form = FormulariUsuari()
	nom = None
	username = None
	email = None
	if form.validate_on_submit():
		user = Users.query.filter_by(email=form.email.data).first()
		if user is None:
			nom = form.nom.data
			username = form.username.data 
			email = form.email.data
			pelicula_preferida = form.pelicula_preferida.data
			#Hash the password
			hashed_password = generate_password_hash(form.password.data, 'sha256')
			user = Users(nom=nom, username=username, email=email, pelicula_preferida=pelicula_preferida, password_hash=hashed_password)
			db.session.add(user)
			db.session.commit()
			flash('Molt be {}!'.format(username))
			return redirect(url_for('usuaris'))
		else:
			flash('Aquest correu ja existeix!')
	return render_template('usuari_nou.html', title='Usuari Nou', username=username, form=form)

@app.route('/usuaris/<int:id>', methods=['GET', 'POST'])
@login_required
def update_usuari(id):
	user = Users.query.get_or_404(id)
	if user:
		if current_user.id == user.id:
			form = FormulariUsuari()
			if form.validate_on_submit():
				user.nom = form.nom.data
				user.email = form.email.data 
				user.pelicula_preferida = form.pelicula_preferida.data
				db.session.commit()
				flash('Molt be {} {}!'.format(user.nom, user.email))
				return redirect(url_for('usuaris'))
			elif request.method == 'GET':
				form.nom.data = user.nom 
				form.email.data = user.email
				form.pelicula_preferida.data = user.pelicula_preferida
		else:
			return redirect(url_for('update_usuari', id=current_user.id))
	return render_template('update_usuari.html', title='Update usuari', form=form)

@app.route('/usuaris/<int:id>/delete')
def delete_usuari(id):
	user = Users.query.get_or_404(id)
	if user:
		db.session.delete(user)
		db.session.commit()
		flash('Usuari {} eliminat!'.format(user))
		return redirect(url_for('usuaris'))

@app.route('/login', methods=['GET', 'POST'])
def login():
	form = FormulariLogin()
	if form.validate_on_submit():
		user = Users.query.filter_by(username = form.username.data).first()
		if user:
			# Comprovem el password hash
			if check_password_hash(user.password_hash, form.password.data):
				login_user(user)
				flash('Login correcte!')
				return redirect(url_for('dashboard'))
			else:
				flash('Password incorrecte!')

		else:
			flash('Usuari inexistent!')
	return render_template('login.html', title='Login', form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
	logout_user()
	flash("Sessió acabada! Vagi bé!")
	return redirect(url_for('login'))

 # Obliguem a l'usuari a estar loguejat si vol accedir al dashboard mitjançant loguin_required
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
	return render_template('dashboard.html', title='Dashboard')

@app.route('/posts')
def posts():
	posts = Posts.query.order_by(Posts.data_publicacio)
	return render_template('posts.html', title='Posts', posts=posts)

@app.route('/posts/nou', methods=['GET', 'POST'])
def post_nou():
	form = FormulariPost()
	titol = None
	autor = None
	contingut = None
	if form.validate_on_submit():
		titol = form.titol.data
		autor = form.autor.data
		contingut = form.contingut.data
		post = Posts(titol=titol, autor=autor, contingut=contingut)
		db.session.add(post)
		db.session.commit()
		flash('Molt be {} {}!'.format(titol, autor))
		return redirect(url_for('posts'))

	return render_template('post_nou.html', title='Post Nou', form=form)

@app.route('/posts/<int:id>')
def post(id):
	post = Posts.query.get_or_404(id)
	if post:
		return render_template('post.html', title='Post', post=post)

@app.route('/posts/<int:id>/update', methods=['GET', 'POST'])
def update_post(id):
	post = Posts.query.get_or_404(id)
	if post:
		form = FormulariPost()
		if form.validate_on_submit():
			post.titol = form.titol.data
			post.autor = form.autor.data 
			post.contingut = form.contingut.data
			db.session.commit()
			flash('Post creat o modificat {} per: {}!'.format(post.titol, post.autor))
			return redirect(url_for('posts'))
		elif request.method == 'GET':
			form.titol.data = post.titol 
			form.autor.data = post.autor
			form.contingut.data = post.contingut
	return render_template('update_post.html', title='Update post', form=form)

@app.route('/posts/<int:id>/delete')
def delete_post(id):
	post = Posts.query.get_or_404(id)
	if post:
		db.session.delete(post)
		db.session.commit()
		flash('Post {} eliminat!'.format(post.titol))
		return redirect(url_for('posts'))

# Tornem els usuaris en format JSON

@app.route('/api')
def api():
	llista_users = []
	llista_users = Users.query.all()

	json_users={}
	for user in llista_users:
		json_users['usuari {}'.format(user.id)] = {"id" : user.id, "nom" : user.nom, "Pelicula preferida" : user.pelicula_preferida, "Data Creacio" : user.date_Added}

	return json_users

# Trastegem una miqueta

@app.route('/tictactoe')
def tictactoe():
	return render_template('tictactoe.html')

@app.route('/calculadora_javascript')
def calculadora_javascript():
	return render_template('calculadora_javascript.html')

@app.route('/calculadora')
def calculadora():
    numero = random.randint(1, 100)
    numero2 = random.randint(1, 25)
    operant = random.randint(1, 4)
    if operant == 4:
    	trobat = False
    	while not trobat:
    		if numero % numero2 != 0:
    			numero = random.randint(1, 5)
    			numero2 = random.randint(1, 5)
    		else:
    			trobat = True
    return render_template('form.html', numero=numero, numero2=numero2, operant=operant)

@app.route('/resultat', methods=['POST'])
def resultat():
    numero = request.form.get("numero", type=int)
    numero2 = request.form.get("numero2", type=int)
    resultat = request.form.get('resultat', type=int)
    operacio = request.form.get("operacio")
    if(operacio == 'Suma'):
        result = numero + numero2
    elif(operacio == 'Resta'):
        result = numero - numero2
    elif(operacio == 'Multiplicacio'):
        result = numero * numero2
    elif(operacio == 'Divisio'):
        result = numero / numero2
    else:
        result = 'Opcio no vàlida!'
    return render_template('result.html', result=result, resultat=resultat)


if __name__ == '__main__':
    app.run(debug=True)