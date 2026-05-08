import sys, os
sys.path.insert(0, os.path.dirname(__file__))

import math
import random
import numpy as np
import pygame

from arena import Arena
from robot import Robot
from controller import ProximityController

ARENA_SIZE      = 200.0
SCREEN_SIZE     = 700
PANEL_H         = 90
SCALE           = SCREEN_SIZE / ARENA_SIZE

FPS             = 60
STEPS_PER_FRAME = 3
SENSOR_RANGE    = ARENA_SIZE * 0.15
MAX_TRAIL       = 3000

ROBOT_COLORS = [
    (220,  80,  80),
    ( 80, 200,  80),
    ( 80, 140, 255),
    (255, 190,  50),
]

SENSOR_COLS = {
    "fl": (255, 220,  60),
    "f":  (255,  80,  80),
    "fr": ( 60, 210, 255),
}

BG       = (13,  13,  26)
WALL_COL = (110, 110, 150)
PANEL_BG = (20,  20,  40)
TEXT_COL = (210, 210, 210)


def w2s(x, y):
    return int(x * SCALE), int((ARENA_SIZE - y) * SCALE)


def make_sim(arena, x0, y0, h0):
    robot = Robot(x0, y0, h0, arena, max_speed=2.5,
                  max_turn=math.pi / 6, turn_gain=0.6)
    ctrl  = ProximityController(robot, arena, SENSOR_RANGE)
    return robot, ctrl


def random_sim(arena):
    m = 20
    x0 = random.uniform(m, ARENA_SIZE - m)
    y0 = random.uniform(m, ARENA_SIZE - m)
    h0 = random.uniform(0, 2 * math.pi)
    return make_sim(arena, x0, y0, h0)


def draw_arena(surf, arena):
    for wall in arena.walls:
        pygame.draw.line(surf, WALL_COL, w2s(*wall.p1), w2s(*wall.p2), 3)


def draw_robot(surf, robot, ctrl, color):
    rx, ry = w2s(robot.x, robot.y)
    r = max(5, int(robot.radius * SCALE * 0.85))

    pygame.draw.circle(surf, color, (rx, ry), r)
    pygame.draw.circle(surf, (255, 255, 255), (rx, ry), r, 1)

    hx = rx + int(r * 1.8 * math.cos(robot.heading))
    hy = ry - int(r * 1.8 * math.sin(robot.heading))
    pygame.draw.line(surf, (255, 255, 255), (rx, ry), (hx, hy), 2)

    for sensor, key in [(ctrl.sensor_fl, "fl"),
                        (ctrl.sensor_f,  "f"),
                        (ctrl.sensor_fr, "fr")]:
        ex, ey = sensor.ray_endpoint(robot, ctrl.arena)
        val    = sensor.read(robot, ctrl.arena)
        col    = SENSOR_COLS[key]
        dim    = tuple(int(c * (0.25 + 0.75 * val)) for c in col)
        pygame.draw.line(surf, dim, (rx, ry), w2s(ex, ey), 1)
        if val > 0.05:
            pygame.draw.circle(surf, col, w2s(ex, ey), 3)


def draw_panel(surf, font, step, sims, paused):
    panel_y = SCREEN_SIZE
    pygame.draw.rect(surf, PANEL_BG, (0, panel_y, SCREEN_SIZE, PANEL_H))
    pygame.draw.line(surf, (70, 70, 100), (0, panel_y), (SCREEN_SIZE, panel_y), 1)

    status = "⏸ PAUSED" if paused else "▶ RUNNING"
    surf.blit(font.render(f"Step: {step}   {status}   ({len(sims)} robots)",
                          True, TEXT_COL), (12, panel_y + 6))

    x_off = 12
    for i, (robot, ctrl, color) in enumerate(sims):
        fl = ctrl.sensor_fl.read(robot, ctrl.arena)
        f  = ctrl.sensor_f .read(robot, ctrl.arena)
        fr = ctrl.sensor_fr.read(robot, ctrl.arena)
        label = f"R{i+1} FL:{fl:.2f} F:{f:.2f} FR:{fr:.2f}  "
        surf.blit(font.render(label, True, color), (x_off, panel_y + 30))
        x_off += font.size(label)[0]

    surf.blit(font.render("SPACE=Pause  R=Reset  ESC=Quit",
                          True, (150, 150, 150)), (12, panel_y + 54))


