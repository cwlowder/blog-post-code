import matplotlib.pyplot as plt
import numpy as np

from constants import *

def plot_apparent_vs_actual_remaining_distance(prefix, ship_times, actual_distances, apparent_distances):
	# halfway = 2*len(ship_times) // 9
	# second =  len(ship_times) // 2

	# # Slice the second half of each array
	# ship_times = ship_times[halfway:second]
	# actual_distances = actual_distances[halfway:second]
	# apparent_distances = apparent_distances[halfway:second]

	plt.figure(figsize=(10, 6))
	plt.suptitle(prefix.replace("_", " "), fontsize=14, y=1.0)  # super title above the regular title
	# plt.plot([d/LY for d in actual_distances], [d/LY for d in apparent_distances], color='purple')

	plt.plot(ship_times/YEAR, actual_distances/LY, label="Actual Distance Remaining (earth frame)", color='blue')
	plt.plot(ship_times/YEAR, apparent_distances/LY, label="Apparent Distance Remaining (ship frame)", color='red')

	plt.xlabel("Ship Time (years)")
	plt.ylabel("Remaining Distance (ly)")
	plt.title("Actual vs Apparent Remaining Distance Over Time")
	plt.legend()
	plt.grid(True)
	plt.savefig(f"output/{prefix}/{prefix}_remaining_apparent_vs_actual_distance.png", transparent=True)

def plot_apparent_vs_actual_target_velocity(prefix, earth_times, actual_distances, ship_times, apparent_distances, show_dialouge=False):
	plt.figure(figsize=(12, 5))
	plt.suptitle(prefix.replace("_", " "), fontsize=14, y=1.0)  # super title above the regular title
	# plt.plot([d/LY for d in actual_distances], [d/LY for d in apparent_distances], color='purple')
	target_vel_earth = np.gradient(actual_distances, earth_times) / C # Earth frame
	target_vel_ship = np.gradient(apparent_distances, ship_times) / C # Ship frame

	plt.subplot(1, 2, 1)
	plt.plot(earth_times/YEAR, target_vel_earth, color='blue')
	plt.xlabel("Earth Time (years)")
	plt.ylabel("Relative Velocity (fraction of c)")
	plt.title("Relative Velocity of Target to Ship (Earth Frame)")
	plt.ylim(top=0)
	plt.grid(True)

	plt.subplot(1, 2, 2)
	plt.plot(ship_times/YEAR, target_vel_ship, color='red')
	plt.xlabel("Ship Time (years)")
	plt.ylabel("Relative Velocity (fraction of c)")
	plt.title("Relative Velocity of Target to Ship (Ship Frame)")
	plt.ylim(top=0)
	plt.grid(True)

	if show_dialouge:
		# Add label for turnaround point
		halfway_time = ship_times[-1] / 2 / YEAR  # Convert to years
		plt.axvline(x=halfway_time, color='black', linestyle='dotted', linewidth=1.5)
		plt.text(halfway_time + 0.02, min(target_vel_ship) * 0.5,  # slight offset for readability
		 "Target appears to move away\nas ship burns to slow down",
		 rotation=0, color='black', fontsize=10,
		 bbox=dict(boxstyle="round,pad=0.3", edgecolor='black', facecolor='white', alpha=0.7))

	plt.tight_layout()
	plt.savefig(f"output/{prefix}/{prefix}_remaining_apparent_vs_target_velocity.png", transparent=True)


def plot_apparent_vs_actual_target_acceleration(prefix, earth_times, actual_distances, ship_times, apparent_distances):
	plt.figure(figsize=(12, 5))
	plt.suptitle(prefix.replace("_", " "), fontsize=14, y=1.0)  # super title above the regular title
	target_vel_earth = np.gradient(actual_distances, earth_times) / C # Earth frame
	target_vel_ship = np.gradient(apparent_distances, ship_times) / C # Ship frame

	target_accel_earth = np.gradient(target_vel_earth, earth_times) / G # Earth frame
	target_accel_ship = np.gradient(target_vel_ship, ship_times) / G # Ship frame

	# target_accel_earth = target_accel_earth[2:]
	# target_accel_ship = target_accel_ship[2:]

	# earth_times = earth_times[2:]
	# ship_times = ship_times[2:]

	plt.subplot(1, 2, 1)
	plt.plot(earth_times/YEAR, target_accel_earth, color='blue')
	plt.xlabel("Earth Time (years)")
	plt.ylabel("Relative Accel (fraction of g)")
	plt.title("Relative Accel of Target to Ship (Earth Frame)")
	plt.grid(True)

	plt.subplot(1, 2, 2)
	plt.plot(ship_times/YEAR, target_accel_ship, color='red')
	plt.xlabel("Ship Time (years)")
	plt.ylabel("Relative Accel (fraction of g)")
	plt.title("Relative Accel of Target to Ship (Ship Frame)")
	plt.grid(True)

	plt.tight_layout()
	plt.savefig(f"output/{prefix}/{prefix}_remaining_apparent_vs_target_accel.png", transparent=True)



