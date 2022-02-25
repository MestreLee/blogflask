from flask import Flask, render_template, url_for, redirect, flash, request
from flask_wtf import FlaskForm
from datetime import datetime
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


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

# Creem el model

class Users(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	nom = db.Column(db.String(200), nullable=False)
	email = db.Column(db.String(120), nullable=False, unique=True)
	date_Added = db.Column(db.DateTime, default=datetime.utcnow)
	# Afegim un camp que no estava d'inici
	pelicula_preferida = db.Column(db.String(250))

	# Creem un tostring
	def __repr__(self):
		return 'Id: {}, Nom: {}, email: {}, pel.lícula preferida: {}'.format(self.id, self.nom, self.email, self.pelicula_preferida)

# Creem un formulari senzill

class FormulariNom(FlaskForm):
	nom = StringField("Nom: ", validators=[DataRequired()])
	submit = SubmitField()

# Creem un formulari per omplir la base de dades

class FormulariUsuari(FlaskForm):
	nom = StringField('Nom: ', validators=[DataRequired()])
	email = StringField('Email: ', validators=[DataRequired()])
	pelicula_preferida = StringField()
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
			user = Users(nom=nom, email=email, pelicula_preferida=pelicula_preferida)
			db.session.add(user)
			db.session.commit()
			return redirect(url_for('usuaris'))
			flash('Molt be {} {} {}!'.format(nom, email, pelicula_preferida))
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
	else:
		return "Aquest usuari no existeix, capsigrany!"


if __name__ == '__main__':
    app.run(debug=True)