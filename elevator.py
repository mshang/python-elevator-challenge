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
        self.destination_floor = None
        self.callbacks = None
        self.destinations = []
        for i in range(FLOOR_COUNT + 1):
          floors = {UP: 0, DOWN: 0, OUT: 0}
          self.destinations.append(floors)
        self.direction = None

    def on_called(self, floor, direction):
        """
        This is called when somebody presses the up or down button to call the elevator.
        This could happen at any time, whether or not the elevator is moving.
        The elevator could be requested at any floor at any time, going in either direction.

        floor: the floor that the elevator is being called to
        direction: the direction the caller wants to go, up or down
        """
        self.destinations[floor][direction] = 1

    def on_floor_selected(self, floor):
        """
        This is called when somebody on the elevator chooses a floor.
        This could happen at any time, whether or not the elevator is moving.
        Any floor could be requested at any time.

        floor: the floor that was requested
        """
        current_floor = self.callbacks.current_floor
        next_direction, _ = on_ready_impl(
          current_floor, self.direction, self.destinations)
        if (next_direction == UP and floor < current_floor or
            next_direction == DOWN and floor > current_floor):
          return
        self.destinations[floor][OUT] = 1

    def on_floor_changed(self):
        """
        This lets you know that the elevator has moved one floor up or down.
        You should decide whether or not you want to stop the elevator.
        """
        floor = self.callbacks.current_floor
        if floor == self.destination_floor:
          self.callbacks.motor_direction = None
          self.destinations[floor] = {UP: 0, DOWN: 0, OUT: 0}

    def on_ready(self):
        """
        This is called when the elevator is ready to go.
        Maybe passengers have embarked and disembarked. The doors are closed,
        time to actually move, if necessary.
        """
        # print 'on_ready'
        direction, destination_floor = on_ready_impl(
          self.callbacks.current_floor, self.direction, self.destinations)
        self.callbacks.motor_direction = self.direction = direction
        self.destination_floor = destination_floor



def on_ready_impl(floor, direction, destinations):
  if direction == UP or direction is None:
    for i in range(floor + 1, FLOOR_COUNT + 1):
      if destinations[i][UP] or destinations[i][OUT]:
        return UP, i

    for i in range(floor + 1, FLOOR_COUNT + 1):
      if destinations[i][DOWN]:
        return UP, i

  for i in range(floor - 1, 0, -1):
    if destinations[i][DOWN] or destinations[i][OUT]:
      return DOWN, i

  for i in range(floor - 1, 0, -1):
    if destinations[i][UP]:
      return DOWN, i

  return None, None
