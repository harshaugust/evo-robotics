"""
Task 1 — Pygame live visualizer
Controls:
  F   → run Fear vehicle
  A   → run Aggressor vehicle
  R   → reset / new random start
  SPACE → pause / resume
  ESC / Q → quit
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import math
import random
import numpy as np
import pygame

from world import World
from light import LightSource
from robot import Robot
from sensors import LightSensor
from vehicles import Fear, Aggressor

# ── constants ──────────────────────────────────────────────────────────────────
WORLD_W, WORLD_H = 200.0, 200.0
SCREEN_W, SCREEN_H = 700, 700        # pixels
PANEL_H = 80                          # bottom info panel height
SCALE = SCREEN_W / WORLD_W           # world units → pixels

FPS = 60
STEPS_PER_FRAME = 2                  # simulation steps per rendered frame

LIGHT_X, LIGHT_Y = 100.0, 100.0

# colours
BG_DARK       = (13,  13,  13)
PANEL_BG      = (25,  25,  35)
LIGHT_COLOUR  = (255, 220, 80)
ROBOT_COLOUR  = (0,   200, 255)
SENSOR_COLOUR = (0,   255, 100)
TRAIL_FEAR    = (255, 80,  80)
TRAIL_AGGR    = (80,  180, 255)
TEXT_COLOUR   = (220, 220, 220)
WALL_COLOUR   = (60,  60,  80)


# ── helpers ────────────────────────────────────────────────────────────────────

def w2s(x: float, y: float) -> tuple[int, int]:
    """World coordinates → screen pixel (y flipped)."""
    return int(x * SCALE), int((WORLD_H - y) * SCALE)


def build_light_surface(light: LightSource, resolution: int = 200) -> pygame.Surface:
    """Pre-render the light field into a pygame Surface."""
    surf = pygame.Surface((SCREEN_W, SCREEN_H))
    field = light.intensity_field(resolution)
    # field is (resolution x resolution), origin lower-left
    # we need to map to pixels
    cell_w = SCREEN_W / resolution
    cell_h = SCREEN_H / resolution
    for i in range(resolution):
        for j in range(resolution):
            v = field[i, j]           # i=row (y), j=col (x)
            r = int(min(255, v * 255 * 1.2))
            g = int(min(255, v * 220))
            b = int(v * 80)
            px = int(j * cell_w)
            py = int((resolution - 1 - i) * cell_h)   # flip y
            pygame.draw.rect(surf, (r, g, b),
                             (px, py, max(1, int(cell_w)+1), max(1, int(cell_h)+1)))
    return surf


def draw_robot(surf: pygame.Surface, robot: Robot,
               sensor_l: LightSensor, sensor_r: LightSensor,
               sl: float, sr: float) -> None:
    rx, ry = w2s(robot.x, robot.y)
    radius = 8

    # body
    pygame.draw.circle(surf, ROBOT_COLOUR, (rx, ry), radius)
    # heading arrow
    hx = rx + int(radius * 1.6 * math.cos(robot.heading))
    hy = ry - int(radius * 1.6 * math.sin(robot.heading))   # y flipped
    pygame.draw.line(surf, (255, 255, 255), (rx, ry), (hx, hy), 2)

    # sensors
    for sensor, val in [(sensor_l, sl), (sensor_r, sr)]:
        sx, sy = sensor.position(robot)
        px, py = w2s(sx, sy)
        intensity = int(50 + val * 200)
        colour = (intensity, 255, intensity)
        pygame.draw.circle(surf, colour, (px, py), 5)
        pygame.draw.line(surf, colour, (rx, ry), (px, py), 1)


def draw_trail(surf: pygame.Surface, trail: list, colour: tuple) -> None:
    if len(trail) < 2:
        return
    # draw segments; skip jumps caused by torus wrap
    for i in range(1, len(trail)):
        x0, y0 = trail[i - 1]
        x1, y1 = trail[i]
        # skip if the robot wrapped around (large jump)
        if abs(x1 - x0) > WORLD_W / 2 or abs(y1 - y0) > WORLD_H / 2:
            continue
        p0 = w2s(x0, y0)
        p1 = w2s(x1, y1)
        pygame.draw.line(surf, colour, p0, p1, 1)


def draw_panel(surf: pygame.Surface, font: pygame.font.Font,
               vehicle_name: str, step: int,
               sl: float, sr: float, paused: bool) -> None:
    panel_rect = pygame.Rect(0, SCREEN_H, SCREEN_W, PANEL_H)
    pygame.draw.rect(surf, PANEL_BG, panel_rect)
    pygame.draw.line(surf, (80, 80, 100), (0, SCREEN_H), (SCREEN_W, SCREEN_H), 1)

    lines = [
        f"Vehicle: {vehicle_name}   Step: {step}   {'⏸ PAUSED' if paused else '▶ RUNNING'}",
        f"Left sensor: {sl:.4f}   Right sensor: {sr:.4f}   Δs: {abs(sl-sr):.4f}",
        "F=Fear  A=Aggressor  R=Reset  SPACE=Pause  ESC=Quit",
    ]
    for k, line in enumerate(lines):
        text = font.render(line, True, TEXT_COLOUR)
        surf.blit(text, (12, SCREEN_H + 8 + k * 22))


def draw_light_marker(surf: pygame.Surface) -> None:
    lx, ly = w2s(LIGHT_X, LIGHT_Y)
    # glowing star
    for r, alpha in [(18, 40), (12, 80), (6, 180)]:
        glow = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*LIGHT_COLOUR, alpha), (r, r), r)
        surf.blit(glow, (lx - r, ly - r))
    pygame.draw.circle(surf, (255, 255, 255), (lx, ly), 4)


# ── main ───────────────────────────────────────────────────────────────────────

def main():
    pygame.init()
    pygame.display.set_caption("Braitenberg Vehicles — Task 1")
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H + PANEL_H))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("monospace", 14)
    big_font = pygame.font.SysFont("monospace", 22, bold=True)

    world = World(WORLD_W, WORLD_H)
    light = LightSource(LIGHT_X, LIGHT_Y, world, I_max=1.0, k=0.008)

    print("Pre-rendering light field … ", end="", flush=True)
    light_surf = build_light_surface(light, resolution=150)
    print("done.")

    sensor_l = LightSensor(+math.pi / 4, arm=10.0)
    sensor_r = LightSensor(-math.pi / 4, arm=10.0)

    # state
    vehicle_name = "Fear"
    VehicleClass = Fear
    trail_colour = TRAIL_FEAR

    def new_vehicle():
        x0 = random.uniform(10, WORLD_W - 10)
        y0 = random.uniform(10, WORLD_H - 10)
        h0 = random.uniform(0, 2 * math.pi)
        robot = Robot(x0, y0, h0, world, max_speed=3.0,
                      max_turn=math.pi / 8, turn_gain=0.5)
        v = VehicleClass(robot, light, gain=3.0, sensor_arm=10.0)
        return v

    vehicle = new_vehicle()
    trail: list[tuple[float, float]] = [vehicle.robot.position]
    step = 0
    paused = False
    sl = sr = 0.0

    # welcome overlay
    show_welcome = True
    welcome_timer = 180  # frames

    running = True
    while running:
        # ── events ──────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                show_welcome = False
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    running = False
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    vehicle = new_vehicle()
                    trail = [vehicle.robot.position]
                    step = 0
                elif event.key == pygame.K_f:
                    vehicle_name = "Fear"
                    VehicleClass = Fear
                    trail_colour = TRAIL_FEAR
                    vehicle = new_vehicle()
                    trail = [vehicle.robot.position]
                    step = 0
                elif event.key == pygame.K_a:
                    vehicle_name = "Aggressor"
                    VehicleClass = Aggressor
                    trail_colour = TRAIL_AGGR
                    vehicle = new_vehicle()
                    trail = [vehicle.robot.position]
                    step = 0

        # ── simulation step ─────────────────────────────────────────────────
        if not paused:
            for _ in range(STEPS_PER_FRAME):
                vl, vr = vehicle.step()
                vehicle.robot.update(vl, vr)
                trail.append(vehicle.robot.position)
                step += 1
            sl = sensor_l.read(vehicle.robot, light)
            sr = sensor_r.read(vehicle.robot, light)

        # keep trail from growing forever
        if len(trail) > 4000:
            trail = trail[-4000:]

        # ── draw ────────────────────────────────────────────────────────────
        screen.blit(light_surf, (0, 0))
        draw_light_marker(screen)
        draw_trail(screen, trail, trail_colour)
        draw_robot(screen, vehicle.robot, sensor_l, sensor_r, sl, sr)
        draw_panel(screen, font, vehicle_name, step, sl, sr, paused)

        # welcome overlay
        if show_welcome:
            welcome_timer -= 1
            if welcome_timer <= 0:
                show_welcome = False
            overlay = pygame.Surface((SCREEN_W, 120), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, SCREEN_H // 2 - 60))
            t1 = big_font.render("Braitenberg Vehicles — Task 1", True, (255, 220, 80))
            t2 = font.render("Press F = Fear   A = Aggressor   SPACE = Pause   R = Reset", True, TEXT_COLOUR)
            screen.blit(t1, (SCREEN_W // 2 - t1.get_width() // 2, SCREEN_H // 2 - 45))
            screen.blit(t2, (SCREEN_W // 2 - t2.get_width() // 2, SCREEN_H // 2 + 5))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    main()
