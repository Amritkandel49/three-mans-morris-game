import random
# from typing import Dict, List, Tuple, Optional


class ThreeMensMorris:
    def __init__(self, difficulty='medium', human_first=None):
        self.positions = {k: None for k in 'abcdefghi'}
        self.adjacency = {
            'a': ['b', 'd', 'e'],
            'b': ['a', 'c', 'e'],
            'c': ['b', 'f', 'e'],
            'd': ['a', 'e', 'g'],
            'e': ['a', 'b', 'c', 'd', 'f', 'g', 'h', 'i'],
            'f': ['c', 'e', 'i'],
            'g': ['d', 'e', 'h'],
            'h': ['e', 'g', 'i'],
            'i': ['e', 'f', 'h']
        }

        self.phase = 'placement'  # 'placement' or 'movement'
        
        # Randomly decide who goes first if not specified
        if human_first is None:
            human_first = random.choice([True, False])
        
        self.human_player = 'blue'  # Blue for human
        self.ai_player = 'red'      # Red for AI
        self.current_player = self.human_player if human_first else self.ai_player
        self.pieces_placed = {'blue': 0, 'red': 0}
        self.max_pieces = 3
        
        # Difficulty levels with different search depths
        self.difficulty_depths = {
            'easy': 1,
            'medium': 2,
            'hard': 3,
            'expert': 5
        }
        self.difficulty = difficulty
        self.search_depth = self.difficulty_depths.get(difficulty, 4)

    def check_winner(self):
        winning_combinations = [
            ('a', 'b', 'c'),
            ('d', 'e', 'f'),
            ('g', 'h', 'i'),
            ('a', 'd', 'g'),
            ('b', 'e', 'h'),
            ('c', 'f', 'i'),
            ('a', 'e', 'i'),
            ('c', 'e', 'g')
        ]
        for combo in winning_combinations:
            if self.positions[combo[0]] is not None and \
               self.positions[combo[0]] == self.positions[combo[1]] == self.positions[combo[2]]:
                return self.positions[combo[0]]
        return None
    
    def is_game_over(self):
        winner = self.check_winner()
        if winner:
            return True, winner
        
        # Check if current player has any valid moves in movement phase
        if self.phase == 'movement':
            valid_moves = self.get_valid_moves(self.current_player)
            if not valid_moves:
                # Current player has no moves, opponent wins
                opponent = 'red' if self.current_player == 'blue' else 'blue'
                return True, opponent
        
        return False, None
    

    def place_piece(self, position):
        if self.phase != 'placement':
            raise Exception("Cannot place piece during movement phase.")
        if self.positions[position] is not None:
            raise Exception(f"Position {position} is already occupied.")
        
        self.positions[position] = self.current_player
        self.pieces_placed[self.current_player] += 1
        
        # Check if placement phase is over
        if self.pieces_placed['blue'] == self.max_pieces and self.pieces_placed['red'] == self.max_pieces:
            self.phase = 'movement'
        
        game_over, winner = self.is_game_over()
        if game_over:
            return f"Player {winner} wins!"
        
        self.current_player = 'red' if self.current_player == 'blue' else 'blue'
        return "Piece placed successfully."
    
    def move_piece(self, from_position, to_position):
        if self.phase != 'movement':
            raise Exception("Cannot move piece during placement phase.")
        if self.positions[from_position] != self.current_player:
            raise Exception(f"Cannot move piece from {from_position} as it is not your piece.")
        if self.positions[to_position] is not None:
            raise Exception(f"Position {to_position} is already occupied.")
        if to_position not in self.adjacency[from_position]:
            raise Exception(f"Cannot move to {to_position} from {from_position}.")
        
        self.positions[to_position] = self.current_player
        self.positions[from_position] = None
        
        game_over, winner = self.is_game_over()
        if game_over:
            return f"Player {winner} wins!"
        
        self.current_player = 'red' if self.current_player == 'blue' else 'blue'
        return "Piece moved successfully."
    

    def render_board(self):
        board = ""
        rows = ['abc', 'def', 'ghi']
        connectors = ['| \\ | / |', '| / | \\ |']
        for i, row in enumerate(rows):
            row_str = ""
            for j, each in enumerate(row):
                row_str += (self.positions[each] if self.positions[each] is not None else '.')
                if j < 2:
                    row_str += "---"
            board += row_str + "\n"
            if i < 2:
                board += connectors[i] + "\n"
        print(board)
        return board.strip()
    
    def get_valid_moves(self, player):
        """Get all valid moves for a player"""
        valid_moves = []
        
        if self.phase == 'placement':
            # In placement phase, any empty position is valid
            for pos in 'abcdefghi':
                if self.positions[pos] is None:
                    valid_moves.append(('place', pos))
        else:
            # In movement phase, find all valid moves
            for pos in 'abcdefghi':
                if self.positions[pos] == player:
                    for adjacent in self.adjacency[pos]:
                        if self.positions[adjacent] is None:
                            valid_moves.append(('move', pos, adjacent))
        
        return valid_moves
    
    def make_move(self, move):
        """Make a move and return the previous state for undo"""
        prev_state = {
            'positions': self.positions.copy(),
            'current_player': self.current_player,
            'phase': self.phase,
            'pieces_placed': self.pieces_placed.copy()
        }
        
        if move[0] == 'place':
            self.place_piece(move[1])
        else:  # move
            self.move_piece(move[1], move[2])
        
        return prev_state
    
    def undo_move(self, prev_state):
        """Undo a move by restoring previous state"""
        self.positions = prev_state['positions']
        self.current_player = prev_state['current_player']
        self.phase = prev_state['phase']
        self.pieces_placed = prev_state['pieces_placed']
    
    def evaluate_position(self):
        """Evaluate the current position for the AI"""
        game_over, winner = self.is_game_over()
        
        if game_over:
            if winner == self.ai_player:
                return 1000
            elif winner == self.human_player:
                return -1000
            else:
                return 0
        
        score = 0
        
        # Check for potential winning lines
        winning_combinations = [
            ('a', 'b', 'c'), ('d', 'e', 'f'), ('g', 'h', 'i'),
            ('a', 'd', 'g'), ('b', 'e', 'h'), ('c', 'f', 'i'),
            ('a', 'e', 'i'), ('c', 'e', 'g')
        ]
        
        for combo in winning_combinations:
            ai_count = sum(1 for pos in combo if self.positions[pos] == self.ai_player)
            human_count = sum(1 for pos in combo if self.positions[pos] == self.human_player)
            empty_count = sum(1 for pos in combo if self.positions[pos] is None)
            
            if human_count == 0:  # AI can potentially win this line
                if ai_count == 2 and empty_count == 1:
                    score += 50  # One move away from winning
                elif ai_count == 1 and empty_count == 2:
                    score += 10  # Two moves away from winning
            
            if ai_count == 0:  # Human can potentially win this line
                if human_count == 2 and empty_count == 1:
                    score -= 50  # Block human from winning
                elif human_count == 1 and empty_count == 2:
                    score -= 10  # Human has potential
        
        # Prefer center position
        if self.positions['e'] == self.ai_player:
            score += 5
        elif self.positions['e'] == self.human_player:
            score -= 5
        
        return score
    
    def minimax(self, depth, maximizing_player, alpha, beta):
        """Minimax algorithm with alpha-beta pruning"""
        game_over, _ = self.is_game_over()
        
        if game_over or depth == 0:
            return self.evaluate_position()
        
        valid_moves = self.get_valid_moves(self.current_player)
        
        if maximizing_player:
            max_eval = float('-inf')
            for move in valid_moves:
                prev_state = self.make_move(move)
                eval_score = self.minimax(depth - 1, False, alpha, beta)
                self.undo_move(prev_state)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Alpha-beta pruning
            return max_eval
        else:
            min_eval = float('inf')
            for move in valid_moves:
                prev_state = self.make_move(move)
                eval_score = self.minimax(depth - 1, True, alpha, beta)
                self.undo_move(prev_state)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha-beta pruning
            return min_eval
    
    def get_ai_move(self, depth=None):
        """Get the best move for AI using minimax with alpha-beta pruning"""
        if depth is None:
            depth = self.search_depth
            
        valid_moves = self.get_valid_moves(self.ai_player)
        
        if not valid_moves:
            return None
        
        # Add some randomness for easy mode
        if self.difficulty == 'easy' and random.random() < 0.3:
            return random.choice(valid_moves)
        
        best_move = None
        best_score = float('-inf')
        
        for move in valid_moves:
            prev_state = self.make_move(move)
            score = self.minimax(depth - 1, False, float('-inf'), float('inf'))
            self.undo_move(prev_state)
            
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move
    
    def to_dict(self):
        """Convert game state to dictionary for JSON serialization"""
        return {
            'positions': self.positions,
            'phase': self.phase,
            'current_player': self.current_player,
            'pieces_placed': self.pieces_placed,
            'difficulty': self.difficulty,
            'human_player': self.human_player,
            'ai_player': self.ai_player
        }
    
    def from_dict(self, data):
        """Restore game state from dictionary"""
        self.positions = data['positions']
        self.phase = data['phase']
        self.current_player = data['current_player']
        self.pieces_placed = data['pieces_placed']
        self.difficulty = data['difficulty']
        self.human_player = data['human_player']
        self.ai_player = data['ai_player']
        self.search_depth = self.difficulty_depths.get(self.difficulty, 4)
    

