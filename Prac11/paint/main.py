import pygame
import sys

pygame.init()

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 650
TOOLBAR_HEIGHT = 100

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (180, 180, 180)
ACTIVE_COLOR = (100, 200, 255)  # подсветка кнопки

# режимы 
MODE_BRUSH = "brush"
MODE_RECT = "rectangle"
MODE_CIRCLE = "circle"
MODE_ERASER = "eraser"

MODE_SQUARE = "square"
MODE_TRIANGLE_RIGHT = "triangle_right"
MODE_TRIANGLE_EQ = "triangle_eq"
MODE_RHOMBUS = "rhombus"

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Paint")
clock = pygame.time.Clock()

# кнопка
class Button:
    def __init__(self, x, y, w, h, color, text=""):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.text = text
        self.font = pygame.font.Font(None, 22)

    def draw(self, surface, active=False):
        if active:
            pygame.draw.rect(surface, ACTIVE_COLOR, self.rect)  # подсветка
        else:
            pygame.draw.rect(surface, self.color, self.rect)

        pygame.draw.rect(surface, BLACK, self.rect, 2)

        if self.text:
            text_surf = self.font.render(self.text, True, BLACK)
            surface.blit(text_surf, text_surf.get_rect(center=self.rect.center))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# палитра
class ColorPalette:
    def __init__(self, x, y):
        self.colors = [BLACK, WHITE, RED, GREEN, BLUE]
        self.rects = []
        self.selected = BLACK

        for i, c in enumerate(self.colors):
            rect = pygame.Rect(x + i * 40, y, 30, 30)
            self.rects.append((rect, c))

    def draw(self, surface):
        for rect, color in self.rects:
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, BLACK, rect, 1)

            if color == self.selected:
                pygame.draw.rect(surface, WHITE, rect, 3)

    def check_click(self, pos):
        for rect, color in self.rects:
            if rect.collidepoint(pos):
                self.selected = color

# плавная линия
def draw_smooth_line(surface, color, start, end, radius):
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    dist = max(abs(dx), abs(dy))

    if dist == 0:
        pygame.draw.circle(surface, color, start, radius)
        return

    for i in range(dist):
        x = int(start[0] + dx * i / dist)
        y = int(start[1] + dy * i / dist)
        pygame.draw.circle(surface, color, (x, y), radius)


