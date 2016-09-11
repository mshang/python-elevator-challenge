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
        if floor == 1 and direction == DOWN:
            return
        if self.non_existent_floor(floor):
            return
        if self.at_or_passed_floor(floor):
            if self.direction == UP:
                direction = DOWN
            elif self.direction == DOWN:
                direction = UP

        # if self.has_no_requests():
        #     import pdb; pdb.set_trace()

        self.requests.append({"floor": floor, "direction": direction})

    def at_or_passed_floor(self, floor):
        if self.direction == UP:
            return floor <= self.callbacks.current_floor
        elif self.direction == DOWN:
            return floor >= self.callbacks.current_floor
        else:
            return floor == self.callbacks.current_floor

    def on_floor_selected(self, floor):
        """
        This is called when somebody on the elevator chooses a floor.
        This could happen at any time, whether or not the elevator is moving.
        Any floor could be requested at any time.

        floor: the floor that was requested
        """
        if self.non_existent_floor(floor):
            return
        if (self.direction == UP and floor < self.callbacks.current_floor or self.direction == DOWN and floor > self.callbacks.current_floor):
            return

        if floor == self.callbacks.current_floor:
            return

        self.requests.insert(0, {"floor": floor, "direction": OUT})

    def non_existent_floor(self, floor):
        return floor < 1 or floor > FLOOR_COUNT

    def has_requests(self):
        return not self.has_no_requests()
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
        # import pdb; pdb.set_trace()
        for request in self.requests :
            if floor == request["floor"] :
                # import pdb; pdb.set_trace()
                age = self.should_stop_at_floor(request)
                if age :
                    self.requests.remove(request)
                    self.callbacks.motor_direction = None
                    # import pdb; pdb.set_trace()
                    if not self.has_requests():
                        self.direction = None


    def should_stop_at_floor(self, request):
        # import pdb; pdb.set_trace()
        return (self.servable_request(request) or not self.requests_beyond_current_floor())
        return (self.servable_request(request) or self.has_one_request())

    def requests_beyond_current_floor(self):
        if self.direction == UP:
            for request in self.requests:
                if request["floor"] > self.callbacks.current_floor:
                    return True
            return False
            # return self.any(request["floor"] > self.current_floorse for request in self.requests)
        elif self.direction == DOWN:
            for request in self.requests:
                if request["floor"] < self.callbacks.current_floor:
                    return True
            return False
            # return any(request["floor"] < self.callbacks.current_floor for request in self.requests)

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
        # import pdb; pdb.set_trace()
        if self.has_no_requests():
            self.direction = None
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

    def reverse_direction(self):
        if self.direction == DOWN:
            self.direction = UP
        elif self.direction == UP:
            self.direction = DOWN
        else:
            self.direction = None
