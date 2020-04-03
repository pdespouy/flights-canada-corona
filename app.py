# TODO: Make sure it only takes data from March 2020

from flask import Flask, render_template, request
import sqlite3 as sql

app = Flask(__name__, static_url_path='/static/')
application = app

@app.route('/')
def index():
	con = sql.connect("data/ghgflights.db")
	con.row_factory = sql.Row

	airline = 'AIR CANADA'

	cur = con.cursor()
	cur.execute('''
		SELECT icao24, DATE(firstSeen, 'unixepoch') AS firstSeen, fromCity, toCity, distance,
			a.latitude AS fromLatitude, a.longitude AS fromLongitude,
			b.latitude AS toLatitude,   b.longitude AS toLongitude,
			CAST(ROUND(co2/1000) AS integer) AS co2
		FROM flights AS f
		JOIN airports AS a
		 ON f.fromAirport = a.gps_code
		JOIN airports AS b
		 ON f.toAirport = b.gps_code
		WHERE owner=?
		  -- AND lastSeen > strftime('%s', date('now','start of month'))
		  AND distance > 0;
		''', (airline,))
	flights = cur.fetchall()

	# edges for map
	links = []
	for f in flights:
		c = [[f['fromLongitude'], f['fromLatitude']], [f['toLongitude'], f['toLatitude']]]
		links.append({'type':'LineString', 'coordinates':c, 'aircraft':f['icao24']})
	print(links);
	return render_template('index.html', links=links)
	con.close()

@app.route('/explorer')
def explorer():
	con = sql.connect("ghgflights.db")
	con.row_factory = sql.Row

	cur = con.cursor()
	cur.execute("SELECT * FROM flights ORDER BY lastSeen LIMIT 1000;")
	rows = cur.fetchall()

	return render_template('explorer.html', rows=rows)

	con.close()

if __name__ == '__main__':
	app.run(debug=True)
