import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patches as patches

from constants import *
from helpers import *

# Normalized ship shape coords (unit size)
base_ship_coords = np.array([
	[0.15, 0],   # nose right
	[0.05, 0.07],
	[-0.05, 0.07], 
	[-0.15, 0],  # tail left
	[-0.05, -0.07], 
	[0.05, -0.07]
])

# Flames normalized coords (unit size)
base_left_flame_coords = np.array([
	[-0.15 - 0.1, 0],
	[-0.15, 0.05],
	[-0.15, -0.05]
])

base_right_flame_coords = np.array([
	[0.15 + 0.1, 0],
	[0.15, 0.05],
	[0.15, -0.05]
])

threshold = 0.01 * G  # threshold for showing flames

base_marker_size = 0.2


def time_based_indices(times, step_seconds):
	indices = [0]
	last_time = times[0]
	for i, t in enumerate(times):
		if t - last_time >= step_seconds:
			indices.append(i)
			last_time = t
	if indices[-1] != len(times) - 1:
		indices.append(len(times) - 1)
	return np.array(indices)


# Function to extend indices with freeze frames
def add_freeze(indices, freeze_start, freeze_end):
	start = np.full(freeze_start, indices[0])
	end = np.full(freeze_end, indices[-1])
	return np.concatenate([start, indices, end])

def create_clock(ax, center_x, center_y, radius=0.05, color='black'):
	"""Creates a simple clock face with a rotating hand."""
	clock_circle = plt.Circle((center_x, center_y), radius, edgecolor=color, facecolor='none', zorder=3)
	clock_hand, = ax.plot([], [], color=color, lw=1.5, zorder=4)
	ax.add_patch(clock_circle)
	return clock_hand, clock_circle, center_x, center_y, radius

def setup_ship_frame_plot(prefix):
	fig, ax = plt.subplots(figsize=(8, 3))
	ax.set_ylim(-1, 1)
	ax.axis('off')

	# Football shape for ship (ellipse-like polygon)
	ship_coords = base_ship_coords

	ship_patch = patches.Polygon(ship_coords, closed=True, color='red', zorder=5)
	ax.add_patch(ship_patch)

	# Flames: triangles on left and right, initially invisible
	left_flame_coords = base_left_flame_coords
	left_flame = patches.Polygon(left_flame_coords, closed=True, color='orange', visible=False, zorder=4)
	ax.add_patch(left_flame)

	right_flame_coords = base_right_flame_coords
	right_flame = patches.Polygon(right_flame_coords, closed=True, color='orange', visible=False, zorder=4)
	ax.add_patch(right_flame)

	# Earth and target markers
	# earth_marker, = ax.plot([], [], 'bo', markersize=20, label='Earth')
	# target_marker, = ax.plot([], [], 'go', markersize=20, label='Target')
	earth_marker = patches.Ellipse((0, 0), width=base_marker_size, height=base_marker_size, color='blue', zorder=3)
	ax.add_patch(earth_marker)

	target_marker = patches.Ellipse((0, 0), width=base_marker_size, height=base_marker_size, color='green', zorder=3)
	ax.add_patch(target_marker)

	clock_earth_hand, clock_earth_circle, clock_earth_x, clock_earth_y, clock_earth_r = create_clock(ax, 0, -0.2, color="blue")
	clock_target_hand, clock_target_circle, clock_target_x, clock_target_y, clock_target_r = create_clock(ax, 0, -0.2, color="blue")
	clock_ship_hand, clock_ship_circle, clock_ship_x, clock_ship_y, clock_ship_r = create_clock(ax, 0, 0.2, color="red")

	title_text = ax.text(0, 0.8, '', transform=ax.transAxes, fontsize=12, fontweight='bold')
	title_text.set_text(prefix.replace("_", " "))
	distance_text = ax.text(0.4, 0.2, '', transform=ax.transAxes, fontsize=12, fontweight='bold')

	return {
		'fig': fig,
		'ax': ax,
		'ship_patch': ship_patch,
		'left_flame': left_flame,
		'right_flame': right_flame,
		'earth_marker': earth_marker,
		'target_marker': target_marker,
		'title_text': title_text,
		'distance_text': distance_text,
		'clock_earth_hand': clock_earth_hand,
		'clock_earth_circle': clock_earth_circle,
		'clock_earth_x': clock_earth_x,
		'clock_earth_y': clock_earth_y,
		'clock_earth_r': clock_earth_r,
		'clock_target_hand': clock_target_hand,
		'clock_target_circle': clock_target_circle,
		'clock_target_x': clock_target_x,
		'clock_target_y': clock_target_y,
		'clock_target_r': clock_target_r,
		'clock_perspective_ship_hand': clock_ship_hand,
		'clock_perspective_ship_circle': clock_ship_circle,
		'clock_perspective_ship_x': clock_ship_x,
		'clock_perspective_ship_y': clock_ship_y,
		'clock_perspective_ship_r': clock_ship_r,
	}

