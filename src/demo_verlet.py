"""
Dealing with Verlet Engine Physics in Python 3 + Kivy 2.1.0
Based on video:
  - How to program a basic Physic Engine by Pezzza's Work
  - https://www.youtube.com/watch?v=lS_qeBy3aQI

Note: The Kivy Widget I'm using to display circles, has a Position,
but the canvas-circle (or Ellipse) has its own Position that determines
where it will be displayed. Widgets are separate from what the canvas draws.

Note: Widget positions (self.pos) are tuples (5, 5), so I added a converter
on the Vector2 dataclass, the iterator method '__iter__()'.
This allows you to unpack the Vector2, similar to doing
    self.pos = *(5, 5)  = self.pos = Vector2(5, 5)
only without the asterisk.

Note: Kivy coordinates - Y=0, at bottom of screen
So acceleration is reversed.
"""

from kivy.app import App
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.uix.widget import Widget
from kivy.uix.relativelayout import RelativeLayout
from kivy.clock import Clock
from kivy.core.window import Window

from verlet_engine import Vector2, VerletObject

Window.top = 0
Window.left = 400
window_size = (1600, 1000)

# Random engine constants
base_gravity = Vector2(0.0, -0.5)
delta_t: float = 0.2


class SomeCircle(Widget):
    def __init__(self, start_pos: tuple, rgb_tuple: tuple, **kwargs):
        super().__init__(**kwargs)
        self.color: tuple = rgb_tuple

        self.pos: tuple = start_pos
        self.size = 50, 50
        self.my_verlet: VerletObject = VerletObject(self.pos, base_gravity, delta_t)

        with self.canvas.before:
            Color(*self.color)
            self.circle = Ellipse(pos=self.pos, size=self.size)

    def UpdatePosition(self):

        # Don't really have to set the Widget's position, but the Circle does have to be set, so...
        self.pos = self.my_verlet.SolveForPosition()
        self.circle.pos = self.pos


class MainPage(RelativeLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.circles = []

        some_pos = (500, 500)
        some_color = (1.0, 0.5, 0.1, 1.0)
        one_circle = SomeCircle(some_pos, some_color)
        self.circles.append(one_circle)
        for a_ball in self.circles:
            self.add_widget(a_ball)

        Clock.schedule_interval(self.update_all_circles, 1/60.0)

        with self.canvas.before:  # Gotta have a background
            Color(0.1, 0.1, 0.1, 1.0)
            self.bg_rect = Rectangle()

    def on_size(self, instance, new_size):

        self.bg_rect.size = self.size

    def update_all_circles(self, *args):

        for a_ball in self.circles:
            a_ball.UpdatePosition()


class canvasMain(App):
    def build(self):

        Window.size = window_size
        return MainPage()


if __name__ == '__main__':

    canvasMain().run()
