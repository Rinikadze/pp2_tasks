"""
Snake Game – Extended (Practice 8 Extra Tasks)
===============================================
Extra features:
  1. Weighted random food generation – rarer food = more points
  2. Food disappears after a timer (colour fades to warn the player)
  3. Full code comments
 
Colour → value legend:
  GREEN      +5   (common,   weight 40)
  YELLOW     +10  (common,   weight 30)
  ORANGE     +20  (uncommon, weight 15)
  CYAN       +30  (rare,     weight 10)
  BLUE       +50  (very rare,weight  4)
  PURPLE     -10  (trap,     weight  1) – also shrinks the snake
"""
 
import pygame
import random
import sys
 
pygame.init()
 
# ── Screen / grid constants ───────────────────────────────────────────────────
SCREEN_WIDTH  = 800
SCREEN_HEIGHT = 600
GRID_SIZE     = 20
GRID_WIDTH    = SCREEN_WIDTH  // GRID_SIZE   # number of columns
GRID_HEIGHT   = SCREEN_HEIGHT // GRID_SIZE   # number of rows
 
# ── Colour palette ────────────────────────────────────────────────────────────
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
RED        = (255, 0,   0)
GREEN      = (0,   255, 0)
DARK_GREEN = (0,   100, 0)
BLUE       = (0,   0,   255)
YELLOW     = (255, 255, 0)
PURPLE     = (255, 0,   255)
CYAN       = (0,   255, 255)
ORANGE     = (255, 165, 0)
LIGHT_BLUE = (100, 200, 255)
 
# ── Movement direction vectors ────────────────────────────────────────────────
UP    = (0,  -1)
DOWN  = (0,   1)
LEFT  = (-1,  0)
RIGHT = (1,   0)
 
# ── Food tier definitions (Task 1 & 3) ───────────────────────────────────────
# Each tier: colour shown on screen, score delta, spawn weight, lifetime (ms).
# Higher weight = appears more often.  Shorter lifetime = more pressure.
FOOD_TIERS = [
    {"color": GREEN,  "value": +5,  "weight": 40, "lifetime": 10_000},  # common
    {"color": YELLOW, "value": +10, "weight": 30, "lifetime":  8_000},  # common
    {"color": ORANGE, "value": +20, "weight": 15, "lifetime":  6_000},  # uncommon
    {"color": CYAN,   "value": +30, "weight": 10, "lifetime":  5_000},  # rare
    {"color": BLUE,   "value": +50, "weight":  4, "lifetime":  4_000},  # very rare
    {"color": PURPLE, "value": -10, "weight":  1, "lifetime": 12_000},  # trap (long)
]
# Pre-extract weights so random.choices() can use them directly
FOOD_WEIGHTS = [t["weight"] for t in FOOD_TIERS]
 
# ── Display setup ─────────────────────────────────────────────────────────────
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Game – Extended")
clock = pygame.time.Clock()
 
