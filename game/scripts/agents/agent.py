import fife
from scripts.common.common import ProgrammingError

class ActionStack (object):
	""" 
    Class, which implements queueing of various user actions.
    Each entry in the ActoinStack is a 6-item tuple consisting of
    (action_func, action_func_args, action_func_kw_args,
    (success_func, success_func_args, success_func_kw_args). 

    Items are processed from index 0 upwards. New actions
    are appended to the list. Successful actions are popped from the
    bottom of the list. If the success function of the current
    action returns True, the current action is popped out, and the
    next action is processed.

    IMPORTANT: To avoid the danger of endlessly pushing actions to the 
    stack, it is automatically cleared when an action is added while 
    the stack is in a running state.

    Example:
    To define something like "Kick him while he's down", you coud do:
    .add_action (kick, (him,), isDown, (him,))

    """
	def __init__ (self):
		
		# This is the actual list that stores the entries
		self.action_list = []
		# A flag to track if the stack was ran after the last item was added
		self.running = False

	def add_kw_args_action (self, 
			action_func, action_args = (), action_kw_args = {},
			success_func = None, success_args = (),success_kw_args = {}):
		"""
		Appends an action entry to the action_list. Supports both args and 
		kwargs. If a previous batch of actions was inserted, and then ran, 
		this will first empty the stack before adding the new entry.
		"""
		# Basic checks to see if the action and success funcitons are callable 
		if not callable (action_func):
			raise ValueError ("%s is not callable!" % action_func)
		if success_func and not callable(success_func):
			raise ValueError ("%s is not callable!" % success_func)
		if self.running:
			# We have a running queue; clean it up before adding anything new
			self.clear()
			self.running = False

		self.action_list.append ( (action_func, action_args, action_kw_args, 
					   success_func, success_args, success_kw_args))

	def add_action (self, action_func, action_args = (),
			success_func = None, success_args = ()):
		"""
		Appends an action entry to the action_list. Shortcut to 
		add_kw_args_action() without kwargs. Only supports positinal arguments 
		for the action_func/success_func
		"""
		self.add_kw_args_action (action_func, action_args, {}, 
					success_func, success_args , {})

	def remove_current_action (self):
		"""Removes an action from the bottom of the list"""
		if self.action_list:
			self.action_list.pop(0)

	def clear (self):
		"""Removes all actions from the stack"""
		self.action_list = []
	
	def perform_action (self, action_item):
		"""Runs the provided action_item. It is a tuple following the same
		format as the items in self.action_list """
		a_func, a_args, a_kw_args = action_item[:3]
		a_func (*a_args, **a_kw_args)
		return True

	def run (self):
		"""
		Runs an action from the queue.

		If there is no success function, just executes the current action 
		and removes it from the queue. If the success function evaluates
		to True, removes the current action and proceeds with the next one. 
		If the success function evaluates to False, only performs 
		the current action.
		
		Returns True if some action was executed, False otherwise.
		"""

		if not self.action_list:
			return False
		# We set the running flag
		self.running = True
		
		# Loop that will go over the aciton_list and exit after performing an 
		# action. Note that the loop iterates over a copy of the action_list
		for action in self.action_list[:]:
			# Load the current entry success function details
			s_func, s_args, s_kw_args = self.action_list[0][3:6]

			if (not s_func):
				# No success function defined - meaning that the 
				# action will be popped form the queue and executed once.
				return self.perform_action(self.action_list.pop(0))
			elif not s_func (*s_args, **s_kw_args):
				# The current success conditions evaluated to False, keep 
				# performing the current action
				return self.perform_action(self.action_list[0])
			else:
				# The success condition is true - meaning that the current action is
				# popped out, and we proceed to the next item in the list
				self.action_list.pop(0)
		
		# We went through the entire action_list but no action was performed
		return False

class Agent(fife.InstanceActionListener):
	def __init__(self, model, agentName, layer, uniqInMap=True):
		fife.InstanceActionListener.__init__(self)
		self.model = model
		self.agentName = agentName
		self.layer = layer
		self.action_stack = ActionStack()
		if uniqInMap:
			self.agent = layer.getInstance(agentName)
			self.agent.addActionListener(self)

	def onInstanceActionFinished(self, instance, action):
		raise ProgrammingError('No OnActionFinished defined for Agent')

	def start(self):
		raise ProgrammingError('No start defined for Agent')
	
	def kickButtonHandler (self):
		"""Placeholder function to enable kick menu display for all children"""
		pass
	def talkButtonHandler (self):
		"""Placeholder function to enable talk menu display for all children"""
		pass

def create_anonymous_agents(model, objectName, layer, agentClass):
	agents = []
	instances = [a for a in layer.getInstances() if a.getObject().getId() == objectName]
	i = 0
	for a in instances:
		agentName = '%s:i:%d' % (objectName, i)
		i += 1
		agent = agentClass(model, agentName, layer, False)
		agent.agent = a
		a.addActionListener(agent)
		agents.append(agent)
	return agents
