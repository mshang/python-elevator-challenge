UP = 1
DOWN = 2
FLOOR_COUNT = 6

class ElevatorLogic(object):
	"""
		https://github.com/mshang/python-elevator-challenge
	"""
	def __init__(self):
		self.destination_floor_cache = [0] * (FLOOR_COUNT + 1) # We are skipping 0 <3
		self.destination_floor_cache_cp = [0] * (FLOOR_COUNT + 1) # We are skipping 0 <3

		self.destination_direction_cache = None
		self.callbacks = None
		
	"""

	"""
	def elevator_set_direction_destination_floor(self, destination_floor):
		if destination_floor > self.callbacks.current_floor:
			self.destination_direction_cache = UP
		elif destination_floor < self.callbacks.current_floor:
			self.destination_direction_cache = DOWN

	"""
		This is called when somebody presses the up or down button to call the elevator.
		This could happen at any time, whether or not the elevator is moving.
		The elevator could be requested at any floor at any time, going in either direction.

		floor: the floor that the elevator is being called to
		direction: the direction the caller wants to go, up or down
	"""
	def on_called(self, floor, direction):
		if floor == self.callbacks.current_floor and self.callbacks.motor_direction == None:
				return # can not choose a floor if elevator has stopped 

		self.destination_floor_cache_cp[floor] |= direction

		if self.destination_direction_cache == None: # decide direction if elevator is idle
			self.elevator_set_direction_destination_floor(floor)

		"""
        This is called when somebody on the elevator chooses a floor.
        This could happen at any time, whether or not the elevator is moving.
        Any floor could be requested at any time.

        floor: the floor that was requested
        """

	def on_floor_selected(self, floor):
		if floor == self.callbacks.current_floor: # missed you chance to click....
			return

		if self.destination_direction_cache == UP:
			if floor > self.callbacks.current_floor:
				self.destination_floor_cache[floor] = 1
		elif self.destination_direction_cache == DOWN:
			if floor < self.callbacks.current_floor:
				self.destination_floor_cache[floor] = 1
		elif self.destination_direction_cache == None: # decide direction if elevator is idle
			self.destination_floor_cache[floor] = 1
			self.elevator_set_direction_destination_floor(floor)



		"""
        This lets you know that the elevator has moved one floor up or down.
        You should decide whether or not you want to stop the elevator.
        """
	def on_floor_changed(self):
		if self.destination_floor_cache[self.callbacks.current_floor] == 1: # (0, 1 bitmask) 1 -> floor choosen
			if self.destination_direction_cache == self.callbacks.motor_direction: # the current floor is in the same direction?
				self.destination_floor_cache[self.callbacks.current_floor] = 0
				self.callbacks.motor_direction = None
				#stop

		if self.destination_floor_cache_cp[self.callbacks.current_floor] == 0: #(UP, DOWN, UP | DOWN bitmask) no elevator UP, DOWN choosen
			return

		if self.destination_direction_cache & self.destination_floor_cache_cp[self.callbacks.current_floor] == self.destination_direction_cache: #same direction on call
			self.destination_floor_cache_cp[self.callbacks.current_floor] ^= self.destination_direction_cache
			self.callbacks.motor_direction = None
		elif self.destination_direction_cache & self.destination_floor_cache_cp[self.callbacks.current_floor] != self.destination_direction_cache: # opposite direction on call
			if self.get_next_destination_floor() == -1 \
			and self.get_next_destination_floor_cp(self.destination_direction_cache, (UP | DOWN), 1) == -1: #if no other floors were choosen/called, switch directions
					self.destination_direction_cache = self.destination_floor_cache_cp[self.callbacks.current_floor]
					self.destination_floor_cache_cp[self.callbacks.current_floor] = 0
					self.callbacks.motor_direction = None

			
		"""
        This is called when the elevator is ready to go.
        Maybe passengers have embarked and disembarked. The doors are closed,
        time to actually move, if necessary.
        """
	def on_ready(self):
		if self.destination_direction_cache == None and self.callbacks.motor_direction == None: #if elevator is idle - return
			return
		
		if self.get_next_destination_floor() == -1:
			if self.get_next_destination_floor_cp(self.destination_direction_cache, (UP | DOWN), 1) == -1:
				if self.get_next_destination_floor_cp(self.destination_direction_cache ^ (UP | DOWN), (UP | DOWN), 1) == -1:
					if self.destination_floor_cache_cp[self.callbacks.current_floor] > 0:
						if self.destination_floor_cache_cp[self.callbacks.current_floor] & self.destination_direction_cache == 0:
							self.destination_direction_cache = self.destination_floor_cache_cp[self.callbacks.current_floor]
							self.destination_floor_cache_cp[self.callbacks.current_floor] = 0
							self.callbacks.motor_direction = None
						else:
							self.destination_direction_cache = self.callbacks.motor_direction = None
					else:
						self.destination_direction_cache = self.callbacks.motor_direction = None
				else:
					self.destination_direction_cache = self.callbacks.motor_direction = self.destination_direction_cache ^ (UP | DOWN)
			else:
				self.callbacks.motor_direction = self.destination_direction_cache
		else:
			self.callbacks.motor_direction = self.destination_direction_cache
	

		"""
		Gets the next choosen floor in the elevator direction, if any.
		"""
	def get_next_destination_floor(self):
		if self.destination_direction_cache == UP:
			for next_cached_floor in range(self.callbacks.current_floor, (FLOOR_COUNT + 1)):
				if self.destination_floor_cache[next_cached_floor] == 1:
					return next_cached_floor
		elif self.destination_direction_cache == DOWN:
			for next_cached_floor in range((FLOOR_COUNT), 0, -1):
				if self.destination_floor_cache[next_cached_floor] == 1:
					return next_cached_floor
		return -1

		"""
		Gets the next called floor in the elevator direction with respect to (cp_direction), if any.
		"""
	def get_next_destination_floor_cp(self, elevator_direction, cp_direction, index):
		if elevator_direction == UP:
			for next_cached_floor in range(self.callbacks.current_floor + index, (FLOOR_COUNT + 1)):
				if self.destination_floor_cache_cp[next_cached_floor] == 0:
					continue
				if self.destination_floor_cache_cp[next_cached_floor] & cp_direction == self.destination_floor_cache_cp[next_cached_floor]:
					return next_cached_floor
		elif elevator_direction == DOWN:
			for next_cached_floor in range(self.callbacks.current_floor - index, 0, -1):
				if self.destination_floor_cache_cp[next_cached_floor] == 0:
					continue
				if self.destination_floor_cache_cp[next_cached_floor] & cp_direction == self.destination_floor_cache_cp[next_cached_floor]:
					return next_cached_floor
		return -1
