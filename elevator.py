UP = 1
DOWN = 2
DESTINATION = 4
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
        # Feel free to add any instance variables you want.
        self.destination_floor = None
        self.callbacks = None
        self.state = [0] * (FLOOR_COUNT + 1)  # UP/DOWN/DESTINATION bitmask per floor (1-based)
        self.trend = None  # current trend (UP/DOWN/None)

    def find(self, start, stop, step, trend):
        for floor in range(start, stop, step):
            if self.state[floor] & (trend | DESTINATION):
                return floor
        return None

    def update_state(self, floor, set_mask, unset_mask=0):
        # set/unset state bitmask for given floor
        self.state[floor] = (self.state[floor] | set_mask) & ~unset_mask
        # find the next potential up/down stops
        # (closest stop in same direction or farthest stop in opposite direction)
        count = len(self.state)
        curr = self.callbacks.current_floor
        next_up = self.find(curr + 1, count, 1, UP) or self.find(count - 1, curr, -1, DOWN)
        next_down = self.find(curr - 1, 0, -1, DOWN) or self.find(1, curr, 1, UP)
        # select the destination floor (taking current trend into account)
        # and set new trend if there is none
        if next_up and (self.trend == UP or not next_down):
            self.destination_floor = next_up
            self.trend = self.trend or UP
        elif next_down and (self.trend == DOWN or not next_up):
            self.destination_floor = next_down
            self.trend = self.trend or DOWN
        else:
            self.destination_floor = None

    def prepare_for_departure(self):
        curr = self.callbacks.current_floor
        # change trend direction if we were called here to go to opposite direction
        opposite_trend = self.trend == UP and DOWN or self.trend == DOWN and UP or None
        if self.state[curr] & ~DESTINATION == opposite_trend:
            self.trend = opposite_trend
        # clear (ignore) destinations that are not in current trend direction
        for f in range(1, len(self.state)):
            if self.trend == UP and f <= curr or self.trend == DOWN and f >= curr:
                self.state[f] &= ~DESTINATION
        # clear used state of current floor and update destination using updated trend
        self.update_state(curr, 0, self.trend or 0)
        # update trend according to actual destination
        dest = self.destination_floor or curr
        self.trend = dest > curr and UP or dest < curr and DOWN or None

    def on_called(self, floor, direction):
        """
        This is called when somebody presses the up or down button to call the elevator.
        This could happen at any time, whether or not the elevator is moving.
        The elevator could be requested at any floor at any time, going in either direction.

        floor: the floor that the elevator is being called to
        direction: the direction the caller wants to go, up or down
        """
        self.update_state(floor, direction)

    def on_floor_selected(self, floor):
        """
        This is called when somebody on the elevator chooses a floor.
        This could happen at any time, whether or not the elevator is moving.
        Any floor could be requested at any time.

        floor: the floor that was requested
        """
        self.update_state(floor, DESTINATION)

    def on_floor_changed(self):
        """
        This lets you know that the elevator has moved one floor up or down.
        You should decide whether or not you want to stop the elevator.
        """
        if self.destination_floor == self.callbacks.current_floor:
            self.callbacks.motor_direction = None

    def on_ready(self):
        """
        This is called when the elevator is ready to go.
        Maybe passengers have embarked and disembarked. The doors are closed,
        time to actually move, if necessary.
        """
        self.prepare_for_departure()
        self.callbacks.motor_direction = self.trend
