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
        # Feel free to add any instance variables you want.
        self.destination_floor = None
        self.callbacks = None
        self.orders = {}
        self.orders[UP] = []
        self.orders[DOWN] = []
        self.current_direction = None

    def on_called(self, floor, direction):
        """
        This is called when somebody presses the up or down button to call the elevator.
        This could happen at any time, whether or not the elevator is moving.
        The elevator could be requested at any floor at any time, going in either direction.

        floor: the floor that the elevator is being called to
        direction: the direction the caller wants to go, up or down
        """

        target_direction = self.direction_to(floor)

        if self.current_direction is None:
            # Change direction
            self.current_direction = target_direction

        self.destination_floor = floor
        self.orders[direction].insert(0, floor)


    def on_floor_selected(self, floor):
        """
        This is called when somebody on the elevator chooses a floor.
        This could happen at any time, whether or not the elevator is moving.
        Any floor could be requested at any time.

        floor: the floor that was requested
        """

        target_direction = self.direction_to(floor)

        if self.current_direction and self.current_direction != target_direction:
            return

        self.orders[target_direction].insert(0, floor)

        # sort the list so closer floors are attended first
        self.orders[target_direction].sort()

        if self.current_direction is None:
            self.current_direction = target_direction

        self.destination_floor = self.orders[self.current_direction][0]

    def on_floor_changed(self):
        """
        This lets you know that the elevator has moved one floor up or down.
        You should decide whether or not you want to stop the elevator.
        """

        if self.destination_floor == self.callbacks.current_floor:
            self.callbacks.motor_direction = None
            if self.current_direction and self.orders[self.current_direction]:
                self.orders[self.current_direction].pop(0)
                if self.orders[self.current_direction]:
                    self.destination_floor = self.orders[self.current_direction][0]

        if self.current_direction and not self.orders[self.current_direction]:
            other_direction = self.other_direction(self.current_direction)
            if other_direction and self.orders[other_direction]:
                self.current_direction = other_direction
                # Set the new target floor
                if self.orders[self.current_direction]:
                    self.destination_floor = self.orders[self.current_direction][0]

        if not self.orders[UP] and not self.orders[DOWN]:
            self.current_direction = None  # Elevator is idle

    def on_ready(self):
        """
        This is called when the elevator is ready to go.
        Maybe passengers have embarked and disembarked. The doors are closed,
        time to actually move, if necessary.
        """
        # print "on ready: dest floor: %d" % self.destination_floor
        if self.destination_floor > self.callbacks.current_floor:
            self.callbacks.motor_direction = UP
        elif self.destination_floor < self.callbacks.current_floor:
            self.callbacks.motor_direction = DOWN

    def direction_to(self, floor):
        direction = None
        if floor > self.callbacks.current_floor:
            direction = UP
        elif floor < self.callbacks.current_floor:
            direction = DOWN
        return direction

    def other_direction(self, direction):
        if UP == direction:
            return DOWN
        if DOWN == direction:
            return UP
        return None
