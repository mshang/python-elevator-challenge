#!/usr/bin/env python

UP = 1
DOWN = 2
FLOOR_COUNT = 6

class ElevatorLogic(object):

    def __init__(self):
        # Required.
        self.callbacks = None

        # Current elevator direction.
        self._direction = None

        # Pending requests. A request is a pair (floor, direction), in which
        # direction can be None if the floor was selected from the elevator, or
        # a given direction if the elevator was called from a floor. Telling
        # both cases apart is actually needed.
        self._requests = set()

    def _try_add(self, floor, direction):
        # Basic checks when storing a new request.
        if ((floor, direction) not in self._requests
            and floor >= 1 and floor <= FLOOR_COUNT
            and (self.callbacks.current_floor != floor
                 or self.callbacks.motor_direction is not None)):

            # Save the request.
            self._requests.add((floor, direction))

            # Set direction now if possible. This gives priority to earliest
            # requests first.
            if self._direction is None:
                cur = self.callbacks.current_floor
                if floor < cur:
                    self._direction = DOWN
                elif floor > cur:
                    self._direction = UP
                elif direction is not None:
                    self._direction = direction

    def on_called(self, floor, direction):
        self._try_add(floor, direction)

    def on_floor_selected(self, floor):
        # This call requires a few additional checks to ignore floors that
        # contradict the current direction.
        cur = self.callbacks.current_floor
        if (self._direction is None or
            (self._direction == UP and floor > cur) or
            (self._direction == DOWN and floor < cur)):
            self._try_add(floor, None)

    def _any_above(self, floor):
        return any(f > floor for (f, d) in self._requests)

    def _any_below(self, floor):
        return any(f < floor for (f, d) in self._requests)

    # Any requests in my current direction?
    def _should_continue(self):
        cur = self.callbacks.current_floor
        return ((self._direction == UP and self._any_above(cur))
                or (self._direction == DOWN and self._any_below(cur)))

    def _opposite(self):
        if self._direction is None:
            return None
        if self._direction == UP:
            return DOWN
        return UP

    def on_floor_changed(self):
        cur = self.callbacks.current_floor

        # Reasons to stop:
        #   (a) Passenger requested the current floor.
        #   (b) Current floor requested in the current direction.
        #   (c) No further requests in this direction.
        if ((cur, None) in self._requests or
            (cur, self._direction) in self._requests or
            (not self._should_continue())):

            self.callbacks.motor_direction = None

            # Deal with (a).
            self._requests.discard((cur, None))

            # Now maybe (b) or, if not, maybe (c).
            aux = (cur, self._direction)
            if aux in self._requests:
                self._requests.discard(aux)
            elif not self._should_continue():
                aux = (cur, self._opposite())
                if aux in self._requests:
                    self._requests.discard(aux)
                    self._direction = self._opposite()

    def on_ready(self):
        # Continue in the current direction if possible.
        if self._should_continue():
            self.callbacks.motor_direction = self._direction

        # Forget direction when done.
        elif len(self._requests) == 0:
            self._direction = None

        else:
            # Change direction. Serve curent floor or start motor.
            aux = (self.callbacks.current_floor, self._opposite())
            if aux in self._requests:
                self._requests.discard(aux)
            else:
                self.callbacks.motor_direction = self._opposite()
            self._direction = self._opposite()