font     = pygame.font.Font(None, 36)
big_font = pygame.font.Font(None, 72)
 
 
# ─────────────────────────────────────────────────────────────────────────────
# Snake
# ─────────────────────────────────────────────────────────────────────────────
class Snake:
    """Player-controlled snake."""
 
    def __init__(self):
        # Start with 3 segments in the middle of the screen, moving right
        cx = GRID_WIDTH  // 2 * GRID_SIZE
        cy = GRID_HEIGHT // 2 * GRID_SIZE
        self.positions = [
            [cx,              cy],
            [cx - GRID_SIZE,  cy],
            [cx - 2*GRID_SIZE, cy],
        ]
        self.direction  = RIGHT
        self.grow_flag  = False       # set to True when the snake should grow
        self.color      = GREEN
        self.head_color = (0, 200, 0)
 
    def move(self):
        """Advance the snake by one step in the current direction."""
        head = self.positions[0].copy()
        head[0] += self.direction[0] * GRID_SIZE
        head[1] += self.direction[1] * GRID_SIZE
 
        self.positions.insert(0, head)      # prepend new head
 
        if not self.grow_flag:
            self.positions.pop()            # remove tail (normal move)
        else:
            self.grow_flag = False          # tail kept → snake is 1 longer
 
    def change_direction(self, new_dir):
        """
        Change direction, but prevent reversing directly into the snake's body.
        """
        if (new_dir[0] != -self.direction[0] or
                new_dir[1] != -self.direction[1]):
            self.direction = new_dir
 
    def grow(self):
        """Schedule growth on the next move."""
        self.grow_flag = True
 
    def shrink(self):
        """Remove the last segment (used by purple trap food)."""
        if len(self.positions) > 1:
            self.positions.pop()
 
    def check_self_collision(self):
        """Return True if the head overlaps any body segment."""
        return self.positions[0] in self.positions[1:]
 
    def check_border_collision(self):
        """Return True if the head has gone outside the screen."""
        hx, hy = self.positions[0]
        return hx < 0 or hx >= SCREEN_WIDTH or hy < 0 or hy >= SCREEN_HEIGHT
 
    def check_wall_collision(self, walls):
        """Return True if the head is inside a wall block."""
        return self.positions[0] in walls.positions
 
    def draw(self, surface):
        """Draw each segment; the head gets a distinct colour and white border."""
        for i, pos in enumerate(self.positions):
            color  = self.head_color if i == 0 else self.color
            border = WHITE if i == 0 else BLACK
            pygame.draw.rect(surface, color,
                             (pos[0], pos[1], GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, border,
                             (pos[0], pos[1], GRID_SIZE, GRID_SIZE), 2 if i == 0 else 1)
 
 
# ─────────────────────────────────────────────────────────────────────────────
# Food  (Tasks 1, 2, 3)
# ─────────────────────────────────────────────────────────────────────────────
class Food:
    """
    A single food item with a randomly chosen tier.
 
    Task 1 – Weighted random generation
    ────────────────────────────────────
    Tiers are selected via random.choices() with FOOD_WEIGHTS.
    Rarer tiers award more points but appear less frequently.
 
    Task 2 – Disappearing timer
    ───────────────────────────
    Every tier has a lifetime (milliseconds).  Once elapsed the food
    automatically respawns as a new randomly chosen tier.
    As the food ages, a white progress bar above it shrinks to zero,
    giving the player a clear visual countdown.
 
    Task 3 – Colour = value
    ───────────────────────
    See the module docstring colour legend at the top of the file.
    """
 
    def __init__(self, snake_positions, walls_positions=None):
        self.position       = [0, 0]
        self.tier           = None    # current FOOD_TIERS entry
        self.color          = GREEN
        self.value          = 0
        self.lifetime       = 10_000  # ms before auto-respawn
        self.spawn_time     = 0
        self._respawn(snake_positions, walls_positions or [])
 
    # ── Internal helpers ──────────────────────────────────────────────────────
 
    def _pick_tier(self):
        """Select a random tier using weighted probabilities (Task 1)."""
        self.tier     = random.choices(FOOD_TIERS, weights=FOOD_WEIGHTS, k=1)[0]
        self.color    = self.tier["color"]
        self.value    = self.tier["value"]
        self.lifetime = self.tier["lifetime"]
 
    def _respawn(self, snake_positions, walls_positions):
        """Find an empty cell, pick a new tier, and reset the timer."""
        self._pick_tier()
        while True:
            x = random.randint(0, GRID_WIDTH  - 1) * GRID_SIZE
            y = random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE
            if [x, y] not in snake_positions and [x, y] not in walls_positions:
                self.position   = [x, y]
                self.spawn_time = pygame.time.get_ticks()
                break
 
    def respawn(self, snake_positions, walls_positions=None):
        """Public wrapper so external code can force a respawn."""
        self._respawn(snake_positions, walls_positions or [])
 
    # ── Per-frame update (Task 2) ─────────────────────────────────────────────
 
    def update(self, snake_positions, walls_positions):
        """
        Check the timer each frame.
        Returns True if the food expired and was auto-respawned, else False.
        """
        elapsed = pygame.time.get_ticks() - self.spawn_time
        if elapsed >= self.lifetime:
            self._respawn(snake_positions, walls_positions)
            return True   # caller can react if needed
        return False
 
    def time_fraction(self):
        """Return how much lifetime remains as a 0.0–1.0 fraction."""
        elapsed = pygame.time.get_ticks() - self.spawn_time
        return max(0.0, 1.0 - elapsed / self.lifetime)
 
    # ── Drawing ───────────────────────────────────────────────────────────────
 
    def draw(self, surface):
        """
        Draw the food square and a shrinking timer bar above it.
        The bar is coloured the same as the food so it's easy to read at a glance.
        """
        fx, fy = self.position
 
        # Food square
        pygame.draw.rect(surface, self.color,
                         (fx, fy, GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(surface, WHITE,
                         (fx, fy, GRID_SIZE, GRID_SIZE), 2)
 
        # Timer bar (Task 2 visual): sits 4 px above the food square
        bar_w = int(GRID_SIZE * self.time_fraction())
        if bar_w > 0:
            pygame.draw.rect(surface, self.color,
                             (fx, fy - 5, bar_w, 3))
 
 
# ─────────────────────────────────────────────────────────────────────────────
# Walls
# ─────────────────────────────────────────────────────────────────────────────
class Walls:
    """Obstacle blocks that accumulate as the level rises."""
 
    def __init__(self):
        self.positions = []  # list of [x, y] pixel coordinates
 
    def generate(self, level):
        """
        Add new wall blocks based on the current level.
        Even levels add an L-shaped cluster; odd levels (≥3) add single blocks.
        """
        if level < 2:
            return  # no walls on level 1
 
        if level % 2 == 0:
            # Place an L-shaped wall in a random corner orientation
            base_x = random.randint(3, GRID_WIDTH  - 8) * GRID_SIZE
            base_y = random.randint(3, GRID_HEIGHT - 8) * GRID_SIZE
            shape  = random.choice([0, 1, 2, 3])
            new_blocks = []
 
            if shape == 0:    # └  (right + down)
                for i in range(5): new_blocks.append([base_x,            base_y + i * GRID_SIZE])
                for i in range(5): new_blocks.append([base_x + i * GRID_SIZE, base_y])
            elif shape == 1:  # ┘  (left + down)
                for i in range(5): new_blocks.append([base_x,            base_y + i * GRID_SIZE])
                for i in range(5): new_blocks.append([base_x - i * GRID_SIZE, base_y])
            elif shape == 2:  # ┌  (right + up)
                for i in range(5): new_blocks.append([base_x,            base_y - i * GRID_SIZE])
                for i in range(5): new_blocks.append([base_x + i * GRID_SIZE, base_y])
            else:             # ┐  (left + up)
                for i in range(5): new_blocks.append([base_x,            base_y - i * GRID_SIZE])
                for i in range(5): new_blocks.append([base_x - i * GRID_SIZE, base_y])
 
            for block in new_blocks:
                if block not in self.positions:
                    self.positions.append(block)
 
        else:
            # Scatter 3 individual blocks
            for _ in range(3):
                x = random.randint(0, GRID_WIDTH  - 1) * GRID_SIZE
                y = random.randint(0, GRID_HEIGHT - 1) * GRID_SIZE
                if [x, y] not in self.positions:
                    self.positions.append([x, y])
 
    def draw(self, surface):
        for pos in self.positions:
            pygame.draw.rect(surface, LIGHT_BLUE,
                             (pos[0], pos[1], GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, WHITE,
                             (pos[0], pos[1], GRID_SIZE, GRID_SIZE), 1)
 
 
# ─────────────────────────────────────────────────────────────────────────────
# Legend overlay  (Task 3)
# ─────────────────────────────────────────────────────────────────────────────
def draw_legend(surface):
    """
    Draw a small colour-coded legend in the top-right corner so the player
    always knows what each food colour is worth.
    """
    legend_font = pygame.font.Font(None, 22)
    x0  = SCREEN_WIDTH - 145
    y0  = 10
    pad = 22
 
    title = legend_font.render("Food values:", True, WHITE)
    surface.blit(title, (x0, y0))
 
    for i, tier in enumerate(FOOD_TIERS):
        y = y0 + pad * (i + 1)
        # Colour swatch
        pygame.draw.rect(surface, tier["color"], (x0, y + 2, 14, 14))
        pygame.draw.rect(surface, WHITE,          (x0, y + 2, 14, 14), 1)
        # Value label
        sign  = "+" if tier["value"] > 0 else ""
        label = legend_font.render(f"{sign}{tier['value']} pts", True, tier["color"])
        surface.blit(label, (x0 + 20, y))
 
 
# ─────────────────────────────────────────────────────────────────────────────
# Game Over screen
# ─────────────────────────────────────────────────────────────────────────────
def show_game_over(surface, score, level):
    """Render the game-over screen; input is handled in the main loop."""
    surface.fill(BLACK)
 
    def cx(surf):
        return SCREEN_WIDTH // 2 - surf.get_width() // 2
 
    over_s    = big_font.render("GAME OVER",             True, RED)
    score_s   = font.render(f"Final Score: {score}",     True, WHITE)
    level_s   = font.render(f"Level Reached: {level}",  True, YELLOW)
    restart_s = font.render("Press SPACE to restart",    True, GREEN)
    quit_s    = font.render("Press ESC to quit",         True, GREEN)
 
    surface.blit(over_s,    (cx(over_s),    150))
    surface.blit(score_s,   (cx(score_s),   260))
    surface.blit(level_s,   (cx(level_s),   300))
    surface.blit(restart_s, (cx(restart_s), 400))
    surface.blit(quit_s,    (cx(quit_s),    450))
 
    pygame.display.flip()
 
 
# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
def main():
    # ── Initial game state ────────────────────────────────────────────────────
    snake = Snake()
    walls = Walls()
 
    score          = 0
    level          = 1
    foods_eaten    = 0
    FOODS_PER_LEVEL = 3
    base_speed     = 10
    current_speed  = base_speed
 
    walls.generate(level)
    food = Food(snake.positions, walls.positions)
 
    running     = True
    game_active = True
 
    # ── Main loop ─────────────────────────────────────────────────────────────
    while running:
        clock.tick(current_speed)
 
        # ── Event handling ────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
 
            if event.type == pygame.KEYDOWN:
                if game_active:
                    # Direction controls (arrow keys + WASD)
                    if   event.key in (pygame.K_UP,    pygame.K_w): snake.change_direction(UP)
                    elif event.key in (pygame.K_DOWN,  pygame.K_s): snake.change_direction(DOWN)
                    elif event.key in (pygame.K_LEFT,  pygame.K_a): snake.change_direction(LEFT)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d): snake.change_direction(RIGHT)
                    elif event.key == pygame.K_ESCAPE: running = False
                    # F – manual food respawn (debug / stuck food fix)
                    elif event.key == pygame.K_f:
                        food.respawn(snake.positions, walls.positions)
                else:
                    # Game-over screen controls
                    if event.key == pygame.K_SPACE:
                        # Full reset
                        score         = 0
                        level         = 1
                        foods_eaten   = 0
                        current_speed = base_speed
 
                        snake = Snake()
                        walls = Walls()
                        walls.generate(level)
                        food  = Food(snake.positions, walls.positions)
 
                        game_active = True
                    elif event.key == pygame.K_ESCAPE:
                        running = False
 
        # ── Game logic ────────────────────────────────────────────────────────
        if game_active:
            snake.move()
 
            # Task 2 – auto-respawn expired food
            food.update(snake.positions, walls.positions)
 
            # Collision checks → game over
            if (snake.check_border_collision() or
                    snake.check_self_collision() or
                    snake.check_wall_collision(walls)):
                game_active = False
                continue
 
            # ── Food collection ───────────────────────────────────────────────
            if snake.positions[0] == food.position:
                value = food.value   # store before respawn changes it
 
                if value < 0:
                    # Trap food (purple): shrink snake, deduct points
                    if len(snake.positions) <= 3:
                        # Snake too short to survive the shrink → game over
                        game_active = False
                        continue
                    snake.shrink()
                    score += value   # value is negative
                else:
                    # Normal food: grow snake, add points, track progress
                    snake.grow()
                    score       += value
                    foods_eaten += 1
 
                    # Level-up when enough food has been eaten
                    if foods_eaten >= FOODS_PER_LEVEL:
                        level        += 1
                        foods_eaten   = 0
                        current_speed = base_speed + level * 2   # get faster each level
                        walls.generate(level)
 
                # Respawn food after collection (regardless of tier)
                food.respawn(snake.positions, walls.positions)
 
            # ── Drawing ───────────────────────────────────────────────────────
            screen.fill(BLACK)
 
            # Subtle grid lines for readability
            for x in range(0, SCREEN_WIDTH,  GRID_SIZE):
                pygame.draw.line(screen, (20, 20, 20), (x, 0), (x, SCREEN_HEIGHT))
            for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
                pygame.draw.line(screen, (20, 20, 20), (0, y), (SCREEN_WIDTH, y))
 
            walls.draw(screen)
            food.draw(screen)    # food drawn before snake so head is always on top
            snake.draw(screen)
 
            # HUD – top-left
            screen.blit(font.render(f"Score: {score}",              True, WHITE),  (10, 10))
            screen.blit(font.render(f"Level: {level}",              True, YELLOW), (10, 50))
            screen.blit(font.render(f"Speed: {current_speed}",      True, CYAN),   (10, 90))
            screen.blit(font.render(
                f"Next Level: {foods_eaten}/{FOODS_PER_LEVEL}",      True, PURPLE), (10, 130))
 
            # Task 3 – colour legend (top-right)
            draw_legend(screen)
 
        else:
            show_game_over(screen, score, level)
 
        pygame.display.flip()
 
    pygame.quit()
    sys.exit()
 
 
if __name__ == "__main__":
    main()