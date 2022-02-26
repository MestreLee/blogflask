from flask import Flask, render_template, url_for, redirect, flash, request
from flask_wtf import FlaskForm
from datetime import datetime
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, logout_user, LoginManager, login_required, logout_user, current_user


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

# Creem el model d'usuari

class Users(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
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
		return 'Id: {}, Nom: {}, email: {}, pel.lícula preferida: {}, password: {}'.format(self.id, self.nom, self.email, self.pelicula_preferida, self.password_hash)

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

# Creem un formulari per omplir els usuaris de la base de dades

class FormulariUsuari(FlaskForm):
	nom = StringField('Nom: ', validators=[DataRequired()])
	email = StringField('Email: ', validators=[DataRequired()])
	pelicula_preferida = StringField()
	password = PasswordField('Password', validators=[DataRequired(), EqualTo('password2')])
	password2 = PasswordField('Confirm Password', validators=[DataRequired()])
	submit = SubmitField()

 # Creem un formulari per omplir els posts de la base de dades

class FormulariPost(FlaskForm):
	titol = StringField('Titol: ', validators=[DataRequired()])
	autor = StringField('Autor: ', validators=[DataRequired()])
	contingut = TextAreaField()
	submit = SubmitField()

@app.route('/')
def index():
	nom = 'Bernat'
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
	email = None
	if form.validate_on_submit():
		user = Users.query.filter_by(email=form.email.data).first()
		if user is None:
			nom = form.nom.data
			email = form.email.data
			pelicula_preferida = form.pelicula_preferida.data
			#Hash the password
			hashed_password = generate_password_hash(form.password.data, 'sha256')
			user = Users(nom=nom, email=email, pelicula_preferida=pelicula_preferida, password_hash=hashed_password)
			db.session.add(user)
			db.session.commit()
			flash('Molt be {} {} {} {}!'.format(nom, email, pelicula_preferida, hashed_password))
			return redirect(url_for('usuaris'))
		else:
			flash('Aquest correu ja existeix!')
	return render_template('usuari_nou.html', title='Usuari Nou', nom=nom, form=form)

@app.route('/usuaris/<int:id>', methods=['GET', 'POST'])
def update_usuari(id):
	user = Users.query.get_or_404(id)
	if user:
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
	return render_template('update_usuari.html', title='Update usuari', form=form)

@app.route('/usuaris/<int:id>/delete')
def delete_usuari(id):
	user = Users.query.get_or_404(id)
	if user:
		db.session.delete(user)
		db.session.commit()
		flash('Usuari {} eliminat!'.format(user))
		return redirect(url_for('usuaris'))

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

if __name__ == '__main__':
    app.run(debug=True)