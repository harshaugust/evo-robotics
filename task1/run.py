"""
Task 1 — Braitenberg Vehicles
Run this file to produce all required plots.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from world import World
from light import LightSource
from robot import Robot
from vehicles import Fear, Aggressor


# ── shared parameters ──────────────────────────────────────────────────────────
WORLD_W, WORLD_H = 200.0, 200.0
LIGHT_X, LIGHT_Y = 100.0, 100.0   # light at center
STEPS = 1000

world = World(WORLD_W, WORLD_H)
light = LightSource(LIGHT_X, LIGHT_Y, world, I_max=1.0, k=0.008)


# ── helper ─────────────────────────────────────────────────────────────────────

def make_robot(x, y, heading):
    return Robot(x, y, heading, world, max_speed=3.0, max_turn=np.pi / 8,
                 turn_gain=0.5)


def plot_trajectory(ax, traj, color, label):
    xs = [p[0] for p in traj]
    ys = [p[1] for p in traj]
    ax.plot(xs, ys, color=color, linewidth=0.8, alpha=0.85, label=label)
    ax.plot(xs[0], ys[0], 'o', color=color, markersize=6)   # start
    ax.plot(xs[-1], ys[-1], 's', color=color, markersize=6)  # end


# ── Plot 1: light intensity field ──────────────────────────────────────────────

def plot_light_field():
    field = light.intensity_field(resolution=300)

    fig, ax = plt.subplots(figsize=(6, 5))
    cmap = LinearSegmentedColormap.from_list("light",
                                             ["#0d0d0d", "#ffdd55", "#ffffff"])
    im = ax.imshow(field, origin="lower", cmap=cmap,
                   extent=[0, WORLD_W, 0, WORLD_H], vmin=0, vmax=1)
    plt.colorbar(im, ax=ax, label="Light intensity")
    ax.set_title("Light intensity field (torus world)")
    ax.set_xlabel("x"); ax.set_ylabel("y")
    ax.plot(LIGHT_X, LIGHT_Y, '*', color='red', markersize=12, label="Light source")
    ax.legend()
    fig.tight_layout()
    fig.savefig("light_field.png", dpi=150)
    print("Saved: light_field.png")
    plt.close(fig)


# ── Plot 2: sensor readings across space ──────────────────────────────────────

def plot_sensor_readings():
    from sensors import LightSensor
    sensor_l = LightSensor(+np.pi / 4, arm=10.0)
    sensor_r = LightSensor(-np.pi / 4, arm=10.0)

    resolution = 100
    xs = np.linspace(0, WORLD_W, resolution)
    ys = np.linspace(0, WORLD_H, resolution)
    sl_field = np.zeros((resolution, resolution))
    sr_field = np.zeros((resolution, resolution))
    diff_field = np.zeros((resolution, resolution))

    heading = 0.0  # robot pointing right — fixed for this illustration
    for i, y in enumerate(ys):
        for j, x in enumerate(xs):
            r = Robot(x, y, heading, world)
            sl = sensor_l.read(r, light)
            sr = sensor_r.read(r, light)
            sl_field[i, j] = sl
            sr_field[i, j] = sr
            diff_field[i, j] = abs(sl - sr)

    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    titles = ["Left sensor (sl)", "Right sensor (sr)", "Difference |sl − sr|"]
    fields = [sl_field, sr_field, diff_field]
    for ax, title, f in zip(axes, titles, fields):
        im = ax.imshow(f, origin="lower", cmap="inferno",
                       extent=[0, WORLD_W, 0, WORLD_H], vmin=0)
        plt.colorbar(im, ax=ax)
        ax.set_title(title)
        ax.set_xlabel("x"); ax.set_ylabel("y")
        ax.plot(LIGHT_X, LIGHT_Y, '*', color='cyan', markersize=10)
    fig.tight_layout()
    fig.savefig("sensor_readings.png", dpi=150)
    print("Saved: sensor_readings.png")
    plt.close(fig)


# ── Plot 3: trajectories — Fear ────────────────────────────────────────────────

def plot_fear():
    inits = [
        (30,  30,  np.pi / 6,     "blue"),
        (170, 50,  np.pi,         "green"),
        (50,  160, -np.pi / 3,    "purple"),
        (160, 160, np.pi * 5 / 4, "orange"),
    ]

    field = light.intensity_field(resolution=200)
    fig, ax = plt.subplots(figsize=(7, 6))
    cmap = LinearSegmentedColormap.from_list("light",
                                             ["#0d0d0d", "#ffdd55", "#ffffff"])
    ax.imshow(field, origin="lower", cmap=cmap,
              extent=[0, WORLD_W, 0, WORLD_H], alpha=0.4)
    ax.plot(LIGHT_X, LIGHT_Y, '*', color='red', markersize=14, zorder=5,
            label="Light source")

    for x0, y0, h0, col in inits:
        robot = make_robot(x0, y0, h0)
        vehicle = Fear(robot, light, gain=3.0, sensor_arm=10.0)
        traj = vehicle.run(STEPS)
        plot_trajectory(ax, traj, col,
                        label=f"start ({x0},{y0}) h={h0:.2f}")

    ax.set_xlim(0, WORLD_W); ax.set_ylim(0, WORLD_H)
    ax.set_title("Braitenberg Vehicle 2b — Fear")
    ax.set_xlabel("x"); ax.set_ylabel("y")
    ax.legend(fontsize=7, loc="upper right")
    fig.tight_layout()
    fig.savefig("trajectory_fear.png", dpi=150)
    print("Saved: trajectory_fear.png")
    plt.close(fig)


# ── Plot 4: trajectories — Aggressor ──────────────────────────────────────────

def plot_aggressor():
    inits = [
        (30,  30,  np.pi / 6,     "blue"),
        (170, 50,  np.pi,         "green"),
        (50,  160, -np.pi / 3,    "purple"),
        (160, 160, np.pi * 5 / 4, "orange"),
    ]

    field = light.intensity_field(resolution=200)
    fig, ax = plt.subplots(figsize=(7, 6))
    cmap = LinearSegmentedColormap.from_list("light",
                                             ["#0d0d0d", "#ffdd55", "#ffffff"])
    ax.imshow(field, origin="lower", cmap=cmap,
              extent=[0, WORLD_W, 0, WORLD_H], alpha=0.4)
    ax.plot(LIGHT_X, LIGHT_Y, '*', color='red', markersize=14, zorder=5,
            label="Light source")

    for x0, y0, h0, col in inits:
        robot = make_robot(x0, y0, h0)
        vehicle = Aggressor(robot, light, gain=3.0, sensor_arm=10.0)
        traj = vehicle.run(STEPS)
        plot_trajectory(ax, traj, col,
                        label=f"start ({x0},{y0}) h={h0:.2f}")

    ax.set_xlim(0, WORLD_W); ax.set_ylim(0, WORLD_H)
    ax.set_title("Braitenberg Vehicle 2a — Aggressor")
    ax.set_xlabel("x"); ax.set_ylabel("y")
    ax.legend(fontsize=7, loc="upper right")
    fig.tight_layout()
    fig.savefig("trajectory_aggressor.png", dpi=150)
    print("Saved: trajectory_aggressor.png")
    plt.close(fig)


# ── Plot 5: combined side-by-side ──────────────────────────────────────────────

def plot_combined():
    inits = [
        (30,  30,  np.pi / 6),
        (170, 50,  np.pi),
        (50,  160, -np.pi / 3),
        (160, 160, np.pi * 5 / 4),
    ]
    colors = ["blue", "green", "purple", "orange"]

    field = light.intensity_field(resolution=200)
    cmap = LinearSegmentedColormap.from_list("light",
                                             ["#0d0d0d", "#ffdd55", "#ffffff"])

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    titles = ["Fear (2b)", "Aggressor (2a)"]
    VehicleClass = [Fear, Aggressor]

    for ax, title, VClass in zip(axes, titles, VehicleClass):
        ax.imshow(field, origin="lower", cmap=cmap,
                  extent=[0, WORLD_W, 0, WORLD_H], alpha=0.35)
        ax.plot(LIGHT_X, LIGHT_Y, '*', color='red', markersize=14, zorder=5)
        for (x0, y0, h0), col in zip(inits, colors):
            robot = make_robot(x0, y0, h0)
            vehicle = VClass(robot, light, gain=3.0, sensor_arm=10.0)
            traj = vehicle.run(STEPS)
            plot_trajectory(ax, traj, col, label=f"({x0},{y0})")
        ax.set_xlim(0, WORLD_W); ax.set_ylim(0, WORLD_H)
        ax.set_title(title, fontsize=13)
        ax.set_xlabel("x"); ax.set_ylabel("y")
        ax.legend(fontsize=8)

    fig.suptitle("Braitenberg Vehicle 2 — Fear vs Aggressor", fontsize=14)
    fig.tight_layout()
    fig.savefig("trajectories_combined.png", dpi=150)
    print("Saved: trajectories_combined.png")
    plt.close(fig)


# ── entrypoint ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    print("Generating plots for Task 1 …\n")
    plot_light_field()
    plot_sensor_readings()
    plot_fear()
    plot_aggressor()
    plot_combined()
    print("\nAll done. Check the PNG files in task1/")