def plot_ship_vs_earth_time(prefix, ship_times, earth_times):
	plt.figure(figsize=(10, 6))
	plt.suptitle(prefix.replace("_", " "), fontsize=14, y=1.0)  # super title above the regular title
	
	plt.plot(ship_times/DAY, earth_times/DAY, color='green', label="Time Flow on Ship vs Earth")
	plt.plot(ship_times/DAY, ship_times/DAY, color='black', linestyle='--', label="Time Flow on Earth (Stationary)")

	plt.xlabel("Time (Days, Ship clock)")
	plt.ylabel("Time (Days, Earth clock)")
	plt.title("Ship Time vs Earth Time (Relativistic Time Dilation)")
	plt.grid(True)
	plt.legend()
	plt.savefig(f"output/{prefix}/{prefix}_ship_vs_earth_time.png",transparent=True)


def plot_velocity_vs_time(prefix, earth_times, earth_velocities, ship_times, ship_velocities):
	plt.figure(figsize=(12, 6))
	plt.suptitle(prefix.replace("_", " "), fontsize=14, y=1.0)  # super title above the regular title

	# Earth-frame coordinate velocity plot
	plt.subplot(1, 2, 1)
	plt.plot(earth_times/YEAR, earth_velocities/C, color='blue', label='Coordinate Velocity (Earth frame)')
	plt.xlabel('Coordinate Time (years)')
	plt.ylabel('Velocity (fraction of c)')
	plt.title('Coordinate Velocity vs Time (Earth frame)')
	plt.grid(True)
	plt.legend()

	# Ship-frame proper velocity plot
	plt.subplot(1, 2, 2)
	plt.plot(ship_times/YEAR, ship_velocities/C, color='red', label='Proper Velocity (Ship frame)')
	plt.xlabel('Coordinate Time (years)')
	plt.ylabel('Proper Velocity (fraction of c)')
	plt.title('Proper Velocity vs Time (Ship frame)')
	plt.grid(True)
	plt.legend()

	plt.tight_layout()
	plt.savefig(f"output/{prefix}/{prefix}_velocities_vs_time.png", transparent=True)

import numpy as np
import matplotlib.pyplot as plt

def plot_acceleration_vs_time(prefix, input_accels, earth_times, earth_Vs, ship_times, ship_Vs):
	# Numerical derivatives dV/dt (acceleration) wrt coordinate time in m/s²
	# np.gradient handles uneven spacing if needed
	earth_accel = np.gradient(earth_Vs, earth_times) / G # Earth frame acceleration
	ship_accel = np.gradient(ship_Vs, ship_times) / G # Ship frame acceleration

	plt.figure(figsize=(12, 5))

	plt.suptitle(prefix.replace("_", " "), fontsize=14, y=1.0)  # super title above the regular title
	plt.subplot(1, 2, 1)
	plt.plot(earth_times/YEAR, earth_accel, '-', color='blue', label='Earth Frame Acceleration')
	input_line1, = plt.plot(earth_times/YEAR, input_accels/G, 'g--', label='Acceleration felt on Ship')
	input_line1.set_dashes([2, 5])  # 10 points on, 10 points off
	plt.xlabel('Earth Time (years)')
	plt.ylabel('Acceleration (g)')
	plt.title('Acceleration vs Time (Earth Observer)')
	plt.grid(True)
	plt.legend()

	plt.subplot(1, 2, 2)
	plt.plot(ship_times/YEAR, ship_accel, 'r-', label='Ship Frame Acceleration')
	input_line2, = plt.plot(ship_times/YEAR, input_accels/G, 'g--', label='Acceleration felt on Ship')
	input_line2.set_dashes([2, 5])  # 10 points on, 10 points off
	plt.xlabel('Ship Time (years)')
	plt.ylabel('Acceleration (g)')
	plt.title('Acceleration vs Time (Ship Observer)')
	plt.grid(True)
	plt.legend()

	plt.tight_layout()
	plt.savefig(f"output/{prefix}/{prefix}_acceleration_vs_time.png", transparent=True)