def animate_spaceship_flight(
	prefix,
	target_distance_ly,
	input_accels,
	proper_times,
	coordinate_times,
	proper_distances,
	coordinate_velocities,
	proper_velocities,
	actual_remaining_ds,
	apparent_remaining_ds,
	apparent_to_earth_ds,
	save_ship_path=None,
	save_earth_path=None,
	fps=20,
	step=WEEK,
	freeze_start_frames=20,
	freeze_end_frames=20,
):
	"""
	Generate two animations of a spaceship flying between Earth and a target:
	  - Ship frame animation
	  - Earth frame animation

	Parameters:
	- prefix: str, name of experiment being conducted
	- target_distance_ly: float, distance to target in lightyears
	- input_accels: np.array, accel ordered by the ship's engine
	- proper_times: np.array, simulation times in ship frame
	- coordinate_times: np.array, simulation times in earth frame
	- proper_distances: np.array, apparent traveled distance from ship frame (meters)
	- coordinate_velocities: np.array, velocity as measured from earth frame (m/s)
	- proper_velocities: np.array, velocity as measured from ship frame (m/s)
	- actual_remaining_ds: np.array, remaining distance from earth frame (meters)
	- apparent_remaining_ds: np.array, remaining distance from ship frame (meters)
	- apparent_to_earth_ds: np.array, apparent distance to earth from ship frame (meters)
	- save_ship_path: str or None, if given save ship frame animation to this path (e.g. 'ship_anim.mp4')
	- save_earth_path: str or None, if given save earth frame animation to this path (e.g. 'earth_anim.mp4')
	- fps: frames per second (controls animation speed)
	- step: how many simulation data points to skip per frame (e.g. step=MONTH means each frame is one Month after the previous)

	Returns:
	- anim_ship, anim_earth: FuncAnimation objects
	"""	
	interval = int(1000 / fps)  # interval in ms between frames'
	ship_indices = time_based_indices(proper_times, step // 5) # Run ship animation slower
	earth_indices = time_based_indices(coordinate_times, step)

	# Freeze start and end of animation
	ship_indices = add_freeze(ship_indices, freeze_start_frames, freeze_end_frames)
	earth_indices = add_freeze(earth_indices, freeze_start_frames, freeze_end_frames)

	# Ship frame
	ship_plot = setup_ship_frame_plot(prefix)

	fig_ship = ship_plot['fig']
	ax_ship = ship_plot['ax']
	ship_patch = ship_plot['ship_patch']
	left_flame = ship_plot['left_flame']
	right_flame = ship_plot['right_flame']
	earth_marker_ship = ship_plot['earth_marker']
	target_marker_ship = ship_plot['target_marker']
	dist_text_ship = ship_plot['distance_text']
	clock_earth_hand = ship_plot['clock_earth_hand']
	clock_earth_circle = ship_plot['clock_earth_circle']
	clock_earth_x = ship_plot['clock_earth_x']
	clock_earth_y = ship_plot['clock_earth_y']
	clock_target_hand = ship_plot['clock_target_hand']
	clock_target_circle = ship_plot['clock_target_circle']
	clock_target_x = ship_plot['clock_target_x']
	clock_target_y = ship_plot['clock_target_y']
	clock_perspective_ship_hand = ship_plot['clock_perspective_ship_hand']
	clock_perspective_ship_circle = ship_plot['clock_perspective_ship_circle']
	clock_ship_perspective_x = ship_plot['clock_perspective_ship_x']
	clock_ship_perspective_y = ship_plot['clock_perspective_ship_y']

	def init_ship():
		earth_marker_ship.center = (0, 0)
		target_marker_ship.center = (0, 0)

		dist_text_ship.set_text('')
		# Flames off initially
		left_flame.set_visible(False)
		right_flame.set_visible(False)

		return ship_patch, left_flame, right_flame, earth_marker_ship, target_marker_ship, dist_text_ship

	def animate_ship(frame_idx):
		i = ship_indices[frame_idx]

		apparent_distance = apparent_remaining_ds[i] / LY
		apparent_dist_to_earth = apparent_to_earth_ds[i] / LY

		total_apparent_distance = apparent_distance + apparent_dist_to_earth
		if total_apparent_distance > 0:
			scale = total_apparent_distance / target_distance_ly
		else:
			scale = 1.0

		# Scale Earth and Target relative positions
		earth_pos_scaled = -apparent_dist_to_earth
		target_pos_scaled = apparent_distance

		earth_marker_ship.center = (earth_pos_scaled, 0)
		target_marker_ship.center = (target_pos_scaled, 0)

		earth_marker_ship.width = base_marker_size * scale
		earth_marker_ship.height = base_marker_size

		target_marker_ship.width = base_marker_size * scale
		target_marker_ship.height = base_marker_size

		ax_ship.set_xlim(-0.5, target_distance_ly + 0.5)

		dist_text_ship.set_text(f"Distance Remaining (ship frame): {toReadableDistance(apparent_remaining_ds[i])}\nShip Speed (ship frame): {toReadableVelocity(proper_velocities[i])}")

		accel = input_accels[i]
		if frame_idx <= freeze_start_frames or frame_idx >= len(ship_indices) - freeze_end_frames:
			left_flame.set_visible(False)
			right_flame.set_visible(False)
		elif accel > threshold:
			left_flame.set_visible(True)
			right_flame.set_visible(False)
		elif accel < -threshold:
			left_flame.set_visible(False)
			right_flame.set_visible(True)
		else:
			left_flame.set_visible(False)
			right_flame.set_visible(False)

		# Total time elapsed in frame
		current_coordinate_time = coordinate_times[ship_indices[frame_idx]]
		current_proper_time = proper_times[ship_indices[frame_idx]]

		# One full rotation every 12 proper time units (e.g., 12 years)
		angle_static = (current_coordinate_time % (12 * step)) / (12 * step) * 2 * np.pi
		angle_ship = (current_proper_time % (12 * step)) / (12 * step) * 2 * np.pi

		# Clock below Earth
		clock_earth_hand.set_data(
			[earth_pos_scaled, earth_pos_scaled + 0.05 * np.cos(angle_static)],
			[-0.2, -0.2 + 0.05 * np.sin(angle_static)]
		)
		clock_earth_circle.center = (earth_pos_scaled, -0.2)

		# Clock below Target
		clock_target_hand.set_data(
			[target_pos_scaled, target_pos_scaled + 0.05 * np.cos(angle_static)],
			[-0.2, -0.2 + 0.05 * np.sin(angle_static)]
		)
		clock_target_circle.center = (target_pos_scaled, -0.2)

		# Clock Above
		clock_perspective_ship_hand.set_data(
		    [0, 0 + 0.05 * np.cos(angle_ship)],
		    [0.2 + 0, 0.2 + 0.05 * np.sin(angle_ship)]
		)
		clock_perspective_ship_circle.center = (0, 0.2)

		return (ship_patch, left_flame, right_flame, earth_marker_ship, target_marker_ship, dist_text_ship, 
				clock_earth_hand, clock_target_hand, clock_earth_circle, clock_target_circle, clock_perspective_ship_hand, clock_perspective_ship_circle)


	anim_ship = animation.FuncAnimation(
		fig_ship, animate_ship, init_func=init_ship,
		frames=len(ship_indices), interval=interval, blit=True
	)


	def setup_earth_frame_plot(target_distance_ly):
		fig, ax = plt.subplots(figsize=(8, 3))
		ax.set_xlim(-0.1, target_distance_ly + 0.1)
		ax.set_ylim(-1, 1)
		ax.axis('off')

		earth_marker, = ax.plot(0, 0, 'bo', markersize=20, label='Earth')
		target_marker, = ax.plot(target_distance_ly, 0, 'go', markersize=20, label='Target')

		ship_patch = patches.Polygon([[0,0]], closed=True, color='red', zorder=5)  # placeholder
		ax.add_patch(ship_patch)

		left_flame = patches.Polygon([[0,0]], closed=True, color='orange', visible=False, zorder=4)
		ax.add_patch(left_flame)

		right_flame = patches.Polygon([[0,0]], closed=True, color='orange', visible=False, zorder=4)
		ax.add_patch(right_flame)

		title_text = ax.text(0, 0.8, '', transform=ax.transAxes, fontsize=12, fontweight='bold')
		title_text.set_text(prefix.replace("_", " "))
		distance_text = ax.text(0.5, 0.2, '', transform=ax.transAxes, fontsize=12)

		clock_perspective_earth_hand, clock_perspective_earth_circle, clock_perspective_earth_x, clock_perspective_earth_y, clock_perspective_earth_r = create_clock(ax, 0, -0.2, color="blue")
		clock_perspective_target_hand, clock_perspective_target_circle, clock_perspective_target_x, clock_perspective_target_y, clock_perspective_target_r = create_clock(ax, 0, -0.2, color="blue")
		clock_ship_hand, clock_ship_circle, clock_ship_x, clock_ship_y, clock_ship_r = create_clock(ax, 0, 0.2, color="red")

		return {
			'fig': fig,
			'ax': ax,
			'earth_marker': earth_marker,
			'target_marker': target_marker,
			'ship_patch': ship_patch,
			'left_flame': left_flame,
			'right_flame': right_flame,
			'title_text': title_text,
			'distance_text': distance_text,
			'clock_ship_hand': clock_ship_hand,
			'clock_ship_circle': clock_ship_circle,
			'clock_ship_x': clock_ship_x,
			'clock_ship_y': clock_ship_y,
			'clock_ship_r': clock_ship_r,
			'clock_perspective_earth_hand': clock_perspective_earth_hand,
			'clock_perspective_earth_circle': clock_perspective_earth_circle,
			'clock_perspective_earth_x': clock_perspective_earth_x,
			'clock_perspective_earth_y': clock_perspective_earth_y,
			'clock_perspective_earth_r': clock_perspective_earth_r,
			'clock_perspective_target_hand': clock_perspective_target_hand,
			'clock_perspective_target_circle': clock_perspective_target_circle,
			'clock_perspective_target_x': clock_perspective_target_x,
			'clock_perspective_target_y': clock_perspective_target_y,
			'clock_perspective_target_r': clock_perspective_target_r,
		}

	earth_plot = setup_earth_frame_plot(target_distance_ly)

	fig_earth = earth_plot['fig']
	ax_earth = earth_plot['ax']
	earth_marker_earth = earth_plot['earth_marker']
	target_marker_earth = earth_plot['target_marker']
	ship_patch_earth = earth_plot['ship_patch']
	left_flame_earth = earth_plot['left_flame']
	right_flame_earth = earth_plot['right_flame']
	dist_text_earth = earth_plot['distance_text']
	clock_ship_hand = earth_plot['clock_ship_hand']
	clock_ship_circle = earth_plot['clock_ship_circle']
	clock_ship_x = earth_plot['clock_ship_x']
	clock_ship_y = earth_plot['clock_ship_y']
	clock_perspective_earth_hand = earth_plot['clock_perspective_earth_hand']
	clock_perspective_earth_circle = earth_plot['clock_perspective_earth_circle']
	clock_perspective_earth_x = earth_plot['clock_perspective_earth_x']
	clock_perspective_earth_y = earth_plot['clock_perspective_earth_y']
	clock_perspective_target_hand = earth_plot['clock_perspective_target_hand']
	clock_perspective_target_circle = earth_plot['clock_perspective_target_circle']
	clock_perspective_target_x = earth_plot['clock_perspective_target_x']
	clock_perspective_target_y = earth_plot['clock_perspective_target_y']

	def init_earth():
		dist_text_earth.set_text('')
		left_flame_earth.set_visible(False)
		right_flame_earth.set_visible(False)
		# Move ship patch offscreen initially
		ship_patch_earth.set_xy(np.array([[10, 10]]))
		left_flame_earth.set_xy(np.array([[10, 10]]))
		right_flame_earth.set_xy(np.array([[10, 10]]))
		return ship_patch_earth, left_flame_earth, right_flame_earth, dist_text_earth

	def animate_earth(frame_idx):
		i = earth_indices[frame_idx]

		ship_pos = target_distance_ly - actual_remaining_ds[i] / LY # offset to center ship

		# Scale ship size relative to total distance
		ship_scale = .5

		# Scale and translate ship polygon
		scaled_coords = base_ship_coords * ship_scale
		translated_coords = scaled_coords + np.array([ship_pos, 0])
		ship_patch_earth.set_xy(translated_coords)

		dist_text_earth.set_text(f"Distance (earth frame): {toReadableDistance(actual_remaining_ds[i])}\nShip Speed (earth frame): {toReadableVelocity(coordinate_velocities[i])}")

		accel = input_accels[i]

		# Don't show frames at beggining or end of animation
		if frame_idx <= freeze_start_frames or frame_idx >= len(earth_indices) - freeze_end_frames:
			left_flame_earth.set_visible(False)
			right_flame_earth.set_visible(False)
		elif accel > threshold:
			left_flame_earth.set_visible(True)
			right_flame_earth.set_visible(False)
			left_flame_coords = base_left_flame_coords * ship_scale + np.array([ship_pos, 0])
			left_flame_earth.set_xy(left_flame_coords)
		elif accel < -threshold:
			left_flame_earth.set_visible(False)
			right_flame_earth.set_visible(True)
			right_flame_coords = base_right_flame_coords * ship_scale + np.array([ship_pos, 0])
			right_flame_earth.set_xy(right_flame_coords)
		else:
			left_flame_earth.set_visible(False)
			right_flame_earth.set_visible(False)

		current_coordinate_time = coordinate_times[earth_indices[frame_idx]]
		current_proper_time = proper_times[earth_indices[frame_idx]]

		# One full rotation every 12 coordinate time units
		angle_static = (current_coordinate_time % (12 * step)) / (12 * step) * 2 * np.pi
		angle_ship = (current_proper_time % (12 * step)) / (12 * step) * 2 * np.pi

		clock_perspective_earth_hand.set_data(
			[clock_perspective_earth_x, clock_perspective_earth_x + 0.05 * np.cos(angle_static)],
			[clock_perspective_earth_y, clock_perspective_earth_y + 0.05 * np.sin(angle_static)]
		)
		clock_perspective_earth_hand.center = (clock_perspective_earth_x, clock_perspective_earth_y)

		clock_perspective_target_hand.set_data(
			[clock_perspective_target_x + target_distance_ly, clock_perspective_target_x + target_distance_ly + 0.05 * np.cos(angle_static)],
			[clock_perspective_earth_y, clock_perspective_earth_y + 0.05 * np.sin(angle_static)]
		)
		clock_perspective_target_circle.center = (clock_perspective_target_x + target_distance_ly, clock_perspective_earth_y)

		clock_ship_hand.set_data(
			[ship_pos, ship_pos + 0.05 * np.cos(angle_ship)],
			[clock_ship_y, clock_ship_y + 0.05 * np.sin(angle_ship)]
		)
		clock_ship_circle.center = (ship_pos, clock_ship_y)

		return ship_patch_earth, left_flame_earth, right_flame_earth, dist_text_earth, clock_ship_circle, clock_ship_hand, clock_ship_circle, clock_perspective_earth_hand, clock_perspective_target_circle, clock_perspective_target_hand

	anim_earth = animation.FuncAnimation(
		fig_earth, animate_earth, init_func=init_earth,
		frames=len(earth_indices), interval=interval, blit=True
	)

	# Optionally save animations
	if save_ship_path:
		anim_ship.save(f"output/{prefix}/"+prefix+"_"+save_ship_path, writer='ffmpeg', fps=fps)
	if save_earth_path:
		anim_earth.save(f"output/{prefix}/"+prefix+"_"+save_earth_path, writer='ffmpeg', fps=fps)

	return anim_ship, anim_earth