#!/usr/bin/env python3
import numpy as np
import argparse
import csv
import os
import re
import time

from animation import animate_spaceship_flight
from plotters import *
from simulation import Simulation
from constants import * 
from helpers import toReadableTime

default_distance = 4.37 * LY

demos = {
	"alpha_centauri_brachistochrone": {
		"maneuvers": [
			(5.0, 8*MONTH+2*DAY+9*HOUR+30*MINUTE*30+2),
			(-5.0, 8*MONTH+2*DAY+9*HOUR+30*MINUTE*30+2),
		],
		"target_distance": 4.37 * LY
	},
	"alpha_centauri_coasting": {
		"maneuvers": [
			(5.0, 6*MONTH),
			(0.0, MONTH*6+WEEK*2+HOUR*9),
			(-5.0, 6*MONTH),
		],
		"target_distance": 4.37 * LY,
	},
	"burst_and_coast": {
		"maneuvers": [
			(10.0, 3*MONTH),
			(0, 9*MONTH),
		],
		"target_distance": 4.37 * LY,
	},
	"slow_burn": {
		"maneuvers": [
			(1, 3*YEAR),
		],
		"target_distance": 4.37 * LY,
	},
	"avatar_isv": {
		"maneuvers": [
			(1.5, MONTH*6.7208), # .7 c
			(0, YEAR*3.93085), # .7 c
			(-1.5, MONTH*6.7208), # .7 c
		],
		"target_distance": 4.37 * LY,
		"ship_model": 'isv',
		"use_sail": True,
	}
}

def get_demo_maneuvers(name):
	if name not in demos:
		raise ValueError(f"Unknown demo name: {name}")
	return demos[name]

def parse_maneuver_file(args):
	"""
	Parses a maneuver file with lines formatted as:
	acceleration_g, duration
	"""
	maneuvers = []
	with open(args.maneuver_file, newline='') as csvfile:
		reader = csv.reader(csvfile)
		for row in reader:
			if len(row) != 2:
				raise ValueError(f"Invalid row in maneuver file: {row}")
			accel_g = float(row[0])
			duration_s = parse_duration_with_units(row[1])
			if args.verbose:
				print(f"Planned maneuver: {accel_g} g, {toReadableTime(duration_s)}")
			maneuvers.append((accel_g, duration_s))
	return maneuvers

def parse_distance_with_units(s):
    """
    Parse a string with optional units: m, km, au, ly
    Example inputs: '5m', '10 m', '4.37 ly', '7au'
    """
    if s == None:
    	return None
    if type(s) == float or type(s) == int:
    	return s

    s = s.strip().lower()
    match = re.match(r'^([0-9.]+)\s*([a-z]*)$', s)
    if not match:
        raise argparse.ArgumentTypeError(f"Invalid distance format: {s}")

    value, unit = match.groups()
    value = float(value)

    unit_multipliers = {
        '': 1.0, # default is meters
        'm': 1.0,
        'km': 1e3,
        'au': AU,
        'ly': LY,
        'pc': PC, # parsecs
    }

    if unit not in unit_multipliers:
        raise argparse.ArgumentTypeError(f"Unsupported unit '{unit}' in distance '{s}'. Supported: m, km, au, ly")

    return value * unit_multipliers[unit]

def parse_duration_with_units(s):
    """
    Parse a string with optional time units:
    s, min, h, d, y
    Supports inputs like '10s', '1.5 h', '2 days', '3y'
    """
    s = s.strip().lower()
    match = re.match(r'^([0-9.]+)\s*([a-z]*)$', s)
    if not match:
        raise argparse.ArgumentTypeError(f"Invalid duration format: '{s}'")

    value_str, unit = match.groups()
    value = float(value_str)

    unit_multipliers = {
        '': 1, # default to seconds
        's': 1,
        'sec': 1,
        'secs': 1,
        'min': MINUTE,
        'm': MINUTE,
        'h': HOUR,
        'hr': HOUR,
        'd': DAY,
        'day': DAY,
        'days': DAY,
        'mn': MONTH,
        'month': MONTH,
        'months': MONTH,
        'y': YEAR,
        'yr': YEAR,
        'yrs': YEAR,
        'year': YEAR,
        'years': YEAR
    }

    if unit not in unit_multipliers:
        raise argparse.ArgumentTypeError(
            f"Unsupported unit '{unit}' in duration '{s}'. Supported: s, min, h, d, y"
        )

    return value * unit_multipliers[unit]

