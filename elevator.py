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
        self.callbacks = None
        self.direction = 0
        self.called_floors_up = set()
        self.called_floors_down = set()
        self.selected_floors = set()

    def on_called(self, floor, direction):
        """
        This is called when somebody presses the up or down button to call the elevator.
        This could happen at any time, whether or not the elevator is moving.
        The elevator could be requested at any floor at any time, going in either direction.

        floor: the floor that the elevator is being called to
        direction: the direction the caller wants to go, up or down
        """
        called_floors = self.called_floors_up if direction == UP else self.called_floors_down
        current_floor = self.callbacks.current_floor
        motor_direction = self.callbacks.motor_direction

        if not floor in called_floors and (motor_direction != None or floor != current_floor):
            called_floors.add(floor)
            if self.direction == 0:
                self.direction = UP if floor > current_floor else DOWN

    def on_floor_selected(self, floor):
        """
        This is called when somebody on the elevator chooses a floor.
        This could happen at any time, whether or not the elevator is moving.
        Any floor could be requested at any time.

        floor: the floor that was requested
        """
        delta = 1 if self.direction == UP else -1
        current_floor = self.callbacks.current_floor

        if not floor in self.selected_floors and floor != current_floor:
            if self.direction == 0 or delta * (floor - current_floor) > 0:
                self.selected_floors.add(floor)
            if self.direction == 0:
                self.direction = UP if floor > current_floor else DOWN

    def on_floor_changed(self):
        """
        This lets you know that the elevator has moved one floor up or down.
        You should decide whether or not you want to stop the elevator.
        """
        called_floors = self.called_floors_up if self.direction == UP else self.called_floors_down
        reverse_called_floors = self.called_floors_down if self.direction == UP else self.called_floors_up
        current_floor = self.callbacks.current_floor

        if current_floor in self.selected_floors:
            self.callbacks.motor_direction = None
            self.selected_floors.discard(current_floor)

        if current_floor in called_floors:
            self.callbacks.motor_direction = None
            called_floors.discard(current_floor)
        elif not self.need_to_go(self.direction) and current_floor in reverse_called_floors:
            self.callbacks.motor_direction = None
            reverse_called_floors.discard(current_floor)
            self.direction = DOWN if self.direction == UP else UP

    def on_ready(self):
        """
        This is called when the elevator is ready to go.
        Maybe passengers have embarked and disembarked. The doors are closed,
        time to actually move, if necessary.
        """
        reverse_called_floors = self.called_floors_down if self.direction == UP else self.called_floors_up
        current_floor = self.callbacks.current_floor

        if self.direction != 0:
            if self.need_to_go(self.direction):
                self.callbacks.motor_direction = self.direction
            elif current_floor in reverse_called_floors:
                reverse_called_floors.discard(current_floor)
                self.direction = DOWN if self.direction == UP else UP
            else:
                self.direction = 0

        if self.direction == 0:
            self.called_floors_up.discard(current_floor)
            self.called_floors_down.discard(current_floor)
            if self.need_to_go(UP):
                self.callbacks.motor_direction = UP
                self.direction = UP
            elif self.need_to_go(DOWN):
                self.callbacks.motor_direction = DOWN
                self.direction = DOWN

    def need_to_go(self, direction):
        delta = 1 if direction == UP else -1
        floors = self.selected_floors | self.called_floors_up | self.called_floors_down

        for floor in floors:
            if delta * (floor - self.callbacks.current_floor) > 0:
                return True

        return False
