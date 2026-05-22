from __future__ import annotations

import cv2
import pygame

from . import config
from .expression_reader import EmotionSnapshot
from .expression_target import ExpressionTarget, TARGET_COLORS, TARGET_LABELS_PT
from .game_manager import GameManager, GamePhase
from .training_mode import TrainingPhase


class Hud:
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        font_name = config.FONT_NAME or None
        # Se houver um PATH de fonte embutida, preferi-la
        if config.FONT_PATH:
            try:
                self.font_small = pygame.font.Font(config.FONT_PATH, 20)
                self.font_regular = pygame.font.Font(config.FONT_PATH, 24)
                self.font_medium = pygame.font.Font(config.FONT_PATH, 34)
                self.font_big = pygame.font.Font(config.FONT_PATH, 56)
                # Simular negrito quando necessário
                self.font_medium.set_bold(True)
                self.font_big.set_bold(True)
            except Exception:
                self.font_small = pygame.font.SysFont(font_name, 20)
                self.font_regular = pygame.font.SysFont(font_name, 24)
                self.font_medium = pygame.font.SysFont(
                    font_name, 34, bold=True)
                self.font_big = pygame.font.SysFont(font_name, 56, bold=True)
        else:
            self.font_small = pygame.font.SysFont(font_name, 20)
            self.font_regular = pygame.font.SysFont(font_name, 24)
            self.font_medium = pygame.font.SysFont(font_name, 34, bold=True)
            self.font_big = pygame.font.SysFont(font_name, 56, bold=True)

    def draw(self, screen, game: GameManager, snapshot: EmotionSnapshot, frame_bgr, show_debug: bool, expression_reader=None) -> None:
        if game.phase == GamePhase.MENU:
            self._draw_main_menu(screen, game, frame_bgr)
            return

        if game.is_in_training():
            self._draw_training_screen(screen, game, snapshot, frame_bgr)
            return

        self._draw_top_bar(screen, game)
        self._draw_target_panel(screen, game.current_target)
        self._draw_feedback(screen, game, snapshot)
        self._draw_camera_preview(screen, frame_bgr)
        self._draw_bottom_bar(screen, snapshot, show_debug, expression_reader)

        if game.phase == GamePhase.GAME_OVER:
            self._draw_game_over(screen, game)

    def _draw_panel(self, screen, rect, border_radius=14):
        br = border_radius or config.PANEL_BORDER_RADIUS
        pygame.draw.rect(screen, config.PANEL_COLOR, rect,
                         border_radius=br)
        pygame.draw.rect(screen, config.PANEL_BORDER_COLOR,
                         rect, width=2, border_radius=br)

    def _draw_text(self, screen, font, text, x, y, color=config.TEXT_COLOR):
        # Desenhar sombra sutil antes do texto para profundidade
        shadow = font.render(text, True, config.TEXT_SHADOW_COLOR)
        screen.blit(
            shadow, (x + config.TEXT_SHADOW_OFFSET[0], y + config.TEXT_SHADOW_OFFSET[1]))
        surface = font.render(text, True, color)
        screen.blit(surface, (x, y))

    def _draw_center_text(self, screen, font, text, y, color=config.TEXT_COLOR):
        surface = font.render(text, True, color)
        x = (self.screen_width - surface.get_width()) // 2
        # sombra centralizada
        shadow = font.render(text, True, config.TEXT_SHADOW_COLOR)
        screen.blit(
            shadow, (x + config.TEXT_SHADOW_OFFSET[0], y + config.TEXT_SHADOW_OFFSET[1]))
        screen.blit(surface, (x, y))

    def _draw_top_bar(self, screen, game: GameManager):
        rect = pygame.Rect(20, 18, self.screen_width - 40, 64)
        self._draw_panel(screen, rect)

        timer_text = f"{max(0.0, game.timer):.1f}s"
        self._draw_text(screen, self.font_regular,
                        f"Pontos: {game.score}", 42, 38)
        self._draw_text(screen, self.font_regular,
                        f"Vidas: {game.lives}", 250, 38)
        self._draw_text(screen, self.font_regular,
                        f"Tempo: {timer_text}", 410, 38)
        self._draw_text(screen, self.font_regular,
                        f"Combo: x{game.combo}", 590, 38)
        self._draw_text(screen, self.font_regular,
                        f"Rodada: {game.round_number}", 740, 38)

    def _draw_target_panel(self, screen, target: ExpressionTarget | None):
        rect = pygame.Rect(250, 98, self.screen_width - 500, 120)
        self._draw_panel(screen, rect, border_radius=18)

        label = TARGET_LABELS_PT.get(target, "-")
        color = TARGET_COLORS.get(target, config.NEUTRAL_COLOR)
        self._draw_center_text(screen, self.font_small,
                               "EXPRESSÃO ALVO", 112, config.TEXT_MUTED_COLOR)
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
            self._draw_center_text(
                screen, self.font_small, snapshot.error_message[:95], 268, config.ERROR_COLOR)

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

    def _draw_bottom_bar(self, screen, snapshot: EmotionSnapshot, show_debug: bool, expression_reader=None):
        rect = pygame.Rect(20, self.screen_height - 112,
                           self.screen_width - 330, 88)
        self._draw_panel(screen, rect)
        # Mostrar status do detector (py-feat ou fallback)
        detector_label = "Detector: unknown"
        try:
            if expression_reader is not None and hasattr(expression_reader, "get_detector_name"):
                name = expression_reader.get_detector_name()
                active = expression_reader.is_pyfeat_active()
                detector_label = f"Detector: {name} {'(py-feat)' if active else '(fallback)'}"
        except Exception:
            detector_label = "Detector: error"

        self._draw_text(screen, self.font_small, detector_label,
                        36, self.screen_height - 36, config.TEXT_MUTED_COLOR)
        # Mostrar erro de carregamento do detector (se existir)
        try:
            if expression_reader is not None and hasattr(expression_reader, "get_load_error"):
                load_err = expression_reader.get_load_error()
                if load_err:
                    short = load_err.splitlines()[0]
                    self._draw_text(
                        screen, self.font_small, f"py-feat error: {short}", 36, self.screen_height - 18, config.ERROR_COLOR)
        except Exception:
            pass

        face_status = "Rosto detectado" if snapshot.face_visible_with_grace() else "Sem rosto"
        processing_status = "Processando..." if snapshot.processing else "Pronto"

        self._draw_text(screen, self.font_small,
                        f"Câmera: {face_status}", 42, self.screen_height - 98)
        self._draw_text(screen, self.font_small,
                        f"Py-Feat: {processing_status}", 260, self.screen_height - 98)
        self._draw_text(screen, self.font_small,
                        f"Detectado: {snapshot.detected_expression}", 460, self.screen_height - 98)

        if show_debug:
            debug = (
                f"happiness={snapshot.scores.get('happiness', 0.0):.2f}  "
                f"disgust={snapshot.scores.get('disgust', 0.0):.2f}  "
                f"surprise={snapshot.scores.get('surprise', 0.0):.2f}  "
                f"neutral={snapshot.scores.get('neutral', 0.0):.2f}"
            )
            self._draw_text(screen, self.font_small, debug, 42,
                            self.screen_height - 62, config.TEXT_MUTED_COLOR)
        else:
            self._draw_text(screen, self.font_small, "D: mostrar/ocultar debug | ESC: sair",
                            42, self.screen_height - 62, config.TEXT_MUTED_COLOR)

    def _draw_game_over(self, screen, game: GameManager):
        overlay = pygame.Surface(
            (self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        screen.blit(overlay, (0, 0))

        panel = pygame.Rect(230, 205, self.screen_width - 460, 230)
        self._draw_panel(screen, panel, border_radius=24)
        self._draw_center_text(screen, self.font_big,
                               "FIM DE JOGO", 235, config.ERROR_COLOR)
        self._draw_center_text(
            screen, self.font_medium, f"Pontuação: {game.score}", 310, config.TEXT_COLOR)
        self._draw_center_text(
            screen, self.font_regular, "Pressione R para reiniciar", 365, config.TEXT_MUTED_COLOR)

    def _draw_training_screen(self, screen, game: GameManager, snapshot: EmotionSnapshot, frame_bgr):
        """Renderiza a tela de treinamento/calibração."""
        training = game.training_manager

        screen.fill(config.BACKGROUND_COLOR)

        # Câmera em tamanho grande
        if frame_bgr is not None:
            preview_w, preview_h = 520, 360
            preview = cv2.resize(frame_bgr, (preview_w, preview_h))
            preview = cv2.cvtColor(preview, cv2.COLOR_BGR2RGB)
            surface = pygame.surfarray.make_surface(preview.swapaxes(0, 1))

            x = (self.screen_width - preview_w) // 2
            y = 50
            border_rect = pygame.Rect(
                x - 4, y - 4, preview_w + 8, preview_h + 8)
            self._draw_panel(screen, border_rect, border_radius=12)
            screen.blit(surface, (x, y))

        # Barra de progresso
        progress_y = 430
        progress_rect = pygame.Rect(
            60, progress_y, self.screen_width - 120, 20)
        pygame.draw.rect(screen, config.PANEL_BORDER_COLOR,
                         progress_rect, border_radius=10)

        filled_width = int((self.screen_width - 120) *
                           training.get_current_progress())
        if filled_width > 0:
            filled_rect = pygame.Rect(60, progress_y, filled_width, 20)
            pygame.draw.rect(screen, config.SUCCESS_COLOR,
                             filled_rect, border_radius=10)

        # Mensagem principal
        if training.phase == TrainingPhase.MENU:
            color = config.TEXT_COLOR
            msg = "MODO DE TREINAMENTO"
            submsg = "Treinaremos com suas expressões específicas"
            instructions = "SPACE para começar | ESC para sair"
        elif training.phase == TrainingPhase.WAITING_FOR_EXPRESSION:
            color = config.WARNING_COLOR
            msg = training.get_current_target_label().upper()
            submsg = training.message
            instructions = "Fique atento para começar em breve"
        elif training.phase == TrainingPhase.RECORDING:
            color = config.SUCCESS_COLOR
            msg = "REGISTRANDO"
            submsg = training.message
            instructions = f"Mantenha a expressão até terminar"
        elif training.phase == TrainingPhase.ANALYZING:
            color = config.WARNING_COLOR
            msg = "ANALISANDO..."
            submsg = "Calculando thresholds recomendados"
            instructions = "Aguarde..."
        elif training.phase == TrainingPhase.RESULTS:
            color = config.SUCCESS_COLOR
            msg = "✓ CALIBRAÇÃO CONCLUÍDA!"
            submsg = training.message
            instructions = "SPACE: salvar | ESC: descartar"
        elif training.phase == TrainingPhase.COMPLETE:
            color = config.SUCCESS_COLOR
            msg = "TREINAMENTO COMPLETO"
            submsg = training.message
            instructions = "ESC para voltar ao jogo"
        else:
            color = config.TEXT_COLOR
            msg = ""
            submsg = ""
            instructions = ""

        self._draw_center_text(screen, self.font_big, msg, 460, color)
        self._draw_center_text(screen, self.font_regular,
                               submsg, 530, config.TEXT_COLOR)
        self._draw_center_text(screen, self.font_small,
                               instructions, 575, config.TEXT_MUTED_COLOR)

        # Mostrar scores se estiver registrando
        if training.phase in (TrainingPhase.RECORDING, TrainingPhase.ANALYZING):
            scores_text = (
                f"happiness={snapshot.scores.get('happiness', 0.0):.2f}  "
                f"disgust={snapshot.scores.get('disgust', 0.0):.2f}  "
                f"surprise={snapshot.scores.get('surprise', 0.0):.2f}  "
                f"neutral={snapshot.scores.get('neutral', 0.0):.2f}"
            )
            self._draw_center_text(
                screen, self.font_small, scores_text, 615, config.TEXT_MUTED_COLOR)

        # Mostrar recomendações se tiver
        if training.recommendations and training.phase == TrainingPhase.RESULTS:
            rec_text = "Thresholds recomendados:"
            self._draw_center_text(
                screen, self.font_small, rec_text, 615, config.TEXT_MUTED_COLOR)

            y_offset = 0
            # recommendations keys may be ExpressionTarget enums or emotion column strings
            from .expression_target import TARGET_TO_EMOTION_COLUMN

            # invert mapping: emotion_column -> ExpressionTarget
            inverse_map = {v: k for k, v in TARGET_TO_EMOTION_COLUMN.items()}

            for target, score in training.recommendations.items():
                # Determinar label de exibição
                if hasattr(target, "value"):
                    label = TARGET_LABELS_PT.get(target, str(target.value))
                elif isinstance(target, str):
                    enum_key = inverse_map.get(target)
                    if enum_key is not None:
                        label = TARGET_LABELS_PT.get(enum_key, target.title())
                    else:
                        label = target.title()
                else:
                    label = str(target)

                rec_line = f"{label}: {score:.2f}"
                self._draw_center_text(
                    screen, self.font_small, rec_line, 645 + y_offset, config.SUCCESS_COLOR)
                y_offset += 25

    def _draw_main_menu(self, screen, game: GameManager, frame_bgr):
        """Renderiza o menu principal."""
        screen.fill(config.BACKGROUND_COLOR)

        # Preview da câmera no fundo
        if frame_bgr is not None:
            preview_w, preview_h = 960, 640
            preview = cv2.resize(frame_bgr, (preview_w, preview_h))
            preview = cv2.cvtColor(preview, cv2.COLOR_BGR2RGB)
            surface = pygame.surfarray.make_surface(preview.swapaxes(0, 1))

            # Escurecer a imagem de fundo
            surface.set_alpha(40)
            screen.blit(surface, (0, 0))

        # Overlay escuro
        overlay = pygame.Surface(
            (self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))

        # Título
        title_font = pygame.font.SysFont("Arial", 72, bold=True)
        self._draw_center_text(
            screen, title_font, "🎮 EXPRESSION WALL", 80, config.SUCCESS_COLOR)

        subtitle_font = pygame.font.SysFont("Arial", 28)
        self._draw_center_text(
            screen, subtitle_font, "Hole in the Wall com Py-Feat", 160, config.TEXT_MUTED_COLOR)

        # Opções do menu
        menu_y = 260
        option_height = 80

        for i, option in enumerate(game.menu_options):
            is_selected = (i == game.menu_selected)

            # Desenhar fundo da opção
            option_rect = pygame.Rect(
                self.screen_width // 2 - 150,
                menu_y + i * option_height,
                300,
                70
            )

            if is_selected:
                color = config.SUCCESS_COLOR
                pygame.draw.rect(screen, config.PANEL_COLOR,
                                 option_rect, border_radius=16)
                pygame.draw.rect(screen, config.SUCCESS_COLOR,
                                 option_rect, width=4, border_radius=16)
            else:
                color = config.TEXT_COLOR
                pygame.draw.rect(screen, config.PANEL_COLOR,
                                 option_rect, border_radius=16)
                pygame.draw.rect(screen, config.PANEL_BORDER_COLOR,
                                 option_rect, width=2, border_radius=16)

            # Texto da opção
            option_font = pygame.font.SysFont("Arial", 32, bold=is_selected)
            self._draw_center_text(
                screen, option_font, option, menu_y + i * option_height + 20, color)

        # Instruções
        instructions_font = pygame.font.SysFont("Arial", 20)
        self._draw_center_text(
            screen, instructions_font, "↑ ↓ para navegar | ENTER para selecionar | ESC para sair", 550, config.TEXT_MUTED_COLOR)

        # Dica
        hint_font = pygame.font.SysFont("Arial", 16)
        self._draw_center_text(
            screen, hint_font, "Dica: Use o modo de calibração para melhorar a precisão!", 590, config.WARNING_COLOR)
