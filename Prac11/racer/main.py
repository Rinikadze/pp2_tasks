import pygame
import sys
from pygame.locals import *
import random
import time

pygame.init()

FPS = 60
FramePerSec = pygame.time.Clock()

BLUE   = (0,   0,   255)
RED    = (255, 0,   0)
GREEN  = (0,   255, 0)
BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
YELLOW = (255, 255, 0)
GRAY   = (128, 128, 128)

SCREEN_WIDTH  = 400
SCREEN_HEIGHT = 600
BASE_SPEED    = 5          # starting fall-speed for enemies & coins
SPEED         = BASE_SPEED # mutable copy used during play

# --- Coin progression: enemy gets faster every N coins ---
COINS_PER_SPEED_BOOST = 3   # collect this many coins → enemy speeds up
ENEMY_BOOST_AMOUNT    = 0.5 # how much SPEED increases per boost
MAX_SPEED             = 12  # absolute speed cap

# --- Score / collection counters (global, reset on restart) ---
SCORE           = 0
COINS_COLLECTED = 0          # total coins grabbed this run
NEXT_BOOST_AT   = COINS_PER_SPEED_BOOST  # milestone for next enemy boost

# --- Font setup ---
font        = pygame.font.SysFont("Verdana", 60)
font_small  = pygame.font.SysFont("Verdana", 20)
font_medium = pygame.font.SysFont("Verdana", 30)


# ── Helper: safe image loader ─────────────────────────────────────────────────
def load_image(filename, default_color=None, width=None, height=None):
    import os
    try:
        path = os.path.join("images", filename)
        img  = pygame.image.load(path if os.path.exists(path) else filename)
        if width and height:
            img = pygame.transform.scale(img, (width, height))
        return img
    except Exception:
        print(f"Warning: could not load '{filename}' – using placeholder.")
        size = (width or 50, height or 50)
        surf = pygame.Surface(size)
        surf.fill(default_color or GRAY)
        return surf


# --- Load / create game assets ---
background = load_image("AnimatedStreet.png", GRAY,  SCREEN_WIDTH, SCREEN_HEIGHT)
player_img = load_image("Player.png",         BLUE,  50, 80)
enemy_img  = load_image("Enemy.png",          RED,   50, 80)

# Load the single coin sprite, then scale it to three different sizes for each tier.
# Small = common (Bronze), Medium = uncommon (Silver), Large = rare (Gold).
_coin_base      = load_image("coin.png", YELLOW, 30, 30)  # base load at any size
coin_bronze_img = pygame.transform.scale(_coin_base, (20, 20))  # small  – Bronze
coin_silver_img = pygame.transform.scale(_coin_base, (30, 30))  # medium – Silver
coin_gold_img   = pygame.transform.scale(_coin_base, (42, 42))  # large  – Gold

# --- Create the main display surface ---
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Street Racer – Extended")


# ── Coin tier definitions ────────────────────────────────────────────────────
# All tiers use the same coin.png sprite – only the size differs.
# Weights are used with random.choices() – higher weight = more common.
COIN_TIERS = [
    {"name": "Bronze", "image": coin_bronze_img, "value": 1,  "weight": 60},  # small  (20×20)
    {"name": "Silver", "image": coin_silver_img, "value": 3,  "weight": 30},  # medium (30×30)
    {"name": "Gold",   "image": coin_gold_img,   "value": 10, "weight": 10},  # large  (42×42)
]
# Pre-compute the weight list once so random.choices() can reuse it
COIN_WEIGHTS = [t["weight"] for t in COIN_TIERS]


# ── Sprite classes ─────────────────────────────────────────────────────────────

