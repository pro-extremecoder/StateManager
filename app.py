from state_manager import MetaStateManager, State, MetaStoredDataSchema


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

class StateManager(metaclass=MetaStateManager):
	
	actions = Actions()
	mutations = Mutations()

	class StoredDataSchema(metaclass=MetaStoredDataSchema):
		num1 = 0
		num2 = 0


#print(ApplicationStateManager)
for i in range(5):
	print(StateManager.actions.calculate())

#state_manager = StateManager()
#StateManager.state.a = 1
print(StateManager._get_state_from_json_file())
#StateManager._put_state_into_json_file({})
#print(StateManager.state.a)

#StateManager._set_default_state()

