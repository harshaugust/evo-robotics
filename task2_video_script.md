# Task 2 — Video Script
**Two parts:** Code walkthrough + Trajectory/coverage plot narration

---

# PART 1 — Code Walkthrough  (~4–5 min)

---

## 1.1  Overview  (~20 sec)

"I'll quickly walk through the code for Task 2. The simulation is split across four files — `arena.py`, `robot.py`, `sensors.py`, and `controller.py` — plus `run.py` which ties everything together and produces the plots."

---

## 1.2  arena.py  (~45 sec)

*[Open arena.py]*

"The `Arena` class sets up the environment. It holds a list of `Wall` objects — each one is just a line segment defined by two points.

The outer boundary is four walls forming the 200 by 200 square. Then `_add_inner_walls` adds six more inner walls — the horizontal bar up top, the tall vertical bar on the right, and so on — which create corridors and dead-ends for the robots to navigate around.

The two key methods are `ray_cast` and `clamp_position`. `ray_cast` fires a ray from a given position and angle, checks it against every wall segment using the `_ray_segment` helper, and returns the distance to the nearest hit. `clamp_position` simply keeps the robot inside the outer boundary by clipping its coordinates."

---

## 1.3  robot.py  (~45 sec)

*[Open robot.py]*

"The `Robot` class is a differential-drive model. It has a position, a heading, and two tunable parameters — max speed and max turn rate.

The `update` method takes left and right wheel speeds. The difference between them — scaled by `turn_gain` — becomes a heading change, clamped to the max turn rate. The average of the two speeds drives the robot forward. A small negative speed is also allowed so the emergency reverse in the controller actually works.

`turn_in_place` directly rotates the heading without moving — used by the controller when it needs an immediate sharp turn before stepping forward."

---

## 1.4  sensors.py  (~40 sec)

*[Open sensors.py]*

"The `ProximitySensor` class models an infrared-style sensor as a single ray cast.

Each sensor has an angle offset relative to the robot's heading and a max range — set to 30 units, which is 15 percent of the arena size.

The `read` method fires the ray via `arena.ray_cast`. If it hits something within range, it returns `1 minus d over r` — so a reading of 1 means a wall is right there, and 0 means nothing in range. This normalised value is what the controller uses directly."

---

## 1.5  controller.py — the hand-coded rules  (~90 sec)

*[Open controller.py]*

"This is the core of the task — the hand-coded `ProximityController`.

The robot has three sensors: front-left at +45 degrees, front at 0 degrees, and front-right at −45 degrees. Every step, `read_sensors` polls all three.

Then `step` applies seven rules in strict priority order.

**Rule 1 — Emergency.** If the front sensor reads 0.70 or above, a wall is very close. The controller checks which side is more open — whichever of front-left or front-right has the lower reading — and rotates 90 degrees or more toward it. It also returns a small negative wheel speed to reverse slightly and create space. This is the rule that prevents the robot from getting pinned.

**Rule 2 — Front blocked.** Front sensor above 0.45. Rotate 60 degrees toward the open side and slow down. Not an emergency yet, but a significant course change is needed.

**Rules 3 and 4 — Diagonal blocked.** If front-left or front-right crosses 0.45, rotate 45 degrees away from the blocked side at reduced speed.

**Rules 5 and 6 — Mild obstacle.** Readings above 0.20 trigger a small 15-degree correction. This smooths out the approach before an obstacle becomes a real problem.

**Rule 7 — Free space.** All sensors clear — cruise at full speed and add a small random heading drift of ±0.06 radians. That random wobble is what drives exploration. Without it the robot would just travel in a straight line and barely cover the arena.

The `run` method loops for however many steps are requested, calls `step` each time, and records the position — that's the trajectory list that gets plotted."

---

## 1.6  run.py  (~30 sec)

*[Open run.py]*

"Finally, `run.py` creates the arena, places four robots at the four corners each pointing inward, runs the controller for 6000 steps per robot, and plots the results.

It produces two outputs — the trajectory plot showing each robot's path, and a combined coverage heatmap using `hist2d` to show where time was spent across the arena."

---

# PART 2 — Trajectory & Coverage Plot Narration  (~2.5 min)

---

## 2.1  Trajectory plot  (~80 sec)

*[Show trajectory_task2.png]*

"This is the output of the simulation. The four coloured lines are the trajectories of the four robots over 6000 steps each. Circles mark starting positions; squares mark where they ended.

Each robot starts in a corner pointing inward. You can immediately see them move toward the centre and then begin curving — that's the sensors picking up the inner walls and the controller steering around them.

Along the outer boundary you see long straight runs where the robot is in free space, and tighter clusters of turns at corners where multiple rules fire in quick succession. The small L-shaped block in the bottom-right is particularly visible — all four trajectories show tight turning behaviour around that area because it creates a narrow gap that forces repeated corrections.

Critically, none of the robots get permanently stuck. The emergency rule breaks them free every time they get too close to a wall head-on."

---

## 2.2  Coverage heatmap  (~50 sec)

*[Show coverage_task2.png]*

"The heatmap shows all four trajectories combined — brighter means more time spent in that cell.

The outer boundary ring is the brightest region. The robots naturally follow walls once detected, so they repeatedly lap the perimeter. The corridors between inner walls are also well-covered.

The dark patches — especially the large enclosed area behind the upper-left horizontal wall, and the pocket behind the tall vertical bar on the right — are regions the robots rarely entered. A reactive controller with no memory can't deliberately navigate into enclosed spaces it hasn't found a path into yet. That's the core limitation of this approach."

---

## 2.3  Closing  (~20 sec)

"To summarise — the hand-coded controller achieves reliable wall avoidance and good general coverage using three sensors and seven rules. The heatmap shows the trade-off: open space is explored well, but enclosed pockets behind inner walls are underexplored. Addressing that would require a controller with some form of memory or deliberate exploration strategy."

---

*Total estimated runtime: ~7–8 minutes*
