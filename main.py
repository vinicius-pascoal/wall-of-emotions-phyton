from __future__ import annotations

import argparse
import sys

import cv2
import pygame

from src import config
from src.expression_reader import PyFeatExpressionReader
from src.game_manager import GameManager, GamePhase
from src.hud import Hud
from src.wall import Wall


def parse_args():
    parser = argparse.ArgumentParser(description="Expression Wall: Hole in the Wall com Py-Feat")
    parser.add_argument("--camera", type=int, default=config.CAMERA_INDEX, help="Índice da webcam. Padrão: 0")
    parser.add_argument(
        "--interval",
        type=float,
        default=config.DETECTION_INTERVAL_SECONDS,
        help="Intervalo entre inferências do Py-Feat em segundos. Padrão: 0.8",
    )
    parser.add_argument("--hide-debug", action="store_true", help="Inicia com debug oculto")
    return parser.parse_args()


def open_camera(camera_index: int):
    camera = cv2.VideoCapture(camera_index)
    if not camera.isOpened():
        return None

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    return camera


def main() -> int:
    args = parse_args()

    pygame.init()
    pygame.display.set_caption("Expression Wall - Py-Feat")
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    camera = open_camera(args.camera)
    if camera is None:
        print(f"Não foi possível abrir a webcam de índice {args.camera}.")
        print("Tente fechar outros apps que usam a câmera ou rode: python main.py --camera 1")
        pygame.quit()
        return 1

    expression_reader = PyFeatExpressionReader(detection_interval=args.interval)
    game = GameManager()
    hud = Hud(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
    wall = Wall(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)

    show_debug = not args.hide_debug
    running = True
    latest_frame = None

    while running:
        dt = clock.tick(config.FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_d:
                    show_debug = not show_debug
                elif event.key == pygame.K_r and game.phase == GamePhase.GAME_OVER:
                    game.restart()

        ok, frame = camera.read()
        if ok:
            latest_frame = cv2.flip(frame, 1)
            expression_reader.submit_frame(latest_frame)

        game.update(dt, expression_reader)
        snapshot = expression_reader.get_snapshot()

        screen.fill(config.BACKGROUND_COLOR)
        wall.draw(screen, game.current_target, game.get_wall_progress(), hud.font_medium)
        hud.draw(screen, game, snapshot, latest_frame, show_debug)
        pygame.display.flip()

    camera.release()
    pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
