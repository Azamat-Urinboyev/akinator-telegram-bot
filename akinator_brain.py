from akinator import Akinator


class MyAkinator(Akinator):
	def __init__(self, language):
		self.aki = self
		self.question = self.start_game(language, child_mode=True)

	def answer_question(self, an: str):
		self.aki.answer(an)
		
