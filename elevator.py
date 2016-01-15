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
        self.waiting = None
        self.trend = None
        self.request_set = set([])

    def on_called(self, floor, direction):
        """
        This is called when somebody presses the up or down button to call the elevator.
        This could happen at any time, whether or not the elevator is moving.
        The elevator could be requested at any floor at any time, going in either direction.

        floor: the floor that the elevator is being called to
        direction: the direction the caller wants to go, up or down
        """
        moving_direction = 1 if self.callbacks.current_floor < self.destination_floor else 2
        moving_further = (floor < self.destination_floor) and (moving_direction == DOWN) \
                or (floor > self.destination_floor) and (moving_direction == UP) or not self.destination_floor
        # moving_further = moving_further if moving_further == UP else not moving_further
        des_change_flag = moving_further or floor == self.destination_floor
        back_flag = (self.destination_direction != moving_direction and not self.callbacks.current_floor ==
                     self.destination_floor) and ((self.destination_floor > self.back_for) ^ (moving_direction == UP)\
                                                  or not self.back_for)
        if des_change_flag or not self.destination_floor:
            if back_flag and (floor != self.destination_floor or direction != self.destination_direction):
                self.back_for = self.destination_floor
                self.back_for_direction = self.destination_direction
            if self.destination_floor in self.stop_list and (self.destination_direction != moving_direction):
                index = self.stop_list.index(self.destination_floor)
                self.back_stop_list.append(self.stop_list.pop(index))
            if moving_direction != direction and moving_direction == self.destination_direction:
                self.back_for = floor
                self.back_for_direction = direction
                self.back_stop_list.append(floor)
            else:
                self.destination_floor = floor
                self.stop_list.append(floor)
                self.destination_direction = direction
        elif self.trend == UP and floor > self.callbacks.current_floor\
                or self.trend == DOWN and floor < self.callbacks.current_floor:
            self.destination_floor = floor
            self.stop_list.append(floor)
            self.destination_direction = direction
        elif moving_direction != direction or (floor < self.callbacks.current_floor) ^ (moving_direction == DOWN) or\
                floor == self.callbacks.current_floor:
            self.back_for = floor
            self.back_for_direction = direction
            self.back_stop_list.append(floor)
        elif direction == moving_direction:
            self.stop_list.append(floor)
        else:
            self.back_stop_list.append(floor)
        self.waiting = False
        self.request_set.add((floor, direction))

    def on_floor_selected(self, floor):

        """
        This is called when somebody on the elevator chooses a floor.
        This could happen at any time, whether or not the elevator is moving.
        Any floor could be requested at any time.

        floor: the floor that was requested
        """
        moving_direction = 2 if self.callbacks.current_floor > self.destination_floor else 1
        floor_to_des = 2 if floor > self.destination_floor else 1
        des_change_flag = floor_to_des != moving_direction or self.callbacks.current_floor == self.destination_floor \
                          or not self.destination_floor
        back_flag = self.destination_direction and (
            (self.destination_floor > self.back_for) ^ (moving_direction == UP)\
                or not self.back_for) and self.callbacks.current_floor != self.destination_floor
        if self.waiting and (self.destination_direction == DOWN) ^ (floor < self.callbacks.current_floor
                                                                    ) and floor != self.callbacks.current_floor:
            self.destination_direction = self.back_for_direction
            self.destination_floor = self.back_for
            self.stop_list.append(self.back_for)
            # self.request_set = self.request_set.difference({(self.destination_floor, self.destination_direction)})
            self.back_for_direction = None
            self.back_for = None
            if not self.destination_floor:
                self.waiting = False
            return
        if des_change_flag or not self.destination_floor:
            if back_flag:
                self.back_for = self.destination_floor
                self.back_for_direction = self.destination_direction
            self.stop_list.append(floor)
            if self.destination_floor in self.stop_list and (self.destination_direction == DOWN) ^ (
                        self.callbacks.current_floor > self.destination_floor):
                index = self.stop_list.index(self.destination_floor)
                self.back_stop_list.append(self.stop_list.pop(index))
            if floor != self.destination_floor:
                self.destination_direction = None
            self.destination_floor = floor
        else:
            self.stop_list.append(floor)
        self.waiting = False
        self.request_set.add((floor, None))

    def on_floor_changed(self):
        """
        This lets you know that the elevator has moved one floor up or down.
        You should decide whether or not you want to stop the elevator.
        """
        if self.callbacks.current_floor in self.stop_list + [1, FLOOR_COUNT]:
            self.trend = self.callbacks.motor_direction
            self.request_set = self.request_set.difference({(self.callbacks.current_floor, None)})
            self.request_set = self.request_set.difference({(self.callbacks.current_floor, self.trend)})
            if self.callbacks.current_floor == self.destination_floor and self.destination_direction:
                self.waiting = True
            self.callbacks.motor_direction = None
            try:
                self.stop_list.remove(self.callbacks.current_floor)
            except ValueError:
                pass

    def on_ready(self):
        """
        This is called when the elevator is ready to go.
        Maybe passengers have embarked and disembarked. The doors are closed,
        time to actually move, if necessary.
        """
        if self.back_for and self.callbacks.current_floor == self.destination_floor:
            self.destination_floor = self.back_for
            self.destination_direction = self.back_for_direction
            self.stop_list = self.back_stop_list
            self.back_stop_list = []
        if self.destination_floor:
            if self.destination_floor > self.callbacks.current_floor:
                self.callbacks.motor_direction = UP
            elif self.destination_floor < self.callbacks.current_floor:
                self.callbacks.motor_direction = DOWN
