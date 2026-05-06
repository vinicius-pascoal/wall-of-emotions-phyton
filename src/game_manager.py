from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum, auto

from . import config
from .expression_reader import PyFeatExpressionReader
from .expression_target import ACTIVE_TARGETS, ExpressionTarget


class GamePhase(Enum):
    MENU = auto()
    ROUND = auto()
    BETWEEN_ROUNDS = auto()
    GAME_OVER = auto()


@dataclass
class RoundResult:
    message: str = ""
    success: bool = False


class GameManager:
    def __init__(self, start_menu: bool = True):
        self.score = 0
        self.lives = config.INITIAL_LIVES
        self.round_duration = config.INITIAL_ROUND_DURATION
        self.timer = self.round_duration
        self.current_target: ExpressionTarget | None = None
        self.phase = GamePhase.MENU if start_menu else GamePhase.ROUND
        self.feedback = ""
        self.last_result = RoundResult()
        self.between_rounds_timer = 0.0
        self.round_number = 0
        self.combo = 0

        # Menu state
        self.menu_selected = 0  # 0: Jogar, 1: Calibrar
        self.menu_options = ["🎮 JOGAR", "⚙️  CALIBRAR"]

        if not start_menu:
            self.start_round()

    def start_round(self) -> None:
        self.round_number += 1
        self.current_target = random.choice(ACTIVE_TARGETS)
        self.timer = self.round_duration
        self.phase = GamePhase.ROUND
        self.feedback = ""
        self.last_result = RoundResult()

    def update(self, dt: float, expression_reader: PyFeatExpressionReader) -> None:
        if self.phase == GamePhase.MENU:
            return

        if self.phase == GamePhase.GAME_OVER:
            return

        if self.phase == GamePhase.BETWEEN_ROUNDS:
            self.between_rounds_timer -= dt
            if self.between_rounds_timer <= 0:
                self.start_round()
            return

        snapshot = expression_reader.get_snapshot()

        if snapshot.error_message:
            self.feedback = "ERRO NO PY-FEAT"
            return

        if not snapshot.face_visible_with_grace():
            self.feedback = "POSICIONE O ROSTO"
            return

        self.feedback = ""
        self.timer -= dt

        if self.timer <= 0:
            self.finish_round(expression_reader)

    def finish_round(self, expression_reader: PyFeatExpressionReader) -> None:
        if self.current_target is None:
            return

        success = expression_reader.is_matching_target(self.current_target)

        if success:
            self.combo += 1
            gained_points = config.POINTS_PER_HIT + max(0, self.combo - 1) * 25
            self.score += gained_points
            self.feedback = f"ACERTOU! +{gained_points}"
            self.last_result = RoundResult(message=self.feedback, success=True)
        else:
            self.combo = 0
            self.lives -= 1
            self.feedback = "ERROU!"
            self.last_result = RoundResult(
                message=self.feedback, success=False)

        if self.lives <= 0:
            self.phase = GamePhase.GAME_OVER
            self.feedback = "FIM DE JOGO"
            return

        self.round_duration = max(
            config.MIN_ROUND_DURATION,
            self.round_duration * config.ROUND_DURATION_MULTIPLIER,
        )
        self.phase = GamePhase.BETWEEN_ROUNDS
        self.between_rounds_timer = config.DELAY_BETWEEN_ROUNDS

    def restart(self) -> None:
        self.__init__()

    def get_wall_progress(self) -> float:
        if self.round_duration <= 0:
            return 0.0
        progress = 1.0 - (self.timer / self.round_duration)
        return max(0.0, min(1.0, progress))

    def enter_training_mode(self) -> None:
        """Entra no modo de treinamento."""
        from .training_mode import TrainingManager
        self.training_manager = TrainingManager()
        self.in_training = True
        self.training_manager.start_training()

    def exit_training_mode(self) -> None:
        """Sai do modo de treinamento."""
        self.in_training = False
        self.training_manager = None
        self.restart()

    def is_in_training(self) -> bool:
        """Verifica se está no modo de treinamento."""
        return getattr(self, 'in_training', False)

    def select_menu_option(self) -> None:
        """Seleciona a opção do menu."""
        if self.menu_selected == 0:
            # Jogar
            self.start_game_from_menu()
        elif self.menu_selected == 1:
            # Calibrar
            self.enter_training_mode()

    def start_game_from_menu(self) -> None:
        """Inicia o jogo a partir do menu."""
        self.score = 0
        self.lives = config.INITIAL_LIVES
        self.round_duration = config.INITIAL_ROUND_DURATION
        self.timer = self.round_duration
        self.round_number = 0
        self.combo = 0
        self.feedback = ""
        self.last_result = RoundResult()
        self.between_rounds_timer = 0.0
        self.start_round()

    def move_menu_selection(self, direction: int) -> None:
        """Move a seleção do menu (-1 para cima, 1 para baixo)."""
        self.menu_selected = (self.menu_selected +
                              direction) % len(self.menu_options)

    def return_to_menu(self) -> None:
        """Volta para o menu principal."""
        self.phase = GamePhase.MENU
        self.menu_selected = 0
