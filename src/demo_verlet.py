"""
Dealing with Verlet Engine Physics in Python 3 + Kivy 2.1.0
Based on video:
  - How to program a basic Physic Engine by Pezzza's Work
  - https://www.youtube.com/watch?v=lS_qeBy3aQI

Because this is Python/Kivy, the code can currently handle 100 balls,
but at 150, starts to have a visible slow-down. 200 is right out.
So, this only goes up to the 5:00 minute-mark in the video - the code
can't handle thousands of balls. Maybe someday I'll optimize it...
(Or more likely, just port it to Rust).

Note: The Kivy Widget I'm using to display balls, has a Position,
but the canvas-circle (or Ellipse) has its own Position that determines
where it will be displayed. Widgets are separate from what the canvas draws.
So you will see an offset applied to the Circle.

Note: Widget positions (self.pos) are tuples (5, 5), so I added a converter
on the Vector2 dataclass, the iterator method '__iter__()'.
This allows you to unpack the Vector2, similar to doing
    self.pos = *(5, 5)  = self.pos = Vector2(5, 5)
only without the asterisk.

Note: Kivy coordinates - Y=0, at bottom of screen
So acceleration is reversed.

Note: Adding constraints - there is currently only one, an "invisible"
circle - so adding a Kivy widget to make it visible.

Note: adding collisions between balls. My code is slightly different from
the video - I don't have a collection of Verlet objects, I have a collection
of Kivy Widgets (circles), each of which has its own Verlet object. While
this works fine, for purposes of falling/constraints - for purposes of
detecting collisions between balls, there has to be an iterator-function
at a different level than the Verlet object.

I'm not entirely sure from the video, but it looks like it might be using
an Entity-Component-System (or possibly that's build-in to C++).

Anyway - the collision-code isn't exactly like the video... Shocker...

Note: adding multiple balls in a loop - all of the balls will be
instantiated at once (instantly), unless I add a time-delay. However...
because of how Kivy constructs Widgets, the time-delay can't be inside
the Widget, or it will just sleep for the time, and *then* instantly
create all of the balls. So I need a Clock-based function to add them
one at a time.

Note: the original video used *sub-steps* per Frame. I'm not really sure
how that's different from having *more* frames-per-second, to be honest.
Either way, it's tricky to do, because I separated Collision-handling,
from the Verlet-Solver function, which runs on each object. I did actually
try a sub-step loop in the Solver, but it basically amplified everything.
Which was fun to watch - sorta like popcorn - but not exactly realistic...

Note: added Links, mostly. The first pass is klunky, because the Widget's
position, isn't identical to the displayed canvas-circle's center. I need
to refactor position-handling in general.

Switching to kv-lang, instead of pure-Python.  Made the BallPit Image
into a Widget (otherwise it displayed a background *and* the canvas-Circle).
Going to add Buttons next, that clear the screen, etc.

Linked-balls still broken, need to figure out the dampening-factor.

Added some pre-collision fast-filtering, up to 150 balls now, before
hitting 1/60th of a second per frame.

TODO: fix Links
TODO: add more sliders/buttons, to play with all of the constraints.

"""

import random
import time

from kivy.app import App
from kivy.graphics import Color, Ellipse
from kivy.uix.widget import Widget
from kivy.uix.relativelayout import RelativeLayout
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.lang import Builder

from verlet_engine import Vector2, VerletObject, Link

Window.top = 0
Window.left = 100
window_size = (1600, 1000)

kv_file = 'layouts.kv'

pit_constraints = {
    'pit_pos': (0, 0),
    'pit_size': (1000, 1000),
    'pit_radius': 500.0,

    'gravity': Vector2(0.0, -2),
    'damp_factor': 0.5,
    'delta_t': 0.5,

    'ball_radius': 15,
}

ball_count = 30
static_ball_count = 0
balls_linked = 5


class OneCircle(Widget):
    def __init__(self, start_pos: tuple, start_size: tuple, rgb_tuple: tuple, **kwargs):
        super().__init__(**kwargs)
        self.color: tuple = rgb_tuple

        self.pos: tuple = start_pos
        self.size = start_size
        self.ball_radius = start_size[0] / 2
        self.my_verlet: VerletObject = VerletObject(self.pos)

        with self.canvas.before:
            Color(*self.color)
            self.circle = Ellipse(pos=self.pos, size=self.size)

    def UpdatePosition(self):

        # Don't really have to set the Widget's position, but the Circle does have to be set, so...
        self.pos: tuple = self.my_verlet.SolveForPosition()
        self.circle.pos = (self.pos[0] - self.ball_radius, self.pos[1] - self.ball_radius)