def run_simulation(maneuvers, args):
	proper_times = []
	coordinate_times = []
	proper_distances = []
	actual_remaining_ds = []
	apparent_remaining_ds = []
	apparent_to_earth_ds = []
	proper_velocities = []
	coordinate_velocities = []
	input_accels = []
	sim = Simulation(args.target_distance)
	if args.verbose:
		print("Starting simulation")
	start_time = time.time()
	for accel_g in sim.run(maneuvers, step_size=HOUR):
		proper_times.append(sim.ship.proper_time)
		coordinate_times.append(sim.earth.coordinate_time)
		proper_distances.append(sim.ship.proper_distance)
		actual_remaining_ds.append(sim.remaining_earth_distance)
		apparent_remaining_ds.append(sim.apparent_remaining_distance)
		apparent_to_earth_ds.append(sim.apparent_distance_to_earth)
		proper_velocities.append(sim.ship.proper_velocity)
		coordinate_velocities.append(sim.earth.coordinate_velocity)
		input_accels.append(accel_g*G)
	elapsed = time.time() - start_time
	if args.verbose:
		print(f"Simulation completed in {elapsed:.2f} seconds.")
	
	proper_times = np.array(proper_times)
	coordinate_times = np.array(coordinate_times)
	proper_distances = np.array(proper_distances)
	actual_remaining_ds = np.array(actual_remaining_ds)
	apparent_to_earth_ds = np.array(apparent_to_earth_ds)
	apparent_remaining_ds = np.array(apparent_remaining_ds)
	proper_velocities = np.array(proper_velocities)
	coordinate_velocities = np.array(coordinate_velocities)
	input_accels = np.array(input_accels)

	if not args.hide_status:
		sim.status()

	if args.log:
		import csv
		import os

		output_path = f"./output/{args.name}/data.csv"
		if args.verbose:
			print(f"Saving logs to {output_path}")
		os.makedirs(os.path.dirname(output_path), exist_ok=True)
		with open(output_path, 'w', newline='') as f:
			writer = csv.writer(f)
			# Header
			writer.writerow([
				"proper_time_s",
				"coordinate_time_s",
				"proper_distance_m",
				"remaining_earth_distance_m",
				"apparent_remaining_distance_m",
				"apparent_distance_to_earth_m",
				"proper_velocity_mps",
				"coordinate_velocity_mps",
				"acceleration_mps2"
			])
			# Data rows
			for row in zip(
				proper_times,
				coordinate_times,
				proper_distances,
				actual_remaining_ds,
				apparent_remaining_ds,
				apparent_to_earth_ds,
				proper_velocities,
				coordinate_velocities,
				input_accels
			):
				writer.writerow(row)
		
		if args.verbose:
			print(f"Simulation results saved to: {output_path}")

	if args.graph:
		import os

		if args.verbose:
			print(f"Saving graphs to ./output/{args.name}/")
		os.makedirs(os.path.dirname(f"./output/{args.name}/"), exist_ok=True)
		plot_apparent_vs_actual_remaining_distance(args.name, proper_times, actual_remaining_ds, apparent_remaining_ds)
		plot_apparent_vs_actual_target_velocity(args.name, coordinate_times, actual_remaining_ds, proper_times, apparent_remaining_ds, show_dialouge=False)
		plot_ship_vs_earth_time(args.name, proper_times, coordinate_times)
		plot_velocity_vs_time(args.name, coordinate_times, coordinate_velocities, proper_times, proper_velocities)
		plot_acceleration_vs_time(args.name, input_accels, coordinate_times, coordinate_velocities, proper_times, proper_velocities)

	if args.animate:
		animate_spaceship_flight(
			prefix=args.name,
			target_distance_ly=args.target_distance/LY,
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
			use_sail=args.use_sail or False,
			ship_model=args.ship_model or 'base',
			fps=10,
			step=MONTH,
		)


def main():
	parser = argparse.ArgumentParser(description="Run relativistic spaceship simulations.")

	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument("--maneuver-file", "--file", "-m", type=str, help="Path to CSV maneuver file with (accel_g, duration_s) rows.")
	group.add_argument("--demo", choices=demos.keys(), help="Run a built-in maneuver demo (e.g., slow_burn, burst_and_coast).")

	parser.add_argument("-n", "--name", type=str, default="test",
						help="Name of maneuver (default: test)")
	parser.add_argument("-d", "--target-distance", type=parse_distance_with_units, default=None,
						help="Target distance with unit (e.g.: 3.0 au, default without unit meters, default: 4.37 light years).")
	parser.add_argument("-s", "--step", type=float, default=60.0,
						help="Step size in seconds of proper time (default: 60).")
	parser.add_argument("--ship-model", type=str, default='base',
						help="Ship model to use for animation (default: base)")
	parser.add_argument("--use-sail", action='store_true',
						help="Use sail in animation (default: false)")
	parser.add_argument("--hide-status", action="store_true",
						help="Print status at end of simulation.")
	parser.add_argument("--verbose", "-v", action="store_true",
						help="Print status at end of simulation.")
	parser.add_argument("--graph", "-g", action="store_true",
						help="Generate graphs into output path.\nSaved to file in ./output/{{name}}")
	parser.add_argument("--log", "-l", action="store_true",
						help="Log raw data to csvfile\nSaved to file ./output/data.csv")
	parser.add_argument("--animate", "-a", action="store_true",
						help="Generate animations\nSaved to file ./output/{}.mp4")

	args = parser.parse_args()

	try:
		if args.demo:
			config = get_demo_maneuvers(args.demo)
			maneuvers = config["maneuvers"]
			args.name = args.demo
			args.target_distance = config["target_distance"]
			args.ship_model = config.get("ship_model", 'base')
			args.use_sail = config.get("use_sail", False)
		else:
			maneuvers = parse_maneuver_file(args)
			args.target_distance = parse_distance_with_units(args.target_distance)
			if not args.target_distance:
				args.target_distance = default_distance

		run_simulation(maneuvers, args)

	except Exception as e:
		print(f"Error: {e}")


if __name__ == "__main__":
	main()
