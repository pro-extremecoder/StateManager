import os
import json
from loguru import logger



class State:

	'''class which's "tunel" between StateManager and 'state.json' file'''

	def __getattribute__(self, attr):

		if attr not in MetaStateManager._default_stored_data:
			if attr in State.__dict__:
				return super().__getattribute__(attr)
			else:
				raise AttributeError(f"type object 'StoredDataSchema' has no attribute '{attr}'")

		return MetaStateManager._cache[attr]

	def __setattr__(self, attr, value):

		if attr not in MetaStateManager._default_stored_data:
			if attr in State.__dict__:
				return super().__setattr__(attr, value)
			else:
				raise AttributeError(f"type object 'StoredDataSchema' has no attribute '{attr}'")

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

	def __delattr__(self, attr):
		raise TypeError("type object 'Cache' can't remove attributes")

	def __delitem__(self, item):
		raise TypeError("type object 'Cache' can't remove dictionary items")

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
	_default_stored_data = None
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

		MetaStateManager._default_stored_data = MetaStateManager._get_stored_data_schema()._get_default_stored_data()

		# checking wheather 'state.json' exists
		if not os.path.exists('state.json'):
			MetaStateManager._set_default_state()
		else:
			with open('state.json', 'r') as file:
				data = file.read()

			if data == "":
				MetaStateManager._set_default_state()
			elif not MetaStateManager._json_file_structure_is_correct():
				raise TypeError("'state.json' data structure doesn't correspond to 'StoredDataSchema'")

		MetaStateManager._cache = Cache(MetaStateManager._get_state_from_json_file())

	@classmethod
	def _json_file_structure_is_correct(cls):

		'''Checking wheather 'state.json' file structure is correct'''
		
		state_from_json = cls._get_state_from_json_file()

		default_state = cls._get_stored_data_schema()._get_default_stored_data()

		if set(default_state.keys()) == set(state_from_json):
			return True

		return False




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

		cls._put_state_into_json_file(cls._default_stored_data)

	@classmethod
	def _get_stored_data_schema(cls):

		'''Return 'StoredDataSchema' class of user state manager class'''

		return cls.__state_manager.StoredDataSchema


	
class MetaStoredDataSchema(type):

	'''metaclass for 'StoredDataSchema' class'''

	def __init__(self, *args, **kwargs):

		default_stored_data = self._get_default_stored_data()

		for attr, value in self.__dict__.items():
			if not attr.startswith('__') and attr not in default_stored_data:
				attr_type = type(value).__name__
				raise TypeError(f"type object 'StoredDataSchema' can't have a '{attr_type}' type attribute")

	def _get_default_stored_data(self):

		'''Return default stored data schema as dictionary'''
		
		default_stored_data = {}
		unallowed_types = ('function', 'classmethod', 'staticmethod')
		
		for attr, value in self.__dict__.items():
			
			attr_type = type(self.__dict__[attr]).__name__
			
			if attr_type not in unallowed_types and not attr.startswith('__'):  
				default_stored_data[attr] = value

		return default_stored_data

	def __setattr__(self, attr, value):
		raise TypeError("type object 'StoredDataSchema' can't set attributes")

	def __delattr__(self, attr):
		raise TypeError("type object 'StoredDataSchema' can't remove attributes")
