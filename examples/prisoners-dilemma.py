from enum import Enum
from dataclasses import dataclass
from gamesim import simulation

class Judgement(Enum):
	WAITING_EITHER = 0
	WAITING_ALICE = 1
	WAITING_BOB = 2
	FINISHED = 3


class Sentence(Enum):
	UNDECIDED = 0
	FREE = 1
	ONE_YEAR = 2
	TWO_YEARS = 3
	THREE_YEARS = 4


class Choice(Enum):
	START = 0
	COOPERATE = 1
	DEFECT = 2


@dataclass
class Judge:
	state: Judgement = Judgement.WAITING_EITHER
	choice_alice: Choice = Choice.START
	choice_bob: Choice = Choice.START
	sentence_alice: Sentence = Sentence.UNDECIDED
	sentence_bob: Sentence = Sentence.UNDECIDED

	def transform(self, actor, choice):
		# Remember Alice and Bob's choices
		if actor.name == Name.ALICE:
			self.choice_alice = choice
		elif actor.name == Name.BOB:
			self.choice_bob = choice

		# Internal state transitions
		if self.state == Judgement.WAITING_EITHER:
			self.state = Judgement.WAITING_BOB if actor.name == Name.ALICE else Judgement.WAITING_ALICE			
		elif self.state == Judgement.WAITING_ALICE and actor.name == Name.ALICE:
			self.state = Judgement.FINISHED
		elif self.state == Judgement.WAITING_BOB and actor.name == Name.BOB:
			self.state = Judgement.FINISHED

		# Determine end-game sentences for both Alice and Bob
		if self.state == Judgement.FINISHED:
			if self.choice_alice == self.choice_bob:
				if self.choice_alice == Choice.COOPERATE:
					self.sentence_alice = Sentence.ONE_YEAR
					self.sentence_bob = Sentence.ONE_YEAR
				elif self.choice_alice == Choice.DEFECT:
					self.sentence_alice = Sentence.TWO_YEARS
					self.sentence_bob = Sentence.TWO_YEARS
			elif self.choice_alice == Choice.COOPERATE:
				self.sentence_alice = Sentence.THREE_YEARS
				self.sentence_bob = Sentence.FREE
			elif self.choice_bob == Choice.COOPERATE:
				self.sentence_alice = Sentence.FREE
				self.sentence_bob = Sentence.THREE_YEARS

		return self


class State(Enum):
	START = 0
	CHOSEN = 1


class Name(Enum):
	ALICE = 0
	BOB = 1


@dataclass
class Prisoner:
	name: Name
	state: State = State.START
	choice: Choice = Choice.START

	def transform(self, choice):
		self.state = State.CHOSEN
		self.choice = choice
		return self


def main():
	objects = [
		Prisoner(Name.ALICE),
		Prisoner(Name.BOB),
		Judge()
	]

	# TODO: add exclusions to remove pairs which shouldn't be worked on
	# e.g. to exclude where `from` and `to` are identical
	system = [
		[[Prisoner(ANY, ANY, ANY), Judge(ANY, ANY, ANY, ANY)], [
			lambda a, b: ((Prisoner(ANY),
						   Judge(Judgement.WAITING_EITHER, ANY, ANY, ANY, ANY)),
						  (lambda x: x.transform(Choice.COOPERATE), lambda x: x.transform(a, Choice.COOPERATE))),

			lambda a, b: ((Prisoner(Name.ALICE),
						   Judge(Judgement.WAITING_ALICE, ANY, ANY, ANY, ANY)),
						  (lambda x: x.transform(Choice.COOPERATE), lambda x: x.transform(a, Choice.COOPERATE))),

			lambda a, b: ((Prisoner(Name.BOB),
			  			   Judge(Judgement.WAITING_BOB, ANY, ANY, ANY, ANY)),
			 			  (lambda x: x.transform(Choice.COOPERATE), lambda x: x.transform(a, Choice.COOPERATE))),

			lambda a, b: ((Prisoner(ANY),
			  			   Judge(Judgement.WAITING_EITHER, ANY, ANY, ANY, ANY)),
			 			  (lambda x: x.transform(Choice.DEFECT), lambda x: x.transform(a, Choice.DEFECT))),

			lambda a, b: ((Prisoner(Name.ALICE),
			  			   Judge(Judgement.WAITING_ALICE, ANY, ANY, ANY, ANY)),
			 			  (lambda x: x.transform(Choice.DEFECT), lambda x: x.transform(a, Choice.DEFECT))),

			lambda a, b: ((Prisoner(Name.BOB),
			  			   Judge(Judgement.WAITING_BOB, ANY, ANY, ANY, ANY)),
			 			  (lambda x: x.transform(Choice.DEFECT), lambda x: x.transform(a, Choice.DEFECT)))
		]]
	]

	for objs, hist in simulation(objects, system, all_orderings=True):
		print(objs)
		print(hist)
		print()

	#for history, new_objects in simulate(objects, system):
	#	print(history, new_objects)


if __name__ == "__main__":
	main()
