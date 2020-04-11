import sqlite3 as sql
import json
import pandas as pd

if __name__ == "__main__":

	con = sql.connect("data/ghgflights.db")
	con.row_factory = sql.Row

	airline = 'AIR CANADA'

	cur = con.cursor()
	cur.execute('''
		SELECT icao24, DATE(firstSeen, 'unixepoch') AS firstSeen, fromCity, toCity, distance, fromAirport, toAirport,
			a.latitude AS fromLatitude, a.longitude AS fromLongitude,
			b.latitude AS toLatitude,   b.longitude AS toLongitude
		FROM flights AS f
		JOIN airports AS a
		 ON f.fromAirport = a.gps_code
		JOIN airports AS b
		 ON f.toAirport = b.gps_code;
		''')
		  # -- AND lastSeen > strftime('%s', date('now','start of month'))
		  # -- AND owner=?;
		# ''', (airline,))
	flights = cur.fetchall()
	
	# we convert to dataframe
	df = pd.DataFrame(flights,
		columns=['icao24','firstSeen','fromCity','toCity','distance','fromAirport','toAirport','fromLatitude','fromLongitude','toLatitude','toLongitude'])

	# for the map, we remove flights with distance 0/none.. and 26 is a bug!
	df = df[df['distance']>26]
	# download file with different columns
	dw = df.copy()
	del dw['fromCity']
	del dw['toCity']
	del dw['distance']
	del dw['fromLatitude']
	del dw['fromLongitude']
	del dw['toLatitude']
	del dw['toLongitude']
	dw.to_csv('download.csv', encoding='utf-8', index=False)

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
