import random
from board import Board

class CheckersGame:
    def __init__(self, mode='ai'):
        self.board = Board()
        self.turn = 'r'
        self.selected = None
        self.valid_moves = []
        self.mode = mode  # 'ai' or 'pvp'
        self.move_history = []
        self.scores = {'r': 0, 'b': 0, 'draw': 0}
        self.chain_capture = False

    def start_new(self, mode='ai'):
        self.mode = mode
        self.reset()
        self.move_history.clear()  

    def reset(self):
        self.board.setup_pieces()
        self.turn = 'r'
        self.selected = None
        self.valid_moves = []
        self.chain_capture = False

    def _snapshot(self):
        return {
            'grid': [row[:] for row in self.board.grid],
            'turn': self.turn,
            'selected': self.selected,
            'valid_moves': list(self.valid_moves),
        }

    def undo(self):
        if not self.move_history:
            return False
        state = self.move_history.pop()
        self.board.grid = [row[:] for row in state['grid']]
        self.turn = state['turn']
        self.selected = state['selected']
        self.valid_moves = list(state['valid_moves'])
        return True

    def select(self, row, col):
        if self.chain_capture and self.selected != (row, col):
            return False  # cannot select other pieces during chain

        piece = self.board.get_piece(row, col)
        if piece is None:
            return False

        if (self.turn == 'r' and piece in ('r', 'R')) or (self.turn == 'b' and piece in ('b', 'B')):
            self.selected = (row, col)
            self.valid_moves = self.board.get_valid_moves_for_piece(row, col, self.turn)
            if self.chain_capture:
                self.valid_moves = [m for m in self.valid_moves if m[1]]  # only captures during chain
            return True

        return False

    def move(self, dest):
        if self.selected is None:
            return False

        move = next((m for m in self.valid_moves if m[0] == dest), None)
        if move is None:
            return False

        self.move_history.append(self._snapshot())
        src = self.selected
        self.board.apply_move(src, dest, move[1])

        # Check for chain capture
        if move[1]:  # was a capture
            more_captures = [m for m in self.board.get_valid_moves_for_piece(dest[0], dest[1], self.turn) if m[1]]
            if more_captures:
                self.chain_capture = True
                self.valid_moves = more_captures
                return True  # continue chain, don't switch turn

        # No more captures, end turn
        self.selected = None
        self.valid_moves = []
        self.chain_capture = False
        self.turn = 'b' if self.turn == 'r' else 'r'
        return True

    def has_move(self):
        return bool(self.board.get_all_moves(self.turn))

    def ai_move(self):
        # Black AI, simple heuristic: prioritize captures, random choice
        moves = self.board.get_all_moves('b')
        if not moves:
            return False

        self.move_history.append(self._snapshot())
        chosen = random.choice(moves)
        src, dst, is_capture = chosen
        self.board.apply_move(src, dst, is_capture)

        # Handle chain captures for AI
        while is_capture:
            more_captures = [m for m in self.board.get_valid_moves_for_piece(dst[0], dst[1], 'b') if m[1]]
            if not more_captures:
                break
            chosen = random.choice(more_captures)
            src = dst
            dst, is_capture = chosen[0], chosen[1]
            self.board.apply_move(src, dst, is_capture)
            self.move_history.append(self._snapshot())

        # switch back to red after AI move
        self.turn = 'r'
        self.selected = None
        self.valid_moves = []
        return True

    def record_result(self, winner):
        if winner in self.scores:
            self.scores[winner] += 1
        elif winner == 'draw':
            self.scores['draw'] += 1


