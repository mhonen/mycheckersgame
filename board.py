import pygame

WIDTH = HEIGHT = 650  # increased board size by 10 pixels
ROWS = COLS = 8
SQUARE_SIZE = WIDTH // COLS

DARK = (181, 136, 99)
LIGHT = (240, 217, 181)

class Board:
    def __init__(self):
        self.grid = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.setup_pieces()

    def setup_pieces(self):
        for row in range(ROWS):
            for col in range(COLS):
                self.grid[row][col] = None
        for row in range(ROWS):
            for col in range(COLS):
                if (row + col) % 2 != 0:
                    if row < 3:
                        self.grid[row][col] = 'b'
                    elif row > 4:
                        self.grid[row][col] = 'r'

    def get_piece(self, row, col):
        if 0 <= row < ROWS and 0 <= col < COLS:
            return self.grid[row][col]
        return None

    def set_piece(self, row, col, piece):
        if 0 <= row < ROWS and 0 <= col < COLS:
            self.grid[row][col] = piece

    def is_enemy(self, piece, other):
        if piece in ('r', 'R'):
            return other in ('b', 'B')
        if piece in ('b', 'B'):
            return other in ('r', 'R')
        return False

    def promote_if_needed(self, row, col):
        piece = self.get_piece(row, col)
        if piece == 'r' and row == 0:
            self.set_piece(row, col, 'R')
        elif piece == 'b' and row == ROWS - 1:
            self.set_piece(row, col, 'B')

    def get_valid_moves_for_piece(self, row, col, player):
        piece = self.get_piece(row, col)
        if piece is None:
            return []
        if player == 'r' and piece not in ('r', 'R'):
            return []
        if player == 'b' and piece not in ('b', 'B'):
            return []

        directions = []
        if piece in ('r', 'R'):
            directions.extend([(-1, -1), (-1, 1)])
        if piece in ('b', 'B'):
            directions.extend([(1, -1), (1, 1)])
        if piece in ('R', 'B'):
            directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        moves = []
        captures = []

        for dr, dc in directions:
            nr = row + dr
            nc = col + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and self.get_piece(nr, nc) is None:
                moves.append(((nr, nc), False))
            elif 0 <= nr < ROWS and 0 <= nc < COLS and self.is_enemy(piece, self.get_piece(nr, nc)):
                jr = nr + dr
                jc = nc + dc
                if 0 <= jr < ROWS and 0 <= jc < COLS and self.get_piece(jr, jc) is None:
                    captures.append(((jr, jc), True))

        return captures if captures else moves

    def get_all_moves(self, player):
        all_moves = []
        all_captures = []
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.get_piece(row, col)
                if piece is None:
                    continue
                if player == 'r' and piece not in ('r', 'R'):
                    continue
                if player == 'b' and piece not in ('b', 'B'):
                    continue
                piece_moves = self.get_valid_moves_for_piece(row, col, player)
                for dest, capture in piece_moves:
                    if capture:
                        all_captures.append(((row, col), dest, capture))
                    else:
                        all_moves.append(((row, col), dest, capture))

        return all_captures if all_captures else all_moves

    def apply_move(self, src, dst, is_capture):
        sr, sc = src
        dr, dc = dst
        piece = self.get_piece(sr, sc)
        self.set_piece(sr, sc, None)
        self.set_piece(dr, dc, piece)

        if is_capture:
            mr = (sr + dr) // 2
            mc = (sc + dc) // 2
            self.set_piece(mr, mc, None)

        self.promote_if_needed(dr, dc)

    def draw(self, win):
        self.draw_squares(win)
        self.draw_pieces(win)

    def draw_squares(self, win):
        for row in range(ROWS):
            for col in range(COLS):
                color = DARK if (row + col) % 2 else LIGHT
                pygame.draw.rect(win, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def draw_pieces(self, win):
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.grid[row][col]
                if piece is not None:
                    center = (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2)
                    radius = SQUARE_SIZE // 2 - 8
                    color = (0, 0, 0) if piece in ('b', 'B') else (220, 20, 60)
                    pygame.draw.circle(win, color, center, radius)
                    if piece in ('B', 'R'):
                        pygame.draw.circle(win, (255, 215, 0), center, radius - 10, 3)
