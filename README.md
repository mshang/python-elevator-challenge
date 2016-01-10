Python Elevator Challenge
=========================

So You Think You Can Program An Elevator?
-----------------------------------------

Many of us ride elevators every day. We intuitively feel like we have a good grasp on them. We understand the how elevators decide where to go. But say you wanted to express this algorithm in code. How would you go about it?

The Test Harness
----------------

Lets consider a simplified model of an elevator. Like all elevators, it can go up or down. We define constants for these. This elevator also happens to be in a building with six floors.

    >>> UP = 1
    >>> DOWN = 2
    >>> FLOOR_COUNT = 6

We will make an `Elevator` class that simulates an elevator. This will delegate to another class which contains the elevator business logic, i.e. deciding what the elevator should do. Your challenge is to implement the business logic.

A user can interact with the elevator in two ways. She can call the elevator by pressing the up or down  button on any floor, and she can select a destination floor by pressing the button for that floor on the panel in the elevator. Both of these actions get passed straight through to the logic delegate.

    >>> class Elevator(object):
    ...     def call(self, floor, direction):
    ...         self._logic_delegate.on_called(floor, direction)
    ... 
    ...     def select_floor(self, floor):
    ...         self._logic_delegate.on_floor_selected(floor)

The logic delegate can respond by setting the elevator to move up, move down, or stop. It can also read the current floor and movement direction of the elevator. These actions are accessed through `Callbacks`, a mediator provided by the `Elevator` class to the logic delegate.

    >>> class Elevator(Elevator):
    ...     def __init__(self, logic_delegate):
    ...         self._current_floor = 1
    ...         print "1...",
    ...         self._motor_direction = None
    ...         self._logic_delegate = logic_delegate
    ...         self._logic_delegate.callbacks = self.Callbacks(self)
    ... 
    ...     class Callbacks(object):
    ...         def __init__(self, outer):
    ...             self._outer = outer
    ... 
    ...         @property
    ...         def current_floor(self):
    ...             return self._outer._current_floor
    ... 
    ...         @property
    ...         def motor_direction(self):
    ...             return self._outer._motor_direction
    ... 
    ...         @motor_direction.setter
    ...         def motor_direction(self, direction):
    ...             self._outer._motor_direction = direction

The simulation runs in steps. Every time step consists of either a change of floor, or a pause at a floor. Either way, the business logic delegate gets notified. Along the way, we print out the movements of the elevator so that we can keep track of it. We also define a few helper methods.

    >>> class Elevator(Elevator):
    ...     def step(self):
    ...        delta = 0
    ...        if self._motor_direction == UP: delta = 1
    ...        elif self._motor_direction == DOWN: delta = -1
    ... 
    ...        if delta:
    ...            self._current_floor = self._current_floor + delta
    ...            print "%s..." % self._current_floor,
    ...            self._logic_delegate.on_floor_changed()
    ...        else:
    ...            self._logic_delegate.on_ready()
    ... 
    ...        assert self._current_floor >= 1
    ...        assert self._current_floor <= FLOOR_COUNT
    ...     
    ...     def run_until_stopped(self):
    ...         self.step()
    ...         while self._motor_direction is not None: self.step()
    ...     
    ...     def run_until_floor(self, floor):
    ...         self.step()
    ...         for i in range(100):
    ...             if self._current_floor == floor: break
    ...             self.step()
    ...         else: assert False

That's it for the framework.

The Business Logic
------------------

As for the business logic, an example implementation is provided in the `elevator.py` file in this project.

    >>> from elevator_solution import ElevatorLogic

As provided, it doesn't pass the tests in this document. Your challenge is to fix it so that it does. To run the tests, run this in your shell:

    python -m doctest -v README.md

With the correct business logic, here's how the elevator should behave:

### Basic usage

Make an elevator. It starts at the first floor.

    >>> elevator = Elevator(ElevatorLogic())
    1...

Somebody on the fifth floor wants to go down.

    >>> elevator.call(5, DOWN)
    >>> elevator.run_until_stopped()
    2... 3... 4... 5...

The elevator went up to the fifth floor. Now, the passenger gets on and presses the button to select the first floor.

    >>> elevator.select_floor(1)
    >>> elevator.run_until_stopped()
    4... 3... 2... 1...

More Tests
----------

    >>> elevator = Elevator(ElevatorLogic())
    1...
    >>> elevator.call(3, UP)
    >>> elevator.call(5, UP)
    >>> elevator.run_until_stopped()
    2... 3...
    >>> elevator.run_until_stopped()
    4... 5...

    >>> elevator = Elevator(ElevatorLogic())
    1...
    >>> elevator.call(5, UP)
    >>> elevator.call(3, UP)
    >>> elevator.run_until_stopped()
    2... 3...
    >>> elevator.run_until_stopped()
    4... 5...


