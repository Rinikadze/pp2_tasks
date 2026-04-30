"""
tools.py  –  Drawing tool implementations for TSIS 2 Paint
"""

import math
import collections
import pygame


# ─────────────────────────────────────────────────────────────────────────────
# Pencil (freehand)
# ─────────────────────────────────────────────────────────────────────────────

class PencilTool:
    def __init__(self):
        self.last_pos = None

    def on_down(self, canvas, pos, color, size):
        self.last_pos = pos
        pygame.draw.circle(canvas, color, pos, size // 2)

    def on_move(self, canvas, pos, color, size):
        if self.last_pos:
            pygame.draw.line(canvas, color, self.last_pos, pos, size)
        self.last_pos = pos

    def on_up(self, canvas, pos, color, size):
        self.last_pos = None

    def preview(self, surface, start, end, color, size):
        pass   # no preview needed for freehand


# ─────────────────────────────────────────────────────────────────────────────
# Straight line
# ─────────────────────────────────────────────────────────────────────────────

class LineTool:
    def preview(self, surface, start, end, color, size):
        pygame.draw.line(surface, color, start, end, size)

    def on_up(self, canvas, start, end, color, size):
        pygame.draw.line(canvas, color, start, end, size)


# ─────────────────────────────────────────────────────────────────────────────
# Rectangle
# ─────────────────────────────────────────────────────────────────────────────

class RectTool:
    def preview(self, surface, start, end, color, size):
        r = _make_rect(start, end)
        pygame.draw.rect(surface, color, r, size)

    def on_up(self, canvas, start, end, color, size):
        r = _make_rect(start, end)
        pygame.draw.rect(canvas, color, r, size)


# ─────────────────────────────────────────────────────────────────────────────
# Circle
# ─────────────────────────────────────────────────────────────────────────────

class CircleTool:
    def preview(self, surface, start, end, color, size):
        radius = int(math.hypot(end[0] - start[0], end[1] - start[1]))
        if radius > 0:
            pygame.draw.circle(surface, color, start, radius, size)

    def on_up(self, canvas, start, end, color, size):
        radius = int(math.hypot(end[0] - start[0], end[1] - start[1]))
        if radius > 0:
            pygame.draw.circle(canvas, color, start, radius, size)


# ─────────────────────────────────────────────────────────────────────────────
# Square
# ─────────────────────────────────────────────────────────────────────────────

class SquareTool:
    def preview(self, surface, start, end, color, size):
        r = _make_square(start, end)
        pygame.draw.rect(surface, color, r, size)

    def on_up(self, canvas, start, end, color, size):
        r = _make_square(start, end)
        pygame.draw.rect(canvas, color, r, size)


# ─────────────────────────────────────────────────────────────────────────────
# Right Triangle
# ─────────────────────────────────────────────────────────────────────────────

class TriangleRightTool:
    def _points(self, start, end):
        return [start, (end[0], start[1]), (start[0], end[1])]

    def preview(self, surface, start, end, color, size):
        pygame.draw.polygon(surface, color, self._points(start, end), size)

    def on_up(self, canvas, start, end, color, size):
        pygame.draw.polygon(canvas, color, self._points(start, end), size)


# ─────────────────────────────────────────────────────────────────────────────
# Equilateral Triangle
# ─────────────────────────────────────────────────────────────────────────────

class TriangleEqTool:
    def _points(self, start, end):
        x1, y1 = start
        x2 = end[0]
        side = abs(x2 - x1)
        height = int((math.sqrt(3) / 2) * side)
        return [(x1, y1), (x1 + side, y1), (x1 + side // 2, y1 - height)]

    def preview(self, surface, start, end, color, size):
        pygame.draw.polygon(surface, color, self._points(start, end), size)

    def on_up(self, canvas, start, end, color, size):
        pygame.draw.polygon(canvas, color, self._points(start, end), size)


# ─────────────────────────────────────────────────────────────────────────────
# Rhombus
# ─────────────────────────────────────────────────────────────────────────────

class RhombusTool:
    def _points(self, start, end):
        x1, y1 = start
        x2, y2 = end
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        return [(cx, y1), (x2, cy), (cx, y2), (x1, cy)]

    def preview(self, surface, start, end, color, size):
        pygame.draw.polygon(surface, color, self._points(start, end), size)

    def on_up(self, canvas, start, end, color, size):
        pygame.draw.polygon(canvas, color, self._points(start, end), size)


# ─────────────────────────────────────────────────────────────────────────────
# Eraser
# ─────────────────────────────────────────────────────────────────────────────

class EraserTool:
    def __init__(self):
        self.last_pos = None

    def on_down(self, canvas, pos, color, size):
        self.last_pos = pos
        pygame.draw.circle(canvas, (255, 255, 255), pos, size)

    def on_move(self, canvas, pos, color, size):
        if self.last_pos:
            pygame.draw.line(canvas, (255, 255, 255), self.last_pos, pos, size * 2)
        self.last_pos = pos

    def on_up(self, canvas, pos, color, size):
        self.last_pos = None

    def preview(self, surface, start, end, color, size):
        pass


# ─────────────────────────────────────────────────────────────────────────────
# Flood Fill
# ─────────────────────────────────────────────────────────────────────────────

class FillTool:
    def flood_fill(self, canvas, pos, fill_color):
        """BFS flood fill using get_at / set_at."""
        x, y = pos
        w, h = canvas.get_size()

        # Clamp to canvas
        if not (0 <= x < w and 0 <= y < h):
            return

        target_color = canvas.get_at((x, y))[:3]
        fc = fill_color[:3] if len(fill_color) > 3 else fill_color

        if target_color == fc:
            return

        queue = collections.deque()
        queue.append((x, y))
        visited = set()
        visited.add((x, y))

        while queue:
            cx, cy = queue.popleft()
            if canvas.get_at((cx, cy))[:3] != target_color:
                continue
            canvas.set_at((cx, cy), fill_color)
            for nx, ny in ((cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)):
                if (0 <= nx < w and 0 <= ny < h and
                        (nx, ny) not in visited and
                        canvas.get_at((nx, ny))[:3] == target_color):
                    visited.add((nx, ny))
                    queue.append((nx, ny))


# ─────────────────────────────────────────────────────────────────────────────
# Text Tool  (state managed here, rendering in main loop)
# ─────────────────────────────────────────────────────────────────────────────

class TextTool:
    def __init__(self):
        self.active = False
        self.pos = (0, 0)
        self.text = ""
        self.font = pygame.font.SysFont("consolas", 22)

    def activate(self, pos):
        self.active = True
        self.pos = pos
        self.text = ""

    def add_char(self, char):
        self.text += char

    def backspace(self):
        self.text = self.text[:-1]

    def confirm(self, canvas, color):
        if self.text:
            surf = self.font.render(self.text, True, color)
            canvas.blit(surf, self.pos)
        self.active = False
        self.text = ""

    def cancel(self):
        self.active = False
        self.text = ""

    def draw_cursor(self, surface, toolbar_height, color):
        """Draw live text + blinking cursor onto the screen surface."""
        if not self.active:
            return
        # Draw typed text
        surf = self.font.render(self.text + "|", True, color)
        screen_pos = (self.pos[0], self.pos[1] + toolbar_height)
        surface.blit(surf, screen_pos)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _make_rect(start, end):
    x = min(start[0], end[0])
    y = min(start[1], end[1])
    w = abs(end[0] - start[0])
    h = abs(end[1] - start[1])
    return pygame.Rect(x, y, w, h)


def _make_square(start, end):
    side = min(abs(end[0] - start[0]), abs(end[1] - start[1]))
    dx = 1 if end[0] >= start[0] else -1
    dy = 1 if end[1] >= start[1] else -1
    return pygame.Rect(start[0], start[1], side * dx, side * dy)