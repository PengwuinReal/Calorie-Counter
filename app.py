import flask
from flask import Blueprint, render_template, request, redirect, url_for

app = flask.Flask(__name__)
@app.route('/')
def home():
    return render_template('index.html')
@app.route('/stats')
def about():
    return render_template('stats.html')
@app.route('/camera')
def support():
    return render_template('camera.html')

if __name__ == '__main__':
    app.run(debug=True)