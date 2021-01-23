import os
import json
from loguru import logger



class State:

	'''class which's "tunel" between StateManager and 'state.json' file'''

	def __getattribute__(self, attr):

		if not MetaStateManager._check_if_attr_is_stored_data(attr):
			return super().__getattribute__(attr)

		return MetaStateManager._cache[attr]

	def __setattr__(self, attr, value):

		if not MetaStateManager._check_if_attr_is_stored_data(attr):
			return super().__setattr__(attr, value)

		cached_state = MetaStateManager._cache.get_cached_state().copy()
		cached_state[attr] = value

		MetaStateManager._put_state_into_json_file(cached_state)
		MetaStateManager._cache[attr] = value
		

	def __delattr__(self, attr):
		raise TypeError("you can't remove attributes")

class Cache:

	'''class which stores state data in RAM'''

	def __init__(self, state_dict):

		'''Get dictionary object and record it in own __dict__'''

		for key, value in state_dict.items():
			self.__dict__[key] = value

	def __setattr__(self, attr, value):

		'''Set attributes given in __init__'''

		if attr in self.__dict__:
			self.__dict__[attr] = value
		else:
			raise AttributeError(f"type object 'Cache' has no attribute '{attr}'")

	def __getitem__(self, item):
		return self.__dict__[item]

	def __setitem__(self, item, value):
		if item in self.__dict__:
			self.__dict__[item] = value
		else:
			raise KeyError(item)

	def get_cached_state(self):

		'''Return cached stored data dictionary'''

		return self.__dict__


class MetaStateManager(type):

	'''metaclass which serves user state manager class'''

	__state_manager = None
	_cache = None
	state = State()

	def __init__(self, *args, **kwargs):

		# checking wheather another user state manager exists
		if MetaStateManager.__state_manager == None: 
			
			# checking wheather StoredDataSchema class is defined in user state manager
			if 'StoredDataSchema' not in self.__dict__: 
				raise TypeError(f"'StoredDataSchema' class isn't defined in '{self.__class__.__name__}' class")

			# checking wheather StoredDataSchema class is instance of MetaStoredDataSchema
			if type(self.StoredDataSchema) == MetaStoredDataSchema:
				MetaStateManager.__state_manager = self
			else:
				raise TypeError("'StoredDataSchema' class must be an instance of 'MetaStoredDataSchema'")
		else:
			raise TypeError("Another instance of 'MetaStateManager' exists")

		self.__init__ = MetaStateManager.__state_manager_init
		self.state = MetaStateManager.state # to make 'state' instance attribute

		# checking wheather 'state.json' exists
		if not os.path.exists('state.json'):
			MetaStateManager._set_default_state()
		else:
			with open('state.json', 'r') as file:
				data = file.read()

			if data == "":
				MetaStateManager._set_default_state()

		MetaStateManager._cache = Cache(MetaStateManager._get_state_from_json_file())


	def __state_manager_init(self, *args, **kwargs):

		'''__init__ method for user state manager class'''
		
		raise TypeError(f"'{self.__class__.__name__}' can't have any instances")

	@classmethod
	def _put_state_into_json_file(cls, state_dict):
		
		'''Get dictionary object as an arguement and put it into 'state.json' file'''
		
		with open('state.json', 'w') as file:
			try:
				file.write(str(json.dumps(state_dict, sort_keys=True, indent=4)))
			except BaseException as e:
				cls._put_state_into_json_file(cls._cache.get_cached_state())
				raise e

	@classmethod
	def _get_state_from_json_file(cls):

		'''Get state from 'state.json' file and return dictionary object of it'''


		with open('state.json', 'r') as file:
			try:
				state_dict = json.load(file)
			except BaseException as e:
				cls._put_state_into_json_file(cls._cache.get_cached_state())
				raise e
		
		return state_dict

	@classmethod
	def _set_default_state(cls):

		'''Set default state based in 'StoredDataSchema' class'''

		state_dict = {}

		for attr in cls._get_stored_data_schema().__dict__:
			if cls._check_if_attr_is_stored_data(attr):
				state_dict[attr] = cls._get_stored_data_schema().__dict__[attr]

		cls._put_state_into_json_file(state_dict)

	@classmethod
	def _check_if_attr_is_stored_data(cls, attr):

		'''Check if the attribute is stored data'''

		key_error_raised = False

		try:
			if type(cls._get_stored_data_schema().__dict__[attr]).__name__ not in ('function', 'method') \
					and not attr.startswith('__'):

				return True
		except KeyError:
			key_error_raised = True
		
		if key_error_raised:
			raise AttributeError(f"type object 'StoredDataSchema' has no attribute '{attr}'")

		return False

	@classmethod
	def _get_stored_data_schema(cls):

		'''Return 'StoredDataSchema' class of user state manager class'''

		return cls.__state_manager.StoredDataSchema


	
class MetaStoredDataSchema(type):

	'''metaclass for 'StoredDataSchema' class'''

	def __setattr__(self, attr, value):
		raise TypeError

	def __delattr__(self, attr):
		raise TypeError