def draw_legend(surf, font):
    x, y = SCREEN_SIZE - 165, 8
    for key, label in [("fl", "Front-Left"), ("f", "Front"), ("fr", "Front-Right")]:
        col = SENSOR_COLS[key]
        pygame.draw.line(surf, col, (x, y + 6), (x + 16, y + 6), 2)
        surf.blit(font.render(label, True, col), (x + 22, y))
        y += 18


def main():
    pygame.init()
    pygame.display.set_caption("Task 2 — 4 Robots, Proximity Sensors")
    screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE + PANEL_H))
    clock  = pygame.time.Clock()
    font   = pygame.font.SysFont("monospace", 13)
    big    = pygame.font.SysFont("monospace", 20, bold=True)

    arena = Arena(ARENA_SIZE)

    arena_surf = pygame.Surface((SCREEN_SIZE, SCREEN_SIZE))
    arena_surf.fill(BG)
    draw_arena(arena_surf, arena)

    starts = [
        (30,  30,  math.pi / 4),
        (170, 30,  math.pi * 3 / 4),
        (30,  170, -math.pi / 4),
        (170, 170, math.pi * 5 / 4),
    ]

    def reset():
        sims = []
        for x0, y0, h0 in starts:
            robot, ctrl = make_sim(arena, x0, y0, h0)
            sims.append((robot, ctrl, ROBOT_COLORS[len(sims)]))
        trails      = [[] for _ in sims]
        trail_surfs = []
        for color in ROBOT_COLORS:
            s = pygame.Surface((SCREEN_SIZE, SCREEN_SIZE), pygame.SRCALPHA)
            trail_surfs.append(s)
        return sims, trails, trail_surfs

    sims, trails, trail_surfs = reset()
    step   = 0
    paused = False

    show_welcome  = True
    welcome_timer = 220

    running = True
    while running:
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
                    sims, trails, trail_surfs = reset()
                    step = 0

        if not paused:
            for _ in range(STEPS_PER_FRAME):
                for i, (robot, ctrl, color) in enumerate(sims):
                    prev = robot.position
                    vl, vr = ctrl.step()
                    robot.update(vl, vr)
                    curr = robot.position
                    trails[i].append(curr)

                    tr_col = (*color, 120)
                    pygame.draw.line(trail_surfs[i], tr_col,
                                     w2s(*prev), w2s(*curr), 1)

                    if len(trails[i]) > MAX_TRAIL:
                        trails[i] = trails[i][-MAX_TRAIL:]
                step += 1

        screen.blit(arena_surf, (0, 0))
        for ts in trail_surfs:
            screen.blit(ts, (0, 0))
        for robot, ctrl, color in sims:
            draw_robot(screen, robot, ctrl, color)

        draw_panel(screen, font, step, sims, paused)
        draw_legend(screen, font)

        if show_welcome:
            welcome_timer -= 1
            if welcome_timer <= 0:
                show_welcome = False
            ov = pygame.Surface((SCREEN_SIZE, 120), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 175))
            screen.blit(ov, (0, SCREEN_SIZE // 2 - 60))
            t1 = big.render("Task 2 — 4 Robots simultaneously", True, (0, 220, 255))
            t2 = font.render("Each colour = one robot with its own sensor rays", True, TEXT_COL)
            t3 = font.render("SPACE=Pause  R=Reset  ESC=Quit", True, (180, 180, 180))
            for k, t in enumerate([t1, t2, t3]):
                screen.blit(t, (SCREEN_SIZE//2 - t.get_width()//2,
                                SCREEN_SIZE//2 - 48 + k * 28))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    main()
