"""Configurações centrais do jogo."""

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 640
FPS = 60
CAMERA_INDEX = 0

# O Py-Feat é mais pesado que um detector simples de OpenCV.
# Por isso, a inferência acontece em intervalos e o jogo usa o último resultado.
DETECTION_INTERVAL_SECONDS = 0.80
DETECTION_MAX_WIDTH = 640
FACE_LOST_GRACE_SECONDS = 0.40

INITIAL_LIVES = 3
INITIAL_ROUND_DURATION = 6.0
MIN_ROUND_DURATION = 2.5
ROUND_DURATION_MULTIPLIER = 0.94
DELAY_BETWEEN_ROUNDS = 1.15
POINTS_PER_HIT = 100

# Py-Feat retorna emoções tipicamente entre 0.0 e 1.0.
# Ajuste estes valores depois de testar com sua webcam/iluminação.
THRESHOLDS = {
    "happiness": 0.55,
    "disgust": 0.35,
    "surprise": 0.45,
    "neutral": 0.45,
}

BACKGROUND_COLOR = (10, 14, 22)
PANEL_COLOR = (17, 24, 39)
PANEL_BORDER_COLOR = (75, 85, 99)
TEXT_COLOR = (249, 250, 251)
TEXT_MUTED_COLOR = (203, 213, 225)
WARNING_COLOR = (245, 158, 11)
SUCCESS_COLOR = (34, 197, 94)
ERROR_COLOR = (239, 68, 68)

SMILE_COLOR = (250, 204, 21)
DISGUST_COLOR = (74, 222, 128)
SURPRISE_COLOR = (56, 189, 248)
NEUTRAL_COLOR = (148, 163, 184)
