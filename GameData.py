# GameData.py

import math
import pygame

from Data import TimeData, MapData, PlayerData, ScreenData
from GameAssets import GameAssets


class GameData:
    """
    Main game‐state: holds flags, subsystems (time_data, map_data, …), and runs the main loop.
    """

    WHITE = (255, 255, 255)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 128)

    # State flags
    resized = True
    load_enemy = False
    zoom = False
    s_left = False
    s_right = False
    left = False
    right = False
    forward = False
    back = False
    escape = False
    run = True
    win = False

    def __init__(
            self,
            score: int = 0,
            pixel_size: int = 8,
            zoom_fov: float = math.pi / 7.0,
            no_zoom_fov: float = math.pi / 4.0,
            default_fov: float = math.pi / 4.0,  # Not editable
            depth: float = 16.0,
            player_speed: float = 3.0,
            enemy_speed: float = 0.5,
            bullet_speed: float = 7.0,
            agro_range: float = 10.0,
    ):
        # We'll fill these in later during `execute()`
        self.crosshair_rect = None
        self.score_rect = None
        self.mag_rect = None
        self.crosshair_surf = None

        # Initialize subsystems in the correct order:
        self.time_data = TimeData(self)
        self.screen_data = ScreenData(self)
        self.player_data = PlayerData(self)
        self.map_data = MapData(self)
        self.game_assets = GameAssets(self)
        self.player_data.__post_init__()
        self.map_data.__post_init__()

        # Score & graphics
        self.score = score
        self.pixel_size = pixel_size

        # FOV & movement parameters
        self.zoom_fov = zoom_fov
        self.no_zoom_fov = no_zoom_fov
        self.default_fov = default_fov
        self.depth = depth
        self.player_speed = player_speed
        self.enemy_speed = enemy_speed
        self.bullet_speed = bullet_speed
        self.agro_range = agro_range

    def event_checker(self, events: list[pygame.event.EventType]) -> None:
        """
        Process all pending Pygame events and toggle internal flags accordingly.
        """
        for event in events:
            if event.type == pygame.QUIT:
                self.run = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:  # Right‐click → zoom in
                    self.player_data.scope = 10
                    self.player_data.zoom = True
                elif event.button == 1 and len(self.game_assets.Bullet.bullets) < 3:
                    self.game_assets.add_bullet()

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 3:  # Release right‐click → zoom out
                    self.player_data.scope = 0
                    self.player_data.zoom = False

            elif event.type in (pygame.KEYDOWN, pygame.KEYUP):
                # Escape toggles on KEYDOWN only
                if event.key == pygame.K_ESCAPE and event.type == pygame.KEYDOWN:
                    self.escape = not self.escape

                # Tab toggles screen resize on KEYDOWN
                if event.key == pygame.K_TAB and event.type == pygame.KEYDOWN:
                    self.resized = True

                # Movement keys toggle on press & release
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    self.left = not self.left
                if event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.right = not self.right
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.forward = not self.forward
                if event.key in (pygame.K_DOWN, pygame.K_s):
                    self.back = not self.back
                if event.key == pygame.K_q:
                    self.s_left = not self.s_left
                if event.key == pygame.K_e:
                    self.s_right = not self.s_right

    def _handle_resize(
            self,
            screen: pygame.Surface,
            full_w: int,
            full_h: int,
    ) -> pygame.Surface:
        """
        Switch between full screen and fixed‐size mode when resized is True.
        Returns the new pygame.Surface.
        """
        target_w = int(225 * 4 / self.pixel_size)
        target_h = int(150 * 4 / self.pixel_size)

        # Fixed-size toggle
        if (self.screen_data.screen_width, self.screen_data.screen_height) != (target_w, target_h):
            self.screen_data.screen_width = target_w
            self.screen_data.screen_height = target_h
            screen = pygame.display.set_mode(
                (target_w * self.pixel_size, target_h * self.pixel_size),
                pygame.DOUBLEBUF,
            )
        else:
            screen = pygame.display.set_mode(
                (0, 0),
                pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE,
            )
            self.screen_data.screen_width = full_w // self.pixel_size
            self.screen_data.screen_height = full_h // self.pixel_size

        # Recompute center
        cw = self.screen_data.screen_width
        ch = self.screen_data.screen_height
        center_x = cw * self.pixel_size // 2
        center_y = ch * self.pixel_size // 2
        self.screen_data.center = (center_x, center_y)

        # Update crosshair & UI positions
        if self.crosshair_rect:
            self.crosshair_rect.center = (center_x, center_y)
        if self.score_rect:
            self.score_rect.topright = (
                cw * self.pixel_size - 190,
                10,
            )
        if self.mag_rect:
            self.mag_rect.bottomright = (
                cw * self.pixel_size - 60,
                ch * self.pixel_size,
            )

        self.resized = False
        return screen

    def _update_movement_and_zoom(self) -> None:
        """
        Apply movement flags (left..., back) to move player,
        then adjust the FOV according to zoom.
        """
        if self.s_left:
            self.player_data.move("s_left")
        if self.s_right:
            self.player_data.move("s_right")
        if self.left:
            self.player_data.move("left")
        if self.right:
            self.player_data.move("right")
        if self.forward:
            self.player_data.move("forward")
        if self.back:
            self.player_data.move("back")

        self.player_data.fFOV = self.zoom_fov if self.zoom else self.no_zoom_fov

    def _draw_ui(self, screen: pygame.Surface, font: pygame.font.Font) -> None:
        """
        Draw crosshair, score, and magazine count.
        """
        screen.blit(self.crosshair_surf, self.crosshair_rect)

        score_surf = font.render(f"SCORE = {self.score}", True, self.GREEN)
        screen.blit(score_surf, self.score_rect)

        bullets_left = 3 - len(self.game_assets.Bullet.bullets)
        mag_surf = font.render(f"{bullets_left}/3", False, (0, 0, 0))
        screen.blit(mag_surf, self.mag_rect)

    def execute(self) -> None:
        """
        Main game loop.
        """
        pygame.init()

        # Start in fullscreen
        screen = pygame.display.set_mode(
            (0, 0), pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE
        )
        full_w, full_h = screen.get_size()
        # Initialize ScreenData from actual fullscreen dims
        self.screen_data.screen_width = full_w // self.pixel_size
        self.screen_data.screen_height = full_h // self.pixel_size

        # Try setting a simple crosshair cursor
        try:
            pygame.mouse.set_cursor(pygame.cursors.broken_x)
        except pygame.error:
            print("Cursor setting is not supported in this environment")
            self.run = False

        # Pre-render crosshair and UI rects
        font = pygame.font.Font("freesansbold.ttf", 32)
        self.crosshair_surf = font.render("+", True, self.WHITE)
        self.crosshair_rect = self.crosshair_surf.get_rect()
        self.crosshair_rect.center = self.screen_data.center

        self.score_rect = self.crosshair_surf.get_rect()
        cw = self.screen_data.screen_width
        ch = self.screen_data.screen_height
        self.score_rect.topright = (cw * self.pixel_size - 160, 10)

        self.mag_rect = self.crosshair_surf.get_rect()
        self.mag_rect.bottomright = (cw * self.pixel_size - 40, ch * self.pixel_size)

        while self.run:
            if self.resized:
                screen = self._handle_resize(screen, full_w, full_h)
            else:
                self.main()

            self._update_movement_and_zoom()

            # Center‐mouse look
            mouse_pos = pygame.mouse.get_pos()
            if not self.escape and mouse_pos != self.screen_data.center:
                self.player_data.look(mouse_pos)
                pygame.mouse.set_pos(self.screen_data.center)

            pygame.mouse.set_visible(self.escape)

            # Process events
            self.event_checker(pygame.event.get())

            # Draw UI
            self._draw_ui(screen, font)

            pygame.display.flip()

        pygame.quit()

        # Print final result
        if self.win:
            print("You WON\nYour score is", self.score)
        else:
            print("You LOST\nYour score is", self.score)

    def main(self) -> None:
        """
        Placeholder for per-frame game logic: (e.g., move bullets, check collisions, draw 3D view, etc.)
        """
        self.time_data.time_update()

        if self.time_data.elapsed_time == 0:
            self.map_data.create_enemies()

        self.map_data.update_enemies()

        for x in range(0, nScreenWidth):
            fRayAngle = (fPlayerA - fFOV / 2.0) + (float(x) / float(nScreenWidth)) * fFOV
            fStepSize = 0.1
            fDistanceToWall = 0.0
            bHitWall = False
            fDistanceToEnemy = 100.0
            bHitShield = False
            bHitEnemy = False
            bBoundary = False
            fEyeX = cos(fRayAngle)
            fEyeY = sin(fRayAngle)
            x_temp = 0.0
            delta_distX = math.sqrt(1 + (fEyeY ** 2) / (fEyeX ** 2)) if abs(fEyeX) > 0.0001 else 999999
            delta_distY = math.sqrt(1 + (fEyeX ** 2) / (fEyeY ** 2)) if abs(fEyeY) > 0.0001 else 999999
            mapX = int(fPlayerX)
            mapY = int(fPlayerY)
            side = 0
            if fEyeX < 0:
                stepX = -1
                sideDistX = (fPlayerX - float(mapX)) * delta_distX
            else:
                stepX = 1
                sideDistX = (float(mapX + 1) - fPlayerX) * delta_distX
            if fEyeY < 0:
                stepY = -1
                sideDistY = (fPlayerY - float(mapY)) * delta_distY
            else:
                stepY = 1
                sideDistY = (float(mapY + 1) - fPlayerY) * delta_distY

            while not bHitWall and fDistanceToWall < fDepth:
                if sideDistX < sideDistY:
                    fDistanceToWall = sideDistX * cos(abs(fRayAngle - fPlayerA))
                    mapX += stepX
                    sideDistX += delta_distX
                    side = 5 * (sin(fPlayerA) ** 2)
                else:
                    fDistanceToWall = sideDistY * cos(abs(fRayAngle - fPlayerA))
                    mapY += stepY
                    sideDistY += delta_distY
                    side = 5 * (cos(fPlayerA) ** 2)

                if mapX < 0 or mapX >= nMapWidth or mapY < 0 or mapY >= nMapHeight:
                    bHitWall = True
                    fDistanceToWall = fDepth
                else:
                    if g_map[int(mapX + nMapWidth * mapY)] == '.':
                        update_map(mapX, mapY, -1)
                    elif not bHitEnemy and not bHitShield and g_map[int(mapX + nMapWidth * mapY)] == '+':
                        tester_x = fPlayerX + fEyeX * fDistanceToWall
                        tester_y = fPlayerY + fEyeY * fDistanceToWall
                        while not bHitEnemy:
                            distance = math.sqrt((mapX + 0.5 - tester_x) ** 2 + (mapY + 0.5 - tester_y) ** 2)
                            if distance <= 0.15:
                                bHitEnemy = True
                                fDistanceToEnemy = math.sqrt(
                                    (tester_x - fPlayerX) ** 2 + (tester_y - fPlayerY) ** 2)
                            elif abs(tester_x - mapX) > 2.0 or abs(tester_x - mapX) > 2.0:
                                break
                            else:
                                tester_x += fEyeX * fStepSize
                                tester_y += fEyeY * fStepSize

                    elif not bHitEnemy and not bHitShield and (g_map[int(mapX + nMapWidth * mapY)] == '*'
                                                               or g_map[int(mapX + nMapWidth * mapY)] == '='):
                        tester_x = fPlayerX + fEyeX * fDistanceToWall
                        tester_y = fPlayerY + fEyeY * fDistanceToWall
                        while not bHitShield:

                            distance = math.sqrt((mapX + 0.5 - tester_x) ** 2 + (mapY + 0.5 - tester_y) ** 2)

                            if distance <= 0.5:
                                bHitShield = True
                                fDistanceToEnemy = math.sqrt(
                                    (tester_x - fPlayerX) ** 2 + (tester_y - fPlayerY) ** 2)

                                # Circle calculations
                                VectorAx, VectorAy = mapX + 0.5 - tester_x, mapY + 0.5 - tester_y
                                VectorBx, VectorBy = mapX + 0.5 - fPlayerX, mapY + 0.5 - fPlayerY

                                VectorA_len = math.sqrt(VectorAx ** 2 + VectorAy ** 2)
                                VectorB_len = math.sqrt(VectorBx ** 2 + VectorBy ** 2)

                                theta = math.acos(
                                    (VectorAx * VectorBx + VectorAy * VectorBy) / (VectorA_len * VectorB_len))
                                x_temp = sin(theta) * VectorA_len
                            elif abs(tester_x - mapX) > 2.0 or abs(tester_x - mapX) > 2.0:
                                break
                            else:
                                tester_x += fEyeX * fStepSize
                                tester_y += fEyeY * fStepSize

                    if g_map[int(mapX + nMapWidth * mapY)] == '#':
                        bHitWall = True
                        p = []

                        for tx in range(0, 2):
                            for ty in range(0, 2):
                                vx = float(mapX + tx - fPlayerX)
                                vy = float(mapY + ty - fPlayerY)
                                d = math.sqrt(vx * vx + vy * vy)
                                dot = (fEyeX * vx / d) + (fEyeY * vy / d)
                                p.append([d, dot])

                        p.sort()
                        fBound = 0.01

                        if math.acos(p[0][1]) < fBound:
                            bBoundary = True
                        if math.acos(p[1][1]) < fBound:
                            bBoundary = True
                        if math.acos(p[2][1]) < fBound:
                            bBoundary = True

            nCeiling = float(nScreenHeight / 2.0) - (
                    nScreenHeight / float(fDistanceToWall)) - scope + vertical_angle
            nFloor = float(nScreenHeight / 2.0) + (nScreenHeight / float(fDistanceToWall)) + scope + vertical_angle
            if fDistanceToWall >= fDepth:
                nCeiling = int(nScreenHeight / 2.0) + vertical_angle
                nFloor = int(nScreenHeight / 2.0) + vertical_angle
            nCeilingAntiAliasing = nCeiling - int(nCeiling)
            nFloorAntiAliasing = 1 + int(nFloor) - nFloor

            enemy_ceiling = float(nScreenHeight / 2.0) - (
                    nScreenHeight / float(fDistanceToEnemy)) - scope + vertical_angle
            enemy_floor = float(nScreenHeight / 2.0) + (
                    nScreenHeight / float(fDistanceToEnemy)) + scope + vertical_angle

            enemy_radius = (enemy_ceiling - enemy_floor) / 2.0
            middle = (enemy_ceiling + enemy_floor) / 2.0

            enemy_height = math.sqrt(enemy_radius ** 2 - (x_temp * enemy_radius / 0.5) ** 2)

            for y in range(0, nScreenHeight):
                if bHitEnemy and middle - enemy_height / 2.0 < y <= middle + enemy_height / 2.0 and x_temp <= 0.1:
                    color = (255, random.randint(100, 150), 0)

                elif bHitShield and middle - enemy_height / 2.0 < y <= middle + enemy_height / 2.0 and x_temp <= 0.1:
                    color = (255, random.randint(100, 150), 0)

                elif bHitShield and middle - enemy_height < y <= middle + enemy_height:
                    color = (random.randint(0, 255), 0, 0)

                elif y < int(nCeiling):
                    shade = int((255 * (nScreenHeight / 2.0) / (y + nScreenHeight / 2.0)) / 2)
                    color = (int(shade / 2), 0, shade)

                # Ceiling to Wall Anti-Aliasing
                elif y == int(nCeiling):
                    if fDistanceToWall < fDepth:
                        shadeCeiling = 255 - int((255 * (nScreenHeight / 2.0) / (y + nScreenHeight / 2.0)) / 2)
                        shadeWall = int(fDistanceToWall * 255 / fDepth) * ((1 + side) / 6)
                        shade = abs(shadeWall * (1 - nCeilingAntiAliasing) + shadeCeiling * nCeilingAntiAliasing)
                        color = (int(shade / 5), 0, 255 - int(shade))
                    else:
                        color = (0, 0, 0)

                elif int(nCeiling) < y < int(nFloor):
                    if fDistanceToWall < fDepth:
                        shade = abs(int(fDistanceToWall * 255 / fDepth) * ((1 + side) / 6))
                    else:
                        shade = 255
                    color = (0, 0, 255 - int(shade)) if bBoundary else (0, 0, int(255 / 1.1) - int(shade / 1.1))

                # Wall to Floor Anti-Aliasing
                elif y == int(nFloor):
                    if fDistanceToWall < fDepth:
                        shadeFloor = int(
                            ((1.7 + 1.7 * (vertical_angle + 50) / 200) * (y - nScreenHeight + 0.0) + 255) / 2.0)
                        shadeWall = 255 - int(fDistanceToWall * 255 / fDepth) * ((1 + side) / 6)
                        shade = abs(shadeWall * (1 - nFloorAntiAliasing) + shadeFloor * nFloorAntiAliasing)
                    else:
                        shade = 0
                    color = (0, 0, int(shade))

                else:
                    shade = int(((1.7 + 1.7 * (vertical_angle + 50) / 200) * (y - nScreenHeight + 0.0) + 255) / 2.0)
                    color = (0, 0, shade)

                screen[x][y] = color

        for i in range(fBulletSpeed):
            for bul in bullets:
                x, y, z = bul.x, bul.y, bul.z
                if not check_collisions(x, y, z):
                    bullets.remove(bul)
                    del bul
                else:
                    bul.move()

        display_bullets()

        display_map()

        if (g_map[int(fPlayerX) + nMapWidth * int(fPlayerY)] == "*"
                or g_map[int(fPlayerX) + nMapWidth * int(fPlayerY)] == "+"
                or g_map[int(fPlayerX) + nMapWidth * int(fPlayerY)] == "="):
            run = False
        elif g_map[int(fPlayerX) + nMapWidth * int(fPlayerY)] == "$":
            win = True
            run = False

        for y in range(0, nScreenHeight):
            for x in range(0, nScreenWidth):
                pixel = pygame.Rect((x * pixel_size, y * pixel_size, pixel_size, pixel_size))
                pygame.draw.rect(screen2, "#{:02x}{:02x}{:02x}".format(*screen[x][y]), pixel)
        print(1 / elapsedTime if elapsedTime != 0.0 else 0)

        print(1 / self.time_data.elapsed_time if self.time_data.elapsed_time != 0.0 else 0)
        pass

