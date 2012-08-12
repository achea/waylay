#!/usr/bin/env python

import sys
import math, numbers
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

	def mapPos(self, mapX, mapZ):
		self.mapX = int(mapX)
		self.mapZ = int(mapZ)

	def overlayPos(self, overlayX, overlayZ):
		self.overlayX = int(overlayX)
		self.overlayZ = int(overlayZ)

	def __str__(self):
		return "Map({},{}) == World({},{}) == Overlay({},{})".format( \
				self.mapX, self.mapZ, self.worldX, self.worldZ, self.overlayX, self.overlayZ)

def main(mapFilename, waypointsFilename, calibrationFilename):
	# quadrant 4 of world is positive (i.e., SE, and negative is impossible)
	# quadrant 4 of map is positive (no negative possible)
	#map = PythonMagick.Image("mapFilename")
	#mapSize = (image.size().width(), image.size().height())

	(scale, calibPnt) = calibratePoints(calibrationFilename)

	#mapSize = (10624, 10336)
	(overlay, anchor) = makeWaypointLayer(waypointsFilename, scale)

	# calibration point goes from world to map
	# anchor point has a world point, now calculate its corresponding map point
	xDiff = (calibPnt.worldX - anchor.worldX) * scale['x']
	zDiff = (calibPnt.worldZ - anchor.worldZ) * scale['z']
	anchor.mapPos(round(calibPnt.mapX - xDiff, 0), round(calibPnt.mapZ - zDiff, 0))
	print(anchor)
	
	print("Reading {} ... ".format(mapFilename), end="")
	map = PythonMagick.Image(mapFilename)
	print("done\nWriting overlay ... ", end="")
	map.composite(overlay, anchor.mapX + anchor.overlayX, anchor.mapZ + anchor.overlayZ,
			PythonMagick.CompositeOperator.OverCompositeOp)
		# TODO check if need to add overlayX/overlayZ (for now it works since they're both 0)
	print("done\nSaving final map to map.png ... ", end="")
	map.write("map.png")
	print("done")

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
			xDiffs.append(math.fabs((points[i].mapX - points[j].mapX)/(points[i].worldX - points[j].worldX)))
				# python 3 yields floats for division
			zDiffs.append(math.fabs((points[i].mapZ - points[j].mapZ)/(points[i].worldZ - points[j].worldZ)))
				# division in python 3 returns a float
				# numbers should never be negative

	# assert ((min(xDiffs) > 0) and (min(zDiffs) > 0))

	numPairs = choose(len(points), 2)
	scale = {}
	scale['x'] = round(sum(xDiffs)/numPairs, 5)		# average, then truncate
	scale['z'] = round(sum(zDiffs)/numPairs, 5)

	print("{} = {}\n{} = {}".format(xDiffs,scale['x'],zDiffs,scale['z']))
	return (scale, points[0])		# the first point in the list

def makeWaypointLayer(waypointsFilename, scale):
	# need to know how many pixels in the map that one block is

	waypoints = []
	with open(waypointsFilename) as file:
		for line in file:
			waypoints.append(Waypoint(*line.split(":")[:6]))
				# ':' is delimiter
				# ignore Death point's extra entry

	# get the padding that divides evenly when inverse-scaled
	# guaranteed to be at least one, since range goes through all divisors between multiples
	padding = {'x': 200, 'z': 20}
	# -- code for (exact) integer scaling
	#temp = [i for i in range(scale['x']) if divmod(padding['x'] + i, scale['x']) == 0][0]
	#padding['x'] += temp
	#temp = [i for i in range(scale['z']) if divmod(padding['z'] + i, scale['z']) == 0][0]
	#padding['z'] += temp

	xWorld = [wp.x for wp in waypoints]
	zWorld = [wp.z for wp in waypoints]
	
	minX = min(xWorld)
	maxX = max(xWorld)
	minZ = min(zWorld)
	maxZ = max(zWorld)
	
	# calculate overlay (world) dimensions + padding
	# scale could be non-integer, so we round result and convert to integer
	xDim = int(round(abs(maxX - minX)*scale['x'] + padding['x'],0))
	zDim = int(round(abs(maxZ - minZ)*scale['z'] + padding['z'],0))

	# NW is negative, so we need the minX and minZ to equal (0,0)
	# -- code for (exact) integer scaling
	#anchor = CalibrationPoint(0,0, minX - divmod(padding['x'], scale['x'])[0],
	#		minZ - divmod(padding['z'], scale['z'])[0])
	anchor = CalibrationPoint(0, 0, minX - int(padding['x']//scale['x']),
		minZ - int(padding['z']//scale['z']))
		# the error comes from here
	anchor.overlayPos(0,0)

	print("waypoint overlay is {}x{}".format(xDim, zDim))
	world = PythonMagick.Image(PythonMagick.Geometry(xDim, zDim), "none")
		# * to unpack; none for no color

	assert (isinstance(anchor.overlayX, numbers.Integral) and isinstance(anchor.overlayZ, numbers.Integral))

	print("Writing waypoints ... ", end="")
	for waypoint in waypoints:
		wpImg = makeWaypoint(waypoint)		# automatic garbage collection

		# get distance from anchor and translate position
		# since anchor is the upper-left, we can get the absolute distance then add it
		xDiff = int(abs(round((anchor.worldX - waypoint.x)*scale['x'], 0)))
		zDiff = int(abs(round((anchor.worldZ - waypoint.z)*scale['z'], 0)))

		# center the image
		xDiff -= int(wpImg.size().width()//2)		# floor division
		zDiff -= int(wpImg.size().height()//2)

		# http://stackoverflow.com/questions/7793186/drawing-text-in-pythonmagick
		#print("{} ... ".format(waypoint.text), end="")
		world.composite(wpImg, anchor.overlayX + xDiff, anchor.overlayZ + zDiff,
				PythonMagick.CompositeOperator.OverCompositeOp)

	print("done")

	# write
	# for wp in waypoints:
	#	wpImage = 
	#	image add wpImage ( -6000x + wp.x, -5000y + wp.y) 	# temporarily make everything positive

	# how to shift wp which has world pxl coords of x, y to map pxl coords of a,b
	# add text overlay to a-x, b-y ((0,0) of world pxl onto map pxl)

	return (world, anchor)

def makeWaypoint(waypoint):
	# create a label, then position (without centering)
	wpImg = PythonMagick.Image(PythonMagick.Geometry(200,20), "none")
	#wpImg.backgroundColor(PythonMagick.Color("#00000080"))

	# pen color
	wpImg.fillColor("#{}".format(waypoint.color))
	wpImg.annotate(waypoint.text, PythonMagick.GravityType.CenterGravity)

	# remove extra, then draw border around text
	wpImg.trim()
	wpImg.borderColor("black")
	wpImg.border()

	wpImg.opacity(0x8080)

	#wpImg.resize(PythonMagick.Geometry(wpImg.size().width(), wpImg.size().height()))
	#print("{} {} {}x{}".format(wpImg.fileName(), wpImg.magick(), wpImg.size().width(), wpImg.size().height()))

	return wpImg

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

