from constants import *

def toReadableTime(seconds):
	if seconds < MINUTE:
		return f"{seconds:.4f} sec(s)"
	elif seconds < HOUR:
		return f"{seconds / MINUTE:.4f} min(s)"
	elif seconds < DAY:
		return f"{seconds / HOUR:.4f} hr(s)"
	elif seconds < WEEK:
		return f"{seconds / DAY:.4f} day(s)"
	elif seconds < MONTH:
		return f"{seconds / WEEK:.4f} week(s)"
	elif seconds < YEAR:
		return f"{seconds / MONTH:.4f} month(s)"
	elif seconds < DECADE:
		return f"{seconds / YEAR:.4f} yr(s)"
	elif seconds < CENTURY:
		return f"{seconds / DECADE:.4f} decade(s)"
	else:
		return f"{seconds / CENTURY:.4f} century(s)"

def toReadableDistance(distance):
	if abs(distance) < AU/5:
		return f"{distance:.4f}m"
	elif abs(distance) < LY/100:
		distance = distance / AU
		return f"{distance:.4f} au"
	else:
		distance = distance / LY
		return f"{distance:.4f} ly"

def toReadableVelocity(velocity):
	if abs(velocity) < 100:
		return f"{velocity:.4f} m/s"
	elif abs(velocity) < C/100:
		velocity /= 1000
		return f"{velocity:.4f} km/s"
	else:
		velocity /= C
		return f"{velocity:.5f} c"
