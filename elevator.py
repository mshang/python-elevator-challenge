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

    def on_called(self, floor, direction):
        """
        This is called when somebody presses the up or down button to call the elevator.
        This could happen at any time, whether or not the elevator is moving.
        The elevator could be requested at any floor at any time, going in either direction.

        floor: the floor that the elevator is being called to
        direction: the direction the caller wants to go, up or down
        """
        self.requests.append({"floor": floor, "direction": direction})

    def on_floor_selected(self, floor):
        """
        This is called when somebody on the elevator chooses a floor.
        This could happen at any time, whether or not the elevator is moving.
        Any floor could be requested at any time.

        floor: the floor that was requested
        """
        if len(self.requests) != 0:
            next_floor = self.requests[0]["floor"]
            if floor < next_floor:
                return
        self.requests.append({"floor": floor, "direction": OUT})

    def on_floor_changed(self):
        """
        This lets you know that the elevator has moved one floor up or down.
        You should decide whether or not you want to stop the elevator.
        """
        floor = self.callbacks.current_floor

        # print "Requests: %s" % self.requests
        for request in self.requests :
            if floor == request["floor"] :
                age = self.should_stop_at_floor(request)
                if age :
                    self.requests.remove(request)
                    self.callbacks.motor_direction = None

    def should_stop_at_floor(self, request):
        final_floor = self.callbacks.current_floor == FLOOR_COUNT - 1
        wrong_way = self.callbacks.motor_direction == request["direction"]
        out_request = request["direction"] == OUT
        return (wrong_way or out_request) or final_floor

    def on_ready(self):
        """
        This is called when the elevator is ready to go.
        Maybe passengers have embarked and disembarked. The doors are closed,
        time to actually move, if necessary.
        """
        
        if len(self.requests) == 0:
            return
        request = self.requests[0]
        floor = request["floor"]

        if floor > self.callbacks.current_floor:
            self.callbacks.motor_direction = UP
        elif floor < self.callbacks.current_floor:
            self.callbacks.motor_direction = DOWN

    def should_move(self):
        return len(self.requests) == 0
