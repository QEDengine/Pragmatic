


class Registry:
	args = { }

	def argument(func):
		Registry.args[func.__name__] = func
		return func

	argument = staticmethod(argument)