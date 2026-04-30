"""
game.py – Snake, Food, PoisonFood, PowerUp, Obstacles, Walls
"""

import pygame
import random

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE, GRID_WIDTH, GRID_HEIGHT,
    BLACK, WHITE, RED, GREEN, DARK_GREEN, YELLOW, PURPLE, CYAN,
    ORANGE, LIGHT_BLUE, DARK_RED, GOLD, PINK, GRAY, TEAL,
    UP, DOWN, LEFT, RIGHT,
    POWERUP_FIELD_DURATION, POWERUP_EFFECT_DURATION,
    OBSTACLE_START_LEVEL,
)


# ──────────────────────────────────────────────────────────────────────────────
# Snake
# ──────────────────────────────────────────────────────────────────────────────
class Snake:
    def __init__(self, color=None):
        cx = GRID_WIDTH  // 2 * GRID_SIZE
        cy = GRID_HEIGHT // 2 * GRID_SIZE
        self.positions = [
            [cx,                cy],
            [cx - GRID_SIZE,    cy],
            [cx - 2 * GRID_SIZE, cy],
        ]
        self.direction  = RIGHT
        self.grow_flag  = False
        self.color      = list(color) if color else [0, 255, 0]
        self.head_color = (
            min(255, self.color[0] + 50),
            min(255, self.color[1] + 50),
            min(255, self.color[2] + 50),
        )

    # ── movement ──────────────────────────────────────────────────────────────
    def move(self):
        head = self.positions[0].copy()
        head[0] += self.direction[0] * GRID_SIZE
        head[1] += self.direction[1] * GRID_SIZE
        self.positions.insert(0, head)
        if not self.grow_flag:
            self.positions.pop()
        else:
            self.grow_flag = False

    def change_direction(self, new_dir):
        if (new_dir[0] != -self.direction[0] or
                new_dir[1] != -self.direction[1]):
            self.direction = new_dir

    def grow(self):
        self.grow_flag = True

    def shorten(self, amount=2):
        """Remove 'amount' tail segments. Returns True if still alive."""
        for _ in range(amount):
            if len(self.positions) > 1:
                self.positions.pop()
        return len(self.positions) > 1

    # ── collision helpers ─────────────────────────────────────────────────────
    def check_self_collision(self):
        return self.positions[0] in self.positions[1:]

    def check_border_collision(self):
        h = self.positions[0]
        return h[0] < 0 or h[0] >= SCREEN_WIDTH or h[1] < 0 or h[1] >= SCREEN_HEIGHT

    def check_wall_collision(self, obstacle_positions):
        return self.positions[0] in obstacle_positions

    # ── drawing ───────────────────────────────────────────────────────────────
    def draw(self, surface):
        for i, pos in enumerate(self.positions):
            color = self.head_color if i == 0 else self.color
            border = WHITE if i == 0 else BLACK
            pygame.draw.rect(surface, color,
                             (pos[0], pos[1], GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, border,
                             (pos[0], pos[1], GRID_SIZE, GRID_SIZE), 2 if i == 0 else 1)


# ──────────────────────────────────────────────────────────────────────────────
# Food (weighted / disappearing)
# ──────────────────────────────────────────────────────────────────────────────
FOOD_TYPES = [
    {"color": RED,        "points": 10,  "weight": 50},   # normal
    {"color": ORANGE,     "points": 20,  "weight": 25},   # bonus
    {"color": YELLOW,     "points": 15,  "weight": 15},   # medium
    {"color": DARK_GREEN, "points": 30,  "weight": 7},    # rare
    {"color": CYAN,       "points": 25,  "weight": 3},    # ultra-rare
]

class Food:
    LIFESPAN = 10_000   # ms before auto-respawn

    def __init__(self, snake_positions, blocked=None):
        self._blocked = blocked or []
        self._pick_type()
        self.position  = [0, 0]
        self.spawn_time = 0
        self.respawn(snake_positions, self._blocked)

    def _pick_type(self):
        total  = sum(t["weight"] for t in FOOD_TYPES)
        r      = random.randint(1, total)
        cumul  = 0
        for t in FOOD_TYPES:
            cumul += t["weight"]
            if r <= cumul:
                self.color  = t["color"]
                self.points = t["points"]
                return
        self.color  = RED
        self.points = 10

    def respawn(self, snake_positions, blocked=None):
        blocked = blocked or []
        while True:
            x = random.randint(0, GRID_WIDTH  - 1) * GRID_SIZE
            y = random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            if [x, y] not in snake_positions and [x, y] not in blocked:
                self.position   = [x, y]
                self.spawn_time = pygame.time.get_ticks()
                self._pick_type()
                return

    def update(self, snake_positions, blocked=None):
        """Returns remaining ms. 0 means it just respawned."""
        elapsed = pygame.time.get_ticks() - self.spawn_time
        if elapsed > self.LIFESPAN:
            self.respawn(snake_positions, blocked or [])
            return 0
        return self.LIFESPAN - elapsed

    def draw(self, surface):
        pygame.draw.rect(surface, self.color,
                         (self.position[0], self.position[1], GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, WHITE,
                         (self.position[0], self.position[1], GRID_SIZE, GRID_SIZE), 2)
        # timer bar
        elapsed  = pygame.time.get_ticks() - self.spawn_time
        fraction = max(0, 1 - elapsed / self.LIFESPAN)
        bar_w    = int(GRID_SIZE * fraction)
        pygame.draw.rect(surface, YELLOW,
                         (self.position[0], self.position[1] + GRID_SIZE - 3,
                          bar_w, 3))


# ──────────────────────────────────────────────────────────────────────────────
# Poison Food
# ──────────────────────────────────────────────────────────────────────────────
class PoisonFood:
    LIFESPAN = 8_000

    def __init__(self, snake_positions, blocked=None):
        self.position   = [0, 0]
        self.spawn_time = 0
        self.active     = False
        self._blocked   = blocked or []
        self.spawn(snake_positions, blocked)

    def spawn(self, snake_positions, blocked=None):
        blocked = blocked or []
        while True:
            x = random.randint(0, GRID_WIDTH  - 1) * GRID_SIZE
            y = random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            if [x, y] not in snake_positions and [x, y] not in blocked:
                self.position   = [x, y]
                self.spawn_time = pygame.time.get_ticks()
                self.active     = True
                return

    def update(self, snake_positions, blocked=None):
        if not self.active:
            return
        if pygame.time.get_ticks() - self.spawn_time > self.LIFESPAN:
            self.active = False   # just disappears

    def draw(self, surface):
        if not self.active:
            return
        # Dark-red square with skull-like 'X'
        r = (self.position[0], self.position[1], GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(surface, DARK_RED, r)
        pygame.draw.rect(surface, WHITE, r, 2)
        # small X
        x0, y0 = self.position[0] + 4, self.position[1] + 4
        x1, y1 = self.position[0] + GRID_SIZE - 4, self.position[1] + GRID_SIZE - 4
        pygame.draw.line(surface, WHITE, (x0, y0), (x1, y1), 2)
        pygame.draw.line(surface, WHITE, (x1, y0), (x0, y1), 2)


# ──────────────────────────────────────────────────────────────────────────────
# Power-up
# ──────────────────────────────────────────────────────────────────────────────
POWERUP_DEFS = [
    {"kind": "speed_boost",  "color": GOLD,   "symbol": "▶"},
    {"kind": "slow_motion",  "color": TEAL,   "symbol": "◀"},
    {"kind": "shield",       "color": PINK,   "symbol": "★"},
]

class PowerUp:
    def __init__(self, snake_positions, blocked=None, food_positions=None):
        self.position    = [0, 0]
        self.kind        = None
        self.color       = WHITE
        self.symbol      = "?"
        self.spawn_time  = 0
        self.active      = False          # on the field
        self.effect_end  = 0              # when the effect expires (get_ticks)
        self._blocked    = blocked or []
        self._food       = food_positions or []
        self._respawn_cd = 0              # cooldown before next spawn attempt
        self.spawn(snake_positions, blocked, food_positions)

    def spawn(self, snake_positions, blocked=None, food_positions=None):
        blocked        = blocked or []
        food_positions = food_positions or []
        defn           = random.choice(POWERUP_DEFS)
        self.kind      = defn["kind"]
        self.color     = defn["color"]
        self.symbol    = defn["symbol"]
        while True:
            x = random.randint(0, GRID_WIDTH  - 1) * GRID_SIZE
            y = random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            if ([x, y] not in snake_positions and
                    [x, y] not in blocked and
                    [x, y] not in food_positions):
                self.position   = [x, y]
                self.spawn_time = pygame.time.get_ticks()
                self.active     = True
                return

    def update(self):
        if self.active:
            if pygame.time.get_ticks() - self.spawn_time > POWERUP_FIELD_DURATION:
                self.active = False

    def effect_active(self):
        return pygame.time.get_ticks() < self.effect_end

    def activate_effect(self):
        self.active     = False
        self.effect_end = pygame.time.get_ticks() + POWERUP_EFFECT_DURATION

    def draw(self, surface, font_small):
        if not self.active:
            return
        # Pulsing outline
        t     = pygame.time.get_ticks()
        alpha = abs((t % 1000) - 500) / 500   # 0..1..0
        r_off = int(alpha * 4)
        rx    = self.position[0] - r_off
        ry    = self.position[1] - r_off
        rw    = GRID_SIZE + 2 * r_off
        pygame.draw.rect(surface, self.color, (rx, ry, rw, rw))
        pygame.draw.rect(surface, WHITE, (rx, ry, rw, rw), 2)
        txt = font_small.render(self.symbol, True, BLACK)
        surface.blit(txt, (self.position[0] + 3, self.position[1] + 2))


# ──────────────────────────────────────────────────────────────────────────────
# Obstacles  (from Level OBSTACLE_START_LEVEL)
# ──────────────────────────────────────────────────────────────────────────────
class Obstacles:
    def __init__(self):
        self.positions = []   # list of [x, y]

    def _safe_for_snake(self, new_blocks, snake_positions):
        """Make sure none of the new blocks sit under the snake."""
        for b in new_blocks:
            if b in snake_positions:
                return False
        return True

    def generate(self, level, snake_positions):
        if level < OBSTACLE_START_LEVEL:
            return

        attempts = 0
        while attempts < 20:
            attempts += 1
            new_blocks = []
            shape = random.choice(["L", "J", "T", "line", "dot"])
            bx    = random.randint(3, GRID_WIDTH  - 8) * GRID_SIZE
            by    = random.randint(3, GRID_HEIGHT - 8) * GRID_SIZE

            if shape == "L":
                for i in range(5):
                    new_blocks.append([bx, by + i * GRID_SIZE])
                for i in range(4):
                    new_blocks.append([bx + (i + 1) * GRID_SIZE, by + 4 * GRID_SIZE])
            elif shape == "J":
                for i in range(5):
                    new_blocks.append([bx, by + i * GRID_SIZE])
                for i in range(4):
                    new_blocks.append([bx - (i + 1) * GRID_SIZE, by + 4 * GRID_SIZE])
            elif shape == "T":
                for i in range(5):
                    new_blocks.append([bx + i * GRID_SIZE, by])
                for i in range(3):
                    new_blocks.append([bx + 2 * GRID_SIZE, by + (i + 1) * GRID_SIZE])
            elif shape == "line":
                horizontal = random.choice([True, False])
                for i in range(6):
                    if horizontal:
                        new_blocks.append([bx + i * GRID_SIZE, by])
                    else:
                        new_blocks.append([bx, by + i * GRID_SIZE])
            else:  # dot
                for dx in range(2):
                    for dy in range(2):
                        new_blocks.append([bx + dx * GRID_SIZE, by + dy * GRID_SIZE])

            # Filter out out-of-bounds
            new_blocks = [
                b for b in new_blocks
                if 0 <= b[0] < SCREEN_WIDTH and 0 <= b[1] < SCREEN_HEIGHT
            ]

            if self._safe_for_snake(new_blocks, snake_positions):
                for b in new_blocks:
                    if b not in self.positions:
                        self.positions.append(b)
                return   # success

    def draw(self, surface):
        for pos in self.positions:
            pygame.draw.rect(surface, LIGHT_BLUE,
                             (pos[0], pos[1], GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, WHITE,
                             (pos[0], pos[1], GRID_SIZE, GRID_SIZE), 1)