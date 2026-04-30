"""
main.py – Snake Game TSIS 4
Screens: Main Menu → Game → Game Over → Leaderboard / Settings
"""

import pygame
import sys
import json
import random

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, GRID_SIZE, GRID_WIDTH, GRID_HEIGHT,
    BLACK, WHITE, RED, GREEN, YELLOW, CYAN, ORANGE, PURPLE,
    GRAY, DARK_GRAY, GOLD, PINK, TEAL, LIGHT_BLUE,
    UP, DOWN, LEFT, RIGHT,
    BASE_SPEED, FOODS_PER_LEVEL, OBSTACLE_START_LEVEL,
    POWERUP_EFFECT_DURATION,
)
from game import Snake, Food, PoisonFood, PowerUp, Obstacles
import db

# ── Init ──────────────────────────────────────────────────────────────────────
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Snake Game — TSIS 4")
clock = pygame.time.Clock()

font_big   = pygame.font.Font(None, 72)
font_med   = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 32)
font_tiny  = pygame.font.Font(None, 24)

SETTINGS_FILE = "settings.json"

# ── Settings helpers ──────────────────────────────────────────────────────────
def load_settings() -> dict:
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"snake_color": [0, 255, 0], "grid_overlay": True, "sound": False}

def save_settings(s: dict):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(s, f, indent=4)
    except Exception as e:
        print(f"[Settings] save error: {e}")

