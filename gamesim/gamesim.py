from dataclasses import dataclass
from copy import deepcopy, copy
from typing import List
from collections import OrderedDict
from pampy import match, ANY


class System(object):
    def __init__(self, *groups):
        self.groups = groups

    def __iter__(self):
        return iter(self.groups)

    def __len__(self):
        return len(self.groups)


class Rules(object):
    def __init__(self, *rules):
        self.rules = rules

    def __iter__(self):
        return iter(self.rules)

    def __len__(self):
        return len(self.rules)


class Selector(object):
    def __init__(self, *selectors):
        self.selectors = selectors

    def __iter__(self):
        return iter(self.selectors)

    def __len__(self):
        return len(self.selectors)


@dataclass
class Group:
    selector: Selector
    rules: Rules

    def __iter__(self):
        return iter((self.selector, self.rules))


@dataclass
class Rule:
    matchers: List
    actions: List


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


def simulate(objects, system, history, stochastic=None):
    if history is None:
        history = HistoryTracker()
    assert isinstance(history, HistoryTracker)

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
                    # TODO: replace with `(t_i(o_i) or o_i) if t_i else o_i` ?
                    if t_i:
                        # If a transform is specified, apply it
                        # If transform returns None, use the object
                        replacement.append(t_i(o_i) or o_i)
                    else:
                        replacement.append(o_i)

                # Create a new object list with the result of the state transform applied
                new_objects = copy(objects)
                new_history = deepcopy(history)

                for before, after in zip(p, replacement):
                    i = objects.index(before)
                    new_objects[ i ] = after

                cycle = new_history.track(new_objects)

                yield new_objects, new_history, cycle


class HistoryTracker(object):
    def __init__(self):
        self.history = list()

    def track(self, objects):
        try:
            i = self.history.index(objects)
        except ValueError:
            i = None

        # Object state has been found in history
        cycle = None
        if i is not None:
            cycle = self.history[:i][::-1]

        # Prepend objects to list, this keeps list in reverse order (FILO)
        self.history.insert(0, objects)

        return cycle


def simulation(objects, system, history=None, stochastic=False):
    for new_objects, new_history, cycle in simulate(objects, system, history, stochastic):
        yield new_objects, new_history

        if cycle:
            continue

        yield from simulation(new_objects, system, new_history, stochastic)

