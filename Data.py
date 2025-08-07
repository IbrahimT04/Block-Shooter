# Data.py

import math
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from GameData import GameData


class TimeData:
    """
    Holds timing information for the game; elapsed_time is updated externally per frame.
    """

    def __init__(
        self,
        game_data: "GameData",
        elapsed_time: float = 0.0,
        tp1: float = time.time(),
        tp2: float = time.time(),
    ):
        self.game_data = game_data
        self.elapsed_time = elapsed_time
        self.tp1 = tp1
        self.tp2 = tp2

    def time_update(self) -> None:
        self.tp2 = time.time()
        self.elapsed_time = self.tp2 - self.tp1
        self.tp1 = self.tp2


class MapData:
    """
    Manages the game map grid, collision checks, and enemy placement.
    """

    def __init__(
        self,
        game_data: "GameData",
        input_map: str = "*",
        n_map_width: int = 16,
        n_map_height: int = 16,
    ):
        self.game_data = game_data
        self.time_data = game_data.time_data
        self.screen_data = game_data.screen_data
        self.player_data = game_data.player_data

        self.n_map_width = n_map_width
        self.n_map_height = n_map_height

        if input_map == "*":
            # Default hardcoded 16×16 map
            rows = [
                "#######$$#######",
                "#*+.#.*+.......#",
                "#...#########..#",
                "#...#*...#..#..#",
                "#...##...#.....#",
                "#...#..+.......#",
                "#...#######....#",
                "#........*#....#",
                "#..#####.......#",
                "#....*.#########",
                "#..............#",
                "#....#####.....#",
                "#+...#.........#",
                "#.*..#.........#",
                "#....#.........#",
                "################",
            ]
            self.g_map = "".join(rows)
        else:
            self.g_map = input_map

        # Shortcuts to screen parameters
        self.map_size = self.screen_data.map_size
        self.pixel_size = self.screen_data.pixel_size
        self.h_indent = self.screen_data.h_indent
        self.v_indent = self.screen_data.v_indent
        self.buffer = self.screen_data.buffer

    def __post_init__(self):
        self.Enemy = self.game_data.game_assets.Enemy
        self.Bullet = self.game_data.game_assets.Bullet

    def update_map(self, x: int, y: int, status: int) -> None:
        """
        Replace character at (x, y) with:
         - '-' if status == -1
         - '=' if status == 4
         - '*' if status == 3
         - '+' if status == 2
         - '.' otherwise
        """
        idx = x + self.n_map_width * y
        temp = list(self.g_map)
        if status == -1:
            temp[idx] = "-"
        elif status == 4:
            temp[idx] = "="
        elif status == 3:
            temp[idx] = "*"
        elif status == 2:
            temp[idx] = "+"
        else:
            temp[idx] = "."
        self.g_map = "".join(temp)

    def check_collisions(self, x: float, y: float, z: float = 0.0) -> bool:
        """
        Return False if (x, y, z) hits a wall (#) or collectible.
        If hitting '=' or '+', update score and reset elapsed_time; return False,
        Otherwise return True (no collision).
        """
        if not (0.0 <= x < self.n_map_width) or not (0.0 <= y < self.n_map_height) or not (
            -2.0 <= z <= 4.0
        ):
            return False

        ix, iy = int(x), int(y)
        fx, fy = ix + 0.5 - x, iy + 0.5 - y
        iz_scaled = int(z * 1.25)
        distance = math.sqrt(fx * fx + fy * fy + iz_scaled * iz_scaled)
        distance_xy = math.sqrt(fx * fx + fy * fy)
        map_index = ix + self.n_map_width * iy
        tile = self.g_map[map_index]

        if tile == "#" and -1.0 < z < 1.0:
            return False

        if tile == "=" and distance < 0.5:
            self.update_map(ix, iy, 3)
            self.time_data.elapsed_time = 0.0
            self.game_data.score += 1
            return False

        if tile == "*" and distance < 0.5:
            self.update_map(ix, iy, 2)
            self.time_data.elapsed_time = 0.0
            return False

        if tile == "+" and -0.5 < z < 0.5 and distance_xy < 0.15:
            self.update_map(ix, iy, 1)
            self.time_data.elapsed_time = 0.0
            self.game_data.score += 1
            return False

        return True

    def display_map(self) -> None:
        """
        Draw a top‐down view of the map into screen_data.screen.
        Uses color logic based on tile type and proximity.
        """
        fpx = self.player_data.player_x
        fpy = self.player_data.player_y
        screen = self.screen_data.screen

        size = (
            self.map_size / math.sqrt(self.pixel_size)
            if self.pixel_size < 5
            else self.map_size * 4 / self.pixel_size
        )

        for i in range(int(size * (-self.buffer)), int(size * (self.n_map_width + self.buffer))):
            for j in range(int(size * (-self.buffer)), int(size * (self.n_map_height + self.buffer))):
                color: tuple[int, int, int] = (0, 0, 100)

                if i < 0 or j < 0 or i >= self.n_map_width * size or j >= self.n_map_height * size:
                    color = (50, 20, 80)
                else:
                    tile_x = int(i // size)
                    tile_y = int(j // size)
                    map_char = self.g_map[tile_x + self.n_map_width * tile_y]

                    # Player cell = green
                    if tile_x == int(fpx) and tile_y == int(fpy):
                        color = (0, 255, 0)
                    elif map_char in ("+", "=", "*"):
                        highlight = self._highlight_for(tile_x, tile_y, map_char)
                        color = highlight if highlight else (0, 0, 100)
                    elif map_char == "#":
                        color = (200, 200, 200)
                    elif map_char == "$":
                        color = (200, 200, 0)
                    elif map_char == "-":
                        color = (0, 20, 150)
                    """else:
                        color = (0, 0, 100)"""

                x_pix = i + int(self.h_indent * size)
                y_pix = j + int(self.v_indent * size)
                screen[x_pix][y_pix] = color

        self.screen_data.screen = screen

    def _highlight_for(self, tile_x: int, tile_y: int, map_char: str):
        """
        If any of the 8 neighbors is '-', return a special color based on map_char.
        Otherwise, return None.
        """
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx = tile_x + dx
                ny = tile_y + dy
                if 0 <= nx < self.n_map_width and 0 <= ny < self.n_map_height:
                    neighbor = self.g_map[nx + self.n_map_width * ny]
                    if neighbor == "-":
                        if map_char == "+":
                            return 200, 100, 0
                        if map_char == "=":
                            return 200, 50, 0
                        if map_char == "*":
                            return 200, 0, 0
        return None

    def create_enemies(self) -> None:
        """
        Instantiate Enemy objects wherever the map character is '*', '+', or '='.
        '*' → level 2; '+' → level 1; '=' → both level 1 and level 2.
        """
        for i in range(self.n_map_width):
            for j in range(self.n_map_height):
                char = self.g_map[i + self.n_map_width * j]
                if char == "*":
                    self.Enemy(2, i, j)
                elif char == "+":
                    self.Enemy(1, i, j)
                elif char == "=":
                    self.Enemy(1, i, j)
                    self.Enemy(2, i, j)

    def update_enemies(self) -> None:
        """
        1) Erase all previous enemy markers ('*','+','=','-') by setting to '.'.
        2) Call each Enemy.update(...) to move them toward the player.
        3) Re‐place markers based on each Enemy's new position and level.
        """
        # 1) Erase any tile in g_map if it’s in ("*", "+", "=", "-")
        for idx, ch in enumerate(self.g_map):
            if ch in ("*", "+", "=", "-"):
                x = idx % self.n_map_width
                y = idx // self.n_map_width
                self.update_map(x, y, 1)  # status=1 → becomes '.'

        # 2) Move each enemy
        px = self.player_data.player_x
        py = self.player_data.player_y
        for enemy in self.Enemy.enemies:
            enemy.update(px, py)

        # 3) Place new markers
        for enemy in self.Enemy.enemies:
            ix = int(enemy.x)
            iy = int(enemy.y)
            idx = ix + self.n_map_width * iy
            old_char = self.g_map[idx]
            if old_char in ("+", "*"):
                self.update_map(ix, iy, 4)  # status=4 → '='
            else:
                self.update_map(ix, iy, enemy.level + 1)


class ScreenData:
    """
    Holds resolution, buffer, indent, and the surface reference.
    """

    def __init__(
        self,
        game_data: "GameData",
        scr: list[list[tuple[int, int, int]]] | None = None,
        screen_width: int = 225,
        screen_height: int = 150,
        h_indent: int = 2,
        v_indent: int = 2,
        buffer: int = 2,
        map_size: int = 4,
        pixel_size: int = 8,
    ):
        self.game_data = game_data

        self.screen_width = screen_width
        self.screen_height = screen_height

        self.h_indent = h_indent
        self.v_indent = v_indent
        self.buffer = buffer
        self.map_size = map_size
        self.pixel_size = pixel_size

        self.center = (
            int(self.screen_width * self.pixel_size / 2),
            int(self.screen_height * self.pixel_size / 2),
        )
        self.screen = scr


class PlayerData:
    """
    Tracks the player's (x, y), angle, and provides move/look methods.
    """

    def __init__(
        self,
        game_data: "GameData",
        f_player_x: float = 8.0,
        f_player_y: float = 14.0,
        f_player_a: float = math.pi,
        scope: float = 0.0,
        vert_angle: float = 0.0,
    ):
        self.player_x = f_player_x
        self.player_y = f_player_y
        self.player_a = f_player_a

        self.scope = scope
        self.vertical_angle = vert_angle

        self.game_data = game_data
        self.time_data = game_data.time_data

    def __post_init__(self):
        self.map_data = self.game_data.map_data

    def move(self, direction: str) -> None:
        """
        Move or rotate the player:
         - 's_left'/'s_right' → rotate in place
         - 'left'/'right'/'forward'/'back' → translate
        Prevents walking through '#' (walls).
        """
        max_x = self.map_data.n_map_width - 1.0
        max_y = self.map_data.n_map_height - 1.0
        # Clamp current position
        self.player_x = max(0.0, min(self.player_x, max_x))
        self.player_y = max(0.0, min(self.player_y, max_y))

        speed_time = self.game_data.player_speed * self.time_data.elapsed_time
        cos_a = math.cos(self.player_a)
        sin_a = math.sin(self.player_a)
        width = self.map_data.n_map_width
        height = self.map_data.n_map_height
        gmap = self.map_data.g_map

        def is_wall(x: float, y: float) -> bool:
            ix, iy = int(x), int(y)
            if ix < 0 or ix >= width or iy < 0 or iy >= height:
                return True
            return gmap[ix + width * iy] == "#"

        # Pure rotation:
        if direction == "s_left":
            self.player_a -= speed_time
            return
        if direction == "s_right":
            self.player_a += speed_time
            return

        # Compute dx, dy for translation:
        if direction == "right":  # strafe right
            dx = -sin_a * speed_time
            dy = cos_a * speed_time
        elif direction == "left":  # strafe left
            dx = sin_a * speed_time
            dy = -cos_a * speed_time
        elif direction == "forward":
            dx = cos_a * speed_time
            dy = sin_a * speed_time
        elif direction == "back":
            dx = -cos_a * speed_time
            dy = -sin_a * speed_time
        else:
            return  # unrecognized → no movement

        # Attempt to move on X axis
        new_x = self.player_x + dx
        if not is_wall(new_x, self.player_y):
            self.player_x = new_x

        # Attempt to move on Y axis
        new_y = self.player_y + dy
        if not is_wall(self.player_x, new_y):
            self.player_y = new_y

    def look(self, angle: tuple[int, int]) -> None:
        """
        Adjust yaw/pitch based on mouse position (angle = (mouse_x, mouse_y)).
        The "center" of the screen_data is the pivot.
        """
        center_x, center_y = self.game_data.screen_data.center
        diff_h = angle[0] - center_x
        diff_v = angle[1] - center_y

        speed_scaled = self.game_data.player_speed * 0.80
        elapsed = self.time_data.elapsed_time
        pixel_size = self.game_data.pixel_size

        # Horizontal rotation (yaw)
        if diff_h != 0:
            yaw_delta = speed_scaled * elapsed * diff_h * pixel_size / 120
            self.player_a += yaw_delta

        # Vertical rotation (pitch)
        if diff_v != 0:
            pitch_delta = speed_scaled * elapsed * diff_v * pixel_size / 4
            self.vertical_angle -= pitch_delta

            # Clamp pitch back into [-100, +100]
            if not (-100 <= self.vertical_angle <= 100):
                self.vertical_angle += pitch_delta
