import numpy as np

from animation import animate_spaceship_flight
from plotters import *
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
				self.remaining_earth_distance = max(0.0, self.target_distance - self.earth.coordinate_distance)
				gamma = np.cosh(self.ship.rapidity)
				self.apparent_remaining_distance = self.remaining_earth_distance / gamma
				self.apparent_distance_to_earth = self.earth.coordinate_distance / gamma
				
				elapsed += dt
				
				# self.status()

				yield accel_g

				# Stop if target reached
				if self.earth.coordinate_distance >= self.target_distance:
					print("Target distance reached!")
					return

	def status(self):
		print("-" * 60)
		print(f"Distance Remaining (Earth frame): {toReadableDistance(self.remaining_earth_distance)}")
		print(f"Distance Remaining (Ship frame): {toReadableDistance(self.apparent_remaining_distance)}")
		print(f"Velocity (Earth frame): {toReadableVelocity(self.earth.coordinate_velocity)}")
		print(f"Proper velocity (Ship frame): {toReadableVelocity(self.ship.proper_velocity)}")
		print(f"Proper time (Ship frame): {toReadableTime(self.ship.proper_time)}")
		print(f"Coordinate time (Earth frame): {toReadableTime(self.earth.coordinate_time)}")
		print("-" * 60)

if __name__ == "__main__":
	# Example: travel to Alpha Centauri (~4.37 light years)
	# Maneuver sequence: [(acceleration_g, duration_seconds), ...]
	# Brachistochrone Trajectory to Alpha Centuri
	graph_prefix = "Alpha_Centauri_Brachistochrone"
	target_distance = 4.37 * LY
	maneuver_sequence = [
		(5.0, MONTH*8+DAY*2+HOUR*9+MINUTE*30+2),
		(-5.0, MONTH*8+DAY*2+HOUR*9+MINUTE*30+2),
	]

	# Coasting Trajectory to Alpha Centuri
	# graph_prefix = "Alpha_Centauri_Coasting"
	# target_distance = 4.37 * LY
	# maneuver_sequence = [
	# 	(5.0, MONTH*6),
	# 	(0.0, MONTH*6+WEEK*2+HOUR*9),
	# 	(-5.0, MONTH*6),
	# ]

	# Burst and Coast
	# graph_prefix = "Burst_and_Coast"
	# target_distance = 4.37 * LY
	# maneuver_sequence = [
	# 	(10.0, MONTH*3),
	# 	(0.0, MONTH*9),
	# ]

	# Burst and Coast
	# graph_prefix = "Slow_Burn"
	# target_distance = 4.37 * LY
	# maneuver_sequence = [
	# 	(1.0, YEAR*3),
	# ]

	# Trip by ISV in Avatar
	# graph_prefix = "Avatar"
	# target_distance = 4.37 * LY
	# maneuver_sequence = [
	# 	(1.5, MONTH*6.7208), # .7 c
	# 	(0, YEAR*3.93085), # .7 c
	# 	(-1.5, MONTH*6.7208), # .7 c
	# ]

	proper_times = []
	coordinate_times = []
	proper_distances = []
	actual_remaining_ds = []
	apparent_remaining_ds = []
	apparent_to_earth_ds = []
	proper_velocities = []
	coordinate_velocities = []
	input_accels = []
	sim = Simulation(target_distance)
	for accel_g in sim.run(maneuver_sequence, step_size=HOUR):
		# sim.status()
		proper_times.append(sim.ship.proper_time)
		coordinate_times.append(sim.earth.coordinate_time)
		proper_distances.append(sim.ship.proper_distance)
		actual_remaining_ds.append(sim.remaining_earth_distance)
		apparent_remaining_ds.append(sim.apparent_remaining_distance)
		apparent_to_earth_ds.append(sim.apparent_distance_to_earth)
		proper_velocities.append(sim.ship.proper_velocity)
		coordinate_velocities.append(sim.earth.coordinate_velocity)
		input_accels.append(accel_g*G)

	proper_times = np.array(proper_times)
	coordinate_times = np.array(coordinate_times)
	proper_distances = np.array(proper_distances)
	actual_remaining_ds = np.array(actual_remaining_ds)
	apparent_to_earth_ds = np.array(apparent_to_earth_ds)
	apparent_remaining_ds = np.array(apparent_remaining_ds)
	proper_velocities = np.array(proper_velocities)
	coordinate_velocities = np.array(coordinate_velocities)
	input_accels = np.array(input_accels)

	sim.status()
	plot_apparent_vs_actual_remaining_distance(graph_prefix, proper_times, actual_remaining_ds, apparent_remaining_ds)
	plot_apparent_vs_actual_target_velocity(graph_prefix, coordinate_times, actual_remaining_ds, proper_times, apparent_remaining_ds, show_dialouge=False)
	plot_ship_vs_earth_time(graph_prefix, proper_times, coordinate_times)
	plot_velocity_vs_time(graph_prefix, coordinate_times, coordinate_velocities, proper_times, proper_velocities)
	plot_acceleration_vs_time(graph_prefix, input_accels, coordinate_times, coordinate_velocities, proper_times, proper_velocities)
	animate_spaceship_flight(
		prefix=graph_prefix,
		target_distance_ly=target_distance/LY,
		input_accels=input_accels,
		proper_times=proper_times,
		coordinate_times=coordinate_times,
		proper_distances=proper_distances,
		coordinate_velocities=coordinate_velocities,
		proper_velocities=proper_velocities,
		actual_remaining_ds=actual_remaining_ds,
		apparent_remaining_ds=apparent_remaining_ds,
		apparent_to_earth_ds=apparent_to_earth_ds,
		save_ship_path="ship_frame_animation.mp4",
		save_earth_path="earth_frame_animation.mp4",
		fps=10,
		step=WEEK
	)

# ------------------------------------------------------------
# Distance (Earth frame): 4.3700 ly / 4.3700 ly
# Velocity (Earth frame): -0.00 m/s
# Proper velocity (Ship frame): -0.00 m/s
# Proper time (Ship frame): 1.24 yr(s)
# Coordinate time (Earth frame): 4.74 yr(s)
# ------------------------------------------------------------

# (4.60253727/2) Years to reach 27900 Lightyears at 5 G
