UP = 1
DOWN = 2
FLOOR_COUNT = 6
OUT = 3

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
        # self.destination_floor = None
        self.callbacks = None
        self.destinations = []
        for i in range(FLOOR_COUNT + 1):
          floors = {UP: 0, DOWN: 0, OUT: 0}
          self.destinations.append(floors)
        self.direction = UP

    def on_called(self, floor, direction):
        """
        This is called when somebody presses the up or down button to call the elevator.
        This could happen at any time, whether or not the elevator is moving.
        The elevator could be requested at any floor at any time, going in either direction.

        floor: the floor that the elevator is being called to
        direction: the direction the caller wants to go, up or down
        """
        # print 'on_called', floor, direction
        self.destinations[floor][direction] = 1
        # self.destination_floor = floor

    def on_floor_selected(self, floor):
        """
        This is called when somebody on the elevator chooses a floor.
        This could happen at any time, whether or not the elevator is moving.
        Any floor could be requested at any time.

        floor: the floor that was requested
        """
        self.destinations[floor][OUT] = 1
        # self.destination_floor = floor

    def on_floor_changed(self):
        """
        This lets you know that the elevator has moved one floor up or down.
        You should decide whether or not you want to stop the elevator.
        """
        # if self.destination_floor == self.callbacks.current_floor:
        floor = self.callbacks.current_floor
        try:
          # if (
            # self.destinations[floor][self.direction] or self.destinations[floor][OUT] or
            # floor == FLOOR_COUNT)
          if floor == self.destination_floor:
              self.callbacks.motor_direction = None
        except:
          print floor
          print len(self.destinations)
          # print self.destinations[floor]
          print self.direction

    def on_ready(self):
        """
        This is called when the elevator is ready to go.
        Maybe passengers have embarked and disembarked. The doors are closed,
        time to actually move, if necessary.
        """
        # print 'on_ready'
        floor = self.callbacks.current_floor
        if self.direction == UP:
          for i in range(floor + 1, FLOOR_COUNT + 1):
            # print 'trying ', i, self.destinations[i].itervalues()
            if self.destinations[i][UP] or self.destinations[i][OUT]:
              self.destination_floor = i
              self.callbacks.motor_direction = UP
              return

          for i in range(floor + 1, FLOOR_COUNT + 1):
            # print 'trying ', i, self.destinations[i].itervalues()
            if self.destinations[i][DOWN]:
              self.destination_floor = i
              self.callbacks.motor_direction = UP
              return

        self.direction = DOWN
        for i in range(floor - 1, 0, -1):
          # print 'trying ', i
          if self.destinations[i][DOWN] or self.destinations[i][OUT]:
            self.destination_floor = i
            self.callbacks.motor_direction = DOWN
            return

        for i in range(floor - 1, 0, -1):
          # print 'trying ', i
          if self.destinations[i][UP]:
            self.destination_floor = i
            self.callbacks.motor_direction = DOWN
            return

        self.direction = UP
        self.destination_floor = None
        self.callbacks.motor_direction = None

        # if self.destination_floor > self.callbacks.current_floor:
            # self.callbacks.motor_direction = UP
        # elif self.destination_floor < self.callbacks.current_floor:
            # self.callbacks.motor_direction = DOWN
