#!/usr/bin/env python

import sys
import math
import PythonMagick

class Waypoint:
	def __init__(self, text, x, y, z, isOn=True, color="none"):
		# x and z are position, text is the text
		# y is unecessary
		self.x = int(x)
		self.z = int(z)
		self.text = text.strip()		# remove leading and trailing whitespace
		# color is the text color, isOn is if it is enabled
		self.color = color.strip()		# remove eol
		self.isOn = [True if isOn == "true" else False][0]

	def __str__(self):
			return "{} @ ({},{})".format(self.text, self.x, self.z)

class CalibrationPoint:
	# stores a point that links map pxl coords to world coords to overlay pxl coords
	def __init__(self, mapX, mapZ, worldX, worldZ):
		self.mapX = int(mapX)
		self.mapZ = int(mapZ)
		self.worldX = int(worldX)
		self.worldZ = int(worldZ)
		# NaN for invalidity (check with math.isnan())
		self.overlayX = float('NaN')
		self.overlayZ = float('NaN')

	def overlayPos(self, overlayX, overlayZ):
		self.overlayX = overlayX
		self.overlayZ = overlayZ

def main(mapFilename, waypointsFilename, calibrationFilename):
	# quadrant 4 of world is positive (i.e., SE, and negative is impossible)
	# quadrant 4 of map is positive (no negative possible)
	#map = PythonMagick.Image("mapFilename")
	#mapSize = (image.size().width(), image.size().height())

	scale = calibratePoints(calibrationFilename)

	mapSize = (10624, 10336)
	(overlay, anchor) = makeWaypointLayer(waypointsFilename, mapSize)

	#info(map)

def choose(n, k):
    """
    A fast way to calculate binomial coefficients by Andrew Dalke (contrib).

	http://stackoverflow.com/questions/3025162/statistics-combinations-in-python
    """
    if 0 <= k <= n:
        ntok = 1
        ktok = 1
        for t in range(1, min(k, n - k) + 1):
            ntok *= n
            ktok *= t
            n -= 1
        return ntok // ktok
    else:
        return 0

def calibratePoints(calibrationFilename):
	""" Returns a world to map scale """

	points = []
	with open(calibrationFilename) as file:
		for line in file:
			points.append(CalibrationPoint(*line.split(":")))

	xDiffs = []
	zDiffs = []
	for i in range(len(points)-1, -1, -1):			# start from valid upper index, to 0, step down
		for j in range(i-1, -1, -1):
			xDiffs.append((points[i].mapX - points[j].mapX)/(points[i].worldX - points[j].worldX))
				# python 3 yields floats for division
			zDiffs.append((points[i].mapZ - points[j].mapZ)/(points[i].worldZ - points[j].worldZ))
				# division in python 3 returns a float
				# numbers should never be negative

	numPairs = choose(len(points), 2)
	scaleX = round(sum(xDiffs)/numPairs, 5)		# average, then truncate
	scaleZ = round(sum(zDiffs)/numPairs, 5)

	print("{} = {}\n{} = {}".format(xDiffs,scaleX,zDiffs,scaleZ))
	return (scaleX, scaleZ)

def makeWaypointLayer(waypointsFileName, mapSize, scale):
	# need to know how many pixels in the map that one block is
	world = PythonMagick.Image(PythonMagick.Geometry(*mapSize), "none")
		# * to unpack; none for no color

	waypoints = []
	with open(waypointsFilename) as file:
		for line in file:
			waypoints.append(Waypoint(*line.split(":")[:6]))
				# ':' is delimiter
				# ignore Death point's extra entry


	# write
	# for wp in waypoints:
	#	wpImage = 
	#	image add wpImage ( -6000x + wp.x, -5000y + wp.y) 	# temporarily make everything positive

	# how to shift wp which has world pxl coords of x, y to map pxl coords of a,b
	# add text overlay to a-x, b-y ((0,0) of world pxl onto map pxl)

	world.write("overlay.png")
	return (world, 0)

def writeWaypoint(image, waypoint):
	# create a label, then position (without centering)

	pass

def transformWorldToMap(worldPos):
	# pass a tuple
	return mapPos

def info(image):
	print("{} {} {}x{}".format(image.fileName(), image.magick(), image.size().width(), image.size().height()))
	print(dir(PythonMagick.Image()))

if __name__ == "__main__":
	main(*sys.argv[1:])			# takes 3 arguments
	# read image
	# create a transparent layer that has text labels from waypoint data
	sys.exit(0)

