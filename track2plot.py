#!/usr/bin/python2


from math import sin, cos, sqrt, asin, pi
from os.path import isfile
from sys import argv, exit
import datetime


# print help
def usage():
	"""print help"""
	print "This program converts track files to gnu plot compatible files\n"
	print "Synopsis: track2plot.py file1 file2\n"
	print "Options:"
	print "  -h : print this help"


# read track files
def read_track_from_file(f):
	""" read track file and return a list with track points"""
	if not isfile(f):
		return None

	tracks = []

	handle = open(f)
	
	for line in handle:
		if line.startswith("!") or len(line) == 0:
			continue

		entry = line.strip("\n").strip().split("\t")
		if len(entry) == 4:
			tracks.append(entry)
	
	return tracks


# convert degrees to radian messure
def rad(deg):
	return (deg/180.0 * pi)

# convert degree in [ degrees, minutes, seconds ] to decimal degree
def decimal_deg(dd,mm,ss):
	return (((ss / 60) + mm) / 60) + dd

# calc the distance between two points
def diff(lon1, lat1, lon2, lat2):
	"""Berechnet Abstand zweier Punkte (lat1,lon1)/(lat2,lon2) auf der Erdkugel
	Eingabe der Werte erfolge in Grad Ausgabe in km"""
	lon1 = rad(lon1)
	lat1 = rad(lat1)
	lon2 = rad(lon2)
	lat2 = rad(lat2)
	dlon = lon2 - lon1
	dlat = lat2 - lat1
	a = sin(dlat/2.0)**2 + cos(lat1) * cos(lat2) * sin(dlon/2.0)**2
	c = 2.0 * asin(min(1,sqrt(a)))
	d = 6396.0 * c
	return d


# main function
def main():
	args = argv[1:]

	if len(args) == 0:
		print "No files given. Exiting"
		exit(1)
	
	for path in args:
		tracks = read_track_from_file(path)
	
	# build the gnuplot table, start with the first entry
	gp = []
	
	# entry have following format
	# number, lenght difference, absolute length, time difference, whole time, speed, latitude, longitude
	entry = [ 0, 0, 0, 0, 0, 0, tracks[0][3], tracks[0][1], tracks[0][2] ]
	gp.append(entry)

	absLength = 0
	absTime = datetime.timedelta(0)

	# enter loop
	for k in range(1, len(tracks)):
		# create entry and append idx
		entry = []
		entry.append(k)

		# calc lenght difference to the point before and absolute length
		lat1 = tracks[k-1][1].split()
		lon1 = tracks[k-1][2].split()
		lat2 = tracks[k][1].split()
		lon2 = tracks[k][2].split()

		lat1 = decimal_deg(float(lat1[0]), float(lat1[1]), float(lat1[2]))
		lon1 = decimal_deg(float(lon1[0]), float(lon1[1]), float(lon1[2]))
		lat2 = decimal_deg(float(lat2[0]), float(lat2[1]), float(lat2[2]))
		lon2 = decimal_deg(float(lon2[0]), float(lon2[1]), float(lon2[2]))

		wayDifference = diff(lon1, lat1, lon2, lat2)
		absLength += wayDifference

		entry.append(wayDifference)
		entry.append(absLength)

		# calc time difference and and absolute time
		dateTimeString = tracks[k][0].split()
		curTimeList = dateTimeString[1].split(":")

		dateTimeStringBefore = tracks[k-1][0].split()
		curTimeListBefore = dateTimeStringBefore[1].split(":")

		curTime = datetime.datetime(1, 1, 1, int(curTimeList[0]), int(curTimeList[1]), int(curTimeList[2]))
		curTimeBefore = datetime.datetime(1, 1, 1, int(curTimeListBefore[0]), int(curTimeListBefore[1]), int(curTimeListBefore[2]))

		dTime = curTime - curTimeBefore

		absTime += dTime

		entry.append(str(dTime))
		entry.append(str(absTime))

		# calc partial speed
		speed = (wayDifference) / (dTime.total_seconds() / 60 / 60)

		entry.append(speed)

		
		# append height , latitude, longitude
		entry.append(tracks[k][3])
		entry.append(tracks[k][1])
		entry.append(tracks[k][2])

		gp.append(entry)
	
	# print data to std out
	
	# number, lenght difference, absolute length, time difference, whole time, speed, latitude, longitude
	for entry in gp:
		line = ""
		for item in entry:
			line += str(item) + "\t"

		print line

# main module check
if __name__ == "__main__":
	main()