class Player(pygame.sprite.Sprite):
    """The player-controlled car at the bottom of the screen."""

    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect  = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80)
        self.move_speed = 7  # horizontal pixels per frame

    def move(self):
        """Read keyboard input and translate the car left / right within bounds."""
        keys = pygame.key.get_pressed()

        # Left arrow or A → move left, but not past the screen edge
        if (keys[K_LEFT] or keys[K_a]) and self.rect.left > 0:
            self.rect.move_ip(-self.move_speed, 0)

        # Right arrow or D → move right, but not past the screen edge
        if (keys[K_RIGHT] or keys[K_d]) and self.rect.right < SCREEN_WIDTH:
            self.rect.move_ip(self.move_speed, 0)

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Enemy(pygame.sprite.Sprite):
    """Oncoming traffic car that falls from the top of the screen."""

    def __init__(self):
        super().__init__()
        self.image = enemy_img
        self.rect  = self.image.get_rect()
        self.reset_position()

    def reset_position(self):
        """Teleport the enemy to a random horizontal position at the top."""
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), 0)

    def move(self):
        """
        Move the enemy downward by the current global SPEED.
        Award 1 point and recycle the enemy when it exits the bottom.
        """
        global SCORE
        self.rect.move_ip(0, SPEED)

        if self.rect.top > SCREEN_HEIGHT:
            SCORE += 1          # player successfully dodged this car
            self.reset_position()

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.active        = False   # coins start hidden; activated by a timer
        self.delay_counter = 0
        self.spawn_delay   = random.randint(60, 180)  # frames before first spawn

        # Pick an initial tier and apply it
        self._pick_tier()
        self._place_at_top()

    # ── Tier helpers ──────────────────────────────────────────────────────────

    def _pick_tier(self):
        """
        Randomly select a coin tier using weighted probabilities.
        Updates self.tier_data, self.image, and self.value.
        """
        # random.choices returns a 1-element list; [0] unpacks it
        self.tier_data = random.choices(COIN_TIERS, weights=COIN_WEIGHTS, k=1)[0]
        self.image     = self.tier_data["image"]
        self.value     = self.tier_data["value"]   # score bonus on collection

        # Keep the rect consistent with the (possibly new) image size
        centre = getattr(self, "rect", None)
        self.rect = self.image.get_rect()
        if centre:
            self.rect.center = centre.center

    def _place_at_top(self):
        """Position the coin off-screen at a random x coordinate."""
        self.rect.center = (
            random.randint(30, SCREEN_WIDTH - 30),
            random.randint(-400, -80),   # well above the visible area
        )

    # ── Per-frame update ──────────────────────────────────────────────────────

    def activate(self):
        """
        Pick a fresh random tier, place the coin, and mark it visible.
        Called when the spawn timer fires.
        """
        self._pick_tier()
        self._place_at_top()
        self.active = True

    def move(self):
        """
        Manage the spawn-delay timer and the downward movement.
        Coins fall at half the enemy speed so they are easier to collect.
        """
        if not self.active:
            # Count down until the next spawn
            self.delay_counter += 1
            if self.delay_counter >= self.spawn_delay:
                self.activate()
                self.delay_counter = 0
                # Randomise the delay for the *next* spawn after this one exits
                self.spawn_delay = random.randint(120, 300)
            return

        # Fall downward at half speed
        self.rect.move_ip(0, max(1, SPEED // 2))

        # Recycle off-screen coins
        if self.rect.top > SCREEN_HEIGHT:
            self.active = False

    def draw(self, surface):
        """Only render when the coin is in play."""
        if self.active:
            surface.blit(self.image, self.rect)


# ── Game-state helpers ─────────────────────────────────────────────────────────

def check_coin_boost():
    global SPEED, NEXT_BOOST_AT
    if COINS_COLLECTED >= NEXT_BOOST_AT:
        SPEED = min(SPEED + ENEMY_BOOST_AMOUNT, MAX_SPEED)
        NEXT_BOOST_AT += COINS_PER_SPEED_BOOST
        print(f"[BOOST] Speed → {SPEED:.1f}  (next boost at {NEXT_BOOST_AT} coins)")


def show_game_over(score, coins):
    """Render the Game Over screen and wait for player input."""
    DISPLAYSURF.fill(RED)

    # Build text surfaces
    over_surf    = font.render("GAME OVER", True, BLACK)
    score_surf   = font_medium.render(f"Score: {score}", True, WHITE)
    coins_surf   = font_medium.render(f"Coins: {coins}", True, YELLOW)
    restart_surf = font_small.render("SPACE – restart", True, GREEN)
    quit_surf    = font_small.render("ESC   – quit",    True, GREEN)

    # Centre each surface horizontally
    def cx(surf):
        return SCREEN_WIDTH // 2 - surf.get_width() // 2

    DISPLAYSURF.blit(over_surf,    (cx(over_surf),    150))
    DISPLAYSURF.blit(score_surf,   (cx(score_surf),   260))
    DISPLAYSURF.blit(coins_surf,   (cx(coins_surf),   300))
    DISPLAYSURF.blit(restart_surf, (cx(restart_surf), 400))
    DISPLAYSURF.blit(quit_surf,    (cx(quit_surf),    435))

    pygame.display.update()


def reset_game():
    """Reset all mutable game state so a new run can begin cleanly."""
    global SCORE, COINS_COLLECTED, SPEED, NEXT_BOOST_AT

    SCORE           = 0
    COINS_COLLECTED = 0
    SPEED           = BASE_SPEED
    NEXT_BOOST_AT   = COINS_PER_SPEED_BOOST

    # Return player to centre-bottom
    P1.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80)

    # Put the enemy back at the top
    E1.reset_position()

    # Deactivate all coins and reset their timers
    for coin in coins:
        coin.active        = False
        coin.delay_counter = 0
        coin.spawn_delay   = random.randint(60, 180)


# ── Sprite initialisation ──────────────────────────────────────────────────────

P1 = Player()
E1 = Enemy()

# Sprite groups make collision detection and drawing easier
enemies = pygame.sprite.Group()
enemies.add(E1)

coins = pygame.sprite.Group()
coin1 = Coin()   # only one coin on screen at a time (keeps the game fair)
coins.add(coin1)

all_sprites = pygame.sprite.Group()
all_sprites.add(P1, E1, coin1)

# ── Custom timer event: gradual speed increase over time ──────────────────────
INC_SPEED = pygame.USEREVENT + 1
pygame.time.set_timer(INC_SPEED, 5000)  # fires every 5 seconds

# ── Game-state constants ───────────────────────────────────────────────────────
PLAYING   = 0
GAME_OVER = 1
game_state = PLAYING

# ── Background scrolling state ─────────────────────────────────────────────────
bg_y          = 0
bg_scroll_spd = 2   # pixels per frame the background scrolls downward



while True:

    # ── 1. Event processing ───────────────────────────────────────────────────
    for event in pygame.event.get():

        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if game_state == PLAYING:
            # Periodic speed ramp-up (time-based, separate from coin boosts)
            if event.type == INC_SPEED:
                SPEED = min(SPEED + 0.2, MAX_SPEED)

        elif game_state == GAME_OVER:
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    reset_game()
                    game_state = PLAYING
                elif event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()

    # ── 2. Update & draw (only while playing) ─────────────────────────────────
    if game_state == PLAYING:

        # Scroll background: tile two copies so the seam is never visible
        bg_y = (bg_y + bg_scroll_spd) % SCREEN_HEIGHT
        DISPLAYSURF.blit(background, (0, bg_y - SCREEN_HEIGHT))
        DISPLAYSURF.blit(background, (0, bg_y))

        # Move all sprites
        P1.move()
        E1.move()
        for coin in coins:
            coin.move()

        # ── Coin collision ──────────────────────────────────────────────────
        for coin in coins:
            if coin.active and P1.rect.colliderect(coin.rect):
                # Award points based on the coin's tier value
                SCORE           += coin.value
                COINS_COLLECTED += 1

                # Extra Task 2: check whether a speed boost is due
                check_coin_boost()

                # Deactivate so the coin respawns after a delay
                coin.active = False

        # ── Enemy collision → game over ─────────────────────────────────────
        if P1.rect.colliderect(E1.rect):
            time.sleep(0.4)          # brief freeze so the crash feels impactful
            game_state = GAME_OVER

        # ── Redraw scene (background first, then sprites on top) ────────────
        DISPLAYSURF.blit(background, (0, bg_y - SCREEN_HEIGHT))
        DISPLAYSURF.blit(background, (0, bg_y))

        P1.draw(DISPLAYSURF)
        E1.draw(DISPLAYSURF)
        for coin in coins:
            coin.draw(DISPLAYSURF)

        # ── HUD ─────────────────────────────────────────────────────────────
        score_surf  = font_small.render(f"Score:  {SCORE}",          True, BLACK)
        coins_surf  = font_small.render(f"Coins:  {COINS_COLLECTED}", True, BLACK)
        speed_surf  = font_small.render(f"Speed:  {SPEED:.1f}",       True,
                                         RED if SPEED > 7 else BLACK)
        # Panel behind the HUD text (3 lines: Score, Coins, Speed)
        pygame.draw.rect(DISPLAYSURF, WHITE, (5, 5, 160, 73))
        pygame.draw.rect(DISPLAYSURF, BLACK, (5, 5, 160, 73), 2)

        DISPLAYSURF.blit(score_surf,  (10, 10))
        DISPLAYSURF.blit(coins_surf,  (10, 32))
        DISPLAYSURF.blit(speed_surf,  (10, 54))

    # ── 3. Game Over screen ───────────────────────────────────────────────────
    else:
        show_game_over(SCORE, COINS_COLLECTED)

    # ── 4. Flip display & tick clock ─────────────────────────────────────────
    pygame.display.update()
    FramePerSec.tick(FPS)