class MainPage(RelativeLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.balls = []
        self.delayed_balls = []
        self.static_balls = []
        self.links = []
        self.constraints = {}

        # self.start_demo()  # There's a Button for that...

    def start_demo(self):
        global ball_count

        if self.ids and 'ball_slider_id' in self.ids:
            ball_count = self.ids['ball_slider_id'].value
            # print(f"*** Slider set to: {self.ids['ball_slider_id'].value}")

        self.remove_all()

        self.add_balls()
        self.add_static_balls()
        self.add_links()

        Clock.schedule_interval(self.update_all_circles, 1/60.0)

    def remove_all(self):

        if self.balls:
            for one_ball in self.balls:
                self.remove_widget(one_ball)
        self.balls = []
        self.delayed_balls = []
        self.static_balls = []
        self.links = []

    def add_balls(self):

        VerletObject.constraints = pit_constraints
        ball_radius = pit_constraints['ball_radius']

        some_size = (ball_radius * 2, ball_radius * 2)
        some_color = (1.0, 1.0, 1.0, 1.0)

        for x in range(0, ball_count):
            rand_x = random.randrange(0, 200, 20)
            some_pos = (600 + rand_x, 800)
            one_circle = OneCircle(some_pos, some_size, some_color)
            self.delayed_balls.append(one_circle)

        Clock.schedule_interval(self.add_circle_on_delay, 1/6.0)

    def add_static_balls(self):

        VerletObject.constraints = pit_constraints
        ball_radius = pit_constraints['ball_radius']

        some_pos = (500, 800)
        some_size = (ball_radius * 2, ball_radius * 2)
        some_color = (1.0, 1.0, 1.0, 1.0)
        for x in range(0, static_ball_count):
            one_circle = OneCircle(some_pos, some_size, some_color)
            self.static_balls.append(one_circle)
            self.add_widget(one_circle)

    def add_links(self):

        if balls_linked < 2 or static_ball_count == 0:
            return

        # Link the static-ball first
        one_link = Link(self.static_balls[0].my_verlet, self.delayed_balls[0].my_verlet, 40, True)
        self.links.append(one_link)

        for x in range(0, balls_linked - 1):
            one_link = Link(self.delayed_balls[x].my_verlet, self.delayed_balls[x+1].my_verlet, 40, True)
            self.links.append(one_link)

    def add_circle_on_delay(self, *args):

        if self.delayed_balls:
            one_ball = self.delayed_balls.pop(0)
            self.balls.append(one_ball)
            self.add_widget(one_ball)
        else:
            Clock.unschedule(self.add_circle_on_delay)

    def update_all_circles(self, *args):

        start_time = time.time()
        collision_list = []
        the_radius = pit_constraints['ball_radius'] * 2.1

        for a_ball in self.balls:
            a_ball.UpdatePosition()

            # TODO: definitely room for optimization here, this is O**2
            # Handle collisions
            for one_ball in self.balls:
                if a_ball == one_ball:
                    continue

                # Basic fast collision-filtering
                x_check = abs(one_ball.my_verlet.position_current.x - a_ball.my_verlet.position_current.x)
                y_check = abs(one_ball.my_verlet.position_current.y - a_ball.my_verlet.position_current.y)
                if x_check > the_radius or y_check > the_radius:
                    continue

                maybe_new_vec = a_ball.my_verlet.DetectCollision(one_ball.my_verlet)
                if maybe_new_vec:
                    collision_list.append((a_ball, one_ball))
                    a_ball.my_verlet.position_current += maybe_new_vec
                    one_ball.my_verlet.position_current -= maybe_new_vec

        # Update links
        for one_link in self.links:
            one_link.apply_link()

        end_time = time.time()
        func_time = end_time - start_time
        pain_str = ""
        if func_time > 1/60.0:
            pain_str = "***"
        print(f"[{pain_str}] update.time = [{func_time:.6f}] sec. Total balls: {len(self.balls)}")


class canvasMain(App):
    def build(self):

        Window.size = window_size

        kv_loaded = Builder.load_file(kv_file)

        return kv_loaded


if __name__ == '__main__':

    canvasMain().run()
