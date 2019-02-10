from copy import deepcopy, copy
from pampy import match, ANY


def yield_permuations(sub_items, path=None):
	"""
	For a list of lists
	Return the permutation of all combinations of items
	"""
	path = [] if path is None else path
	for item in sub_items[0]:
		sub_path = path + [item]
		if len(sub_items) > 1:
			yield from yield_permuations(sub_items[1:], sub_path)
		else:
			yield path + [item]


# The result is the product of the length each of the lists
assert 4 == len(list(yield_permuations([[1,2],[3,4]])))
assert 6 == len(list(yield_permuations([[1,2],[3,4,5]])))


def simulate(objects, system, history=None, stochastic=None):
	if history is None:
		history = [list() for x in range(len(objects))]
	else:
		# Shallow copy of the history, retaining the items
		# Duplicate the lists, but not the objects in the lists
		history = [copy(x) for x in history]

	for S, T in system:
		# Identify which items the transforms are run on
		# The selectors / filters are used to reduce the list of items
		sub_items = [list() for _ in range(len(S))]
		for i, s_i in enumerate(S):
			for o_i in objects:
				if match(o_i, s_i, True, default=False):
					sub_items[i].append(o_i)

		# Then iterate through the permutations of all combinations of objects
		for p in yield_permuations(sub_items):
			# When doing stochastic simulation, call a function to exclude this branch
			if stochastic and not stochastic():
				continue

			# Then iterate through all of the applicable transforms
			for T_i in T:
				matchers, transforms = T_i(*p)
				failed = False
				for i, m_i in enumerate(matchers):
					# All matchers for the rule must match, otherwise the combination is excluded
					if not match(p[i], m_i, True, default=False):
						failed = True
						break
				if failed:
					continue

				# Then need to apply the transforms to every object
				# And create a new state where all of the objects are replaced with the new ones
				replacement = list()
				for i, t_i in enumerate(transforms):
					o_i = deepcopy(p[i])
					replacement.append(t_i(o_i))

				# Create a new object list with the result of the state transform applied
				new_objects = copy(objects)
				for before, after in zip(p, replacement):
					i = objects.index(before)
					new_objects[ i ] = after
					# A new history is created for every single object on every state transform
					history[i].append(before)

				yield new_objects, history


def simulation(objects, system, history=None, stochastic=False):
	for new_objects, new_history in simulate(objects, system, history, stochastic):
		yield new_objects, new_history
		yield from simulation(new_objects, system, new_history, stochastic)

