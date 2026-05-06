from __future__ import annotations

import cv2
import pygame

from . import config
from .expression_reader import EmotionSnapshot
from .expression_target import ExpressionTarget, TARGET_COLORS, TARGET_LABELS_PT
from .game_manager import GameManager, GamePhase


class Hud:
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.font_small = pygame.font.SysFont("Arial", 20)
        self.font_regular = pygame.font.SysFont("Arial", 24)
        self.font_medium = pygame.font.SysFont("Arial", 34, bold=True)
        self.font_big = pygame.font.SysFont("Arial", 56, bold=True)

    def draw(self, screen, game: GameManager, snapshot: EmotionSnapshot, frame_bgr, show_debug: bool) -> None:
        self._draw_top_bar(screen, game)
        self._draw_target_panel(screen, game.current_target)
        self._draw_feedback(screen, game, snapshot)
        self._draw_camera_preview(screen, frame_bgr)
        self._draw_bottom_bar(screen, snapshot, show_debug)

        if game.phase == GamePhase.GAME_OVER:
            self._draw_game_over(screen, game)

    def _draw_panel(self, screen, rect, border_radius=14):
        pygame.draw.rect(screen, config.PANEL_COLOR, rect, border_radius=border_radius)
        pygame.draw.rect(screen, config.PANEL_BORDER_COLOR, rect, width=2, border_radius=border_radius)

    def _draw_text(self, screen, font, text, x, y, color=config.TEXT_COLOR):
        surface = font.render(text, True, color)
        screen.blit(surface, (x, y))

    def _draw_center_text(self, screen, font, text, y, color=config.TEXT_COLOR):
        surface = font.render(text, True, color)
        x = (self.screen_width - surface.get_width()) // 2
        screen.blit(surface, (x, y))

    def _draw_top_bar(self, screen, game: GameManager):
        rect = pygame.Rect(20, 18, self.screen_width - 40, 64)
        self._draw_panel(screen, rect)

        timer_text = f"{max(0.0, game.timer):.1f}s"
        self._draw_text(screen, self.font_regular, f"Pontos: {game.score}", 42, 38)
        self._draw_text(screen, self.font_regular, f"Vidas: {game.lives}", 250, 38)
        self._draw_text(screen, self.font_regular, f"Tempo: {timer_text}", 410, 38)
        self._draw_text(screen, self.font_regular, f"Combo: x{game.combo}", 590, 38)
        self._draw_text(screen, self.font_regular, f"Rodada: {game.round_number}", 740, 38)

    def _draw_target_panel(self, screen, target: ExpressionTarget | None):
        rect = pygame.Rect(250, 98, self.screen_width - 500, 120)
        self._draw_panel(screen, rect, border_radius=18)

        label = TARGET_LABELS_PT.get(target, "-")
        color = TARGET_COLORS.get(target, config.NEUTRAL_COLOR)
        self._draw_center_text(screen, self.font_small, "EXPRESSÃO ALVO", 112, config.TEXT_MUTED_COLOR)
        self._draw_center_text(screen, self.font_big, label, 142, color)

    def _draw_feedback(self, screen, game: GameManager, snapshot: EmotionSnapshot):
        message = game.feedback
        if not message:
            return

        if "ACERTOU" in message:
            color = config.SUCCESS_COLOR
        elif "ERROU" in message or "FIM" in message or "ERRO NO" in message:
            color = config.ERROR_COLOR
        elif "ROSTO" in message:
            color = config.WARNING_COLOR
        else:
            color = config.TEXT_COLOR

        self._draw_center_text(screen, self.font_medium, message, 228, color)

        if snapshot.error_message:
            self._draw_center_text(screen, self.font_small, snapshot.error_message[:95], 268, config.ERROR_COLOR)

    def _draw_camera_preview(self, screen, frame_bgr):
        if frame_bgr is None:
            return

        preview_w, preview_h = 260, 180
        preview = cv2.resize(frame_bgr, (preview_w, preview_h))
        preview = cv2.cvtColor(preview, cv2.COLOR_BGR2RGB)
        surface = pygame.surfarray.make_surface(preview.swapaxes(0, 1))

        x = self.screen_width - preview_w - 24
        y = self.screen_height - preview_h - 24
        border_rect = pygame.Rect(x - 4, y - 4, preview_w + 8, preview_h + 8)
        self._draw_panel(screen, border_rect, border_radius=12)
        screen.blit(surface, (x, y))

    def _draw_bottom_bar(self, screen, snapshot: EmotionSnapshot, show_debug: bool):
        rect = pygame.Rect(20, self.screen_height - 112, self.screen_width - 330, 88)
        self._draw_panel(screen, rect)

        face_status = "Rosto detectado" if snapshot.face_visible_with_grace() else "Sem rosto"
        processing_status = "Processando..." if snapshot.processing else "Pronto"

        self._draw_text(screen, self.font_small, f"Câmera: {face_status}", 42, self.screen_height - 98)
        self._draw_text(screen, self.font_small, f"Py-Feat: {processing_status}", 260, self.screen_height - 98)
        self._draw_text(screen, self.font_small, f"Detectado: {snapshot.detected_expression}", 460, self.screen_height - 98)

        if show_debug:
            debug = (
                f"happiness={snapshot.score('happiness'):.2f}  "
                f"disgust={snapshot.score('disgust'):.2f}  "
                f"surprise={snapshot.score('surprise'):.2f}  "
                f"neutral={snapshot.score('neutral'):.2f}"
            )
            self._draw_text(screen, self.font_small, debug, 42, self.screen_height - 62, config.TEXT_MUTED_COLOR)
        else:
            self._draw_text(screen, self.font_small, "D: mostrar/ocultar debug | ESC: sair", 42, self.screen_height - 62, config.TEXT_MUTED_COLOR)

    def _draw_game_over(self, screen, game: GameManager):
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        panel = pygame.Rect(230, 205, self.screen_width - 460, 230)
        self._draw_panel(screen, panel, border_radius=24)
        self._draw_center_text(screen, self.font_big, "FIM DE JOGO", 235, config.ERROR_COLOR)
        self._draw_center_text(screen, self.font_medium, f"Pontuação: {game.score}", 310, config.TEXT_COLOR)
        self._draw_center_text(screen, self.font_regular, "Pressione R para reiniciar", 365, config.TEXT_MUTED_COLOR)
