import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from contextlib import closing
import csv
from sklearn.externals import joblib

app = Flask(__name__)

# configuration
DATABASE = '/tmp/players.db'
DEBUG = True
# SECRET_KEY = 'development key'
# USERNAME = 'admin'
# PASSWORD = 'default'
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

# def make_dicts(cursor, row):
# 	return dict((cur.description[idx][0], value)
# 	for idx, value in enumerate(row))

# def query_db(query, args=(), one=False):
# 	cur = connect_db().cursor().execute(query, args)
# 	rv = cur.fetchall()
# 	cur.close()
# 	return (rv[0] if rv else None) if one else rv

@app.route('/')
def show_entries():
	# cur = g.db.execute('select * from players order by name desc')
	# entries = [dict(name=row[0], height=row[1], weight=row[2], left_handed=row[3], age=row[4]) for row in cur.fetchall()]
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
		print prediction
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
	print player1_query
	print player2_query

	db = connect_db()
	cur = db.cursor()
	player1_features = cur.execute(player1_query)
	for row in player1_features:
		print "player 1"
		print row
		age_diff += row[3]
		height_diff += row[4]
		weight_diff += row[2]
		hand += row[1]

	db = connect_db()
	cur = db.cursor()
	player2_features = cur.execute(player2_query)	
	for row in player2_features:
		print "player 2"
		print row
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
	print [age_diff, height_diff, weight_diff, hand]
	return [age_diff, height_diff, weight_diff, hand]

if __name__ == '__main__':
	app.run()





