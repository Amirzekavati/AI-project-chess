#!/usr/bin/env python
from game import Board, game_as_text
from random import randint

# This file is your main submission that will be graded against. Do not
# add any classes or functions to this file that are not part of the classes
# that we want.

threshold = 2


class OpenMoveEvalFn:

    def score(self, game, maximizing_player_turn=True):
        """Score the current game state

        Evaluation function that outputs a score equal to how many
        moves are open for AI player on the board minus how many moves
        are open for Opponent's player on the board.
        Note:
            1. Be very careful while doing opponent's moves. You might end up
               reducing your own moves.
            3. If you think of better evaluation function, do it in CustomEvalFn below.

            Args
                param1 (Board): The board and game state.
                param2 (bool): True if maximizing player is active.

            Returns:
                float: The current state's score. MyMoves-OppMoves.

            """

        # TODO: finish this function!
        return len(game.get_legal_moves()) - len(game.get_opponent_moves())


class CustomEvalFn:
    def __init__(self):
        pass

    def score(self, game, maximizing_player_turn=True):
        # 1. Number of open moves (Basic mobility heuristic)
        my_moves = len(game.get_legal_moves())
        opponent_moves = len(game.get_opponent_moves())

        # 2. Positional advantage based on Manhattan distance
        my_queen_position = game.__last_queen_move__[game.get_active_players_queen()]
        opponent_queen_position = game.__last_queen_move__[game.get_inactive_players_queen()]

        # Manhattan distance between the two queens
        queen_distance = abs(my_queen_position[0] - opponent_queen_position[0]) + \
                         abs(my_queen_position[1] - opponent_queen_position[1])

        # 3. Control of the center of the board (advantageous positions for queens)
        center_x, center_y = game.width // 2, game.height // 2
        my_queen_to_center = abs(my_queen_position[0] - center_x) + abs(my_queen_position[1] - center_y)
        opponent_queen_to_center = abs(opponent_queen_position[0] - center_x) + abs(
            opponent_queen_position[1] - center_y)

        # 4. Push opportunity (whether a queen can be pushed off the board)
        push_advantage = 0
        if game.get_legal_moves():
            for move in game.get_legal_moves():
                _, _, is_push = move
                if is_push:
                    push_advantage += 1

        # Combine these factors to generate a score.
        score = 0

        # Mobility: the more open moves, the better
        score += (my_moves - opponent_moves) * 10

        # Positional advantage: the closer to the center, the better
        score += (opponent_queen_to_center - my_queen_to_center) * 5

        # Distance between queens: closer queens may lead to more exciting moves
        score += queen_distance * 2

        # Push advantage: reward pushes
        score += push_advantage * 8

        return score


class CustomPlayer:

    def __init__(self, eval_fn=CustomEvalFn()):
        self.eval_fn = eval_fn
        self.search_depth = 7  # You can change it!
        self.time_left = None

    def move(self, game, legal_moves, time_left):
        self.time_left = time_left
        best_move, utility = self.alphabeta(game, time_left, depth=self.search_depth)
        return best_move

    def utility(self, game, maximizing_player):
        """Can be updated if desired. Not compulsory. """
        return self.eval_fn.score(game)

    def minimax(self, game, time_left, depth, maximizing_player=True):
        best_move = (0, 0)
        best_val = float('-inf')

        if not game.get_legal_moves():
            return best_move, best_val

        for move in game.get_legal_moves():
            next_game, _, _ = game.forecast_move(move)
            value = self.min_value(next_game, depth - 1, best_move) if maximizing_player else self.max_value(next_game,
                                                                                                             depth - 1,
                                                                                                             best_move)
            if maximizing_player:
                if value > best_val:
                    best_val, best_move = value, move
            else:
                if value < best_val:
                    best_val, best_move = value, move

        return best_move, best_val

    # Maximizing player strategy
    def max_value(self, game, depth, last_best_move):
        if self.time_left() < threshold:
            raise TimeoutError

        # Terminal situation: depth = 0 or illegal move
        if depth == 0 or not game.get_legal_moves():
            return self.utility(game, True)

        # Normal situation: find the maximizing value
        best_score = float('-inf')
        for move in game.get_legal_moves():
            next_game, _, _ = game.forecast_move(move)
            best_score = max(best_score, self.min_value(next_game, depth - 1, last_best_move))
        return best_score

    # Minimizing player strategy
    def min_value(self, game, depth, last_best_move):

        if self.time_left() < threshold:
            raise TimeoutError

        # Terminal situation: depth = 0 or illegal move
        if depth == 0 or not game.get_legal_moves():
            return self.utility(game, False)

        # Normal situation: find the minimizing value
        best_score = float('inf')
        for move in game.get_legal_moves():
            next_game, _, _ = game.forecast_move(move)
            best_score = min(best_score, self.max_value(next_game, depth - 1, last_best_move))
        return best_score

    def alphabeta(self, game, time_left, depth, alpha=float("-inf"), beta=float("inf"), maximizing_player=True):

        best_move = None

        if time_left() < threshold:
            return best_move, self.utility(game, True)

        legal_moves = game.get_legal_moves()
        if not legal_moves or depth == 0:
            return best_move, self.utility(game, True)

        if maximizing_player:
            max_eval = float("-inf")
            for move in legal_moves:
                if time_left() < threshold:
                    return best_move, self.utility(game, True)
                new_game, _, _ = game.forecast_move(move)
                _, eval_value = self.alphabeta(new_game, time_left, depth - 1, alpha, beta, False)
                if eval_value > max_eval:
                    max_eval = eval_value
                    best_move = move
                alpha = max(alpha, eval_value)
                if beta <= alpha:
                    break
            return best_move, max_eval
        else:
            min_eval = float("inf")
            for move in legal_moves:
                if time_left() < threshold:
                    return best_move, self.utility(game, False)
                new_game, _, _ = game.forecast_move(move)
                _, eval_value = self.alphabeta(new_game, time_left, depth - 1, alpha, beta, True)
                if eval_value < min_eval:
                    min_eval = eval_value
                    best_move = move
                beta = min(beta, eval_value)
                if beta <= alpha:
                    break
            return best_move, min_eval
