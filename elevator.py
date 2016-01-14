UP = 1
DOWN = 2
FLOOR_COUNT = 6

# Helper functions to scan through sets to find any matching elements
def contains(theSet, theFloor, theDirection):
    for floor in theSet:
        if theDirection == UP and floor > theFloor:
            return True
        if theDirection == DOWN and floor < theFloor:
            return True
    return False

def flip_dir(direction):
    if direction == UP:
        return DOWN
    else:
        return UP

class ElevatorLogic(object):
    """
    A correct implementation! It does indeed pass all the tests

    The tests are integrated into `README.md`. To run the tests:
    $ python -m doctest -v README.md

    To learn when each method is called, read its docstring.
    To interact with the world, you can get the current floor from the
    `current_floor` property of the `callbacks` object, and you can move the
    elevator by setting the `motor_direction` property. See below for how this is done.
    """

    def __init__(self):
        self.callbacks = None

        # Any the floors where there are pending calls
        self.calls = {}
        self.calls[UP] = set()
        self.calls[DOWN] = set()
        # The floors that have been selected by riders (and not ignored)
        self.selections = set()
        # The current target movement direction of the elevator, separate from motor direction
        self.direction = None

    def on_called(self, floor, direction):
        """
        This is called when somebody presses the up or down button to call the elevator.
        This could happen at any time, whether or not the elevator is moving.
        The elevator could be requested at any floor at any time, going in either direction.

        floor: the floor that the elevator is being called to
        direction: the direction the caller wants to go, up or down
        """
        # Ignore any calls if the elevator is sitting idle on that floor and already
        # going in that direction.  If the elevator is just speeding by, however,
        # the request should be noted
        if not (self.callbacks.current_floor == floor and
                self.direction == direction and
                not self.callbacks.motor_direction):
            self.calls[direction].add(floor)
            # If the elevator is sitting idle, it should target the floor of the new
            # request.  This is set immediately so that calls are first-come-first-served
            if self.direction == None:
                self.direction = UP if floor > self.callbacks.current_floor else DOWN

    def on_floor_selected(self, floor):
        """
        This is called when somebody on the elevator chooses a floor.
        This could happen at any time, whether or not the elevator is moving.
        Any floor could be requested at any time.

        floor: the floor that was requested
        """
        # Ignore any floor requests that are not in the current direction of travel
        if self.direction in (UP, None) and floor > self.callbacks.current_floor:
            self.selections.add(floor)
        elif self.direction in (DOWN, None) and floor < self.callbacks.current_floor:
            self.selections.add(floor)
        # If the elevator is sitting idle, prompt it to start moving. This is set
        # immediately rather than when the elevator doors close (self.on_ready) so
        # that the first requested floor will choose the new travel direction.
        if self.direction == None:
            if contains(self.selections, self.callbacks.current_floor, UP):
                self.direction = UP
            else:
                self.direction = DOWN

    def on_floor_changed(self):
        """
        This lets you know that the elevator has moved one floor up or down.
        You should decide whether or not you want to stop the elevator.
        """
        # Always stop on a selected floor
        if (self.callbacks.current_floor in self.selections):
            self.callbacks.motor_direction = None;
        # Stop on a floor with a pending call in the current direction of travel
        if (self.callbacks.current_floor in self.calls[self.direction]):
            self.calls[self.direction].discard(self.callbacks.current_floor)
            self.callbacks.motor_direction = None;
        # Otherwise, if there is no type of request in the direction of travel AND
        # there is a requested call in the other direction, go ahead and stop
        # here and swap target directions
        elif (not contains(self.selections, self.callbacks.current_floor, self.direction) and
              not contains(self.calls[UP], self.callbacks.current_floor, self.direction) and
              not contains(self.calls[DOWN], self.callbacks.current_floor, self.direction)):
            if (self.callbacks.current_floor in self.calls[flip_dir(self.direction)]):
                self.callbacks.motor_direction = None;
                self.direction = flip_dir(self.direction)

        # Remove any selection requests for this floor...
        self.selections.discard(self.callbacks.current_floor)
        # and any calls from this floor in the direction we are heading
        self.calls[self.direction].discard(self.callbacks.current_floor)

    def on_ready(self):
        """
        This is called when the elevator is ready to go.
        Maybe passengers have embarked and disembarked. The doors are closed,
        time to actually move, if necessary.
        """
        # If the elevator is idle or headed a direction and there is any type of
        # request in that direction, start moving
        for d in (UP, DOWN):
            if (self.direction in (d, None) and
                (contains(self.selections, self.callbacks.current_floor, d) or
                 contains(self.calls[UP], self.callbacks.current_floor, d) or
                 contains(self.calls[DOWN], self.callbacks.current_floor, d))):
                self.callbacks.motor_direction = d
                self.direction = d
                return

        # Otherwise, if there is any type of request pending (by getting this far we know
        # the elevator must reverse direction to get to this floor)
        if self.calls[UP] or self.calls[DOWN] or self.selections:
            # Reverse direction, BUT if the current floor has a pending request in the new
            # direction of travel, we should wait one step to give riders a chance to
            # enter new selections in the new direction of travel
            self.direction = flip_dir(self.direction)
            delay = True if self.callbacks.current_floor in self.calls[self.direction] else False
            self.calls[self.direction].discard(self.callbacks.current_floor)
            # If there are no boarders on this level, then just continue immediately with the
            # new direction of travel dialed in
            if not delay:
                self.on_ready()
        else:
            # If there's nothing left to do, then just hang out at this floor
            self.direction = None
            self.callbacks.motor_direction = None

