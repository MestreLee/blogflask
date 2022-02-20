from flask import Flask, render_template

#Inicialitzem Flask

app = Flask(__name__)

@app.route('/')
def index():
	nom = 'Bernat'
	return render_template ('index.html', title='Home', nom=nom)

@app.route('/about')
def about():
	return render_template('about.html', title='About')