class Peeker:
	def __init__(self, stream):
		self.__current = None
		self.__stream = stream

	def peek(self):
		if self.__current is None:
			self.__current = next(self.__stream)

		return self.__current

	def __next__(self):
		current = self.peek()
		self.__current = None

		return current

	def __iter__(self):
		return self
