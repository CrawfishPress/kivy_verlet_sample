"""
Dealing with Verlet Engine Physics in Python 3 + Kivy 2.1.0
Based on video:
  - How to program a basic Physic Engine by Pezzza's Work
  - https://www.youtube.com/watch?v=lS_qeBy3aQI

This module has the actual Verlet code, and no Kivy code.

Note that Constraints, currently consist of a Circle with point.radius - if
the Ball objects touch the radius, they're *out*.
"""

import math
import random
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

    def __truediv__(self, some_float: float):
        return Vector2(self.x / some_float, self.y / some_float)

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
    constraints: dict = None

    def __init__(self, initial_pos: tuple, **kwargs):

        self.position_current: Vector2 = Vector2(*initial_pos)
        self.position_old: Vector2 = Vector2(*initial_pos)
        self.base_gravity: Vector2 = self.constraints['gravity']

        self.acceleration: Vector2 = Vector2(0.0, 0.0)

    def SolveForPosition(self) -> Vector2:

        self.ApplyGravity()
        self.ApplyConstraints()
        # self.SolveCollisions()  # Checked externally
        self.UpdatePosition()

        return self.position_current

    def ApplyGravity(self) -> None:

        self.acceleration += self.base_gravity

    def ApplyConstraints(self) -> None:

        widget_position = self.constraints['pit_pos']
        pit_radius = self.constraints['pit_radius']
        ball_radius = self.constraints['ball_radius']

        # This is a bit kludgy, turning the radius into a Vector, but it was that, or overload the add-function
        pit_center: Vector2 = Vector2(*widget_position) + Vector2(pit_radius, pit_radius)

        vector_to_center: Vector2 = self.position_current - pit_center

        dist_to_center = math.hypot(*vector_to_center)

        if dist_to_center + ball_radius > pit_radius:
            new_vec: Vector2 = vector_to_center / dist_to_center
            new_pos = pit_center + new_vec * (pit_radius - ball_radius)
            self.position_current = new_pos

    def UpdatePosition(self) -> None:

        delta_t = self.constraints['delta_t']

        velocity: Vector2 = self.position_current - self.position_old

        self.position_old = self.position_current
        self.position_current = self.position_current + velocity + self.acceleration * delta_t * delta_t

        self.acceleration = Vector2(0.0, 0.0)  # Reset acceleration to zero - not actually sure why...

    def DetectCollision(self, some_other_Verlet) -> Vector2:

        object_1 = self
        object_2 = some_other_Verlet
        ball_diameter = self.constraints['ball_radius'] * 2
        damp_factor = self.constraints['damp_factor']

        # This is just as slow as hypot()
        # the_distance = math.dist((object_1.position_current.x, object_1.position_current.y),
        #                          (object_2.position_current.x, object_2.position_current.y))

        collision_axis: Vector2 = object_1.position_current - object_2.position_current
        collision_distance: float = math.hypot(*collision_axis)

        if collision_distance < ball_diameter:
            new_vec: Vector2 = collision_axis / collision_distance
            new_delta: float = ball_diameter - collision_distance
            new_position: Vector2 = new_vec * new_delta * damp_factor

            return new_position

        return None


@dataclass
class Link:
    ball_one: VerletObject
    ball_two: VerletObject
    target_dist: float
    is_static: bool  # First object
    damper_factor: float = 0.3

    def apply_link(self):

        link_axis: Vector2 = self.ball_one.position_current - self.ball_two.position_current
        obj_distance: float = math.hypot(*link_axis)

        new_vec: Vector2 = link_axis / obj_distance
        new_delta: float = self.target_dist - obj_distance
        big_delta = new_vec * new_delta * self.damper_factor

        if not self.is_static:
            self.ball_one.position_current += big_delta
        self.ball_two.position_current -= big_delta
