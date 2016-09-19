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
        if self.stopped_at_floor(floor):
            return

        if self.floor_is_upcoming(floor):
            self.requests.insert(0, {"floor": floor, "direction": direction})
        else:
            self.requests.append({"floor": floor, "direction": direction})

    def floor_is_upcoming(self, floor):
        if self.direction == UP:
            return self.higher_than_current_floor(floor)
        elif self.direction == DOWN:
            return self.lower_than_current_floor(floor)

    def stopped_at_floor(self, floor):
        return self.equal_to_current_floor(floor) and self.callbacks.motor_direction == None

    def on_floor_selected(self, floor):
        """
        This is called when somebody on the elevator chooses a floor.
        This could happen at any time, whether or not the elevator is moving.
        Any floor could be requested at any time.

        floor: the floor that was requested
        """
        if self.request_is_in_opposite_direction(floor) or self.has_requests_at_floor(floor):
            return

        if self.higher_than_current_floor(floor):
            self.direction = UP
        elif self.lower_than_current_floor(floor):
            self.direction = DOWN
        else:
            return

        self.requests.insert(0, {"floor": floor, "direction": OUT})

    def has_requests_at_floor(self, floor):
        return len(self.requests_for_floor(floor)) > 0

    def requests_for_floor(self, floor):
        return filter(lambda request: request["floor"] == floor, self.requests)

    def floor_requested(self, floor):
        return any(request["floor"] == floor for request in self.requests)

    def request_is_in_opposite_direction(self, floor):
        if self.direction == UP:
            return self.lower_than_current_floor(floor)
        elif self.direction == DOWN:
            return self.higher_than_current_floor(floor)

    def on_floor_changed(self):
        """
        This lets you know that the elevator has moved one floor up or down.
        You should decide whether or not you want to stop the elevator.
        """
        fulfilled_requests = []
        for request in self.requests_for_floor(self.callbacks.current_floor):
            if self.should_stop_at_floor(request):
                self.callbacks.motor_direction = None
                fulfilled_requests.append(request)
                direction = request["direction"]

        self.remove_requests(fulfilled_requests)
        if self.has_no_requests():
            self.direction = direction

    def should_stop_at_floor(self, request):
        return self.servable_request(request) or not self.has_further_servable_requests()

    def servable_request(self, request):
        correct_direction = self.callbacks.motor_direction == request["direction"]
        out_request = request["direction"] == OUT
        return correct_direction or out_request

    def has_further_servable_requests(self):
        for request in self.requests:
            if self.equal_to_current_floor(request["floor"]) and self.request_not_in_opposite_direction(request):
                return True
        return self.further_requests_in_current_direction()

    def request_not_in_opposite_direction(self, request):
        return not request["direction"] == self.opposite_direction()

    def opposite_direction(self):
        if self.direction == UP:
            return DOWN
        elif self.direction == DOWN:
            return UP

    def further_requests_in_current_direction(self):
        upcoming_floors = filter(lambda request: self.floor_is_upcoming(request["floor"]), self.requests)
        return len(upcoming_floors) > 0

    def on_ready(self):
        """
        This is called when the elevator is ready to go.
        Maybe passengers have embarked and disembarked. The doors are closed,
        time to actually move, if necessary.
        """
        if self.has_no_requests():
            self.direction = None
            return

        next_request_floor = self.requests[0]["floor"]
        if self.higher_than_current_floor(next_request_floor):
            self.callbacks.motor_direction = UP
            self.direction = UP
        elif self.lower_than_current_floor(next_request_floor):
            self.callbacks.motor_direction = DOWN
            self.direction = DOWN
        else:
            self.direction = self.opposite_direction()
            requests_for_removal = self.requests_for_floor(self.callbacks.current_floor)
            self.remove_requests(requests_for_removal)

    def remove_requests(self, requests):
        for request in requests:
            self.requests.remove(request)

    def has_no_requests(self):
        return len(self.requests) == 0

    def higher_than_current_floor(self, floor):
        return floor > self.callbacks.current_floor

    def lower_than_current_floor(self, floor):
        return floor < self.callbacks.current_floor

    def equal_to_current_floor(self, floor):
        return floor == self.callbacks.current_floor
