"""
paint.py  –  Extended Paint Application  (TSIS 2)
Extends Practice 10 & 11 with: pencil, line, brush sizes,
flood-fill, text tool, and Ctrl+S canvas save.
"""

import sys
import math
import datetime
import pygame

from tools import (
    PencilTool, LineTool, RectTool, CircleTool, SquareTool,
    TriangleRightTool, TriangleEqTool, RhombusTool,
    EraserTool, FillTool, TextTool,
)

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

SCREEN_WIDTH  = 1000
SCREEN_HEIGHT = 660
TOOLBAR_HEIGHT = 90

WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
GRAY   = (180, 180, 180)
DARK   = (60,  60,  60)
ACCENT = (255, 80,  60)

BRUSH_SIZES = {"S": 2, "M": 5, "L": 10}

PALETTE = [
    (0,   0,   0),    # black
    (255, 255, 255),  # white
    (220, 50,  50),   # red
    (50,  180, 50),   # green
    (50,  80,  220),  # blue
    (255, 200, 0),    # yellow
    (255, 130, 0),    # orange
    (160, 0,   200),  # purple
    (0,   200, 200),  # cyan
    (180, 100, 60),   # brown
    (255, 180, 200),  # pink
    (100, 100, 100),  # mid-gray
]

# Tool name constants
T_PENCIL   = "pencil"
T_LINE     = "line"
T_BRUSH    = "brush"      # kept for legacy label compatibility
T_RECT     = "rectangle"
T_CIRCLE   = "circle"
T_ERASER   = "eraser"
T_SQUARE   = "square"
T_TRI_R    = "tri_right"
T_TRI_E    = "tri_eq"
T_RHOMBUS  = "rhombus"
T_FILL     = "fill"
T_TEXT     = "text"


# ─────────────────────────────────────────────────────────────────────────────
# Button
# ─────────────────────────────────────────────────────────────────────────────

class Button:
    def __init__(self, x, y, w, h, label, tag=None):
        self.rect  = pygame.Rect(x, y, w, h)
        self.label = label
        self.tag   = tag
        self._font = None

    def draw(self, surface, active=False):
        if self._font is None:
            self._font = pygame.font.SysFont("segoeui", 15, bold=True)
        color = ACCENT if active else DARK
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, BLACK, self.rect, 1, border_radius=5)
        txt = self._font.render(self.label, True, WHITE)
        surface.blit(txt, txt.get_rect(center=self.rect.center))

    def hit(self, pos):
        return self.rect.collidepoint(pos)


# ─────────────────────────────────────────────────────────────────────────────
# Save helper
# ─────────────────────────────────────────────────────────────────────────────

