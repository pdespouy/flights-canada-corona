import sqlite3 as sql
import json
import pandas as pd

if __name__ == "__main__":

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
		WHERE distance > 0;
		''')
		  # -- AND lastSeen > strftime('%s', date('now','start of month'))
		  # -- AND owner=?;
		# ''', (airline,))
	flights = cur.fetchall()
	
	# we convert to dataframe
	df = pd.DataFrame(flights,
		columns=['icao24','firstSeen','fromCity','toCity','distance','fromLatitude',
		'fromLongitude','toLatitude','toLongitude','co2'])

	# range of date
	dateRange = pd.date_range(start="2020-03-01", end="2020-03-31")

	# we create list of list
	a = [[]]

	# we go through all dates
	for d in range(0, len(dateRange)):
		dd = dateRange[d].strftime("%Y-%m-%d")
		# we filter dataframe by date
		sub = df[df.firstSeen==dd]
		links = []
		# we go through subset
		for i,row in sub.iterrows():
			c = [[row['fromLongitude'], row['fromLatitude']], [row['toLongitude'], row['toLatitude']]]
			links.append({'type':'LineString', 'date': row['firstSeen'], 'coordinates':c})
		a.append(links)

	# we remove first element
	a.pop(0)
	with open('data.json', 'w') as f:
		json.dump(a, f)

	con.close()
