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
        self.bounded_direction = None

    def on_called(self, floor, direction):
        """
        This is called when somebody presses the up or down button to call the elevator.
        This could happen at any time, whether or not the elevator is moving.
        The elevator could be requested at any floor at any time, going in either direction.

        floor: the floor that the elevator is being called to
        direction: the direction the caller wants to go, up or down
        """

        direction_to_floor = self.direction_to(floor)

        if self.current_direction is None:
            # Change direction
            self.current_direction = direction_to_floor

        if self.callbacks.current_floor != floor:
            self.orders[direction].insert(0, floor)
            # Reorder
            self.orders[UP].sort()
            self.orders[DOWN].sort(reverse=True)
            if self.current_direction == UP and self.orders[UP]:
                self.destination_floor = self.orders[UP][0]
            else:
                self.destination_floor = self.orders[direction][0]
        else:
            # Missed the boat, come back later
            self.orders[self.other_direction(self.current_direction)].insert(0, floor)

        # print "on called. Status: ", self.status()

    def on_floor_selected(self, floor):
        """
        This is called when somebody on the elevator chooses a floor.
        This could happen at any time, whether or not the elevator is moving.
        Any floor could be requested at any time.

        floor: the floor that was requested
        """

        direction_to_floor = self.direction_to(floor)

        if direction_to_floor is None:
            # print "missed the boat. status: %s " % self.status()
            return

        if self.bounded_direction:
            if direction_to_floor == self.bounded_direction:
                self.current_direction = self.bounded_direction
                self.bounded_direction = None
            else:
                self.bounded_direction = None
                return

        if self.current_direction and self.current_direction != direction_to_floor:
            # Set it to wait for requests to move to the other direction
            self.current_direction = self.other_direction(self.current_direction)
            return

        self.orders[direction_to_floor].insert(0, floor)

        # sort the list so closer floors are attended first
        self.orders[direction_to_floor].sort()

        if self.current_direction is None:
            self.current_direction = direction_to_floor

        self.destination_floor = self.orders[self.current_direction][0]

    def on_floor_changed(self):
        """
        This lets you know that the elevator has moved one floor up or down.
        You should decide whether or not you want to stop the elevator.
        """

        if self.destination_floor == self.callbacks.current_floor:
            self.callbacks.motor_direction = None
            if self.orders[self.current_direction]:
                self.orders[self.current_direction].pop(0)
            else:
                self.orders[self.other_direction(self.current_direction)].pop(0) #something had to be served (
            if self.orders[self.current_direction]:
                next_destination = self.orders[self.current_direction][0]
                if next_destination != self.callbacks.current_floor:
                    self.destination_floor = next_destination
                else:
                    self.orders[self.current_direction].pop(0)  # drop it, already there
                    self.destination_floor = None
                    self.bounded_direction = self.current_direction
            else:
                self.bounded_direction = self.current_direction

        if not self.orders[self.current_direction]:
            other_direction = self.other_direction(self.current_direction)
            if other_direction and self.orders[other_direction]:
                self.current_direction = other_direction
                # Set the new target floor
                if self.orders[self.current_direction]:
                    self.destination_floor = self.orders[self.current_direction][0]

        if self.is_idle():
            self.current_direction = None  # Elevator is idle

        # print "on_changed. status: %s" % self.status()

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
        else:
            self.bounded_direction = None

        # print "on ready. status: %s" % self.status()

    def direction_to(self, floor):
        direction = None
        if floor > self.callbacks.current_floor:
            direction = UP
        elif floor < self.callbacks.current_floor:
            direction = DOWN
        return direction

    def is_idle(self):
        return not self.orders[UP] and not self.orders[DOWN]

    @staticmethod
    def other_direction(direction):
        if UP == direction:
            return DOWN
        if DOWN == direction:
            return UP
        return None

    def status(self):
        def direction_str(direction):
            if UP == direction:
                return "UP"
            elif DOWN == direction:
                return "DOWN"
            else:
                return "None"

        return """Current direction: %s
               Current floor: %d
               Destination floor: %d
               orders UP: %s
               orders DOWN: %s
               """ % (direction_str(self.current_direction),
                      self.callbacks.current_floor,
                      self.destination_floor,
                      self.orders[UP],
                      self.orders[DOWN])
