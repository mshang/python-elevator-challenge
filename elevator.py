UP = 1
DOWN = 2
FLOOR_COUNT = 6

class ElevatorLogic(object):
    """
    An incorrect implementation. Can you make it pass all the tests?

    Fix the methods below to implement the correct logic for elevators.
    The tests are integrated into `README.md`. To run the tests:
    $ python -m doctest -v README.md

    To learn when each method is called, read its docstring.
    To interact with the world, you can get the current floor from the
    `current_floor` property of the `callbacks` object, and you can move the
    elevator by setting the `motor_direction` property. See below for how this is done.
    """

    def __init__(self):
        # Track floor selections (people inside elevator selecting floors)
        self.floor_selections = set()

        # Track calls from outside (people calling elevator with direction)
        # Using lists to preserve order for FIFO behavior when choosing direction
        self.up_calls = []
        self.down_calls = []

        # Track the order of all calls for FIFO resolution
        self.call_order = {}  # floor -> order number
        self.call_counter = 0

        # Track the committed direction (None means idle)
        self.committed_direction = None

        self.callbacks = None

    def on_called(self, floor, direction):
        """
        This is called when somebody presses the up or down button to call the elevator.
        This could happen at any time, whether or not the elevator is moving.
        The elevator could be requested at any floor at any time, going in either direction.

        floor: the floor that the elevator is being called to
        direction: the direction the caller wants to go, up or down
        """
        # Track the order of this call
        if floor not in self.call_order:
            self.call_order[floor] = self.call_counter
            self.call_counter += 1

        if direction == UP:
            if floor not in self.up_calls:
                self.up_calls.append(floor)
        else:
            if floor not in self.down_calls:
                self.down_calls.append(floor)

    def on_floor_selected(self, floor):
        """
        This is called when somebody on the elevator chooses a floor.
        This could happen at any time, whether or not the elevator is moving.
        Any floor could be requested at any time.

        floor: the floor that was requested
        """
        # Ignore selections that contradict the committed direction
        current_floor = self.callbacks.current_floor

        if self.committed_direction == UP:
            # Only accept floors above current floor when going up
            if floor > current_floor:
                self.floor_selections.add(floor)
        elif self.committed_direction == DOWN:
            # Only accept floors below current floor when going down
            if floor < current_floor:
                self.floor_selections.add(floor)
        else:
            # Idle - first floor selection sets the direction
            if floor != current_floor:
                self.floor_selections.add(floor)
                # Establish committed direction based on first selection
                if floor > current_floor:
                    self.committed_direction = UP
                elif floor < current_floor:
                    self.committed_direction = DOWN

    def on_floor_changed(self):
        """
        This lets you know that the elevator has moved one floor up or down.
        You should decide whether or not you want to stop the elevator.
        """
        current_floor = self.callbacks.current_floor
        should_stop = False

        # Check if we should stop at this floor
        if self.committed_direction == UP:
            # Stop if there's a floor selection, an up call,
            # OR a down call with no requests above (this is the top of our journey)
            if (current_floor in self.floor_selections or current_floor in self.up_calls or
                (current_floor in self.down_calls and not self._has_requests_above(current_floor))):
                should_stop = True
        elif self.committed_direction == DOWN:
            # Stop if there's a floor selection, a down call,
            # OR an up call with no requests below (this is the bottom of our journey)
            if (current_floor in self.floor_selections or current_floor in self.down_calls or
                (current_floor in self.up_calls and not self._has_requests_below(current_floor))):
                should_stop = True

        if should_stop:
            self.callbacks.motor_direction = None
            # Clear this floor from floor selections and the appropriate call
            self.floor_selections.discard(current_floor)

            # Clear the call for the current direction if we stopped for it
            # Track whether we cleared a call to determine if we should switch direction
            cleared_current_direction_call = False
            if self.committed_direction == UP:
                if current_floor in self.up_calls:
                    self.up_calls.remove(current_floor)
                    cleared_current_direction_call = True
                    if current_floor not in self.down_calls:
                        self.call_order.pop(current_floor, None)
            elif self.committed_direction == DOWN:
                if current_floor in self.down_calls:
                    self.down_calls.remove(current_floor)
                    cleared_current_direction_call = True
                    if current_floor not in self.up_calls:
                        self.call_order.pop(current_floor, None)

            # Switch direction if at end of travel AND there's an opposite direction call here
            # But ONLY if we didn't just clear a call in the current direction
            # (to handle the "wait for each direction" case)
            if not cleared_current_direction_call:
                if self.committed_direction == UP:
                    if (current_floor in self.down_calls and
                        not self._has_requests_above(current_floor)):
                        self.committed_direction = DOWN
                elif self.committed_direction == DOWN:
                    if (current_floor in self.up_calls and
                        not self._has_requests_below(current_floor)):
                        self.committed_direction = UP

    def on_ready(self):
        """
        This is called when the elevator is ready to go.
        Maybe passengers have embarked and disembarked. The doors are closed,
        time to actually move, if necessary.
        """
        current_floor = self.callbacks.current_floor

        # Clear any call at current floor for the current committed direction
        if self.committed_direction == UP:
            if current_floor in self.up_calls:
                self.up_calls.remove(current_floor)
                if current_floor not in self.down_calls:
                    self.call_order.pop(current_floor, None)
        elif self.committed_direction == DOWN:
            if current_floor in self.down_calls:
                self.down_calls.remove(current_floor)
                if current_floor not in self.up_calls:
                    self.call_order.pop(current_floor, None)

        # Check if there are requests in the current direction
        if self.committed_direction == UP:
            if self._has_requests_above(current_floor):
                # Continue going up
                self.callbacks.motor_direction = UP
                return
        elif self.committed_direction == DOWN:
            if self._has_requests_below(current_floor):
                # Continue going down
                self.callbacks.motor_direction = DOWN
                return

        # No more requests in current direction, try to switch direction
        if self.committed_direction == UP:
            # Check if there's a down call at current floor
            if current_floor in self.down_calls:
                # Switch to down direction and wait
                self.committed_direction = DOWN
                self.callbacks.motor_direction = None
                return
            # Check if there are any requests below
            if self._has_requests_below(current_floor):
                self.committed_direction = DOWN
                self.callbacks.motor_direction = DOWN
                return
        elif self.committed_direction == DOWN:
            # Check if there's an up call at current floor
            if current_floor in self.up_calls:
                # Switch to up direction and wait
                self.committed_direction = UP
                self.callbacks.motor_direction = None
                return
            # Check if there are any requests above
            if self._has_requests_above(current_floor):
                self.committed_direction = UP
                self.callbacks.motor_direction = UP
                return

        # No committed direction or no requests in any direction from committed state
        # When idle, check which direction to go based on first call
        # Get the first call above or below
        first_call_above = self._get_first_call_above(current_floor)
        first_call_below = self._get_first_call_below(current_floor)

        if first_call_above is not None and first_call_below is not None:
            # Have calls in both directions, go to whichever was called first
            # Check which appears first in the combined list
            if self._get_call_index(first_call_above) < self._get_call_index(first_call_below):
                self.committed_direction = UP
                self.callbacks.motor_direction = UP
            else:
                self.committed_direction = DOWN
                self.callbacks.motor_direction = DOWN
        elif first_call_above is not None:
            self.committed_direction = UP
            self.callbacks.motor_direction = UP
        elif first_call_below is not None:
            self.committed_direction = DOWN
            self.callbacks.motor_direction = DOWN
        elif self._has_requests_above(current_floor):
            # Only floor selections above
            self.committed_direction = UP
            self.callbacks.motor_direction = UP
        elif self._has_requests_below(current_floor):
            # Only floor selections below
            self.committed_direction = DOWN
            self.callbacks.motor_direction = DOWN
        else:
            # No requests at all, become idle
            self.committed_direction = None
            self.callbacks.motor_direction = None

    def _has_requests_above(self, floor):
        """Check if there are any requests above the given floor"""
        for f in self.floor_selections:
            if f > floor:
                return True
        for f in self.up_calls:
            if f > floor:
                return True
        for f in self.down_calls:
            if f > floor:
                return True
        return False

    def _has_requests_below(self, floor):
        """Check if there are any requests below the given floor"""
        for f in self.floor_selections:
            if f < floor:
                return True
        for f in self.up_calls:
            if f < floor:
                return True
        for f in self.down_calls:
            if f < floor:
                return True
        return False

    def _get_first_call_above(self, floor):
        """Get the first call above the given floor, or None"""
        for f in self.up_calls:
            if f > floor:
                return f
        for f in self.down_calls:
            if f > floor:
                return f
        return None

    def _get_first_call_below(self, floor):
        """Get the first call below the given floor, or None"""
        for f in self.up_calls:
            if f < floor:
                return f
        for f in self.down_calls:
            if f < floor:
                return f
        return None

    def _get_call_index(self, floor):
        """Get the index of when a floor was called (lower = earlier)"""
        return self.call_order.get(floor, float('inf'))
