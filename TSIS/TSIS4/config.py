import pygame

# Screen
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Colors
BLACK       = (0,   0,   0)
WHITE       = (255, 255, 255)
RED         = (255,  0,   0)
GREEN       = (0,  255,   0)
DARK_GREEN  = (0,  100,   0)
BLUE        = (0,   0,  255)
YELLOW      = (255, 255,  0)
PURPLE      = (148,  0, 211)
CYAN        = (0,  255, 255)
ORANGE      = (255, 165,  0)
LIGHT_BLUE  = (100, 200, 255)
DARK_RED    = (139,   0,   0)
GOLD        = (255, 215,   0)
PINK        = (255, 105, 180)
GRAY        = (80,   80,  80)
DARK_GRAY   = (30,   30,  30)
TEAL        = (0,  128, 128)

# Movement directions
UP    = (0, -1)
DOWN  = (0,  1)
LEFT  = (-1, 0)
RIGHT = (1,  0)

# Gameplay
BASE_SPEED      = 10
FOODS_PER_LEVEL = 3

# Food point weights
FOOD_POINTS = {
    "normal":  10,
    "bonus":   20,
    "penalty": -5,
}

# Power-up durations (ms)
POWERUP_FIELD_DURATION = 8000   # disappears from field after 8 s
POWERUP_EFFECT_DURATION = 5000  # effect lasts 5 s

# Obstacle
OBSTACLE_START_LEVEL = 3