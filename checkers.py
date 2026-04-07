#!/usr/bin/env python3
"""Main entrypoint for graphical Checkers using pygame."""

import sys

try:
    import pygame
except ImportError:
    print("pygame is required. Install with: pip install pygame")
    sys.exit(1)

from board import Board, ROWS, COLS, SQUARE_SIZE, WIDTH, HEIGHT
from game import CheckersGame

UI_PANEL_HEIGHT = 100
BUTTON_Y = HEIGHT + 60

NEW_GAME_AI_BUTTON = {'x': 10, 'y': BUTTON_Y, 'w': 130, 'h': 30, 'text': 'New Game (AI)'}
NEW_GAME_2P_BUTTON = {'x': 150, 'y': BUTTON_Y, 'w': 140, 'h': 30, 'text': 'New Game (2P)'}
UNDO_BUTTON = {'x': 310, 'y': BUTTON_Y, 'w': 100, 'h': 30, 'text': 'Undo'}
RESTART_BUTTON = {'x': WIDTH - 135, 'y': BUTTON_Y, 'w': 120, 'h': 30, 'text': 'Restart'}


def draw_button(win, font, button, hovered=False):
    color = (212, 212, 212) if hovered else (180, 180, 180)
    rect = pygame.Rect(button['x'], button['y'], button['w'], button['h'])
    pygame.draw.rect(win, color, rect)
    pygame.draw.rect(win, (0, 0, 0), rect, 2)
    label = font.render(button['text'], True, (0, 0, 0))
    label_rect = label.get_rect(center=rect.center)
    win.blit(label, label_rect)


def point_in_button(point, button):
    x, y = point
    return button['x'] <= x <= button['x'] + button['w'] and button['y'] <= y <= button['y'] + button['h']


def main():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT + UI_PANEL_HEIGHT))
    pygame.display.set_caption('Checkers - Click to Move')

    font = pygame.font.SysFont(None, 24)
    big_font = pygame.font.SysFont(None, 48)
    clock = pygame.time.Clock()

    game = CheckersGame()
    running = True
    game_over = False
    winner = None

    while running:
        clock.tick(60)

        mouse_pos = pygame.mouse.get_pos()
        restart_hover = point_in_button(mouse_pos, RESTART_BUTTON)
        ai_hover = point_in_button(mouse_pos, NEW_GAME_AI_BUTTON)
        pvp_hover = point_in_button(mouse_pos, NEW_GAME_2P_BUTTON)
        undo_hover = point_in_button(mouse_pos, UNDO_BUTTON)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_over:
                    if ai_hover:
                        game.start_new('ai')
                        game_over = False
                        winner = None
                        continue
                    if pvp_hover:
                        game.start_new('pvp')
                        game_over = False
                        winner = None
                        continue
                    if restart_hover:
                        game.start_new(game.mode)
                        game_over = False
                        winner = None
                        continue
                    # Ignore other clicks when game over
                    continue

                if restart_hover:
                    game.start_new(game.mode)
                    continue
                if ai_hover:
                    game.start_new('ai')
                    continue
                if pvp_hover:
                    game.start_new('pvp')
                    continue
                if undo_hover:
                    game.undo()
                    continue

                if game.turn != 'r':
                    continue

                x, y = event.pos
                if y >= HEIGHT:
                    continue
                col = x // SQUARE_SIZE
                row = y // SQUARE_SIZE

                if game.selected:
                    if game.move((row, col)):
                        if not game.has_move():
                            winner = 'b' if game.turn == 'r' else 'r'
                            game.record_result(winner)
                            game_over = True
                        continue

                game.select(row, col)

        # AI plays automatically for black in AI mode
        if not game_over and game.mode == 'ai' and game.turn == 'b':
            pygame.time.wait(200)  # slight pause so user can follow
            if not game.ai_move():
                game.record_result('r')
                winner = 'r'
                game_over = True
            elif not game.has_move():
                game.record_result('b')
                winner = 'b'
                game_over = True

        game.board.draw(win)

        if game.selected and not game_over:
            r, c = game.selected
            pygame.draw.rect(win, (0, 0, 255), (c * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 3)
            for target, capture in game.valid_moves:
                tr, tc = target
                pygame.draw.rect(win, (0, 255, 0), (tc * SQUARE_SIZE + 8, tr * SQUARE_SIZE + 8, SQUARE_SIZE - 16, SQUARE_SIZE - 16), 3)

        status = f"Turn: {'Red' if game.turn == 'r' else 'Black'} | Mode: {'AI' if game.mode == 'ai' else '2-player'}{' | Chain Capture!' if game.chain_capture else ''}"
        label = font.render(status, True, (0, 0, 0))
        pygame.draw.rect(win, (220, 220, 220), (0, HEIGHT, WIDTH, UI_PANEL_HEIGHT))
        win.blit(label, (10, HEIGHT + 10))

        # Scoreboard with contrasting background and bolder color
        scores = f"Score - Red: {game.scores['r']}  Black: {game.scores['b']}  Draw: {game.scores['draw']}"
        score_rect = pygame.Surface((WIDTH, 22), flags=pygame.SRCALPHA)
        score_rect.fill((0, 0, 0, 170))
        win.blit(score_rect, (0, HEIGHT + 35))
        score_label = font.render(scores, True, (255, 255, 255))
        win.blit(score_label, (10, HEIGHT + 38))

        # Buttons
        draw_button(win, font, NEW_GAME_AI_BUTTON, ai_hover)
        draw_button(win, font, NEW_GAME_2P_BUTTON, pvp_hover)
        draw_button(win, font, UNDO_BUTTON, undo_hover)
        draw_button(win, font, RESTART_BUTTON, restart_hover)

        if game_over:
            # Game over overlay
            overlay = pygame.Surface((WIDTH, HEIGHT + UI_PANEL_HEIGHT), flags=pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            win.blit(overlay, (0, 0))

            winner_text = f"{'Red' if winner == 'r' else 'Black'} Wins!"
            winner_label = big_font.render(winner_text, True, (255, 255, 255))
            winner_rect = winner_label.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            win.blit(winner_label, winner_rect)

            sub_text = "Click New Game or Restart to play again"
            sub_label = font.render(sub_text, True, (255, 255, 255))
            sub_rect = sub_label.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
            win.blit(sub_label, sub_rect)

        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
