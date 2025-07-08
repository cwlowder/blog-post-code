import numpy as np

from constants import *
from helpers import *

class EarthFrame:
	def __init__(self):
		self.coordinate_time = 0.0  # seconds
		self.coordinate_distance = 0.0  # meters
		self.coordinate_velocity = 0.0  # m/s
	
	def update(self, rapidity_old, rapidity_new, proper_acceleration_g, delta_tau):
		proper_acceleration = proper_acceleration_g * G  # convert g to m/s²
		if np.isclose(proper_acceleration, 0):
			# Coasting phase, constant velocity
			velocity = C * np.tanh(rapidity_new)  # constant coordinate velocity
			gamma = 1 / np.sqrt(1 - (velocity**2) / (C**2))

			assert abs(velocity) <= C, "Velocity exceeded speed of light!"
			
			delta_t = gamma * delta_tau
			delta_x = velocity * delta_t
			
			self.coordinate_distance += delta_x
			self.coordinate_time += delta_t
			self.coordinate_velocity = velocity
		else:
			delta_x = (C**2 / proper_acceleration) * (np.cosh(rapidity_new) - np.cosh(rapidity_old))
			self.coordinate_distance += delta_x

			delta_t = (C / proper_acceleration) * (np.sinh(rapidity_new) - np.sinh(rapidity_old))
			self.coordinate_time += delta_t

			self.coordinate_velocity = C * np.tanh(rapidity_new)


class ShipFrame:
	def __init__(self, target_distance=0):
		self.proper_time = 0.0  # seconds onboard ship
		self.rapidity = 0.0     # hyperbolic angle
		self.proper_distance = 0.0
		self.proper_velocity = 0.0  # w = gamma * v

		self.target_distance = target_distance
	
	def apply_maneuver(self, duration_s, accel_g):
		accel = accel_g * G

		if accel == 0:
			# Coasting phase: constant velocity, linear proper distance growth
			velocity = C * np.tanh(self.rapidity)
			gamma = 1 / np.sqrt(1 - (velocity**2) / (C**2))
			delta_distance = velocity * duration_s * gamma  # Δx = v * Δτ * γ
			self.proper_distance += delta_distance

			# Proper velocity remains unchanged
			self.proper_velocity = C * np.sinh(self.rapidity)

			# Increment proper time
			self.proper_time += duration_s

			# Return unchanged rapidity for consistency
			return self.rapidity, self.rapidity
		else:
			# Increase rapidity by a * Δτ / c
			delta_rapidity = accel * duration_s / C
			rapidity_old = self.rapidity
			self.rapidity += delta_rapidity

			# Determine Distance
			old_cosh = np.cosh(self.rapidity - delta_rapidity)
			new_cosh = np.cosh(self.rapidity)
			delta_distance = (C ** 2 / accel) * (new_cosh - old_cosh)
			self.proper_distance += delta_distance
			
			# Proper velocity w = c * sinh(rapidity)
			self.proper_velocity = C * np.sinh(self.rapidity)
			
			# Increment proper time
			self.proper_time += duration_s

			return rapidity_old, self.rapidity

class Simulation:
	def __init__(self, target_distance_m):
		self.ship = ShipFrame(target_distance_m)
		self.earth = EarthFrame()
		self.target_distance = target_distance_m
		self.remaining_earth_distance = target_distance_m
		self.apparent_remaining_distance = target_distance_m

	def run(self, maneuver_sequence, step_size=60):
		"""
		maneuver_sequence: list of tuples [(acceleration_g, duration_s), ...]
		step_size: simulation time step in seconds (proper time)
		"""
		for accel_g, duration_s in maneuver_sequence:
			elapsed = 0
			while elapsed < duration_s:
				dt = min(step_size, duration_s - elapsed)
				
				# Apply maneuver for dt seconds of proper time
				rapidity_old, rapidity_new = self.ship.apply_maneuver(dt, accel_g)
				
				# Update Earth frame based on new rapidity
				self.earth.update(rapidity_old, rapidity_new, accel_g, dt)

				# Calculate aparent remaining distance
				self.remaining_earth_distance = self.target_distance - self.earth.coordinate_distance
				gamma = np.cosh(self.ship.rapidity)
				self.apparent_remaining_distance = self.remaining_earth_distance / gamma
				self.apparent_distance_to_earth = self.earth.coordinate_distance / gamma
				
				elapsed += dt
				
				# self.status()

				yield accel_g

				# # Stop if target reached
				# if self.earth.coordinate_distance >= self.target_distance:
				# 	print("Target distance reached!")
				# 	return

	def status(self):
		print("-" * 60)
		print(f"Distance Remaining (Earth frame): {toReadableDistance(self.remaining_earth_distance)}")
		print(f"Distance Remaining (Ship frame): {toReadableDistance(self.apparent_remaining_distance)}")
		print(f"Velocity (Earth frame): {toReadableVelocity(self.earth.coordinate_velocity)}")
		print(f"Proper velocity (Ship frame): {toReadableVelocity(self.ship.proper_velocity)}")
		print(f"Proper time (Ship frame): {toReadableTime(self.ship.proper_time)}")
		print(f"Coordinate time (Earth frame): {toReadableTime(self.earth.coordinate_time)}")
		print("-" * 60)
