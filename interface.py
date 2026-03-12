import pygame
import sys
import math
import random
import time
import threading
from pygame import gfxdraw
from enum import Enum

# Import solver classes
try:
    from Board import Board
    from Knight import Knight
    from KnightTourSolver import KnightTourSolver
except ImportError as e:
    print(f"Warning: Solver modules not found. {e}")
    Board = None
    Knight = None
    KnightTourSolver = None

# Initialisation de Pygame
pygame.init()

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 650
BOARD_SIZE = 8
CELL_SIZE = 55
BOARD_OFFSET_X = 40
BOARD_OFFSET_Y = 120
FPS = 60

# États du jeu
class GameState(Enum):
    MENU = "MENU"
    ALGORITHM_SELECT = "ALGORITHM_SELECT"
    COMPARING = "COMPARING"
    SOLVING = "SOLVING"
    PLAYING = "PLAYING"
    PAUSED = "PAUSED"
    SOLUTION_COMPLETE = "SOLUTION_COMPLETE"
    SETTINGS = "SETTINGS"

class Colors:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    PRIMARY_BLUE = (41, 128, 185)
    PRIMARY_GREEN = (46, 204, 113)
    PRIMARY_PURPLE = (155, 89, 182)
    PRIMARY_ORANGE = (230, 126, 34)
    PRIMARY_RED = (231, 76, 60)
    ACCENT_CYAN = (52, 152, 219)
    ACCENT_TEAL = (26, 188, 156)
    CHESS_LIGHT = (200, 230, 255)
    CHESS_DARK = (135, 206, 235)
    SKY_BLUE = (135, 206, 235)
    DEEP_BLUE = (25, 25, 112)
    GOLD = (255, 215, 0)
    GRAY = (128, 128, 128)
    DARK_GRAY = (64, 64, 64)
    LIGHT_GRAY = (200, 200, 200)

class Particle:
    def __init__(self, x, y, color, velocity=None, size=None, lifetime=30):
        self.x = x
        self.y = y
        self.vx = velocity[0] if velocity else random.uniform(-3, 3)
        self.vy = velocity[1] if velocity else random.uniform(-3, 3)
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size if size else random.randint(2, 6)
        self.gravity = 0.1

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.lifetime -= 1
        self.size = max(1, self.size * (self.lifetime / self.max_lifetime))

    def draw(self, screen):
        if self.lifetime > 0:
            alpha = int(255 * (self.lifetime / self.max_lifetime))
            color = (*self.color[:3], alpha) if len(self.color) == 4 else self.color
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), int(self.size))

class Star:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.size = random.randint(1, 3)
        self.brightness = random.uniform(0.3, 1.0)
        self.twinkle_speed = random.uniform(0.02, 0.05)

    def update(self):
        self.brightness = 0.5 + 0.5 * math.sin(time.time() * self.twinkle_speed)

    def draw(self, screen):
        color = int(255 * self.brightness)
        pygame.draw.circle(screen, (color, color, color), (self.x, self.y), self.size)

