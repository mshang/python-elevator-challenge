UP = 1
DOWN = 2
FLOOR_COUNT = 6

import operator

class ElevatorLogic(object):
    def __init__(self):
        self.requested_floors = {UP: set([]), DOWN: set([])}
        self.selected_floors = set([])
        self.notional_direction = None
        self.callbacks = None

    def on_called(self, floor, direction):
        self.requested_floors[direction].add(floor)
        self._set_notional_direction_for_idle()

    def on_floor_selected(self, floor):
        if floor >= self.callbacks.current_floor and self.notional_direction == DOWN: return
        if floor <= self.callbacks.current_floor and self.notional_direction == UP: return
        self.selected_floors.add(floor)
        self._set_notional_direction_for_idle()

    def _end_of_the_line(self, direction):
        f = max if direction == UP else min
        s = self.selected_floors.union(self.requested_floors[UP].union(self.requested_floors[DOWN]))
        if len(s) == 0: return None
        return f(s)

    def _set_notional_direction_for_requests(self):
        notional_direction = self.notional_direction
        opposite = UP if notional_direction == DOWN else DOWN
        self.notional_direction = None
        if self.callbacks.current_floor in self.requested_floors[notional_direction]:
            self.notional_direction = notional_direction
        elif self.callbacks.current_floor in self.requested_floors[opposite]:
            self.notional_direction = opposite
        self._set_notional_direction_for_idle()

    def _set_notional_direction_for_idle(self):
        if self.notional_direction is None:
            if self._should_move(UP): self.notional_direction = UP
            elif self._should_move(DOWN): self.notional_direction = DOWN

    def on_floor_changed(self):
        if self.callbacks.current_floor == self._end_of_the_line(self.notional_direction):
            self._set_notional_direction_for_requests()
        elif self.callbacks.current_floor in self.selected_floors.union(
            self.requested_floors[self.notional_direction]
        ): pass
        else: return

        self.callbacks.motor_direction = None

    def _should_move(self, direction):
        c = operator.lt if direction == UP else operator.gt
        end_of_the_line = self._end_of_the_line(direction)
        if end_of_the_line is None: return False
        return c(self.callbacks.current_floor, self._end_of_the_line(direction))

    def on_ready(self):
        self.selected_floors.discard(self.callbacks.current_floor)
        if self.notional_direction is not None:
            self.requested_floors[self.notional_direction].discard(self.callbacks.current_floor)
            if self._should_move(self.notional_direction):
                self.callbacks.motor_direction = self.notional_direction
            else:
                self._set_notional_direction_for_requests()
                if self.notional_direction is not None:
                    self.requested_floors[self.notional_direction].discard(self.callbacks.current_floor)
                    if self._should_move(self.notional_direction):
                        self.callbacks.motor_direction = self.notional_direction

