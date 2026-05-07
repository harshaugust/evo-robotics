"""
Task 2 — Proximity sensors and rule-based navigation
Run this file to produce trajectory plots.
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

from arena import Arena
from robot import Robot
from controller import ProximityController

ARENA_SIZE = 200.0
SENSOR_RANGE = ARENA_SIZE * 0.15   # 15% of arena size = 30 units
STEPS = 6000

COLORS = ["#e74c3c", "#2ecc71", "#3498db", "#f39c12"]


def make_robot(x, y, heading, arena):
    return Robot(x, y, heading, arena, max_speed=2.5,
                 max_turn=np.pi / 6, turn_gain=0.6)


def draw_arena(ax, arena: Arena):
    for wall in arena.walls:
        xs = [wall.p1[0], wall.p2[0]]
        ys = [wall.p1[1], wall.p2[1]]
        ax.plot(xs, ys, color="#555566", linewidth=2, solid_capstyle="round")


def plot_trajectory(ax, traj, color, label):
    xs = [p[0] for p in traj]
    ys = [p[1] for p in traj]
    ax.plot(xs, ys, color=color, linewidth=0.7, alpha=0.85)
    ax.plot(xs[0],  ys[0],  'o', color=color, markersize=7, zorder=5,
            label=f"Start {label}")
    ax.plot(xs[-1], ys[-1], 's', color=color, markersize=7, zorder=5)


def run_and_plot():
    arena = Arena(ARENA_SIZE)

    inits = [
        (30,   30,  np.pi / 4),
        (170,  30,  np.pi * 3 / 4),
        (30,  170, -np.pi / 4),
        (170, 170,  np.pi * 5 / 4),
    ]

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.set_facecolor("#0d0d1a")
    ax.set_xlim(-5, ARENA_SIZE + 5)
    ax.set_ylim(-5, ARENA_SIZE + 5)
    ax.set_aspect("equal")
    ax.set_title("Task 2 — Rule-Based Navigation with Proximity Sensors",
                 fontsize=11)
    ax.set_xlabel("x"); ax.set_ylabel("y")

    draw_arena(ax, arena)

    for (x0, y0, h0), col in zip(inits, COLORS):
        robot = make_robot(x0, y0, h0, arena)
        ctrl  = ProximityController(robot, arena, SENSOR_RANGE)
        traj  = ctrl.run(STEPS)
        plot_trajectory(ax, traj, col, f"({x0},{y0})")

    # legend
    legend_els = [
        Line2D([0], [0], color=c, linewidth=1.5,
               label=f"({x},{y})")
        for (x, y, _), c in zip(inits, COLORS)
    ]
    legend_els += [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='white',
               markersize=7, label="Start"),
        Line2D([0], [0], marker='s', color='w', markerfacecolor='white',
               markersize=7, label="End"),
    ]
    ax.legend(handles=legend_els, fontsize=8, loc="upper right",
              facecolor="#1a1a2e", labelcolor="white")

    fig.tight_layout()
    fig.savefig("trajectory_task2.png", dpi=150)
    print("Saved: trajectory_task2.png")
    plt.close(fig)

    # ── coverage heatmap ───────────────────────────────────────────────────
    fig2, ax2 = plt.subplots(figsize=(7, 7))
    ax2.set_facecolor("#0d0d1a")
    ax2.set_xlim(0, ARENA_SIZE); ax2.set_ylim(0, ARENA_SIZE)
    ax2.set_aspect("equal")
    ax2.set_title("Exploration coverage heatmap", fontsize=11)

    # collect positions from all runs combined
    all_x, all_y = [], []
    for (x0, y0, h0) in inits:
        robot = make_robot(x0, y0, h0, arena)
        ctrl  = ProximityController(robot, arena, SENSOR_RANGE)
        traj  = ctrl.run(STEPS)
        all_x += [p[0] for p in traj]
        all_y += [p[1] for p in traj]

    ax2.hist2d(all_x, all_y, bins=60, cmap="hot",
               range=[[0, ARENA_SIZE], [0, ARENA_SIZE]])
    draw_arena(ax2, arena)
    fig2.tight_layout()
    fig2.savefig("coverage_task2.png", dpi=150)
    print("Saved: coverage_task2.png")
    plt.close(fig2)


if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    print("Running Task 2 simulations …\n")
    run_and_plot()
    print("\nDone.")
