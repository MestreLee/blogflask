from flask import Flask, render_template

#Inicialitzem Flask

app = Flask(__name__)

@app.route('/')
def index():

	nom = 'Bernat'

	return render_template ('index.html', nom=nom)