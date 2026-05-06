from enum import Enum
from . import config


class ExpressionTarget(Enum):
    SMILE = "Smile"
    DISGUST = "Disgust"
    SURPRISE = "Surprise"
    NEUTRAL = "Neutral"


TARGET_TO_EMOTION_COLUMN = {
    ExpressionTarget.SMILE: "happiness",
    ExpressionTarget.DISGUST: "disgust",
    ExpressionTarget.SURPRISE: "surprise",
    ExpressionTarget.NEUTRAL: "neutral",
}

TARGET_LABELS_PT = {
    ExpressionTarget.SMILE: "SORRIA",
    ExpressionTarget.DISGUST: "NOJO",
    ExpressionTarget.SURPRISE: "SURPRESA",
    ExpressionTarget.NEUTRAL: "NEUTRO",
}

TARGET_COLORS = {
    ExpressionTarget.SMILE: config.SMILE_COLOR,
    ExpressionTarget.DISGUST: config.DISGUST_COLOR,
    ExpressionTarget.SURPRISE: config.SURPRISE_COLOR,
    ExpressionTarget.NEUTRAL: config.NEUTRAL_COLOR,
}

ACTIVE_TARGETS = [
    ExpressionTarget.SMILE,
    ExpressionTarget.DISGUST,
    ExpressionTarget.SURPRISE,
]
