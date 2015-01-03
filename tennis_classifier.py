import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from contextlib import closing
import csv
from sklearn.externals import joblib
import os

app = Flask(__name__)

# configuration
DATABASE = '/tmp/players.db'
DEBUG = True
app.config.from_object(__name__)

def connect_db():
	return sqlite3.connect(app.config['DATABASE'])

def init_db():
	with closing(connect_db()) as db:
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()

def insert():	
	db = connect_db()
	players_file = open("/Users/danielchen/Documents/Flask Projects/TennisClassifier/static/players.csv", "r")
	reader = csv.reader(players_file)
	fields = "name, age, weight, height, left_handed"
	cur = db.cursor()
	for row in reader:	
		query = 'INSERT INTO %s (%s) VALUES (%s)' % (
			"players",
			fields,
			', '.join(row)
		)
		print query
		cur.execute(query)
		db.commit()
	cur.close()

@app.before_request
def before_request():
	g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
	db = getattr(g, 'db', None)
	if db is not None:
		db.close()

@app.route('/')
def show_entries():
	return render_template('show_entries.html')

@app.route('/predict', methods=['POST'])
def prediction():
	player1 = request.form['player1']
	player2 = request.form['player2']
	error = None
	winner = None
	if player1 == player2:
		error = 'Same player!'
		return render_template('show_entries.html', error=error)
	else:
		features = extract_features(player1, player2)
		classifier = joblib.load("/Users/danielchen/Documents/Flask Projects/TennisClassifier/static/tennis_classifier.pkl")
		prediction = classifier.predict(features)
		if prediction[0] == 1:
			winner = player1
		else:
			winner = player2
		return render_template('show_entries.html', winner=winner)

def extract_features(player1, player2):	
	age_diff = 0
	height_diff = 0
	weight_diff = 0
	hand = 0
	player1_query = 'SELECT * from players where name = \"%s\"' % player1
	player2_query = 'SELECT * from players where name = \"%s\"' % player2

	db = connect_db()
	cur = db.cursor()
	player1_features = cur.execute(player1_query)
	for row in player1_features:
		age_diff += row[3]
		height_diff += row[4]
		weight_diff += row[2]
		hand += row[1]

	db = connect_db()
	cur = db.cursor()
	player2_features = cur.execute(player2_query)	
	for row in player2_features:
		age_diff -= row[3]
		height_diff -= row[4]
		weight_diff -= row[2]
		if hand == 1 and row[1] == 0:
			hand += 2
		elif hand == 0 and row[1] == 1:
			hand += 2
		elif hand == 1 and row[1] == 1:
			hand += 3
		else:
			hand = 0
	return [age_diff, height_diff, weight_diff, hand]

if __name__ == '__main__':
	port = int(os.environ.get("PORT", 5000))
	app.run(host='0.0.0.0', port=port)





