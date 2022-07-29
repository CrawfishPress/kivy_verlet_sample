"""
Dealing with Verlet Engine Physics in Python 3 + Kivy 2.1.0
Based on video:
  - How to program a basic Physic Engine by Pezzza's Work
  - https://www.youtube.com/watch?v=lS_qeBy3aQI

This module has the actual Verlet code, and no Kivy code.
"""

from dataclasses import dataclass


@dataclass
class Vector2:
    x: int
    y: int

    def __sub__(self, other_vec):
        return Vector2(self.x - other_vec.x, self.y - other_vec.y)

    def __add__(self, other_vec):
        return Vector2(self.x + other_vec.x, self.y + other_vec.y)

    def __mul__(self, some_float: float):
        return Vector2(self.x * some_float, self.y * some_float)

    def __iter__(self):
        """ This is so a Vector2 can be unpacked into a Tuple easily. It's the equivalent
            of doing 'foo = *(5, 5)'
        """
        return self.make_tuple()

    def make_tuple(self, *args):
        yield self.x
        yield self.y

    def __str__(self):
        return f"Vector2: [{self.x}:{self.y}]"


class VerletObject:
    def __init__(self, initial_pos: tuple, base_gravity: Vector2, delta_t: float, **kwargs):

        self.position_current: Vector2 = Vector2(*initial_pos)
        self.position_old: Vector2 = Vector2(*initial_pos)
        self.base_gravity: Vector2 = base_gravity
        self.delta_t = delta_t

        self.acceleration: Vector2 = Vector2(0.0, 0.0)

    def SolveForPosition(self) -> Vector2:

        self.ApplyGravity()
        self.UpdatePosition()

        return self.position_current

    def ApplyGravity(self):

        self.acceleration += self.base_gravity

    def UpdatePosition(self):

        velocity: Vector2 = self.position_current - self.position_old

        self.position_old = self.position_current
        self.position_current = self.position_current + velocity + self.acceleration * self.delta_t * self.delta_t

        self.acceleration = Vector2(0.0, 0.0)  # Reset acceleration to zero - not actually sure why...
