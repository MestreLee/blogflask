from flask import Flask, render_template

#Inicialitzem Flask

app = Flask(__name__)

@app.route('/')
def index():
	return "hola que taaaal, com et va!"