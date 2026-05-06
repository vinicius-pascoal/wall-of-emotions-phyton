"""Modo de treinamento para calibração de expressões.

Permite ao usuário treinar o modelo com suas próprias expressões
e gerar thresholds otimizados para sua webcam e iluminação.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field, asdict
from enum import Enum, auto
from pathlib import Path
from typing import Dict, List

from . import config
from .expression_reader import PyFeatExpressionReader
from .expression_target import ACTIVE_TARGETS, ExpressionTarget


class TrainingPhase(Enum):
    """Fases do modo de treinamento."""
    MENU = auto()
    WAITING_FOR_EXPRESSION = auto()
    RECORDING = auto()
    ANALYZING = auto()
    RESULTS = auto()
    COMPLETE = auto()


@dataclass
class ExpressionSample:
    """Amostra de uma expressão durante o treinamento."""
    emotion: str
    scores: Dict[str, float]


@dataclass
class TrainingSession:
    """Sessão de treinamento com múltiplas amostras."""
    target: ExpressionTarget
    samples: List[ExpressionSample] = field(default_factory=list)

    def average_scores(self) -> Dict[str, float]:
        """Calcula scores médios para esta expressão."""
        if not self.samples:
            return {e: 0.0 for e in ["happiness", "disgust", "surprise", "neutral"]}

        num_samples = len(self.samples)
        avg = {
            "happiness": sum(s.scores.get("happiness", 0.0) for s in self.samples) / num_samples,
            "disgust": sum(s.scores.get("disgust", 0.0) for s in self.samples) / num_samples,
            "surprise": sum(s.scores.get("surprise", 0.0) for s in self.samples) / num_samples,
            "neutral": sum(s.scores.get("neutral", 0.0) for s in self.samples) / num_samples,
        }
        return avg


class TrainingManager:
    """Gerencia o modo de treinamento e calibração de thresholds."""

    TRAINING_DATA_FILE = ".training_data.json"
    RECORDING_DURATION = 3.0  # segundos por expressão

    def __init__(self):
        self.phase = TrainingPhase.MENU
        self.current_target_index = 0
        self.sessions: List[TrainingSession] = []
        self.timer = 0.0
        self.current_session: TrainingSession | None = None
        self.message = ""
        self.recommendations: Dict[str, float] = {}

        # Carregar dados anteriores se existirem
        self._load_previous_training()

    def start_training(self) -> None:
        """Inicia novo modo de treinamento."""
        self.sessions = []
        self.current_target_index = 0
        self.phase = TrainingPhase.WAITING_FOR_EXPRESSION
        self._start_next_expression()

    def _start_next_expression(self) -> None:
        """Começa o treinamento para a próxima expressão."""
        if self.current_target_index >= len(ACTIVE_TARGETS):
            self.phase = TrainingPhase.ANALYZING
            self._analyze_results()
            return

        target = ACTIVE_TARGETS[self.current_target_index]
        self.current_session = TrainingSession(target=target)
        self.timer = self.RECORDING_DURATION
        self.phase = TrainingPhase.WAITING_FOR_EXPRESSION
        self.message = f"Prepare-se para fazer: {target.value}"

    def update(self, dt: float, expression_reader: PyFeatExpressionReader) -> None:
        """Atualiza o treinamento."""
        if self.phase == TrainingPhase.MENU:
            return

        if self.phase == TrainingPhase.WAITING_FOR_EXPRESSION:
            self.timer -= dt
            if self.timer <= 0:
                self.phase = TrainingPhase.RECORDING
                self.timer = self.RECORDING_DURATION
                self.message = "REGISTRANDO... Faça a expressão agora!"
                return

            remaining = int(self.timer) + 1
            self.message = f"Prepare-se em: {remaining}s"

        elif self.phase == TrainingPhase.RECORDING:
            snapshot = expression_reader.get_snapshot()

            if snapshot.face_visible_with_grace():
                sample = ExpressionSample(
                    emotion=snapshot.detected_expression,
                    scores=dict(snapshot.scores)
                )
                self.current_session.samples.append(sample)
                self.message = f"Registrando... ({len(self.current_session.samples)} amostras)"
            else:
                self.message = "⚠ Rosto não detectado! Mostre seu rosto."

            self.timer -= dt
            if self.timer <= 0:
                self.sessions.append(self.current_session)
                self.current_target_index += 1
                self._start_next_expression()

    def _analyze_results(self) -> None:
        """Analisa resultados e recomenda thresholds."""
        if not self.sessions:
            self.message = "Nenhuma amostra coletada!"
            self.phase = TrainingPhase.COMPLETE
            return

        # Calcular thresholds recomendados
        recommendations = self._calculate_recommendations()
        self.recommendations = recommendations
        self.phase = TrainingPhase.RESULTS
        self.message = "Calibração concluída! Pressione SPACE para salvar ou ESC para descartar."

    def _calculate_recommendations(self) -> Dict[str, float]:
        """Calcula thresholds recomendados baseado nas amostras."""
        recommendations = {}

        for session in self.sessions:
            avg_scores = session.average_scores()
            target_emotion = session.target.value.lower()

            # Usar a média como threshold, com margem de segurança
            target_score = avg_scores.get(target_emotion, 0.0)
            # Reduzir um pouco para ser mais permissivo, mas não demais
            recommended = max(0.2, target_score * 0.85)
            recommendations[session.target] = recommended

        return recommendations

    def save_training_data(self) -> None:
        """Salva dados de treinamento e thresholds personalizados."""
        data = {
            "thresholds": {
                target.value: score
                for target, score in self.recommendations.items()
            },
            "sessions": [
                {
                    "target": s.target.value,
                    "average_scores": s.average_scores(),
                    "num_samples": len(s.samples),
                }
                for s in self.sessions
            ]
        }

        with open(self.TRAINING_DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)

        self.phase = TrainingPhase.COMPLETE
        self.message = "✓ Dados salvos com sucesso!"

    def _load_previous_training(self) -> None:
        """Carrega dados de treinamento anterior se existirem."""
        if not Path(self.TRAINING_DATA_FILE).exists():
            return

        try:
            with open(self.TRAINING_DATA_FILE, "r") as f:
                data = json.load(f)

            # Aqui poderíamos aplicar os thresholds salvos
            print("[Training] Dados de treinamento anterior carregados.")
        except Exception as e:
            print(f"[Training] Erro ao carregar dados: {e}")

    def get_current_target_label(self) -> str:
        """Retorna o rótulo da expressão atual."""
        if self.current_session:
            return self.current_session.target.value
        return "---"

    def get_current_progress(self) -> float:
        """Retorna progresso do treinamento (0.0 a 1.0)."""
        if len(ACTIVE_TARGETS) == 0:
            return 0.0
        progress = self.current_target_index / len(ACTIVE_TARGETS)
        return min(1.0, progress)
