import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

from elevator import ElevatorController

# Gigantic
# controller = ElevatorController(learning_rate=0.3, max_capacity=4, num_floors=10, epochs=1_000_000)
## Complex
# controller = ElevatorController(learning_rate=0.3, max_capacity=2, epochs=100_000)
## Simple
controller = ElevatorController(learning_rate=0.3, num_elevators=1, num_floors=3, max_capacity=2, epochs=10_000)

# controller.train()
# controller.save("gigantic_elevator.pkl")

# controller.load("gigantic_elevator.pkl")
# controller.load("models/complex_elevator.pkl")
controller.load("models/simple_elevator.pkl")

# Parameters
num_circles_per_row = 2  # Increased number of circles per row
num_rows = 2  # Increased number of rows
circle_radius = 1  # Smaller radius of the circles to allow them to fit closer together
square_height = 10#(circle_radius*5)*num_rows  # Size of the square (this remains the same)
square_width = (3*circle_radius+1)*np.ceil(controller.max_capacity//2)

# Grid layout for the circle centers (adjusted for closer spacing)
floor_lights = []
elevators = []

# Set up the plot
fig, ax = plt.subplots(dpi=300)
max_dim = np.max([(1+square_width)*controller.num_elevators, (square_height)*controller.num_floors + 1])
ax.set_xlim(-2*circle_radius, max_dim)
ax.set_ylim(-2, max_dim)

for _ in range(controller.num_elevators):
    x_positions = np.linspace(circle_radius * 2, square_width - circle_radius * 2, num_circles_per_row)
    y_positions = np.linspace(circle_radius * 2, square_height - circle_radius * 2, num_rows)


    # Create the grid of circle centers
    circle_centers = [(x, y) for x in x_positions for y in y_positions]

    # Create the square (this will be moving)
    square = plt.Rectangle((0, 0), square_width, square_height, linewidth=1, edgecolor='black', facecolor='none')
    ax.add_patch(square)

    # Create the circles (initially at grid positions inside the square)
    circles = []
    for center in circle_centers:
        circle = plt.Circle(center, circle_radius, edgecolor='black', facecolor='lightblue')
        ax.add_patch(circle)
        circles.append(circle)

    # Add numbers inside the circles
    texts = []
    for i, circle in enumerate(circles):
        text = ax.text(circle.center[0], circle.center[1], str(i + 1), color='black', ha='center', va='center')
        texts.append(text)

    elevators.append((square, circles, texts))

# for _ in range(controller.num_floors):
#     floor_centers = [(-circle_radius, y*square_height+square_height//2) for y in range(controller.num_floors)]

for y in range(controller.num_floors):
    center = (-circle_radius, y*square_height+square_height//2)
    circle = plt.Circle(center, circle_radius/2, edgecolor='black', facecolor='lightgrey')
    ax.add_patch(circle)
    floor_lights.append(circle)

# Show frame number + current reward
label = ax.text(0, -1, str(0), color='black', ha='left', va='center')
# Extend the controller to run longer
controller.goal_iters = 10000
sim = controller.run()

# Animation function to update the square and circles' positions
def update(frame):
    global elevators
    sim_state = next(sim)
    if sim_state == None:
        # Animation is done
        raise StopIteration

    updated = []


    # Update calls
    for i, light in enumerate(floor_lights):
        light.set_facecolor('yellow' if i in sim_state[0] else 'lightgrey')
        updated.append(light)

    label.set_text("frame: {0: <3} reward: {1: <4}".format(frame, controller.reward(sim_state)))
    updated.append(label)

    for i, (animation_e, state) in enumerate(zip(elevators, sim_state[1:])):
        square, circles, texts = animation_e
        pos, num_passangers, desired_floors, moving = state

        # Move the square up and down using a sine wave for smooth motion
        y_offset = square_height*pos
        x_offset = i * (square_width + 1)
        
        # Update the position of the square
        square.set_y(y_offset)
        square.set_x(x_offset)
        square.set_edgecolor('black' if moving else 'grey')
        square.set_facecolor('grey' if moving else 'white')
        updated.append(square)

        # Update the positions of the circles and the numbers inside
        for i, circle in enumerate(circles):
            # Update the Y position of the circle while keeping X fixed
            circle.set_center((circle_centers[i][0]+x_offset, circle_centers[i][1] + y_offset))  # Pass a tuple (X, Y)
            circle.set_visible(i < num_passangers)
            updated.append(circle)
            texts[i].set_position((circle_centers[i][0]+x_offset, circle_centers[i][1] + y_offset))  # Update the text position
            texts[i].set_visible(i < num_passangers)
            if i < num_passangers:
                texts[i].set_text(desired_floors[i])
            updated.append(texts[i])

    return updated
    # return circles + texts + [square]  # Return both the circles, text objects, and square to be updated

fig.tight_layout()
fig.patch.set_facecolor('white')
ax.set_axis_off()

# Create the animation
ani = FuncAnimation(fig, update, frames=range(100), interval=300, blit=True)

# # To save the animation using Pillow as a gif
writer = PillowWriter(fps=3,
    metadata=dict(artist='curtislowder.com'),
    bitrate=1800)
ani.save('elevator.gif', writer=writer)

# Show the plot with animation
# plt.show()
