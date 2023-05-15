# More here: https://www.redblobgames.com/grids/hexagons/
import math
from typing import List, Tuple, Union

ANGLES: Tuple[float] = tuple([math.radians(60 * i) for i in range(6)])


def get_dots(x: int, y: int, radius: int, dx: int = 0, dy: int = 0) -> Tuple[Tuple[int, int]]:
    return tuple([(int(x + dx + radius * math.cos(a)), int(y + dy + radius * math.sin(a))) for a in ANGLES])


class Cube:
    """Class for cube coordinates, cube vector."""

    def __init__(self, q: int, r: int, s: int = None):
        self.q: int = q
        self.r: int = r
        self.s: int = -q - r if s is None else s

    @property
    def qrs(self) -> Tuple[int, int, int]:
        return self.q, self.r, self.s

    @property
    def qr(self) -> Tuple[int, int]:
        return self.q, self.r

    @property
    def qrs_abs_sum(self):
        return abs(self.q) + abs(self.r) + abs(self.s)


CUBE_VECTORS: List[Cube] = [
    Cube(+1, 0, -1), Cube(+1, -1, 0), Cube(0, -1, +1),
    Cube(-1, 0, +1), Cube(-1, +1, 0), Cube(0, +1, -1),
]


class XYIdHex:
    def __init__(self, x_id: int, y_id: int):
        self.x_id: int = x_id
        self.y_id: int = y_id

    @property
    def xy_id(self) -> Tuple[int, int]:
        return self.x_id, self.y_id


class Hexagon(XYIdHex, Cube):
    def __init__(self, x_id, y_id, radius):
        self.radius: int = radius
        super(Hexagon, self).__init__(x_id=x_id, y_id=y_id)
        Cube.__init__(self, *HexMath.xy_id_to_qr(x_id, y_id))

        self.x: int = HexMath.get_x_coord(q=self.q, radius=self.radius)
        self.y: int = HexMath.get_y_coord(q=self.q, r=self.r, radius=self.radius)
        self.dots: Tuple[Tuple[int, int]] = None
        self.create_dots()

    @property
    def center(self) -> Tuple[int, int]:
        return self.x, self.y

    def create_dots(self):
        self.dots: Tuple[Tuple[int, int]] = get_dots(self.x, self.y, radius=self.radius)


