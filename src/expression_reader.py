"""Leitor de expressões usando Py-Feat.

A inferência é executada em uma thread auxiliar para manter a janela do Pygame
responsiva. O jogo usa o último snapshot válido enquanto uma nova detecção roda.
"""

from __future__ import annotations

import os
import tempfile
import threading
import time
from dataclasses import dataclass, field
from typing import Dict, Optional

import cv2

from . import config
from .expression_target import ExpressionTarget, TARGET_TO_EMOTION_COLUMN

EMOTION_COLUMNS = ("happiness", "disgust", "surprise", "neutral")


@dataclass
class EmotionSnapshot:
    has_face: bool = False
    scores: Dict[str, float] = field(
        default_factory=lambda: {
            "happiness": 0.0,
            "disgust": 0.0,
            "surprise": 0.0,
            "neutral": 0.0,
        }
    )
    detected_expression: str = "none"
    processing: bool = False
    error_message: str = ""
    last_face_timestamp: float = 0.0
    last_detection_timestamp: float = 0.0

    def face_visible_with_grace(self) -> bool:
        if self.has_face:
            return True
        if self.last_face_timestamp <= 0:
            return False
        return (time.time() - self.last_face_timestamp) <= config.FACE_LOST_GRACE_SECONDS

    def score(self, emotion_column: str) -> float:
        return float(self.scores.get(emotion_column, 0.0))


class PyFeatExpressionReader:
    def __init__(self, detection_interval: float = config.DETECTION_INTERVAL_SECONDS):
        self.detection_interval = detection_interval
        self.lock = threading.Lock()
        self.snapshot = EmotionSnapshot()
        self.last_submit_timestamp = 0.0
        self._detector = None
        self._load_error: Optional[str] = None
        self._load_detector()

    def _load_detector(self) -> None:
        try:
            from feat import Detector

            print("[Py-Feat] Carregando Detector. Na primeira execução, os modelos podem ser baixados...")
            self._detector = Detector()
            print("[Py-Feat] Detector carregado com sucesso.")
        except Exception as exc:  # pragma: no cover - depende do ambiente local
            self._load_error = str(exc)
            with self.lock:
                self.snapshot.error_message = (
                    "Erro ao carregar Py-Feat. Verifique a instalação com: "
                    "pip install -r requirements.txt. Detalhe: " + str(exc)
                )
            print("[Py-Feat] Erro ao carregar Detector:", exc)

    def submit_frame(self, frame_bgr) -> None:
        if self._detector is None:
            return

        now = time.time()
        with self.lock:
            if self.snapshot.processing:
                return
            if now - self.last_submit_timestamp < self.detection_interval:
                return
            self.snapshot.processing = True
            self.last_submit_timestamp = now

        frame_copy = self._prepare_frame(frame_bgr)
        thread = threading.Thread(target=self._detect_async, args=(frame_copy,), daemon=True)
        thread.start()

    def _prepare_frame(self, frame_bgr):
        height, width = frame_bgr.shape[:2]
        if width <= config.DETECTION_MAX_WIDTH:
            return frame_bgr.copy()

        scale = config.DETECTION_MAX_WIDTH / float(width)
        new_size = (config.DETECTION_MAX_WIDTH, int(height * scale))
        return cv2.resize(frame_bgr, new_size)

    def _detect_async(self, frame_bgr) -> None:
        temp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp_file:
                temp_path = temp_file.name

            cv2.imwrite(temp_path, frame_bgr)
            result = self._detector.detect(temp_path, data_type="image")
            new_snapshot = self._snapshot_from_result(result)
            self._set_snapshot(new_snapshot)

        except Exception as exc:  # pragma: no cover - depende do ambiente local
            previous = self.get_snapshot()
            previous.has_face = False
            previous.error_message = f"Erro na detecção: {exc}"
            previous.last_detection_timestamp = time.time()
            self._set_snapshot(previous)
            print("[Py-Feat] Erro na detecção:", exc)

        finally:
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
            with self.lock:
                self.snapshot.processing = False

    def _snapshot_from_result(self, result) -> EmotionSnapshot:
        now = time.time()

        if result is None or len(result) == 0:
            previous = self.get_snapshot()
            return EmotionSnapshot(
                has_face=False,
                scores=previous.scores,
                detected_expression="none",
                processing=False,
                error_message="",
                last_face_timestamp=previous.last_face_timestamp,
                last_detection_timestamp=now,
            )

        try:
            emotions_df = result.emotions
        except Exception:
            emotions_df = result

        if emotions_df is None or len(emotions_df) == 0:
            previous = self.get_snapshot()
            return EmotionSnapshot(
                has_face=False,
                scores=previous.scores,
                detected_expression="none",
                last_face_timestamp=previous.last_face_timestamp,
                last_detection_timestamp=now,
            )

        selected_index = self._select_best_face_index(result, emotions_df)
        row = emotions_df.loc[selected_index] if selected_index in emotions_df.index else emotions_df.iloc[0]

        scores = {}
        for column in EMOTION_COLUMNS:
            try:
                scores[column] = float(row.get(column, 0.0))
            except Exception:
                scores[column] = 0.0

        detected_expression = max(scores, key=scores.get)

        return EmotionSnapshot(
            has_face=True,
            scores=scores,
            detected_expression=detected_expression,
            processing=False,
            error_message="",
            last_face_timestamp=now,
            last_detection_timestamp=now,
        )

    def _select_best_face_index(self, result, emotions_df):
        try:
            faceboxes = result.faceboxes
            if faceboxes is not None and len(faceboxes) > 0 and "FaceScore" in faceboxes.columns:
                return faceboxes["FaceScore"].astype(float).idxmax()
        except Exception:
            pass
        return emotions_df.index[0]

    def _set_snapshot(self, snapshot: EmotionSnapshot) -> None:
        with self.lock:
            snapshot.processing = self.snapshot.processing
            self.snapshot = snapshot

    def get_snapshot(self) -> EmotionSnapshot:
        with self.lock:
            return EmotionSnapshot(
                has_face=self.snapshot.has_face,
                scores=dict(self.snapshot.scores),
                detected_expression=self.snapshot.detected_expression,
                processing=self.snapshot.processing,
                error_message=self.snapshot.error_message,
                last_face_timestamp=self.snapshot.last_face_timestamp,
                last_detection_timestamp=self.snapshot.last_detection_timestamp,
            )

    def is_matching_target(self, target: ExpressionTarget) -> bool:
        snapshot = self.get_snapshot()
        if not snapshot.face_visible_with_grace():
            return False

        if target == ExpressionTarget.NEUTRAL:
            return (
                snapshot.score("happiness") < config.THRESHOLDS["happiness"]
                and snapshot.score("disgust") < config.THRESHOLDS["disgust"]
                and snapshot.score("surprise") < config.THRESHOLDS["surprise"]
            )

        column = TARGET_TO_EMOTION_COLUMN[target]
        return snapshot.score(column) >= config.THRESHOLDS[column]
