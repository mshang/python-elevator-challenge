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
        self.back_for = None
        self.back_for_direction = None
        self.destination_direction = None
        self.destination_floor = None
        self.callbacks = None
        self.stop_list = []
        self.back_stop_list = []

    def on_called(self, floor, direction):
        global DOWN
        """
        This is called when somebody presses the up or down button to call the elevator.
        This could happen at any time, whether or not the elevator is moving.
        The elevator could be requested at any floor at any time, going in either direction.

        floor: the floor that the elevator is being called to
        direction: the direction the caller wants to go, up or down
        """
        des_change_flag = (floor > self.destination_floor) ^ (direction == DOWN) and (direction == DOWN) ^ (
            self.callbacks.current_floor < self.destination_floor
        ) or self.callbacks.current_floor == self.destination_floor
        if des_change_flag or not self.destination_floor:
            self.stop_list.append(floor)
            if self.destination_floor in self.stop_list and (self.destination_direction == DOWN) ^ (
                        self.callbacks.current_floor > self.destination_floor):
                index = self.stop_list.index(self.destination_floor)
                self.back_stop_list.append(self.stop_list.pop(index))
            self.destination_floor = floor
            self.destination_direction = direction
        elif (direction == DOWN) ^ (self.callbacks.current_floor < self.destination_floor):
            self.stop_list.append(floor)
        else:
            self.back_stop_list.append(floor)

    def on_floor_selected(self, floor):
        """
        This is called when somebody on the elevator chooses a floor.
        This could happen at any time, whether or not the elevator is moving.
        Any floor could be requested at any time.

        floor: the floor that was requested
        """
        des_change_flag = (floor > self.destination_floor) ^ (self.callbacks.current_floor > self.destination_floor) \
                          or self.callbacks.current_floor == self.destination_floor
        back_flag = self.destination_direction != self.callbacks.motor_direction and self.destination_direction and not\
            ((self.destination_floor > self.back_for) ^ (self.callbacks.current_floor < self.destination_floor))
        if des_change_flag or not self.destination_floor:
            if back_flag:
                self.back_for = self.destination_floor
                self.back_for_direction = self.destination_direction
            self.stop_list.append(floor)
            if self.destination_floor in self.stop_list and (self.destination_direction == DOWN) ^ (
                        self.callbacks.current_floor > self.destination_floor):
                index = self.stop_list.index(self.destination_floor)
                self.back_stop_list.append(self.stop_list.pop(index))
            self.destination_floor = floor
        else:
            self.stop_list.append(floor)

    def on_floor_changed(self):
        """
        This lets you know that the elevator has moved one floor up or down.
        You should decide whether or not you want to stop the elevator.
        """
        if self.callbacks.current_floor in self.stop_list:
            self.callbacks.motor_direction = None
            self.stop_list.remove(self.callbacks.current_floor)

    def on_ready(self):
        """
        This is called when the elevator is ready to go.
        Maybe passengers have embarked and disembarked. The doors are closed,
        time to actually move, if necessary.
        """
        if self.back_for and self.callbacks.current_floor == self.destination_floor:
            self.destination_floor = self.back_for
            self.stop_list = self.back_stop_list
            self.back_stop_list = []
        if self.destination_floor > self.callbacks.current_floor:
            self.callbacks.motor_direction = UP
        elif self.destination_floor < self.callbacks.current_floor:
            self.callbacks.motor_direction = DOWN
