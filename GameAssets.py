# GameAssets.py

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from GameData import GameData


class Enemy:
    enemies: list["Enemy"] = []

    def __init__(
        self,
        game_data: "GameData",
        level: int,
        x: float,
        y: float,
        agro_range: int = 10,
    ):
        self.level = level
        self.x = x
        self.y = y
        self.agro_range = agro_range

        # pull in all the game‐wide settings via the passed‐in reference
        self.game_data = game_data
        self.n_map_width = game_data.map_data.n_map_width
        self.map_data = game_data.map_data
        self.f_speed = game_data.player_speed
        self.f_enemy_speed = game_data.enemy_speed
        self.time_data = game_data.time_data
        # self.player_data = game_data.player_data  # uncomment if needed

        Enemy.enemies.append(self)

    def update(self, player_x: float, player_y: float):
        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.hypot(dx, dy)
        if 0 < dist < self.agro_range:
            self.move(dx / dist, dy / dist)

    def move(self, vx: float, vy: float):
        multiplier = 2 if self.level == 1 else 1
        speed_factor = (
            self.f_speed * self.time_data.elapsed_time * self.f_enemy_speed * multiplier
        )

        x_new = self.x + vx * speed_factor
        y_new = self.y + vy * speed_factor

        # simple collision check against wall (‘#’)
        if (
            abs(x_new - self.x) <= 1
            and self.map_data.g_map[int(x_new) + self.n_map_width * int(self.y)] != "#"
        ):
            self.x = x_new

        if (
            abs(y_new - self.y) <= 1
            and self.map_data.g_map[int(self.x) + self.n_map_width * int(y_new)] != "#"
        ):
            self.y = y_new


class Bullet:
    bullets: list["Bullet"] = []

    def __init__(
        self,
        game_data: "GameData",
        x: float,
        y: float,
        z: float,
        vx: float,
        vy: float,
        vz: float,
    ):
        self.x = x
        self.y = y
        self.z = z
        self.vx = vx
        self.vy = vy
        self.vz = vz

        self.game_data = game_data
        # self.player_data = game_data.player_data  # uncomment if needed
        Bullet.bullets.append(self)

    def move(self):
        dt = self.game_data.time_data.elapsed_time
        fs = self.game_data.player_speed
        self.x += self.vx * fs * dt
        self.y += self.vy * fs * dt
        self.z += self.vz * fs * dt


class GameAssets:
    def __init__(self, game_data: "GameData"):
        self.game_data = game_data
        # these always reflect all active enemies/bullets
        self.Enemy = Enemy
        self.Bullet = Bullet
        self.player_data = game_data.player_data

    def add_bullet(self) -> Bullet:
        fv_x = math.cos(self.player_data.player_a)
        fv_y = math.sin(self.player_data.player_a)
        fv_z = 0.6877944 * self.player_data.vertical_angle / 100.0
        v_len = math.sqrt(fv_x * fv_x + fv_y * fv_y + fv_z * fv_z)

        shot = Bullet(
            self.game_data,
            self.player_data.player_x,
            self.player_data.player_y,
            0.0,
            fv_x / v_len,
            fv_y / v_len,
            fv_z / v_len,
        )
        return shot
