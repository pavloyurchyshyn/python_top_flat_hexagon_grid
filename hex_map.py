import pygame
from typing import List, Dict, Tuple

from hex_math import Hexagon, HexMath

pygame.init()

HEX_RADIUS = 50
HORIZONTAL_GRID_SIZE = 20
VERTICAL_GRID_SIZE = 10

SCREEN_WIDTH, SCREEN_HEIGHT = HexMath.get_grid_size(h_size=HORIZONTAL_GRID_SIZE,
                                                    v_size=VERTICAL_GRID_SIZE,
                                                    radius=HEX_RADIUS)
W_MID = SCREEN_WIDTH // 2
H_MID = SCREEN_HEIGHT // 2
size = (SCREEN_WIDTH, SCREEN_HEIGHT)
screen = pygame.display.set_mode(size)

pygame_clock = pygame.time.Clock()

FONT = pygame.font.SysFont('Arial', HEX_RADIUS // 5)


class GridHex(Hexagon):
    def __init__(self, x_id, y_id, radius=HEX_RADIUS, border_size=1, draw_text=True):
        super(GridHex, self).__init__(x_id=x_id, y_id=y_id, radius=radius)
        self.border_size: int = border_size
        self.draw_text: border_size = draw_text
        self.text = FONT.render(f'{self.qrs}-{self.xy_id}', True, (255, 255, 255))

    def draw(self):
        pygame.draw.lines(screen, (255, 255, 255), True, self.dots, self.border_size)
        if self.draw_text:
            x, y = self.center
            screen.blit(self.text, (x - self.text.get_width() // 2, y - self.text.get_height() // 2))


class HexWorld:
    def __init__(self):
        self.hexes_list: List[GridHex] = []
        self.xy_to_hex: Dict[Tuple[int, int], GridHex] = {}
        self.qr_to_hex: Dict[Tuple[int, int], GridHex] = {}

    def create_hexes(self):
        for y, line in enumerate([[1 for _ in range(HORIZONTAL_GRID_SIZE)] for _ in range(VERTICAL_GRID_SIZE)]):
            for x, val in enumerate(line):
                if val:
                    h = GridHex(x_id=x, y_id=y, radius=HEX_RADIUS)
                    self.hexes_list.append(h)
                    self.qr_to_hex[h.qr] = h
                    self.xy_to_hex[h.xy_id] = h


world = HexWorld()
world.create_hexes()
RANGE_RADIUS = 1
TARGET_HEX = (0, 0)


def draw_hex_under_mouse(h: GridHex):
    if h.qr in world.qr_to_hex:
        pygame.draw.lines(screen, (0, 255, 0), True, h.dots, 3)


def draw_square(q, r):
    neighbors = HexMath.get_neighbors_qr(q=q, r=r, range_radius=RANGE_RADIUS)
    for qr in neighbors:
        if qr in world.qr_to_hex:
            pygame.draw.polygon(screen, (110, 111, 111), world.qr_to_hex[qr].dots)


def draw_hexes_ring(q, r):
    neighbors_at_radius = HexMath.ring_at_radius(q=q, r=r, range_radius=RANGE_RADIUS)
    for qr in neighbors_at_radius:
        if qr in world.qr_to_hex:
            pygame.draw.polygon(screen, (150, 150, 150, 50), world.qr_to_hex[qr].dots)


def draw_square_edge(q, r):
    if dots_at_edge := HexMath.ring_at_radius_border(q=q, r=r, range_radius=RANGE_RADIUS, radius=HEX_RADIUS):
        pygame.draw.lines(screen, (255, 100, 100), True, dots_at_edge, 5)


def draw_from_a_to_b(a_xy, b_xy):
    a_hex = Hexagon(*a_xy, HEX_RADIUS)
    b_hex = Hexagon(*b_xy, HEX_RADIUS)

    if line := HexMath.ray_from_a_to_b(a_hex, b_hex):
        line = [HexMath.qr_to_xy_coords(*qr, HEX_RADIUS) for qr in line]
        pygame.draw.lines(screen, (0, 0, 255), False, line, 6)


def draw_target_in_range_line(a_xy, b_xy):
    a_hex = Hexagon(*a_xy, HEX_RADIUS)
    b_hex = Hexagon(*b_xy, HEX_RADIUS)
    in_range = HexMath.get_cube_distance(a_hex, b_hex)
    color = (255, 0, 0) if in_range > RANGE_RADIUS else (0, 255, 0)
    pygame.draw.line(screen, color, a_hex.center, b_hex.center, 2)


while True:
    mouse_pos = pygame.mouse.get_pos()
    screen.fill((0, 0, 0))
    pygame.draw.line(screen, (200, 100, 100), (W_MID, 0),
                     (W_MID, HexMath.get_grid_vertical_size(VERTICAL_GRID_SIZE, HEX_RADIUS)), 3)
    pygame.draw.line(screen, (100, 100, 100), (W_MID, 0), (W_MID, SCREEN_HEIGHT))
    pygame.draw.line(screen, (100, 100, 200), (0, H_MID),
                     (HexMath.get_grid_horizontal_size(HORIZONTAL_GRID_SIZE, HEX_RADIUS), H_MID), 3)
    pygame.draw.line(screen, (100, 100, 100), (0, H_MID), (SCREEN_WIDTH, H_MID))
    pygame_clock.tick(60)

    mouse_qr = HexMath.xy_coord_to_qr(*mouse_pos, HEX_RADIUS)
    mouse_xy_id = HexMath.normalize_coordinates(*mouse_pos, HEX_RADIUS)
    mouse_hex = GridHex(*mouse_xy_id, HEX_RADIUS, draw_text=False)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                RANGE_RADIUS += 1

            elif event.button == 5:
                RANGE_RADIUS -= 1
                if RANGE_RADIUS < 0:
                    RANGE_RADIUS = -1
            elif event.button == 1:
                if mouse_xy_id in world.xy_to_hex:
                    TARGET_HEX = mouse_xy_id

    pygame.draw.polygon(screen, (100, 150, 100), world.xy_to_hex[TARGET_HEX].dots)

    draw_square(*mouse_qr)
    draw_hexes_ring(*mouse_qr)

    for h in world.hexes_list:
        h.draw()

    draw_square_edge(*mouse_qr)
    draw_hex_under_mouse(mouse_hex)
    draw_from_a_to_b(mouse_xy_id, TARGET_HEX)
    draw_target_in_range_line(mouse_xy_id, TARGET_HEX)

    pygame.display.update()