def main():
    canvas = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT - TOOLBAR_HEIGHT))
    canvas.fill(WHITE)

    drawing = False
    start_pos = None
    last_pos = None

    current_mode = MODE_BRUSH
    brush_size = 5
    eraser_size = 20
    current_color = BLACK

    # кнопки
    buttons = [
        Button(10, 10, 80, 30, GRAY, "Brush"),
        Button(100, 10, 80, 30, GRAY, "Rect"),
        Button(190, 10, 80, 30, GRAY, "Circle"),

        Button(280, 10, 80, 30, GRAY, "Square"),
        Button(370, 10, 80, 30, GRAY, "R.Tri"),
        Button(460, 10, 80, 30, GRAY, "E.Tri"),
        Button(550, 10, 80, 30, GRAY, "Rhomb"),

        Button(640, 10, 80, 30, GRAY, "Eraser"),  # теперь раньше
        Button(730, 10, 80, 30, WHITE, "Clear"),  # теперь в конце
    ]

    palette = ColorPalette(10, 60)

    running = True
    while running:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos

                if y < TOOLBAR_HEIGHT:
                    if buttons[0].is_clicked(event.pos): current_mode = MODE_BRUSH
                    elif buttons[1].is_clicked(event.pos): current_mode = MODE_RECT
                    elif buttons[2].is_clicked(event.pos): current_mode = MODE_CIRCLE

                    elif buttons[3].is_clicked(event.pos): current_mode = MODE_SQUARE
                    elif buttons[4].is_clicked(event.pos): current_mode = MODE_TRIANGLE_RIGHT
                    elif buttons[5].is_clicked(event.pos): current_mode = MODE_TRIANGLE_EQ
                    elif buttons[6].is_clicked(event.pos): current_mode = MODE_RHOMBUS

                    elif buttons[7].is_clicked(event.pos): current_mode = MODE_ERASER
                    elif buttons[8].is_clicked(event.pos): canvas.fill(WHITE)

                    palette.check_click(event.pos)
                    current_color = palette.selected

                else:
                    drawing = True
                    start_pos = (x, y - TOOLBAR_HEIGHT)
                    last_pos = start_pos

            elif event.type == pygame.MOUSEMOTION:
                if drawing and current_mode in [MODE_BRUSH, MODE_ERASER]:
                    x, y = event.pos
                    if y > TOOLBAR_HEIGHT:
                        pos = (x, y - TOOLBAR_HEIGHT)

                        if current_mode == MODE_BRUSH:
                            draw_smooth_line(canvas, current_color, last_pos, pos, brush_size)
                        else:
                            draw_smooth_line(canvas, WHITE, last_pos, pos, eraser_size)

                        last_pos = pos

            elif event.type == pygame.MOUSEBUTTONUP:
                if drawing:
                    x, y = event.pos
                    if y > TOOLBAR_HEIGHT:
                        end_pos = (x, y - TOOLBAR_HEIGHT)

                        if current_mode == MODE_RECT:
                            rect = pygame.Rect(start_pos[0], start_pos[1],
                                               end_pos[0] - start_pos[0],
                                               end_pos[1] - start_pos[1])
                            pygame.draw.rect(canvas, current_color, rect, 2)

                        elif current_mode == MODE_CIRCLE:
                            radius = int(((end_pos[0]-start_pos[0])**2 +
                                          (end_pos[1]-start_pos[1])**2)**0.5)
                            pygame.draw.circle(canvas, current_color, start_pos, radius, 2)

                        elif current_mode == MODE_SQUARE:
                            side = max(abs(end_pos[0]-start_pos[0]),
                                       abs(end_pos[1]-start_pos[1]))
                            rect = pygame.Rect(start_pos[0], start_pos[1], side, side)
                            pygame.draw.rect(canvas, current_color, rect, 2)

                        elif current_mode == MODE_TRIANGLE_RIGHT:
                            x1, y1 = start_pos
                            x2, y2 = end_pos
                            pygame.draw.polygon(canvas, current_color,
                                                [(x1,y1),(x2,y2),(x1,y2)], 2)

                        elif current_mode == MODE_TRIANGLE_EQ:
                            x1, y1 = start_pos
                            side = abs(end_pos[0] - x1)
                            height = int((3**0.5 / 2) * side)

                            pygame.draw.polygon(canvas, current_color, [
                                (x1, y1),
                                (x1 + side, y1),
                                (x1 + side//2, y1 - height)
                            ], 2)

                        elif current_mode == MODE_RHOMBUS:
                            x1, y1 = start_pos
                            x2, y2 = end_pos
                            cx = (x1 + x2)//2
                            cy = (y1 + y2)//2

                            pygame.draw.polygon(canvas, current_color, [
                                (cx, y1),
                                (x2, cy),
                                (cx, y2),
                                (x1, cy)
                            ], 2)

                drawing = False
                start_pos = None
                last_pos = None

        # отрисовка
        screen.fill(GRAY)

        screen.blit(canvas, (0, TOOLBAR_HEIGHT))

        pygame.draw.rect(screen, (200, 200, 200),
                         (0, 0, SCREEN_WIDTH, TOOLBAR_HEIGHT))

        for i, b in enumerate(buttons):
            active = False

            if i == 0 and current_mode == MODE_BRUSH: active = True
            elif i == 1 and current_mode == MODE_RECT: active = True
            elif i == 2 and current_mode == MODE_CIRCLE: active = True
            elif i == 3 and current_mode == MODE_SQUARE: active = True
            elif i == 4 and current_mode == MODE_TRIANGLE_RIGHT: active = True
            elif i == 5 and current_mode == MODE_TRIANGLE_EQ: active = True
            elif i == 6 and current_mode == MODE_RHOMBUS: active = True
            elif i == 7 and current_mode == MODE_ERASER: active = True  # обновлено

            b.draw(screen, active)

        palette.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()