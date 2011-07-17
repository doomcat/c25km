import math
try:
	import location, gobject
except:
	pass

class Workout:
	def __init__(self,week=1,workout=1,time=0,warmup=300):
		self.week = week
		self.workout = workout
		self.startTime = time
		self.pattern = []
		self.index = 0
		self.state = 'Walk'
		self.warmup = warmup
		self.started = False
		self.distance = 0.0

		try:
			self.oldLatLong = (0,0)
			self.gpsControl = location.GPSDControl.get_default()
			self.gps = location.GPSDevice()
			self.gps.connect('changed', self.onGPS, self.gpsControl)
		except:
			pass

		pattern = []
		duration = 0
		alt = 0

		if week == 1:
			pattern = [60,90]
			duration = 60*20
		elif week == 2:
			pattern = [60,120]
			duration = 60*20
		elif week == 3:
			pattern = [90,90,180,180]
			duration = sum(pattern)
		elif week == 4:
			pattern = [180,90,300,150,180,90,300]
			duration = sum(pattern)
		elif week == 5:
			if workout == 1:
				pattern = [300,180,300,180,300]
			elif workout == 2:
				pattern = [480,300,480]
			elif workout == 3:
				pattern = [1200]
			duration = sum(pattern)
		elif week == 6:
			if workout == 1:
				pattern = [300,180,480,180,300]
			elif workout == 2:
				pattern = [600,180,600]
			elif workout == 3:
				pattern = [1500]
			duration = sum(pattern)
		elif week == 7:
			pattern = [1500]
			duration = sum(pattern)
		elif week == 8:
			pattern = [1680]
			duration = sum(pattern)
		elif week == 9:
			pattern = [1800]
			duration = sum(pattern)

		x = 0
		while sum(self.pattern) < duration:	
			self.pattern.append(pattern[x % len(pattern)-1])
			x += 1

	def onGPS(self,device,data):
		try:
			d2r = 3.141592 / 180.0
			if not device:
				return
			if device.fix:
				if device.fix[1] & location.GPS_DEVICE_LATLONG_SET:
					pos = device.fix[4:6]
					#dlat = (pos[0]-self.oldLatLong[0]) * d2r
					#dlong = (pos[1]-self.oldLatLong[1]) * d2r
					#a = pow(math.sin(dlat/2.0), 2) + math.cos(self.oldLatLong[0]*d2r) * math.cos(pos[0]*d2r) * pow(math.sin(dlong/2.0), 2)
					#c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
					#d = round((3956 * c) / 10000,2)
					d = distVincenty(self.oldLatLong[0],self.oldLatLong[1],pos[0],pos[1])

					if self.oldLatLong != (0,0):
						self.distance += d
					self.oldLatLong = pos
		except:
			pass

	def gStart(self,data):
		data.start()

	def start(self,time):
		self.startTime = time
		self.started = True
		try:
			gobject.idle_add(self.gStart, self.gpsControl)
		except:
			pass

	def get(self,time):
		time -= self.startTime
		duration = self.warmup + sum(self.pattern[0:self.index+1])
		if time > duration:
			self.index += 1
		if time < self.warmup:
			return ('Walk',time)
		if time > self.warmup + sum(self.pattern):
			return ('Finished!',time)
		return (['Jog','Walk'][self.index % 2],time)

# Python version of the Vincenty algorithm as described
# on this very helpful page:
# http://www.movable-type.co.uk/scripts/latlong-vincenty.html
def distVincenty(lat1, lon1, lat2, lon2):
	a = 6378137
	b = 6356752.314245
	f = 1/298.257223563 # WGS-84 ellipsoid
	L = math.radians(lon2-lon1)
	U1 = math.atan((1-f) * math.tan(math.radians(lat1)))
	U2 = math.atan((1-f) * math.tan(math.radians(lat2)))
	sinU1 = math.sin(U1)
	cosU1 = math.cos(U1)
	sinU2 = math.sin(U2)
	cosU2 = math.cos(U2)
	lamb = L
	lambdaP = lamb
	iterLimit = 100

	while abs(lamb-lambdaP) > 1e-12 and --iterLimit>0:
		sinLambda = math.sin(lamb)
		cosLambda = math.cos(lamb)
		sinSigma = math.sqrt((cosU2*sinLambda) * (cosU2*sinLambda) +
			(cosU1*sinU2-sinU1*cosU2*cosLambda) * (cosU1*sinU2-sinU1*cosU2*cosLambda))
		if sinSigma == 0: return 0
		cosSigma = sinU1*sinU2 + cosU1*cosU2*cosLambda
		sigma = math.atan2(sinSigma, cosSigma)
		sinAlpha = cosU1 * cosU2 * sinLambda / sinSigma
		cosSqAlpha = 1 - sinAlpha * sinAlpha
		cos2SigmaM = cosSigma - 2*sinU1*sinU2/cosSqAlpha
		if math.isnan(cos2SigmaM): cos2SigmaM = 0
		c = f/16*cosSqAlpha*(4+f*(4-3*cosSqAlpha))
		lambdaP = lamb
		lamb = L + (1-C) * f * sinAlpha * (sigma +
			C*sinSigma * (cos2SigmaM+C*cosSigma*(-1+2*cos2SigmaM*cos2SigmaM)))

		if iterLimit == 0: return float('nan')

		uSq = cosSqAlpha * (a*a - b*b) / (b*b)
		A = 1 + uSq/16384 * (4096+uSq*(-768+uSq*(74-47*uSq)))
		B = uSq/1024 * (256+uSq*(-128+uSq*(74-47*uSq)))
		deltaSigma = B*sinSigma*(cos2SigmaM+B/4*(cosSigma*(-1+2*cos2SigmaM*cos2SigmaM) -
			B/6*cos2SigmaM*(-3+4*sinSigma*sinSigma)*(-3+4*cos2SigmaM*cos2SigmaM)))
		s = b*A*(sigma-deltaSigma)

		return round(s*0.000621371192,2)