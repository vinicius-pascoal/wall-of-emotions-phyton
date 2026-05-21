"""Gerencia configurações de treinamento personalizadas.

Carrega e aplica thresholds salvos do modo de treinamento.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from . import config


class TrainingConfig:
    """Gerencia thresholds personalizados do modo de treinamento."""

    TRAINING_DATA_FILE = ".training_data.json"

    @staticmethod
    def load_custom_thresholds() -> Optional[Dict[str, float]]:
        """Carrega thresholds personalizados se existirem.

        Returns:
            Dicionário com thresholds customizados ou None se não existir.
        """
        training_file = Path(TrainingConfig.TRAINING_DATA_FILE)

        if not training_file.exists():
            return None

        try:
            with open(training_file, "r") as f:
                data = json.load(f)

            thresholds = data.get("thresholds", {})

            if not thresholds:
                return None

            # Converter de volta para o formato esperado
            result = {}
            for emotion_name, value in thresholds.items():
                # Mapear de volta para as chaves esperadas (aceitar mais emoções)
                emotion_key = emotion_name.lower()
                if emotion_key in [
                    "happiness",
                    "disgust",
                    "surprise",
                    "neutral",
                    "anger",
                    "sadness",
                    "fear",
                    "contempt",
                ]:
                    result[emotion_key] = float(value)

            if result:
                print(
                    "[Training] Thresholds personalizados carregados de .training_data.json")
                return result

        except Exception as e:
            print(f"[Training] Erro ao carregar thresholds: {e}")

        return None

    @staticmethod
    def get_thresholds() -> Dict[str, float]:
        """Retorna thresholds personalizados ou padrão."""
        custom = TrainingConfig.load_custom_thresholds()

        if custom:
            print(f"[Training] Usando thresholds customizados: {custom}")
            return custom

        print("[Training] Usando thresholds padrão")
        return config.THRESHOLDS