def save_canvas(canvas):
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"canvas_{ts}.png"
    pygame.image.save(canvas, filename)
    print(f"[Saved] {filename}")
    return filename


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Paint – TSIS 2")
    clock = pygame.time.Clock()

    canvas = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT - TOOLBAR_HEIGHT))
    canvas.fill(WHITE)

    # Tool instances
    tools = {
        T_PENCIL:  PencilTool(),
        T_LINE:    LineTool(),
        T_RECT:    RectTool(),
        T_CIRCLE:  CircleTool(),
        T_ERASER:  EraserTool(),
        T_SQUARE:  SquareTool(),
        T_TRI_R:   TriangleRightTool(),
        T_TRI_E:   TriangleEqTool(),
        T_RHOMBUS: RhombusTool(),
        T_FILL:    FillTool(),
        T_TEXT:    TextTool(),
    }

    current_tool = T_PENCIL
    brush_size   = BRUSH_SIZES["M"]
    color        = BLACK
    drawing      = False
    start_pos    = None

    # ── Build toolbar buttons ─────────────────────────────────────────────
    bw, bh, gap = 68, 28, 6

    tool_buttons = [
        Button(gap + i * (bw + gap), 6, bw, bh, label, tag)
        for i, (label, tag) in enumerate([
            ("Pencil",  T_PENCIL),
            ("Line",    T_LINE),
            ("Rect",    T_RECT),
            ("Circle",  T_CIRCLE),
            ("Square",  T_SQUARE),
            ("Tri R",   T_TRI_R),
            ("Tri Eq",  T_TRI_E),
            ("Rhombus", T_RHOMBUS),
            ("Eraser",  T_ERASER),
            ("Fill",    T_FILL),
            ("Text",    T_TEXT),
        ])
    ]

    clear_btn = Button(SCREEN_WIDTH - 80, 6, 70, bh, "Clear")

    # Brush size buttons
    size_buttons = [
        Button(gap + i * (50 + gap), 42, 46, 24, f"{k} ({v}px)", k)
        for i, (k, v) in enumerate(BRUSH_SIZES.items())
    ]

    # Palette swatches
    swatch_size = 22
    palette_x0  = 280
    palette_y0  = 44
    swatches = [
        pygame.Rect(palette_x0 + i * (swatch_size + 3), palette_y0, swatch_size, swatch_size)
        for i in range(len(PALETTE))
    ]

    font_status = pygame.font.SysFont("consolas", 14)
    save_msg    = ""
    save_timer  = 0

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            # ── Quit ──────────────────────────────────────────────────────
            if event.type == pygame.QUIT:
                running = False

            # ── Key down ──────────────────────────────────────────────────
            elif event.type == pygame.KEYDOWN:
                text_tool = tools[T_TEXT]

                if text_tool.active:
                    if event.key == pygame.K_RETURN:
                        text_tool.confirm(canvas, color)
                    elif event.key == pygame.K_ESCAPE:
                        text_tool.cancel()
                    elif event.key == pygame.K_BACKSPACE:
                        text_tool.backspace()
                    elif event.unicode and event.unicode.isprintable():
                        text_tool.add_char(event.unicode)
                else:
                    # Ctrl+S → save
                    if event.key == pygame.K_s and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                        save_msg   = save_canvas(canvas)
                        save_timer = 180  # frames to show message

                    # Brush size shortcuts 1/2/3
                    elif event.key == pygame.K_1:
                        brush_size = BRUSH_SIZES["S"]
                    elif event.key == pygame.K_2:
                        brush_size = BRUSH_SIZES["M"]
                    elif event.key == pygame.K_3:
                        brush_size = BRUSH_SIZES["L"]

            # ── Mouse button down ──────────────────────────────────────────
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos

                if y < TOOLBAR_HEIGHT:
                    # Tool buttons
                    for btn in tool_buttons:
                        if btn.hit(event.pos):
                            current_tool = btn.tag
                            tools[T_TEXT].cancel()

                    # Clear
                    if clear_btn.hit(event.pos):
                        canvas.fill(WHITE)
                        tools[T_TEXT].cancel()

                    # Size buttons
                    for btn in size_buttons:
                        if btn.hit(event.pos):
                            brush_size = BRUSH_SIZES[btn.tag]

                    # Palette
                    for i, swatch in enumerate(swatches):
                        if swatch.collidepoint(event.pos):
                            color = PALETTE[i]

                else:
                    # Canvas area
                    canvas_pos = (x, y - TOOLBAR_HEIGHT)

                    if current_tool == T_FILL:
                        tools[T_FILL].flood_fill(canvas, canvas_pos, color)

                    elif current_tool == T_TEXT:
                        tools[T_TEXT].activate(canvas_pos)

                    elif current_tool in (T_PENCIL, T_BRUSH):
                        drawing = True
                        tools[T_PENCIL].on_down(canvas, canvas_pos, color, brush_size)

                    elif current_tool == T_ERASER:
                        drawing = True
                        tools[T_ERASER].on_down(canvas, canvas_pos, color, brush_size)

                    else:
                        drawing  = True
                        start_pos = canvas_pos

            # ── Mouse move ────────────────────────────────────────────────
            elif event.type == pygame.MOUSEMOTION:
                if drawing:
                    x, y = event.pos
                    if y > TOOLBAR_HEIGHT:
                        canvas_pos = (x, y - TOOLBAR_HEIGHT)
                        if current_tool in (T_PENCIL, T_BRUSH):
                            tools[T_PENCIL].on_move(canvas, canvas_pos, color, brush_size)
                        elif current_tool == T_ERASER:
                            tools[T_ERASER].on_move(canvas, canvas_pos, color, brush_size)

            # ── Mouse button up ───────────────────────────────────────────
            elif event.type == pygame.MOUSEBUTTONUP:
                if drawing:
                    x, y = event.pos
                    canvas_pos = (x, max(0, y - TOOLBAR_HEIGHT))

                    if current_tool in (T_PENCIL, T_BRUSH):
                        tools[T_PENCIL].on_up(canvas, canvas_pos, color, brush_size)

                    elif current_tool == T_ERASER:
                        tools[T_ERASER].on_up(canvas, canvas_pos, color, brush_size)

                    elif start_pos and current_tool == T_LINE:
                        tools[T_LINE].on_up(canvas, start_pos, canvas_pos, color, brush_size)

                    elif start_pos and current_tool == T_RECT:
                        tools[T_RECT].on_up(canvas, start_pos, canvas_pos, color, brush_size)

                    elif start_pos and current_tool == T_CIRCLE:
                        tools[T_CIRCLE].on_up(canvas, start_pos, canvas_pos, color, brush_size)

                    elif start_pos and current_tool == T_SQUARE:
                        tools[T_SQUARE].on_up(canvas, start_pos, canvas_pos, color, brush_size)

                    elif start_pos and current_tool == T_TRI_R:
                        tools[T_TRI_R].on_up(canvas, start_pos, canvas_pos, color, brush_size)

                    elif start_pos and current_tool == T_TRI_E:
                        tools[T_TRI_E].on_up(canvas, start_pos, canvas_pos, color, brush_size)

                    elif start_pos and current_tool == T_RHOMBUS:
                        tools[T_RHOMBUS].on_up(canvas, start_pos, canvas_pos, color, brush_size)

                    drawing   = False
                    start_pos = None

        # ── Render ────────────────────────────────────────────────────────

        # Toolbar background
        screen.fill((230, 230, 230))
        pygame.draw.rect(screen, (210, 210, 210), (0, 0, SCREEN_WIDTH, TOOLBAR_HEIGHT))
        pygame.draw.line(screen, DARK, (0, TOOLBAR_HEIGHT), (SCREEN_WIDTH, TOOLBAR_HEIGHT), 2)

        # Blit canvas + live preview overlay
        screen.blit(canvas, (0, TOOLBAR_HEIGHT))

        # Live preview for shape/line tools while dragging
        if drawing and start_pos and current_tool not in (T_PENCIL, T_BRUSH, T_ERASER):
            mx, my = mouse_pos
            if my > TOOLBAR_HEIGHT:
                cur_canvas_pos = (mx, my - TOOLBAR_HEIGHT)
                # Draw preview on a temp surface to avoid dirtying canvas
                preview_surf = canvas.copy()
                tool = tools.get(current_tool)
                if tool and hasattr(tool, "preview"):
                    tool.preview(preview_surf, start_pos, cur_canvas_pos, color, brush_size)
                screen.blit(preview_surf, (0, TOOLBAR_HEIGHT))

        # Tool buttons
        for btn in tool_buttons:
            btn.draw(screen, active=(btn.tag == current_tool))

        # Clear button
        clear_btn.draw(screen)

        # Size buttons
        for btn in size_buttons:
            active = (BRUSH_SIZES[btn.tag] == brush_size)
            btn.draw(screen, active=active)

        # Palette swatches
        for i, swatch in enumerate(swatches):
            pygame.draw.rect(screen, PALETTE[i], swatch)
            pygame.draw.rect(screen, BLACK, swatch, 1)

        # Current color preview
        cx_rect = pygame.Rect(palette_x0 + len(PALETTE) * (swatch_size + 3) + 6, palette_y0, 30, 22)
        pygame.draw.rect(screen, color, cx_rect)
        pygame.draw.rect(screen, BLACK, cx_rect, 2)

        # Status bar
        size_label = next((k for k, v in BRUSH_SIZES.items() if v == brush_size), "?")
        status = f"Tool: {current_tool}  |  Size: {size_label} ({brush_size}px)  |  Ctrl+S = save  |  1/2/3 = size"
        screen.blit(font_status.render(status, True, DARK), (palette_x0, 70))

        # Save confirmation message
        if save_timer > 0:
            msg_surf = font_status.render(f"Saved: {save_msg}", True, (0, 140, 0))
            screen.blit(msg_surf, (SCREEN_WIDTH - msg_surf.get_width() - 10, TOOLBAR_HEIGHT + 6))
            save_timer -= 1

        # Text tool cursor overlay
        tools[T_TEXT].draw_cursor(screen, TOOLBAR_HEIGHT, color)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()