class Button:
    def __init__(self, x, y, width, height, text, action, color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.action = action
        if color is None:
            if "play" in action or "solve" in action or "compare" in action: color = Colors.PRIMARY_GREEN
            elif "basic" in action: color = Colors.PRIMARY_BLUE
            elif "enhanced" in action: color = Colors.PRIMARY_ORANGE
            elif "restart" in action: color = Colors.PRIMARY_BLUE
            elif "quit" in action: color = Colors.PRIMARY_RED
            else: color = Colors.ACCENT_TEAL

        self.color = color
        self.hover_color = tuple(min(255, c + 30) for c in self.color)
        self.pressed_color = tuple(max(0, c - 20) for c in self.color)
        self.is_hovered = False
        self.is_pressed = False
        self.animation_offset = 0
        self.particles = []
        self.glow_intensity = 0

    def update(self, mouse_pos, mouse_clicked):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

        if self.is_hovered:
            self.animation_offset = min(4, self.animation_offset + 0.4)
            self.glow_intensity = min(1.0, self.glow_intensity + 0.08)
            if random.random() < 0.05:
                self.particles.append(
                    Particle(random.randint(self.rect.left, self.rect.right),
                           random.randint(self.rect.top, self.rect.bottom),
                           self.color, lifetime=15))
        else:
            self.animation_offset = max(0, self.animation_offset - 0.4)
            self.glow_intensity = max(0, self.glow_intensity - 0.08)

        if self.is_hovered and mouse_clicked:
            self.is_pressed = True
        else:
            self.is_pressed = False

        for particle in self.particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                self.particles.remove(particle)

    def draw(self, screen, font):
        for particle in self.particles:
            particle.draw(screen)

        button_rect = self.rect.copy()
        button_rect.y -= self.animation_offset

        if self.glow_intensity > 0:
            glow_size = int(8 + self.glow_intensity * 8)
            glow_surf = pygame.Surface((button_rect.width + glow_size*2,
                                        button_rect.height + glow_size*2), pygame.SRCALPHA)
            glow_alpha = int(60 + self.glow_intensity * 40)
            pygame.draw.rect(glow_surf, (*self.hover_color, glow_alpha),
                            glow_surf.get_rect(), border_radius=12)
            screen.blit(glow_surf, (button_rect.x - glow_size, button_rect.y - glow_size))

        shadow_rect = button_rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 60), shadow_rect, border_radius=10)
        screen.blit(shadow_surf, shadow_rect)

        color = self.pressed_color if self.is_pressed else (self.hover_color if self.is_hovered else self.color)
        pygame.draw.rect(screen, color, button_rect, border_radius=10)
        border_color = tuple(min(255, c + 50) for c in color) if self.is_hovered else tuple(max(0, c - 30) for c in self.color)
        pygame.draw.rect(screen, border_color, button_rect, 3, border_radius=10)

        if not self.is_pressed:
            highlight_rect = pygame.Rect(button_rect.x + 6, button_rect.y + 4,
                                         button_rect.width - 12, button_rect.height // 4)
            highlight_surf = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
            for i in range(highlight_rect.height):
                alpha = int(40 * (1 - i / highlight_rect.height))
                pygame.draw.line(highlight_surf, (255, 255, 255, alpha),
                                (0, i), (highlight_rect.width, i))
            screen.blit(highlight_surf, highlight_rect)

        offset_y = 2 if self.is_pressed else 0
        shadow_text = font.render(self.text, True, (0, 0, 0))
        shadow_rect = shadow_text.get_rect(center=(button_rect.centerx + 2,
                                                    button_rect.centery + 2 + offset_y))
        shadow_surf = pygame.Surface(shadow_text.get_size(), pygame.SRCALPHA)
        shadow_surf.blit(shadow_text, (0, 0))
        shadow_surf.set_alpha(100)
        screen.blit(shadow_surf, shadow_rect)

        text_surface = font.render(self.text, True, Colors.WHITE)
        text_rect = text_surface.get_rect(center=(button_rect.centerx,
                                                   button_rect.centery + offset_y))
        screen.blit(text_surface, text_rect)

    def is_clicked(self, mouse_pos, mouse_clicked):
        return self.rect.collidepoint(mouse_pos) and mouse_clicked

class KnightTourGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Knight's Tour - CSP Solver")
        self.clock = pygame.time.Clock()

        try:
            self.font_title = pygame.font.Font(None, 56)
            self.font_large = pygame.font.SysFont('arial', 36, bold=True)
            self.font_medium = pygame.font.SysFont('arial', 28, bold=True)
            self.font_small = pygame.font.SysFont('arial', 18)
        except:
            self.font_title = pygame.font.SysFont('arial', 56, bold=True)
            self.font_large = pygame.font.SysFont('arial', 36, bold=True)
            self.font_medium = pygame.font.SysFont('arial', 28, bold=True)
            self.font_small = pygame.font.SysFont('arial', 18)

        self.current_solution = None
        self.selected_algorithm = None
        self.solver_thread = None
        self.solving_stats = {}

        self.comparison_results = None
        self.state = GameState.MENU
        self.running = True
        self.current_move_index = 0
        self.animation_speed = 300
        self.last_move_time = 0

        self.particles = []
        self.stars = [Star() for _ in range(100)]

        self.show_grid = True
        self.auto_rotate = False
        self.rotation_angle = 0
        self.screen_shake = 0

        self.score = 0
        self.combo = 0
        self.moves_count = 0

        self.create_buttons()
        self.load_assets()

        self.menu_time = 0
        self.background_offset = 0

    def create_buttons(self):
        button_width = 320
        button_height = 55
        start_y = 230
        spacing = 75

        self.menu_buttons = [
            Button(SCREEN_WIDTH//2 - button_width//2, start_y, button_width, button_height,
                    "CHOISIR ALGO", "choose_algo", Colors.PRIMARY_GREEN),
            Button(SCREEN_WIDTH//2 - button_width//2, start_y + spacing, button_width, button_height,
                    "QUITTER", "quit", Colors.PRIMARY_RED)
        ]

        game_btn_x = SCREEN_WIDTH - 180
        game_btn_width = 160
        game_btn_height = 40

        self.game_buttons = [
            Button(game_btn_x, 105, game_btn_width, game_btn_height, "MENU", "menu", Colors.ACCENT_TEAL),
            Button(game_btn_x, 153, game_btn_width, game_btn_height, "PAUSE", "pause", Colors.PRIMARY_ORANGE),
            Button(game_btn_x, 201, game_btn_width, game_btn_height, "REDÉMARRER", "restart", Colors.PRIMARY_BLUE),
            Button(game_btn_x, 249, 75, game_btn_height, "-", "speed_down", Colors.LIGHT_GRAY),
            Button(game_btn_x + 85, 249, 75, game_btn_height, "+", "speed_up", Colors.PRIMARY_GREEN),
            Button(game_btn_x, 297, game_btn_width, game_btn_height, "GRILLE", "toggle_grid", Colors.PRIMARY_PURPLE),
            Button(game_btn_x, 345, game_btn_width, game_btn_height, "ROTATION", "toggle_rotation", Colors.ACCENT_CYAN)
        ]

        algo_button_width = 420
        algo_button_height = 58
        algo_start_y = 180
        algo_spacing = 75

        self.algorithm_buttons = [
            Button(SCREEN_WIDTH//2 - algo_button_width//2, algo_start_y, algo_button_width, algo_button_height,
                   "1. Backtracking", "solve_basic", Colors.PRIMARY_BLUE),
            Button(SCREEN_WIDTH//2 - algo_button_width//2, algo_start_y + algo_spacing, algo_button_width, algo_button_height,
                   "2. Backtracking + CSP", "solve_enhanced", Colors.PRIMARY_ORANGE),
            Button(SCREEN_WIDTH//2 - 85, SCREEN_HEIGHT - 100, 170, 45, "RETOUR", "menu", Colors.DARK_GRAY)
        ]

        self.comparison_buttons = [
            Button(SCREEN_WIDTH//2 - 85, SCREEN_HEIGHT - 100, 170, 45, "RETOUR", "menu", Colors.DARK_GRAY)
        ]

    def load_assets(self):
        self.knight_surface = pygame.Surface((CELL_SIZE-10, CELL_SIZE-10), pygame.SRCALPHA)
        self.draw_realistic_knight(self.knight_surface, CELL_SIZE//2-5, CELL_SIZE//2-5, 20)

        try:
            self.move_sound = None
            self.complete_sound = None
        except:
            self.move_sound = None
            self.complete_sound = None

    def draw_realistic_knight(self, surface, x, y, size):
        body_points = [(x - size//2, y - size//4), (x - size//3, y - size//2), (x + size//4, y - size//2), (x + size//2, y - size//4), (x + size//2, y + size//4), (x - size//2, y + size//4)]
        pygame.draw.polygon(surface, Colors.WHITE, body_points)
        pygame.draw.polygon(surface, Colors.BLACK, body_points, 2)
        head_points = [(x + size//4, y - size//2), (x + size//2, y - size//3), (x + size//2, y - size//6), (x + size//3, y - size//4)]
        pygame.draw.polygon(surface, Colors.WHITE, head_points)
        pygame.draw.polygon(surface, Colors.BLACK, head_points, 2)
        ear1_points = [(x + size//3, y - size//2), (x + size//3 + 3, y - size//2 - 8), (x + size//3 + 6, y - size//2)]
        pygame.draw.polygon(surface, Colors.WHITE, ear1_points)
        pygame.draw.polygon(surface, Colors.BLACK, ear1_points, 1)
        ear2_points = [(x + size//3 + 10, y - size//2), (x + size//3 + 13, y - size//2 - 8), (x + size//3 + 16, y - size//2)]
        pygame.draw.polygon(surface, Colors.WHITE, ear2_points)
        pygame.draw.polygon(surface, Colors.BLACK, ear2_points, 1)
        pygame.draw.circle(surface, Colors.BLACK, (x + size//3 + 8, y - size//3), 2)
        leg_width = 3
        legs = [[(x - size//3, y + size//4), (x - size//3, y + size//2)], [(x - size//6, y + size//4), (x - size//6, y + size//2)], [(x + size//6, y + size//4), (x + size//6, y + size//2)], [(x + size//3, y + size//4), (x + size//3, y + size//2)]]
        for leg in legs: pygame.draw.line(surface, Colors.BLACK, leg[0], leg[1], leg_width); pygame.draw.circle(surface, Colors.BLACK, leg[1], 3)
        tail_points = [(x - size//2, y), (x - size//2 - 10, y - size//6), (x - size//2 - 8, y + size//6)]
        pygame.draw.polygon(surface, Colors.WHITE, tail_points)
        pygame.draw.polygon(surface, Colors.BLACK, tail_points, 2)
        mane_points = [(x, y - size//2), (x - size//6, y - size//3), (x - size//6, y), (x, y - size//4)]
        pygame.draw.polygon(surface, Colors.BLACK, mane_points)

    def create_explosion(self, x, y, color, count=30):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 5)
            velocity = (speed * math.cos(angle), speed * math.sin(angle))
            self.particles.append(Particle(x, y, color, velocity, random.randint(2, 8), random.randint(20, 40)))

    def draw_background(self):
        for i in range(SCREEN_HEIGHT):
            progress = i / SCREEN_HEIGHT
            r = int(Colors.DEEP_BLUE[0] * (1 - progress) + Colors.SKY_BLUE[0] * progress)
            g = int(Colors.DEEP_BLUE[1] * (1 - progress) + Colors.SKY_BLUE[1] * progress)
            b = int(Colors.DEEP_BLUE[2] * (1 - progress) + Colors.SKY_BLUE[2] * progress)
            pygame.draw.line(self.screen, (r, g, b), (0, i), (SCREEN_WIDTH, i))

        for star in self.stars: star.update(); star.draw(self.screen)

        self.background_offset += 0.5
        mountain_offset = self.background_offset % 100
        mountain_points = [(0, SCREEN_HEIGHT // 2), (150, SCREEN_HEIGHT // 3), (300, SCREEN_HEIGHT // 2.5), (450, SCREEN_HEIGHT // 3.5), (600, SCREEN_HEIGHT // 2.8), (750, SCREEN_HEIGHT // 3.2), (900, SCREEN_HEIGHT // 2.6), (SCREEN_WIDTH, SCREEN_HEIGHT // 2), (SCREEN_WIDTH, SCREEN_HEIGHT), (0, SCREEN_HEIGHT)]
        pygame.draw.polygon(self.screen, (100, 100, 150), mountain_points)

        for i in range(3):
            x = (i * 400 + mountain_offset) % (SCREEN_WIDTH + 200) - 100
            y = 80 + i * 40
            self.draw_cloud(x, y)

    def draw_cloud(self, x, y):
        cloud_color = (255, 255, 255, 180)
        cloud_surf = pygame.Surface((120, 60), pygame.SRCALPHA)
        pygame.draw.ellipse(cloud_surf, cloud_color, (0, 20, 40, 40))
        pygame.draw.ellipse(cloud_surf, cloud_color, (20, 10, 40, 40))
        pygame.draw.ellipse(cloud_surf, cloud_color, (40, 15, 40, 40))
        pygame.draw.ellipse(cloud_surf, cloud_color, (60, 20, 40, 40))
        pygame.draw.ellipse(cloud_surf, cloud_color, (80, 25, 40, 35))
        self.screen.blit(cloud_surf, (x, y))

    def draw_menu(self):
        self.draw_background()
        title_offset = math.sin(self.menu_time * 2) * 3
        title_y = 100 + title_offset
        title_text = self.font_title.render("KNIGHT'S TOUR", True, Colors.PRIMARY_BLUE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, title_y))
        shadow_text = self.font_title.render("KNIGHT'S TOUR", True, Colors.BLACK)
        shadow_rect = shadow_text.get_rect(center=(SCREEN_WIDTH // 2 + 3, title_y + 3))
        self.screen.blit(shadow_text, shadow_rect)
        self.screen.blit(title_text, title_rect)

        subtitle = self.font_medium.render("CSP Solver", True, Colors.ACCENT_TEAL)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, title_y + 45))
        self.screen.blit(subtitle, subtitle_rect)

        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]

        for button in self.menu_buttons:
            button.update(mouse_pos, mouse_clicked)
            button.draw(self.screen, self.font_large)

        instructions = ["Clic gauche pour sélectionner", "ESC pour quitter"]
        y_offset = SCREEN_HEIGHT - 80
        for instruction in instructions:
            text = self.font_small.render(instruction, True, Colors.LIGHT_GRAY)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 25

    def draw_algorithm_select_screen(self):
        self.draw_background()
        title_text = self.font_title.render("CHOISIR L'ALGORITHME", True, Colors.WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title_text, title_rect)
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        for button in self.algorithm_buttons:
            button.update(mouse_pos, mouse_clicked)
            button.draw(self.screen, self.font_medium)

    def draw_comparison_screen(self):
        self.draw_background()
        title_text = self.font_title.render("RÉSULTATS", True, Colors.WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 60))
        self.screen.blit(title_text, title_rect)
        if self.comparison_results:
            y_offset = 140
            headers = ["Algorithme", "Étapes", "Backtracks", "Temps (s)"]
            col_widths = [250, 120, 120, 120]
            x_offset = (SCREEN_WIDTH - sum(col_widths)) // 2
            for i, header in enumerate(headers):
                text = self.font_medium.render(header, True, Colors.GOLD)
                text_rect = text.get_rect(center=(x_offset + sum(col_widths[:i]) + col_widths[i]//2, y_offset))
                self.screen.blit(text, text_rect)

            y_offset += 40
            pygame.draw.line(self.screen, Colors.GRAY, (x_offset, y_offset), (x_offset + sum(col_widths), y_offset), 2)
            y_offset += 20
            for result in self.comparison_results:
                data = [result['name'], str(result['steps']), str(result['backtracks']), f"{result['time']:.4f}"]
                for i, data_item in enumerate(data):
                    text = self.font_medium.render(data_item, True, Colors.WHITE if result['name'] == 'Backtracking Classique' else Colors.PRIMARY_GREEN)
                    text_rect = text.get_rect(center=(x_offset + sum(col_widths[:i]) + col_widths[i]//2, y_offset))
                    self.screen.blit(text, text_rect)
                y_offset += 50
            if len(self.comparison_results) > 1:
                y_offset += 30
                speedup = self.comparison_results[0]['time'] / self.comparison_results[1]['time']
                improvement_text = f"Accélération : {speedup:.2f}x"
                text = self.font_large.render(improvement_text, True, Colors.ACCENT_CYAN)
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
                self.screen.blit(text, text_rect)
        else:
            no_result_text = self.font_medium.render("En attente...", True, Colors.PRIMARY_RED)
            no_result_rect = no_result_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(no_result_text, no_result_rect)
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        for button in self.comparison_buttons:
            button.update(mouse_pos, mouse_clicked)
            button.draw(self.screen, self.font_medium)

    def draw_solving_screen(self):
        self.draw_background()
        solving_text = self.font_title.render("Résolution...", True, Colors.WHITE)
        solving_rect = solving_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(solving_text, solving_rect)
        algo_text = self.font_large.render(f"Algo: {self.selected_algorithm}", True, Colors.ACCENT_CYAN)
        algo_rect = algo_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(algo_text, algo_rect)
        loading_angle = (pygame.time.get_ticks() / 10) % 360
        for i in range(8):
            angle = math.radians(loading_angle + i * 45)
            x = SCREEN_WIDTH // 2 + math.cos(angle) * 40
            y = SCREEN_HEIGHT // 2 + 80 + math.sin(angle) * 40
            size = 5 + i * 0.5
            pygame.draw.circle(self.screen, Colors.PRIMARY_GREEN, (int(x), int(y)), int(size))

    def draw_board(self):
        shake_x = math.sin(self.screen_shake) * 2 if self.screen_shake > 0 else 0
        shake_y = math.cos(self.screen_shake * 1.5) * 2 if self.screen_shake > 0 else 0
        board_surf = pygame.Surface((BOARD_SIZE * CELL_SIZE, BOARD_SIZE * CELL_SIZE))
        light_color = (200, 230, 255)
        dark_color = (135, 206, 235)
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                x = col * CELL_SIZE
                y = row * CELL_SIZE
                color = light_color if (row + col) % 2 == 0 else dark_color
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(board_surf, color, rect)
                if self.show_grid: pygame.draw.rect(board_surf, Colors.BLACK, rect, 1)
        board_rect = board_surf.get_rect()
        board_rect.topleft = (BOARD_OFFSET_X + shake_x, BOARD_OFFSET_Y + shake_y)
        self.screen.blit(board_surf, board_rect)
        for i in range(BOARD_SIZE):
            letter = self.font_small.render(chr(ord('a') + i), True, Colors.LIGHT_GRAY)
            letter_rect = letter.get_rect(center=(BOARD_OFFSET_X + i * CELL_SIZE + CELL_SIZE // 2 + shake_x, BOARD_OFFSET_Y - 20 + shake_y))
            self.screen.blit(letter, letter_rect)
            number = self.font_small.render(str(BOARD_SIZE - i), True, Colors.LIGHT_GRAY)
            number_rect = number.get_rect(center=(BOARD_OFFSET_X - 20 + shake_x, BOARD_OFFSET_Y + i * CELL_SIZE + CELL_SIZE // 2 + shake_y))
            self.screen.blit(number, number_rect)

    def draw_knight(self):
        if not self.current_solution or self.current_move_index >= len(self.current_solution): return
        pos = self.current_solution[self.current_move_index]
        x = BOARD_OFFSET_X + pos[0] * CELL_SIZE + CELL_SIZE // 2
        y = BOARD_OFFSET_Y + pos[1] * CELL_SIZE + CELL_SIZE // 2
        if self.auto_rotate: self.rotation_angle += 1.5
        knight_rotated = pygame.transform.rotate(self.knight_surface, self.rotation_angle)
        knight_rect = knight_rotated.get_rect(center=(x, y))
        self.screen.blit(knight_rotated, knight_rect)
        num_text = self.font_medium.render(str(self.current_move_index + 1), True, Colors.WHITE)
        num_rect = num_text.get_rect(center=(x, y))
        pygame.draw.circle(self.screen, Colors.PRIMARY_BLUE, num_rect.center, num_rect.width // 2 + 8)
        pygame.draw.circle(self.screen, Colors.WHITE, num_rect.center, num_rect.width // 2 + 6, 2)
        self.screen.blit(num_text, num_rect)

    def draw_path(self):
        if not self.current_solution or len(self.current_solution) < 2: return
        for i in range(min(self.current_move_index + 1, len(self.current_solution) - 1)):
            start_pos = self.current_solution[i]
            end_pos = self.current_solution[i + 1]
            start_x = BOARD_OFFSET_X + start_pos[0] * CELL_SIZE + CELL_SIZE // 2
            start_y = BOARD_OFFSET_Y + start_pos[1] * CELL_SIZE + CELL_SIZE // 2
            end_x = BOARD_OFFSET_X + end_pos[0] * CELL_SIZE + CELL_SIZE // 2
            end_y = BOARD_OFFSET_Y + end_pos[1] * CELL_SIZE + CELL_SIZE // 2
            pygame.draw.line(self.screen, Colors.ACCENT_TEAL, (start_x, start_y), (end_x, end_y), 3)
        for i in range(min(self.current_move_index + 1, len(self.current_solution))):
            pos = self.current_solution[i]
            x = BOARD_OFFSET_X + pos[0] * CELL_SIZE + CELL_SIZE // 2
            y = BOARD_OFFSET_Y + pos[1] * CELL_SIZE + CELL_SIZE // 2
            if i == 0:
                pulse = abs(math.sin(time.time() * 2)) * 3 + 8
                pygame.draw.circle(self.screen, Colors.PRIMARY_GREEN, (x, y), int(pulse))
                pygame.draw.circle(self.screen, Colors.WHITE, (x, y), int(pulse - 2), 1)
            elif i == len(self.current_solution) - 1 and self.state == GameState.SOLUTION_COMPLETE:
                pulse = abs(math.sin(time.time() * 3)) * 6 + 10
                pygame.draw.circle(self.screen, Colors.PRIMARY_RED, (x, y), int(pulse))
                pygame.draw.circle(self.screen, Colors.WHITE, (x, y), int(pulse - 3), 1)
                if random.random() < 0.15: self.create_explosion(x, y, Colors.GOLD, 8)
            else:
                pulse = abs(math.sin(time.time() * 2 + i * 0.2)) * 2 + 4
                pygame.draw.circle(self.screen, Colors.PRIMARY_BLUE, (x, y), int(pulse))
                pygame.draw.circle(self.screen, Colors.WHITE, (x, y), int(pulse - 1), 1)
            num_text = self.font_small.render(str(i + 1), True, Colors.WHITE)
            num_rect = num_text.get_rect(center=(x, y))
            pygame.draw.circle(self.screen, Colors.PRIMARY_BLUE, num_rect.center, num_rect.width // 2 + 4)
            pygame.draw.circle(self.screen, Colors.WHITE, num_rect.center, num_rect.width // 2 + 2, 1)
            self.screen.blit(num_text, num_rect)

    def draw_ui(self):
        top_bar = pygame.Surface((SCREEN_WIDTH, 90), pygame.SRCALPHA)
        pygame.draw.rect(top_bar, (*Colors.BLACK[:3], 180), top_bar.get_rect(), border_radius=8)
        self.screen.blit(top_bar, (0, 0))
        pygame.draw.rect(self.screen, Colors.ACCENT_TEAL, (0, 0, SCREEN_WIDTH, 90), 2)

        self.score = self.current_move_index * 100 + self.combo * 50
        score_text = self.font_large.render(f"SCORE {self.score:06d}", True, Colors.GOLD)
        score_rect = score_text.get_rect(topleft=(15, 25))
        self.screen.blit(score_text, score_rect)

        if self.combo > 0:
            combo_text = self.font_small.render(f"COMBO x{self.combo}", True, Colors.PRIMARY_ORANGE)
            combo_rect = combo_text.get_rect(topleft=(15, 60))
            self.screen.blit(combo_text, combo_rect)

        if self.current_solution:
            move_text = self.font_medium.render(f"Mvt: {self.current_move_index + 1}/{len(self.current_solution)}", True, Colors.WHITE)
            move_rect = move_text.get_rect(topleft=(SCREEN_WIDTH // 2 - 90, 30))
            self.screen.blit(move_text, move_rect)

        side_panel = pygame.Surface((220, SCREEN_HEIGHT - 110), pygame.SRCALPHA)
        pygame.draw.rect(side_panel, (*Colors.BLACK[:3], 190), side_panel.get_rect(), border_radius=8)
        self.screen.blit(side_panel, (SCREEN_WIDTH - 230, 95))
        pygame.draw.rect(self.screen, Colors.PRIMARY_BLUE, (SCREEN_WIDTH - 230, 95, 220, SCREEN_HEIGHT - 110), 2)

        title = self.font_medium.render("STATS", True, Colors.PRIMARY_BLUE)
        title_rect = title.get_rect(centerx=SCREEN_WIDTH - 120, y=520)
        self.screen.blit(title, title_rect)

        if self.current_solution:
            info_y = 560
            line_height = 30
            algo_text = self.font_small.render(f"Algo: {self.selected_algorithm}", True, Colors.LIGHT_GRAY)
            self.screen.blit(algo_text, (SCREEN_WIDTH - 220, info_y))
            info_y += line_height

            visited = len(self.current_solution)
            visited_text = self.font_small.render(f"Cases: {visited}/64", True, Colors.PRIMARY_GREEN)
            self.screen.blit(visited_text, (SCREEN_WIDTH - 220, info_y))
            info_y += line_height

            progress = (visited / 64) * 100
            progress_text = self.font_small.render(f"Prog: {progress:.0f}%", True, Colors.ACCENT_TEAL)
            self.screen.blit(progress_text, (SCREEN_WIDTH - 220, info_y))
            info_y += line_height

            bar_rect = pygame.Rect(SCREEN_WIDTH - 220, info_y, 200, 15)
            pygame.draw.rect(self.screen, Colors.DARK_GRAY, bar_rect, border_radius=3)
            fill_width = int(200 * progress / 100)
            fill_rect = pygame.Rect(SCREEN_WIDTH - 220, info_y, fill_width, 15)
            pygame.draw.rect(self.screen, Colors.PRIMARY_GREEN, fill_rect, border_radius=3)
            pygame.draw.rect(self.screen, Colors.PRIMARY_GREEN, bar_rect, 1, border_radius=3)

            info_y += 25
            steps_text = self.font_small.render(f"Étapes: {self.solving_stats.get('steps', 'N/A')}", True, Colors.LIGHT_GRAY)
            self.screen.blit(steps_text, (SCREEN_WIDTH - 220, info_y))
            info_y += line_height

            back_text = self.font_small.render(f"Back: {self.solving_stats.get('backtracks', 'N/A')}", True, Colors.LIGHT_GRAY)
            self.screen.blit(back_text, (SCREEN_WIDTH - 220, info_y))
            info_y += line_height

            time_text = self.font_small.render(f"Temps: {self.solving_stats.get('time', 'N/A'):.2f}s", True, Colors.LIGHT_GRAY)
            self.screen.blit(time_text, (SCREEN_WIDTH - 220, info_y))

        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = pygame.mouse.get_pressed()[0]
        for button in self.game_buttons:
            button.update(mouse_pos, mouse_clicked)
            button.draw(self.screen, self.font_small)

    def update_particles(self):
        for particle in self.particles[:]:
            particle.update()
            if particle.lifetime <= 0: self.particles.remove(particle)
            else: particle.draw(self.screen)

    def handle_menu_input(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: self.running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for button in self.menu_buttons:
                if button.is_clicked(mouse_pos, event.button == 1):
                    self.execute_menu_action(button.action)

    def handle_algorithm_select_input(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: self.state = GameState.MENU
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for button in self.algorithm_buttons:
                if button.is_clicked(mouse_pos, event.button == 1):
                    self.execute_algorithm_action(button.action)

    def handle_comparison_input(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: self.state = GameState.MENU
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for button in self.comparison_buttons:
                if button.is_clicked(mouse_pos, event.button == 1):
                    self.execute_menu_action(button.action)

    def handle_game_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: self.state = GameState.MENU
            elif event.key == pygame.K_SPACE:
                self.state = GameState.PAUSED if self.state == GameState.PLAYING else GameState.PLAYING
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            for button in self.game_buttons:
                if button.is_clicked(mouse_pos, event.button == 1):
                    self.execute_game_action(button.action)

    def execute_menu_action(self, action):
        if action == "choose_algo": self.state = GameState.ALGORITHM_SELECT
        elif action == "quit": self.running = False
        elif action == "menu": self.state = GameState.MENU

    def execute_algorithm_action(self, action):
        if action == "menu": self.state = GameState.MENU
        else:
            self.selected_algorithm = action.replace("solve_", "").upper()
            self.state = GameState.SOLVING
            self.current_solution = None
            self.solving_stats = {}
            self.run_solver_in_thread(action)

    def run_solver_in_thread(self, algorithm_action):
        def solver_task():
            start_x, start_y = 0, 0
            if Board is None or Knight is None or KnightTourSolver is None:
                print("Solver modules not available.")
                return

            board = Board(8)
            knight = Knight()
            solver = KnightTourSolver(board, knight)
            solver.reset_stats()

            start_time = time.time()
            success = False
            if algorithm_action == "solve_basic":
                success = solver.solve_basic(start_x, start_y, 0)
            elif algorithm_action == "solve_enhanced":
                success = solver.solve_enhanced(start_x, start_y, 0)

            elapsed_time = time.time() - start_time
            if success:
                self.current_solution = board.path
                self.solving_stats = {
                    'steps': solver.stats['steps'],
                    'backtracks': solver.stats['backtracks'],
                    'time': elapsed_time
                }
            else:
                self.current_solution = []
                self.solving_stats = {
                    'steps': solver.stats['steps'],
                    'backtracks': solver.stats['backtracks'],
                    'time': elapsed_time
                }

            if self.current_solution:
                self.state = GameState.PLAYING
            else:
                self.state = GameState.MENU

        self.solver_thread = threading.Thread(target=solver_task)
        self.solver_thread.daemon = True
        self.solver_thread.start()

    def run_comparison_solvers(self):
        self.state = GameState.SOLVING
        self.selected_algorithm = "COMPARISON"
        def comparison_task():
            results = []

            if Board is not None and Knight is not None and KnightTourSolver is not None:
                board_basic = Board(8)
                knight_basic = Knight()
                solver_basic = KnightTourSolver(board_basic, knight_basic)
                solver_basic.reset_stats()
                start_time_basic = time.time()
                success_basic = solver_basic.solve_basic(0, 0, 0)
                elapsed_time_basic = time.time() - start_time_basic
                results.append({
                    'name': 'Backtracking Classique',
                    'success': success_basic,
                    'steps': solver_basic.stats['steps'],
                    'backtracks': solver_basic.stats['backtracks'],
                    'time': elapsed_time_basic
                })

                board_enhanced = Board(8)
                knight_enhanced = Knight()
                solver_enhanced = KnightTourSolver(board_enhanced, knight_enhanced)
                solver_enhanced.reset_stats()
                start_time_enhanced = time.time()
                success_enhanced = solver_enhanced.solve_enhanced(0, 0, 0)
                elapsed_time_enhanced = time.time() - start_time_enhanced
                results.append({
                    'name': 'Backtracking + Heuristiques',
                    'success': success_enhanced,
                    'steps': solver_enhanced.stats['steps'],
                    'backtracks': solver_enhanced.stats['backtracks'],
                    'time': elapsed_time_enhanced
                })

            self.comparison_results = results
            self.state = GameState.COMPARING

        self.solver_thread = threading.Thread(target=comparison_task)
        self.solver_thread.daemon = True
        self.solver_thread.start()

    def execute_game_action(self, action):
        if action == "menu": self.state = GameState.MENU
        elif action == "pause": self.state = GameState.PAUSED if self.state == GameState.PLAYING else GameState.PLAYING
        elif action == "restart": self.reset_game()
        elif action == "speed_up": self.animation_speed = max(50, self.animation_speed - 50)
        elif action == "speed_down": self.animation_speed = min(2000, self.animation_speed + 50)
        elif action == "toggle_grid": self.show_grid = not self.show_grid
        elif action == "toggle_rotation": self.auto_rotate = not self.auto_rotate

    def reset_game(self):
        self.current_move_index = 0
        self.last_move_time = 0
        self.state = GameState.PLAYING
        self.particles.clear()
        self.screen_shake = 0
        self.combo = 0
        self.moves_count = 0

    def update(self):
        self.menu_time += 0.02
        if self.screen_shake > 0: self.screen_shake -= 0.3
        if self.state == GameState.PLAYING and self.current_solution:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_move_time > self.animation_speed:
                if self.current_move_index < len(self.current_solution) - 1:
                    self.current_move_index += 1
                    self.last_move_time = current_time
                    self.moves_count += 1
                    pos = self.current_solution[self.current_move_index]
                    x = BOARD_OFFSET_X + pos[0] * CELL_SIZE + CELL_SIZE // 2
                    y = BOARD_OFFSET_Y + pos[1] * CELL_SIZE + CELL_SIZE // 2
                    self.create_explosion(x, y, Colors.PRIMARY_BLUE, 12)
                    self.screen_shake = 3
                    if self.move_sound: self.move_sound.play()
                    self.combo += 1
                else:
                    self.state = GameState.SOLUTION_COMPLETE
                    if self.complete_sound: self.complete_sound.play()
                    self.create_explosion(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, Colors.GOLD, 80)

    def draw(self):
        if self.state == GameState.MENU: self.draw_menu()
        elif self.state == GameState.ALGORITHM_SELECT: self.draw_algorithm_select_screen()
        elif self.state == GameState.COMPARING: self.draw_comparison_screen()
        elif self.state == GameState.SOLVING: self.draw_solving_screen()
        else:
            self.draw_background()
            self.draw_board()
            self.draw_path()
            self.draw_knight()
            self.draw_ui()
        self.update_particles()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: self.running = False
                if self.state == GameState.MENU: self.handle_menu_input(event)
                elif self.state == GameState.ALGORITHM_SELECT: self.handle_algorithm_select_input(event)
                elif self.state == GameState.COMPARING: self.handle_comparison_input(event)
                else: self.handle_game_input(event)
            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = KnightTourGame()
    game.run()
