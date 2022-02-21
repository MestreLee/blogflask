from flask import Flask, render_template, url_for, redirect
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

#Inicialitzem Flask

app = Flask(__name__)

#Creem la clau secreta pels formularis de flask

app.config['SECRET_KEY']='holaquetalcomoteva'

# Creem un formulari senzill

class FormulariNom(FlaskForm):
	nom = StringField("Nom: ", validators=[DataRequired()])
	submit = SubmitField()

@app.route('/')
def index():
	nom = 'Bernat'
	return render_template ('index.html', title='Home', nom=nom)

@app.route('/about')
def about():
	return render_template ('about.html', title='About')

@app.route('/nom', methods=['GET', 'POST'])
def nom():
	form = FormulariNom()
	nom = None
	if form.validate_on_submit():
		nom = form.nom.data
		form.nom.data = ''
	return render_template('nom.html', title=nom, nom=nom, form=form)