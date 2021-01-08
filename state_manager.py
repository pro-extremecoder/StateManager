import os
import json



class State:
	num1 = 0 
	num2 = 0
		
	
	def __getattribute__(self, attr):
		
		if attr not in State.__dict__:
			raise AttributeError

		if not StateManager._check_if_attr_is_stored_data(attr):

			return super().__getattribute__(attr)

		state_dict = StateManager._get_state_from_json_file()

		return state_dict[attr]

	def __setattr__(self, attr, value):

		if attr not in State.__dict__:
			raise AttributeError

		if not StateManager._check_if_attr_is_stored_data(attr):
			return super().__setattr__(attr, value)

		state_dict = StateManager._get_state_from_json_file()

		state_dict[attr] = value

		StateManager._put_state_into_json_file(state_dict)

	def __delattr__(self, attr):
		raise TypeError

	
class Actions:

	def calculate(self):		
		print(StateManager.state.__dict__)
		StateManager.state.__dict__['a'] = 1
		#del StateManager.state.num1
		StateManager.mutations.inc_num1()
		StateManager.mutations.inc_num2()
		result = StateManager.state.num1 + StateManager.state.num2
		return result


class Mutations:

	def inc_num1(self):
		StateManager.state.num1 += 1

	def inc_num2(self):
		StateManager.state.num2 += 1



class MetaStateManager(type):

	def __init__(self, *args, **kwargs):

		if not os.path.exists('state.json'):
			MetaStateManager._set_default_state()
		else:
			with open('state.json', 'r') as file:
				data = file.read()

			if data == "":
				MetaStateManager._set_default_state()

	@staticmethod
	def _put_state_into_json_file(state_dict):
		
		with open('state.json', 'w') as file:
			file.write(str(json.dumps(state_dict, sort_keys=True, indent=4)))

	@staticmethod
	def _set_default_state():
		state_dict = {}

		for attr in State.__dict__:
			if MetaStateManager._check_if_attr_is_stored_data(attr):
				state_dict[attr] = State.__dict__[attr]

		MetaStateManager._put_state_into_json_file(state_dict)

	@classmethod
	def _check_if_attr_is_stored_data(cls, attr):
		
		if type(State.__dict__[attr]).__name__ not in ('function', 'method', 'classmethod') and not attr.startswith('__'):

			return True

		return False

	@staticmethod
	def _get_state_from_json_file():
		
		with open('state.json', 'r') as file:
			state_dict = json.load(file)

		return state_dict

class StateManager(metaclass=MetaStateManager):


	state = State()
	actions = Actions()
	mutations = Mutations()

	def __init__(self, *args, **kwargs):
		raise TypeError

	

	

	


if __name__ == "__main__":
	#print(StateManager)
	for i in range(5):
		print(StateManager.actions.calculate())

	#state_manager = StateManager()
	#print(StateManager._get_state_from_json_file())


	#StateManager._set_default_state()