class HexMath:
    @classmethod
    def horizontal_spacing(cls, radius: int) -> float:
        return cls.get_width(radius=radius) * 0.75

    @classmethod
    def vertical_spacing(cls, radius: int) -> float:
        return cls.get_height(radius=radius)

    @staticmethod
    def get_width(radius: int) -> int:
        return int(radius + radius)

    @staticmethod
    def get_height(radius: int) -> float:
        return int(math.sqrt(3) * radius)

    @classmethod
    def qr_to_xy_coords(cls, q: int, r: int, radius: int) -> Tuple[int, int]:
        return cls.get_x_coord(radius=radius, q=q), cls.get_y_coord(radius=radius, q=q, r=r)

    @classmethod
    def get_x_coord(cls, q: int, radius: int) -> int:
        return int(q * cls.horizontal_spacing(radius=radius) + radius)

    @classmethod
    def get_y_coord(cls, q: int, r: int, radius: int) -> int:
        return int(cls.get_height(radius=radius) * (r + q / 2) + cls.get_height(radius=radius) // 2)

    @classmethod
    def get_grid_vertical_size(cls, y: int, radius: int) -> int:
        return int(cls.vertical_spacing(radius=radius) * y + cls.get_height(radius=radius) / 2) + 1

    @classmethod
    def get_grid_size(cls, h_size: int, v_size: int, radius: int) -> Tuple[int, int]:
        return cls.get_grid_horizontal_size(h_size, radius), cls.get_grid_vertical_size(v_size, radius)

    @classmethod
    def get_grid_horizontal_size(cls, x: int, radius: int) -> int:
        return int(cls.horizontal_spacing(radius) * x + cls.get_width(radius) * 0.25) + 1

    @classmethod
    def normalize_coordinates(cls, x: int, y: int, radius: int) -> Tuple[int, int]:
        x = x // cls.horizontal_spacing(radius)
        if x % 2:
            y -= cls.vertical_spacing(radius) // 2
        y = y // cls.vertical_spacing(radius)
        return int(x), int(y)

    @classmethod
    def xy_id_to_qr(cls, x_id: int, y_id: int) -> Tuple[int, int]:
        return x_id, y_id - x_id // 2

    @classmethod
    def xy_id_to_xy_coordinates(cls, x_id: int, y_id: int, radius: int) -> Tuple[int, int]:
        return cls.qr_to_xy_coords(*cls.xy_id_to_qr(x_id=x_id, y_id=y_id), radius=radius)

    @classmethod
    def xy_coord_to_qr(cls, x: int, y: int, radius: int) -> Tuple[int, int]:
        return cls.xy_id_to_qr(*cls.normalize_coordinates(x=x, y=y, radius=radius))

    @classmethod
    def cube_add(cls, h: Cube, vec: Cube) -> Cube:
        return cls.axial_add(h, vec)

    @classmethod
    def cube_scale(cls, h: Cube, factor: float) -> Cube:
        return cls.scale(h, factor)

    @classmethod
    def cube_neighbor(cls, cube: Cube, direction: int) -> Cube:
        return cls.cube_add(cube, CUBE_VECTORS[direction])

    @classmethod
    def get_neighbors_qr(cls, q: int, r: int, range_radius: int = 1) -> List[Tuple[int, int]]:
        results = []
        for dq in range(-range_radius, range_radius + 1):
            for dr in range(max(-range_radius, -dq - range_radius), min(range_radius, -dq + range_radius) + 1):
                ds = -dq - dr
                if abs(ds) <= range_radius:
                    results.append((int(q + dq), int(r + dr)))
        return results

    @classmethod
    def ring_at_radius(cls, q: int, r: int, range_radius: int) -> List[Tuple[int, int]]:
        results = []
        start_hex = cls.cube_add(Cube(q=q, r=r), cls.cube_scale(h=CUBE_VECTORS[4], factor=range_radius))

        for i in range(6):
            for j in range(range_radius):
                results.append(start_hex.qr)
                start_hex = cls.cube_neighbor(start_hex, i)
        return results

    @classmethod
    def get_dots_by_qr(cls, q: int, r: int, radius: int):
        return get_dots(*cls.qr_to_xy_coords(q=q, r=r, radius=radius), radius=radius)

    @classmethod
    def ring_at_radius_border(cls, q: int, r: int, range_radius: int, radius: int) -> List[Tuple[int, int]]:
        results = []
        start_hex = cls.cube_add(Cube(q, r), cls.cube_scale(CUBE_VECTORS[4], range_radius))
        for i in range(6):
            idxs = [3 - i, 2 - i, 1 - i]
            for j in range(range_radius):
                dots = cls.get_dots_by_qr(q=start_hex.q, r=start_hex.r, radius=radius)
                for inx in idxs:
                    if inx > 5:
                        inx -= 6
                    results.append(dots[inx])
                start_hex = cls.cube_neighbor(start_hex, i)
        return results

    @classmethod
    def get_cube_distance(cls, a: Cube, b: Cube) -> float:
        return cls.cube_subtract(a, b).qrs_abs_sum / 2

    @classmethod
    def scale(cls, h: Cube, factor: float) -> 'Cube':
        return Cube(int(h.q * factor), int(h.r * factor), int(h.s * factor))

    @classmethod
    def cube_subtract(cls, a: Cube, b: Cube):
        return Cube(a.q - b.q, a.r - b.r, a.s - b.s)

    @classmethod
    def axial_add(cls, a: Cube, b: Cube):
        return Cube(a.q + b.q, a.r + b.r, a.s + b.s)

    @classmethod
    def lerp(cls, a: Union[int, float], b: Union[int, float], t: Union[int, float]) -> float:
        return a + (b - a) * t

    @classmethod
    def cube_lerp(cls, a: Cube, b: Cube, t: Union[int, float]) -> Cube:
        return Cube(cls.lerp(a.q, b.q, t),
                    cls.lerp(a.r, b.r, t),
                    cls.lerp(a.s, b.s, t))

    @classmethod
    def ray_from_a_to_b(cls, a: Cube, b: Cube) -> List[Tuple[int, int]]:
        distance = cls.get_cube_distance(a, b)
        result = []
        if distance == 0:
            return result

        for i in range(int(distance) + 1):
            result.append(cls.cube_round(cls.cube_lerp(a, b, 1.0 / distance * i)).qr)

        return result

    @classmethod
    def cube_round(cls, frac: Cube) -> Cube:
        q = round(frac.q)
        r = round(frac.r)
        s = round(frac.s)

        q_diff = abs(q - frac.q)
        r_diff = abs(r - frac.r)
        s_diff = abs(s - frac.s)

        if q_diff > r_diff and q_diff > s_diff:
            q = -r - s
        elif r_diff > s_diff:
            r = -q - s
        else:
            s = -q - r

        return Cube(q, r, s)