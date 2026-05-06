from __future__ import annotations

import pygame

from . import config
from .expression_target import ExpressionTarget, TARGET_COLORS, TARGET_LABELS_PT


class Wall:
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height

    def draw(self, screen, target: ExpressionTarget | None, progress: float, font) -> None:
        color = TARGET_COLORS.get(target, config.NEUTRAL_COLOR)
        label = TARGET_LABELS_PT.get(target, "-")

        # A parede cresce e desce na tela, simulando aproximação.
        wall_width = int(230 + progress * 450)
        wall_height = int(90 + progress * 260)
        wall_x = (self.screen_width - wall_width) // 2
        wall_y = int(265 + progress * 115)

        shadow_rect = pygame.Rect(wall_x + 8, wall_y + 10, wall_width, wall_height)
        wall_rect = pygame.Rect(wall_x, wall_y, wall_width, wall_height)

        pygame.draw.rect(screen, (0, 0, 0), shadow_rect, border_radius=22)
        pygame.draw.rect(screen, color, wall_rect, border_radius=22)
        pygame.draw.rect(screen, (255, 255, 255), wall_rect, width=4, border_radius=22)

        # Buraco central estilizado: mantém o tema de Hole in the Wall.
        hole_width = max(100, int(wall_width * 0.36))
        hole_height = max(70, int(wall_height * 0.35))
        hole_rect = pygame.Rect(
            wall_x + (wall_width - hole_width) // 2,
            wall_y + (wall_height - hole_height) // 2,
            hole_width,
            hole_height,
        )
        pygame.draw.ellipse(screen, config.BACKGROUND_COLOR, hole_rect)
        pygame.draw.ellipse(screen, (255, 255, 255), hole_rect, width=3)

        text_surface = font.render(label, True, config.TEXT_COLOR)
        text_x = wall_x + (wall_width - text_surface.get_width()) // 2
        text_y = wall_y + 16
        screen.blit(text_surface, (text_x, text_y))
