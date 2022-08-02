### kivy_verlet_sample

Inspired by the excellent video:

  - https://www.youtube.com/watch?v=lS_qeBy3aQI
  - (How to program a basic Physic Engine by Pezzza's Work)

This is a quick demo of the basic Verlet equations for object-motion,
implemented in Python + Kivy. (Uses Python 3.8/Kivy 2.1.0)

Because this is Python/Kivy, the code can currently handle 100 balls,
but at 150, starts to have a visible slow-down. 200 is right out.
So, this only goes up to the 5:00 minute-mark in the video - the code
can't handle thousands of balls. Maybe someday I'll optimize it...
(Or more likely, just port it to Rust as an exercise).

### To Run

Presuming you have a virtual environment, one of the many that Python has:

    pip install -r requirements.txt
    python src/demo_verlet.py


### Output
![](Screenshot.png)
