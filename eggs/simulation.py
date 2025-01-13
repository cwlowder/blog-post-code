import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

def percent_formatter(x, _):
	return f"{x * 100:.2f}%"

def strategy_pull_num_eggs(carton, num):
	eggs = random.sample(carton, min(num, len(carton)))

	# Broken eggs have a value of 1, good eggs are 0
	return any([egg > 0 for egg in eggs])

def gen_carton_independent(eggs_per_carton=12, chance_broken_egg=0.01):
	return [1 if (random.random() < chance_broken_egg) else 0 for _ in range(eggs_per_carton)]

def gen_carton_dependent(eggs_per_carton=12, chance_broken_egg=0.01, collateral_prob=0.5, num_rounds=3):
	# One broken egg, means we will likely have more broken eggs
	eggs = [1 if (random.random() < chance_broken_egg) else 0 for _ in range(eggs_per_carton)]
	new_eggs = eggs[:]
	# For each round of running:
	for _ in range(num_rounds):
		for i in range(len(eggs)):
			if eggs[i] == 1:  # Check for a `1`
				# Check left neighbor
				if i > 0 and eggs[i - 1] == 0:
					if random.random() < collateral_prob:
						new_eggs[i - 1] = 1
				# Check right neighbor
				if i < len(eggs) - 1 and eggs[i + 1] == 0:
					if random.random() < collateral_prob:
						new_eggs[i + 1] = 1
		eggs = new_eggs
	return eggs

def exec_experiment(epochs=10_000, num_eggs_to_pull=3, gen_method=gen_carton_independent):
	num_found = 0
	num_with_broken = 0
	for _ in range(epochs):
		# 1 for broken eggs
		# 0 for good eggs
		eggs = gen_method()
		has_broken_egg = any([egg > 0 for egg in eggs])
		if has_broken_egg:
			num_with_broken += 1

		found_broken_egg = strategy_pull_num_eggs(eggs, num_eggs_to_pull)
		if found_broken_egg:
			num_found += 1
	return epochs, num_with_broken, num_found

# Test how chance of broken egg changes accuracy
def run_break_chance(gen_method, file_interfix=""):
	x_axis = np.linspace(0, 0.5, 50)
	rejection = {}
	recall = {}

	for num_eggs_to_pull in [1,3,6,9]:
		rejection[num_eggs_to_pull] = []
		recall[num_eggs_to_pull] = []
		for chance_broken_egg in x_axis:
			method = lambda: gen_method(chance_broken_egg=chance_broken_egg)
			total_epochs, num_with_broken, num_found = exec_experiment(num_eggs_to_pull=num_eggs_to_pull, gen_method=method)
			rejection[num_eggs_to_pull].append(num_found/total_epochs)
			recall[num_eggs_to_pull].append((num_found/num_with_broken) if num_with_broken > 0 else None)

	fig, ax = plt.subplots(1, 2, figsize=(10, 4))  # 1 row, 2 columns
	fig.suptitle(f"{file_interfix} egg breakage")

	# Plot on the first subplot
	for num_eggs_to_pull, data in rejection.items():
		ax[0].plot(x_axis, data, label=f"Pull {num_eggs_to_pull} eggs")
	ax[0].set_title("Rejection Chance")
	ax[0].set_xlabel("Break Chance")
	ax[0].set_ylabel("% Rejected")
	ax[0].yaxis.set_major_formatter(FuncFormatter(percent_formatter))
	ax[0].legend()
	ax[0].grid()

	# Plot on the second subplot
	for num_eggs_to_pull, data in recall.items():
		ax[1].plot(x_axis, data, label=f"Pull {num_eggs_to_pull} egg")
	ax[1].set_title("Percent of broken eggs found")
	ax[1].set_xlabel("Break Chance")
	ax[1].set_ylabel("% Found")
	ax[1].yaxis.set_major_formatter(FuncFormatter(percent_formatter))
	ax[1].legend()
	ax[1].grid()

	# Adjust layout and show the plot
	plt.tight_layout()
	plt.savefig(f"figs/chance_egg_breaks_{file_interfix}.png")

# Test how size of carton changes things
def run_carton_size(gen_method, file_interfix=""):
	x_axis = [6, 12, 24, 48, 100]
	rejection = {}
	recall = {}

	for num_eggs_to_pull in [1,3,6,9]:
		rejection[num_eggs_to_pull] = []
		recall[num_eggs_to_pull] = []
		for eggs_per_carton in x_axis:
			method = lambda: gen_method(eggs_per_carton=eggs_per_carton)
			total_epochs, num_with_broken, num_found = exec_experiment(gen_method=method, num_eggs_to_pull=num_eggs_to_pull)
			rejection[num_eggs_to_pull].append(num_found/total_epochs)
			recall[num_eggs_to_pull].append((num_found/num_with_broken) if num_with_broken > 0 else None)

	fig, ax = plt.subplots(1, 2, figsize=(10, 4))  # 1 row, 2 columns
	fig.suptitle(f"{file_interfix} egg breakage")

	# Plot on the first subplot
	for num_eggs_to_pull, data in rejection.items():
		ax[0].plot(x_axis, data, label=f"Pull {num_eggs_to_pull} eggs")
	ax[0].set_title("Rejection Chance")
	ax[0].set_xlabel("Carton Size")
	ax[0].set_ylabel("% Rejected")
	ax[0].yaxis.set_major_formatter(FuncFormatter(percent_formatter))
	ax[0].set_xticks(x_axis)
	ax[0].legend()
	ax[0].grid()

	# Plot on the second subplot
	for num_eggs_to_pull, data in recall.items():
		ax[1].plot(x_axis, data, label=f"Pull {num_eggs_to_pull} egg")
	ax[1].set_title("Percent of broken eggs found")
	ax[1].set_xlabel("Carton Size")
	ax[1].set_ylabel("% Found")
	ax[1].set_xticks(x_axis)
	ax[1].yaxis.set_major_formatter(FuncFormatter(percent_formatter))
	ax[1].legend()
	ax[1].grid()

	# Adjust layout and show the plot
	plt.tight_layout()
	plt.savefig(f"figs/carton_size_{file_interfix}.png")


if __name__ == '__main__':
	run_break_chance(gen_method=gen_carton_independent, file_interfix="independent")

	run_carton_size(gen_method=gen_carton_independent, file_interfix="independent")

	run_break_chance(gen_method=gen_carton_dependent, file_interfix="dependent")

	run_carton_size(gen_method=gen_carton_dependent, file_interfix="dependent")
	

