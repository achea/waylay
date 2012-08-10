#!/usr/bin/env python

import sys
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

def main(mapFilename, waypointsFilename):
	# quadrant 4 of world is positive (i.e., SE, and negative is impossible)
	# quadrant 4 of map is positive (no negative possible)
	#map = PythonMagick.Image("mapFilename")
	#mapSize = (image.size().width(), image.size().height())
	mapSize = (10624, 10336)
	makeWaypointLayer(waypointsFilename, mapSize)

	#info(map)

def makeWaypointLayer(waypointsFileName, mapSize):
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
	main(sys.argv[1], sys.argv[2])
	# read image
	# create a transparent layer that has text labels from waypoint data
	sys.exit(0)