# ── Drawing helpers ───────────────────────────────────────────────────────────
def draw_text_center(surface, text, font, color, y):
    surf = font.render(text, True, color)
    surface.blit(surf, (SCREEN_WIDTH // 2 - surf.get_width() // 2, y))

def draw_button(surface, rect, text, font, bg, fg, border=WHITE):
    pygame.draw.rect(surface, bg, rect, border_radius=8)
    pygame.draw.rect(surface, border, rect, 2, border_radius=8)
    txt = font.render(text, True, fg)
    surface.blit(txt, (rect.centerx - txt.get_width() // 2,
                        rect.centery - txt.get_height() // 2))

def draw_gradient_bg(surface):
    for y in range(SCREEN_HEIGHT):
        c = int(10 + y * 20 / SCREEN_HEIGHT)
        pygame.draw.line(surface, (0, c, c // 3), (0, y), (SCREEN_WIDTH, y))

def draw_grid(surface):
    for x in range(0, SCREEN_WIDTH, GRID_SIZE):
        pygame.draw.line(surface, (20, 20, 20), (x, 0), (x, SCREEN_HEIGHT))
    for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
        pygame.draw.line(surface, (20, 20, 20), (0, y), (SCREEN_WIDTH, y))

# ── Username entry ─────────────────────────────────────────────────────────────
def username_screen() -> str:
    username = ""
    active   = True
    error    = ""
    while active:
        draw_gradient_bg(screen)
        draw_text_center(screen, "SNAKE GAME", font_big, GREEN, 80)
        draw_text_center(screen, "Enter your username:", font_med, WHITE, 200)

        # Input box
        box = pygame.Rect(200, 270, 400, 50)
        pygame.draw.rect(screen, DARK_GRAY, box, border_radius=6)
        pygame.draw.rect(screen, CYAN, box, 2, border_radius=6)
        txt = font_med.render(username + "|", True, WHITE)
        screen.blit(txt, (box.x + 10, box.y + 8))

        if error:
            draw_text_center(screen, error, font_small, RED, 340)

        draw_text_center(screen, "Press ENTER to continue", font_small, GRAY, 380)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if len(username.strip()) >= 2:
                        return username.strip()
                    else:
                        error = "Username must be at least 2 characters"
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif len(username) < 20 and event.unicode.isprintable():
                    username += event.unicode

        pygame.display.flip()
        clock.tick(30)

# ── Main Menu ─────────────────────────────────────────────────────────────────
def main_menu_screen() -> str:
    """Returns: 'play' | 'leaderboard' | 'settings' | 'quit'"""
    buttons = {
        "play":        pygame.Rect(300, 200, 200, 50),
        "leaderboard": pygame.Rect(300, 270, 200, 50),
        "settings":    pygame.Rect(300, 340, 200, 50),
        "quit":        pygame.Rect(300, 410, 200, 50),
    }
    labels = {
        "play":        "▶  Play",
        "leaderboard": "🏆 Leaderboard",
        "settings":    "⚙  Settings",
        "quit":        "✕  Quit",
    }
    colors = {
        "play":        GREEN,
        "leaderboard": GOLD,
        "settings":    CYAN,
        "quit":        RED,
    }
    while True:
        draw_gradient_bg(screen)
        draw_text_center(screen, "SNAKE", font_big, GREEN, 80)
        draw_text_center(screen, "G A M E", font_med, CYAN, 150)

        mx, my = pygame.mouse.get_pos()
        for key, rect in buttons.items():
            hover = rect.collidepoint(mx, my)
            draw_button(screen, rect, labels[key], font_small,
                        colors[key] if hover else DARK_GRAY, WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                for key, rect in buttons.items():
                    if rect.collidepoint(event.pos):
                        return key
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "quit"

        pygame.display.flip()
        clock.tick(30)

# ── Leaderboard Screen ────────────────────────────────────────────────────────
def leaderboard_screen():
    rows = db.get_top10()
    back_btn = pygame.Rect(330, 540, 140, 44)
    while True:
        draw_gradient_bg(screen)
        draw_text_center(screen, "LEADERBOARD", font_big, GOLD, 20)

        # Header
        headers = ["#", "Username", "Score", "Level", "Date"]
        col_x   = [30, 80, 280, 380, 460]
        for i, h in enumerate(headers):
            s = font_tiny.render(h, True, CYAN)
            screen.blit(s, (col_x[i], 110))
        pygame.draw.line(screen, GRAY, (20, 132), (780, 132), 1)

        for rank, row in enumerate(rows, 1):
            y   = 140 + rank * 36
            col = WHITE if rank % 2 == 0 else (220, 220, 220)
            date_str = str(row["played_at"])[:10] if row["played_at"] else "—"
            cells = [
                str(rank),
                str(row["username"])[:16],
                str(row["score"]),
                str(row["level_reached"]),
                date_str,
            ]
            for i, cell in enumerate(cells):
                s = font_small.render(cell, True, col)
                screen.blit(s, (col_x[i], y))

        if not rows:
            draw_text_center(screen, "No records yet. Be the first!", font_small, GRAY, 250)

        mx, my = pygame.mouse.get_pos()
        hover  = back_btn.collidepoint(mx, my)
        draw_button(screen, back_btn, "← Back", font_small,
                    GRAY if hover else DARK_GRAY, WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.collidepoint(event.pos):
                    return
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                    return

        pygame.display.flip()
        clock.tick(30)

# ── Settings Screen ───────────────────────────────────────────────────────────
def settings_screen():
    settings = load_settings()

    COLOR_OPTIONS = [
        ([0,   255,  0],   "Green"),
        ([0,   150, 255],  "Blue"),
        ([255, 200,  0],   "Gold"),
        ([255,  50, 50],   "Red"),
        ([200,   0, 255],  "Purple"),
    ]
    selected_color_idx = 0
    for i, (c, _) in enumerate(COLOR_OPTIONS):
        if c == settings["snake_color"]:
            selected_color_idx = i; break

    save_btn = pygame.Rect(300, 490, 200, 50)

    while True:
        draw_gradient_bg(screen)
        draw_text_center(screen, "SETTINGS", font_big, CYAN, 40)

        # ── Grid overlay toggle ───────────────────────────────────────────────
        pygame.draw.rect(screen, DARK_GRAY, (100, 160, 600, 50), border_radius=6)
        g_txt = font_small.render("Grid Overlay:", True, WHITE)
        screen.blit(g_txt, (120, 174))
        g_state = "ON" if settings["grid_overlay"] else "OFF"
        g_col   = GREEN if settings["grid_overlay"] else RED
        g_btn   = pygame.Rect(490, 165, 100, 38)
        draw_button(screen, g_btn, g_state, font_small, DARK_GRAY, g_col)

        # ── Sound toggle ──────────────────────────────────────────────────────
        pygame.draw.rect(screen, DARK_GRAY, (100, 230, 600, 50), border_radius=6)
        s_txt = font_small.render("Sound:", True, WHITE)
        screen.blit(s_txt, (120, 244))
        s_state = "ON" if settings["sound"] else "OFF"
        s_col   = GREEN if settings["sound"] else RED
        s_btn   = pygame.Rect(490, 235, 100, 38)
        draw_button(screen, s_btn, s_state, font_small, DARK_GRAY, s_col)

        # ── Snake color picker ────────────────────────────────────────────────
        pygame.draw.rect(screen, DARK_GRAY, (100, 300, 600, 70), border_radius=6)
        c_txt = font_small.render("Snake Color:", True, WHITE)
        screen.blit(c_txt, (120, 320))
        color_btns = []
        for i, (col, name) in enumerate(COLOR_OPTIONS):
            btn = pygame.Rect(300 + i * 80, 310, 60, 44)
            color_btns.append(btn)
            border = WHITE if i == selected_color_idx else DARK_GRAY
            pygame.draw.rect(screen, col, btn, border_radius=6)
            pygame.draw.rect(screen, border, btn, 3, border_radius=6)

        # ── Save & Back ───────────────────────────────────────────────────────
        mx, my = pygame.mouse.get_pos()
        draw_button(screen, save_btn, "Save & Back", font_small,
                    GREEN if save_btn.collidepoint(mx, my) else DARK_GRAY, WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if g_btn.collidepoint(event.pos):
                    settings["grid_overlay"] = not settings["grid_overlay"]
                if s_btn.collidepoint(event.pos):
                    settings["sound"] = not settings["sound"]
                for i, btn in enumerate(color_btns):
                    if btn.collidepoint(event.pos):
                        selected_color_idx = i
                        settings["snake_color"] = COLOR_OPTIONS[i][0]
                if save_btn.collidepoint(event.pos):
                    save_settings(settings)
                    return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    save_settings(settings)
                    return

        pygame.display.flip()
        clock.tick(30)

# ── Game Over Screen ──────────────────────────────────────────────────────────
def game_over_screen(score, level, personal_best) -> str:
    """Returns 'retry' or 'menu'"""
    retry_btn = pygame.Rect(150, 430, 200, 50)
    menu_btn  = pygame.Rect(450, 430, 200, 50)

    while True:
        draw_gradient_bg(screen)
        draw_text_center(screen, "GAME OVER", font_big, RED, 80)
        draw_text_center(screen, f"Score: {score}",         font_med,   WHITE,  200)
        draw_text_center(screen, f"Level Reached: {level}", font_med,   YELLOW, 260)
        pb_col = GOLD if score >= personal_best else WHITE
        draw_text_center(screen, f"Personal Best: {personal_best}", font_small, pb_col, 330)
        if score >= personal_best and personal_best > 0:
            draw_text_center(screen, "🎉 New Personal Best!", font_small, GOLD, 370)

        mx, my = pygame.mouse.get_pos()
        draw_button(screen, retry_btn, "▶  Retry",    font_small,
                    GREEN if retry_btn.collidepoint(mx, my) else DARK_GRAY, WHITE)
        draw_button(screen, menu_btn, "⌂  Main Menu", font_small,
                    CYAN if menu_btn.collidepoint(mx, my) else DARK_GRAY, WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if retry_btn.collidepoint(event.pos):
                    return "retry"
                if menu_btn.collidepoint(event.pos):
                    return "menu"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return "retry"
                if event.key == pygame.K_ESCAPE:
                    return "menu"

        pygame.display.flip()
        clock.tick(30)

# ── HUD ───────────────────────────────────────────────────────────────────────
def draw_hud(score, level, foods_eaten, personal_best, snake, powerup, shield_active):
    # Left column
    screen.blit(font_small.render(f"Score: {score}",        True, WHITE),  (10, 10))
    screen.blit(font_small.render(f"Level: {level}",        True, YELLOW), (10, 44))
    screen.blit(font_small.render(f"Next:  {foods_eaten}/{FOODS_PER_LEVEL}", True, CYAN), (10, 78))
    screen.blit(font_small.render(f"Best:  {personal_best}", True, GOLD),  (10, 112))

    # Right column
    speed_txt = font_small.render(f"Len: {len(snake.positions)}", True, CYAN)
    screen.blit(speed_txt, (SCREEN_WIDTH - speed_txt.get_width() - 10, 10))

    # Active power-up effect indicator
    now = pygame.time.get_ticks()
    if powerup.effect_active():
        remaining = (powerup.effect_end - now) / 1000
        kind_str  = powerup.kind.replace("_", " ").title()
        col       = powerup.color
        txt       = font_small.render(f"⚡ {kind_str}: {remaining:.1f}s", True, col)
        screen.blit(txt, (SCREEN_WIDTH - txt.get_width() - 10, 44))

    if shield_active:
        txt = font_small.render("🛡 Shield", True, PINK)
        screen.blit(txt, (SCREEN_WIDTH - txt.get_width() - 10, 78))


# ── Main gameplay loop ────────────────────────────────────────────────────────
def play_game(username: str, settings: dict):
    """Returns: 'retry' | 'menu'"""
    personal_best = db.get_personal_best(username)

    def new_game():
        s      = Snake(color=settings["snake_color"])
        obs    = Obstacles()
        f      = Food(s.positions, obs.positions)
        pf     = PoisonFood(s.positions, obs.positions + [f.position])
        pu     = PowerUp(s.positions, obs.positions, [f.position, pf.position])
        return s, obs, f, pf, pu

    snake, obstacles, food, pf, powerup = new_game()
    score       = 0
    level       = 1
    foods_eaten = 0
    current_speed   = BASE_SPEED
    shield_active   = False
    game_active     = True

    # Poison food respawn cooldown
    poison_cooldown = 0
    POISON_RESPAWN_INTERVAL = 15_000  # ms between poison spawns

    while True:
        clock.tick(current_speed)
        now = pygame.time.get_ticks()

        # ── Events ────────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and game_active:
                if   event.key in (pygame.K_UP,    pygame.K_w): snake.change_direction(UP)
                elif event.key in (pygame.K_DOWN,  pygame.K_s): snake.change_direction(DOWN)
                elif event.key in (pygame.K_LEFT,  pygame.K_a): snake.change_direction(LEFT)
                elif event.key in (pygame.K_RIGHT, pygame.K_d): snake.change_direction(RIGHT)
                elif event.key == pygame.K_ESCAPE:
                    return "menu"

        if not game_active:
            break

        # ── Move ──────────────────────────────────────────────────────────────
        snake.move()

        # ── Collision detection ───────────────────────────────────────────────
        wall_hit   = snake.check_wall_collision(obstacles.positions)
        border_hit = snake.check_border_collision()
        self_hit   = snake.check_self_collision()

        if wall_hit or border_hit or self_hit:
            if shield_active:
                # shield absorbs ONE collision
                shield_active = False
                # push snake back one step
                head = snake.positions[0]
                opp  = (-snake.direction[0], -snake.direction[1])
                head[0] += opp[0] * GRID_SIZE
                head[1] += opp[1] * GRID_SIZE
            else:
                game_active = False
                continue

        # ── Food update ───────────────────────────────────────────────────────
        blocked = obstacles.positions + [pf.position if pf.active else [-1, -1]]
        food.update(snake.positions, blocked)

        # ── Poison food update ────────────────────────────────────────────────
        if pf.active:
            pf.update(snake.positions, blocked)
        else:
            # try to respawn after cooldown
            if now - poison_cooldown > POISON_RESPAWN_INTERVAL:
                pf.spawn(snake.positions,
                         obstacles.positions + [food.position])
                poison_cooldown = now

        # ── Power-up update ───────────────────────────────────────────────────
        powerup.update()

        # ── Eat normal food ───────────────────────────────────────────────────
        if snake.positions[0] == food.position:
            snake.grow()
            score       += food.points
            foods_eaten += 1
            food.respawn(snake.positions,
                         obstacles.positions + ([pf.position] if pf.active else []))

            if foods_eaten >= FOODS_PER_LEVEL:
                level       += 1
                foods_eaten  = 0
                current_speed = BASE_SPEED + level * 2
                obstacles.generate(level, snake.positions)
                # Re-check speed effect
                if powerup.effect_active() and powerup.kind == "speed_boost":
                    current_speed = int(current_speed * 1.5)
                elif powerup.effect_active() and powerup.kind == "slow_motion":
                    current_speed = max(4, current_speed // 2)

        # ── Eat poison food ───────────────────────────────────────────────────
        if pf.active and snake.positions[0] == pf.position:
            pf.active = False
            poison_cooldown = now
            alive = snake.shorten(2)
            if not alive:
                game_active = False
                continue
            score = max(0, score - 5)

        # ── Collect power-up ──────────────────────────────────────────────────
        if powerup.active and snake.positions[0] == powerup.position:
            powerup.activate_effect()
            if powerup.kind == "speed_boost":
                current_speed = BASE_SPEED + level * 2 + int((BASE_SPEED + level * 2) * 0.5)
            elif powerup.kind == "slow_motion":
                current_speed = max(4, (BASE_SPEED + level * 2) // 2)
            elif powerup.kind == "shield":
                shield_active = True
            # Respawn power-up after some delay (handled via active flag)
            powerup.spawn(snake.positions,
                          obstacles.positions,
                          [food.position] + ([pf.position] if pf.active else []))

        # ── Power-up effect expiry ────────────────────────────────────────────
        if not powerup.effect_active() and powerup.kind in ("speed_boost", "slow_motion"):
            # Reset speed to normal for this level
            current_speed = BASE_SPEED + level * 2

        # ── Draw ──────────────────────────────────────────────────────────────
        screen.fill(BLACK)

        if settings.get("grid_overlay", True):
            draw_grid(screen)

        obstacles.draw(screen)
        food.draw(screen)
        if pf.active:
            pf.draw(screen)
        powerup.draw(screen, font_tiny)
        snake.draw(screen)
        draw_hud(score, level, foods_eaten, personal_best,
                 snake, powerup, shield_active)

        pygame.display.flip()

    # ── Game over ─────────────────────────────────────────────────────────────
    db.save_result(username, score, level)
    personal_best = db.get_personal_best(username)
    return game_over_screen(score, level, personal_best)


# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    db.init_db()
    username = username_screen()

    while True:
        choice = main_menu_screen()

        if choice == "quit":
            break
        elif choice == "leaderboard":
            leaderboard_screen()
        elif choice == "settings":
            settings_screen()
        elif choice == "play":
            settings = load_settings()
            result   = play_game(username, settings)
            while result == "retry":
                settings = load_settings()
                result   = play_game(username, settings)
            # result == "menu" → back to main menu

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()