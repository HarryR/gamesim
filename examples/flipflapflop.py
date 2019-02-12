from dataclasses import dataclass
from enum import Enum
from gamesim import System, Group, Selector, Rules, simulation
from pampy import ANY


class State(Enum):
    START = 0
    FLIP = 1
    FLOP = 2
    FLAP = 3

@dataclass
class Player:
    state: State = State.START

    def transform(self, new_state):
        self.state = new_state
        return self


def main():
	objects = [Player(), Player()]

	rules = System(
	    Group(
	        Selector(Player(ANY)),
	        Rules(
	            lambda x: ([Player(State.START)], [lambda o: o.transform(State.FLIP)]),
	            lambda x: ([Player(State.FLIP)], [lambda o: x.transform(State.FLAP)]),
	            lambda x: ([Player(State.FLAP)], [lambda o: x.transform(State.FLOP)]),
	            lambda x: ([Player(State.FLOP)], [lambda o: x.transform(State.FLIP)]),
	        )
	    ),
	    Group(
	        Selector(Player(ANY), Player(ANY)),
	        Rules(
	            lambda x, y: ([Player(State.FLIP), Player(State.FLIP)],
	                          [lambda o: x.transform(State.FLAP), lambda o: y.transform(State.FLOP)])
	        )
	    )
	)

	for objs, hist in simulation(objects, rules):
		print(objs)
		#print(hist)
		print()


if __name__ == "__main__":
	main()