def play_game():
    """Main game loop for human vs AI"""
    game = ThreeMensMorris()
    print("Welcome to Three Men's Morris!")
    print("You are X, AI is O")
    print("Positions are labeled a-i:")
    print("a---b---c")
    print("| \\ | / |")
    print("d---e---f")
    print("| / | \\ |")
    print("g---h---i")
    print()
    
    while True:
        game.render_board()
        print(f"Current phase: {game.phase}")
        print(f"Current player: {game.current_player}")
        
        game_over, winner = game.is_game_over()
        if game_over:
            print(f"\nGame Over! Player {winner} wins!")
            break
        
        if game.current_player == game.human_player:
            # Human player turn
            try:
                if game.phase == 'placement':
                    position = input(f"Enter position to place your piece (a-i): ").strip().lower()
                    if position not in 'abcdefghi':
                        print("Invalid position! Please enter a letter from a-i")
                        continue
                    result = game.place_piece(position)
                    print(result)
                else:
                    # Movement phase
                    valid_moves = game.get_valid_moves(game.human_player)
                    if not valid_moves:
                        print("No valid moves available!")
                        break
                    
                    print("Available moves:")
                    for i, move in enumerate(valid_moves):
                        print(f"{i+1}. Move from {move[1]} to {move[2]}")
                    
                    try:
                        choice = int(input("Choose move number: ")) - 1
                        if 0 <= choice < len(valid_moves):
                            move = valid_moves[choice]
                            result = game.move_piece(move[1], move[2])
                            print(result)
                        else:
                            print("Invalid choice!")
                            continue
                    except ValueError:
                        # Allow manual input
                        move_input = input("Enter move as 'from to' (e.g., 'a b'): ").strip().lower().split()
                        if len(move_input) == 2:
                            from_pos, to_pos = move_input
                            if from_pos in 'abcdefghi' and to_pos in 'abcdefghi':
                                result = game.move_piece(from_pos, to_pos)
                                print(result)
                            else:
                                print("Invalid positions!")
                                continue
                        else:
                            print("Invalid input format!")
                            continue
                        
            except Exception as e:
                print(f"Error: {e}")
                continue
        
        else:
            # AI player turn
            print("AI is thinking...")
            ai_move = game.get_ai_move()
            
            if ai_move is None:
                print("AI has no valid moves!")
                break
            
            try:
                if ai_move[0] == 'place':
                    result = game.place_piece(ai_move[1])
                    print(f"AI placed piece at {ai_move[1]}")
                    print(result)
                else:
                    result = game.move_piece(ai_move[1], ai_move[2])
                    print(f"AI moved piece from {ai_move[1]} to {ai_move[2]}")
                    print(result)
            except Exception as e:
                print(f"AI Error: {e}")
                break
        
        print()


if __name__ == "__main__":
    play_game()