UP = 1
DOWN = 2
OUT = 0
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
        self.callbacks = None
        self.requests = []
        self.direction = None

    def on_called(self, floor, direction):
        """
        This is called when somebody presses the up or down button to call the elevator.
        This could happen at any time, whether or not the elevator is moving.
        The elevator could be requested at any floor at any time, going in either direction.

        floor: the floor that the elevator is being called to
        direction: the direction the caller wants to go, up or down
        """
        # if floor == 3:
        #     import pdb; pdb.set_trace()

        if floor == self.callbacks.current_floor and (self.callbacks.motor_direction == None):
            return

        if (self.direction == UP and floor > self.callbacks.current_floor) or (self.direction == DOWN and floor < self.callbacks.current_floor):
            self.requests.insert(0, {"floor": floor, "direction": direction})
        else:
            self.requests.append({"floor": floor, "direction": direction})

    def on_floor_selected(self, floor):
        """
        This is called when somebody on the elevator chooses a floor.
        This could happen at any time, whether or not the elevator is moving.
        Any floor could be requested at any time.

        floor: the floor that was requested
        """

        if (self.direction == UP and floor < self.callbacks.current_floor or self.direction == DOWN and floor > self.callbacks.current_floor):
            return

        for request in self.requests:
            if floor == request["floor"]:
                return

        if floor > self.callbacks.current_floor:
            self.direction = UP
        elif floor < self.callbacks.current_floor:
            self.direction = DOWN
        else:
            return

        self.requests.insert(0, {"floor": floor, "direction": OUT})

    def has_no_requests(self):
        return len(self.requests) == 0
    def has_one_request(self):
        return len(self.requests) == 1

    def on_floor_changed(self):
        """
        This lets you know that the elevator has moved one floor up or down.
        You should decide whether or not you want to stop the elevator.
        """
        floor = self.callbacks.current_floor
        for request in self.requests:
            if floor == request["floor"]:
                if self.should_stop_at_floor(request):
                    self.requests.remove(request)
                    direction = self.callbacks.motor_direction
                    self.callbacks.motor_direction = None
                    if self.has_no_requests():
                        self.direction = request["direction"]

    def should_stop_at_floor(self, request):
        return (self.servable_request(request) or not self.requests_beyond_current_floor())

    def remove_requests_at_floor(self, floor):
        requests_for_removal = []
        for request in self.requests:
            if floor == request["floor"]:
                requests_for_removal.append(request)
        for r in requests_for_removal:
            self.requests.remove(r)
        return len(requests_for_removal)

    def requests_beyond_current_floor(self):
        if self.direction == UP:
            for request in self.requests:
                if request["floor"] > self.callbacks.current_floor:
                    return True
            return False
        elif self.direction == DOWN:
            for request in self.requests:
                if request["floor"] < self.callbacks.current_floor:
                    return True
            return False

    def servable_request(self, request):
        requested_floor = request["floor"] == self.callbacks.current_floor
        correct_direction = self.callbacks.motor_direction == request["direction"]
        out_request = request["direction"] == OUT
        return requested_floor and (correct_direction or out_request)

    def on_ready(self):
        """
        This is called when the elevator is ready to go.
        Maybe passengers have embarked and disembarked. The doors are closed,
        time to actually move, if necessary.
        """
        if self.has_no_requests():
            self.reverse_direction()
            return

        request = self.requests[0]
        floor = request["floor"]

        if floor > self.callbacks.current_floor:
            self.callbacks.motor_direction = UP
            self.direction = UP
        elif floor < self.callbacks.current_floor:
            self.callbacks.motor_direction = DOWN
            self.direction = DOWN
        else:
            self.reverse_direction()

        if self.callbacks.motor_direction == None:
            self.remove_requests_at_floor(self.callbacks.current_floor)

    def reverse_direction(self):
        if self.direction == DOWN:
            self.direction = UP
        elif self.direction == UP:
            self.direction = DOWN
