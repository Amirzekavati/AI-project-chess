#!/usr/bin/env python
from game import Board, game_as_text
from random import randint


# This file is your main submission that will be graded against. Do not
# add any classes or functions to this file that are not part of the classes
# that we want.


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

        raise NotImplementedError


class CustomEvalFn:
    def __init__(self):
        pass

    def score(self, game, maximizing_player_turn=True):
        """Score the current game state

        Custom evaluation function that acts however you think it should. This
        is not required but highly encouraged if you want to build the best
        AI possible.

        Args
            game (Board): The board and game state.
            maximizing_player_turn (bool): True if maximizing player is active.

        Returns:
            float: The current state's score, based on your own heuristic.

        """
   
        acitve_player_pos = game.__last_queen_move__[game.__active_players_queen__]
        inactive_player_pos = game.__last_queen_move__[game.__inactive_players_queen__]
        edge_distance = min(acitve_player_pos[0], game.height - 1 - acitve_player_pos[0], acitve_player_pos[1], game.width - 1 - acitve_player_pos[1])

        # center_v = 1 / (1 + abs(game.height//2 - acitve_player_pos[0]) + abs(game.width//2 - acitve_player_pos[1]))
        mobility_score = len(game.get_legal_moves()) - len(game.get_opponent_moves())

        attacking_score = -1 if inactive_player_pos in game.get_legal_moves() else 0
        # attacking_score = -1 if inactive_player_pos in game.get_legal_moves() else 0
        
        edge_v = -1 if edge_distance == 0 else (-0.5 if edge_distance == 1 else 0)
        
        # return mobility_score + 3 * attacking_score + 2*edge_v
        return mobility_score + 3 * attacking_score + 2*edge_v 
        # return mobility_score + 2*edge_v 
            
        

        # # TODO: finish this function!
        # raise NotImplementedError
    


class CustomPlayer:
    
    # TODO: finish this class!
    """Player that chooses a move using your evaluation function
    and a minimax algorithm with alpha-beta pruning.
    You must finish and test this player to make sure it properly
    uses minimax and alpha-beta to return a good move."""

    def __init__(self, eval_fn=OpenMoveEvalFn()):
        """Initializes your player.

        if you find yourself with a superior eval function, update the default
        value of `eval_fn` to `CustomEvalFn()`

        Args:
            search_depth (int): The depth to which your agent will search
            eval_fn (function): Utility function used by your agent
        """
        self.eval_fn = CustomEvalFn()
        self.search_depth = 4

    def move(self, game, legal_moves, time_left):
        """Called to determine one move by your agent

            Note:
                1. Do NOT change the name of this 'move' function. We are going to call
                the this function directly.
                2. Change the name of minimax function to alphabeta function when
                required. Here we are talking about 'minimax' function call,
                NOT 'move' function name.
                Args:
                game (Board): The board and game state.
                legal_moves (list): List of legal moves
                time_left (function): Used to determine time left before timeout

            Returns:
                tuple: best_move
            """
        best_move, utility = self.alphabeta(game, time_left, depth=self.search_depth)
        return best_move

    def utility(self, game, maximizing_player):
        """Can be updated if desired. Not compulsory. """
        return self.eval_fn.score(game)

    def minimax(self, game, time_left, depth, maximizing_player=True):
        """Implementation of the minimax algorithm

        Args:
            game (Board): A board and game state.
            time_left (function): Used to determine time left before timeout
            depth: Used to track how deep you are in the search tree
            maximizing_player (bool): True if maximizing player is active.

        Returns:
            (tuple, int): best_move, val
        """
        # TODO: finish this function!
        best_move = (0, 0)
        best_val = float('-inf')

        if not game.get_legal_moves():
            return best_move, best_val

        for move in game.get_legal_moves():
            next_game, _, _ = game.forecast_move(move)
            value = self.min_value(next_game, depth - 1, best_move) if maximizing_player else self.max_value(next_game, depth - 1, best_move)
            if maximizing_player:
                if value > best_val:
                    best_val, best_move = value, move
            else:
                if value < best_val:
                    best_val, best_move = value, move

        return best_move, best_val

    # Maximizing player strategy
    def max_value(self, game, depth, last_best_move):
        if self.time_left() < 10:
            return self.utility(game, maximizing_player=True)

        
        # Terminal situation: depth = 0 or illegal move
        if depth == 0 or not game.get_legal_moves():
            return self.utility(game, maximizing_player=True)

        # Normal situation: find the maximizing value
        best_score = float('-inf')
        for move in game.get_legal_moves():
            next_game, _, _ = game.forecast_move(move)
            best_score = max(best_score, self.min_value(next_game, depth - 1, last_best_move))
        return best_score

    # Minimizing player strategy
    def min_value(self, game, depth, last_best_move):
        if self.time_left() < 0.1:
            return self.utility(game, maximizing_player=False)


        # Terminal situation: depth = 0 or illegal move
        if depth == 0 or not game.get_legal_moves():
            return self.utility(game, maximizing_player=False)

        # Normal situation: find the minimizing value
        best_score = float('inf')
        for move in game.get_legal_moves():
            next_game, _, _ = game.forecast_move(move)
            best_score = min(best_score, self.max_value(next_game, depth - 1, last_best_move))
        return best_score


    def alphabeta(self, game, time_left, depth, alpha=float("-inf"), beta=float("inf"), maximizing_player=True):
        """Implementation of the alphabeta algorithm

        Args:
            game (Board): A board and game state.
            time_left (function): Used to determine time left before timeout
            depth: Used to track how deep you are in the search tree
            alpha (float): Alpha value for pruning
            beta (float): Beta value for pruning
            maximizing_player (bool): True if maximizing player is active.

        Returns:
            (tuple, int): best_move, val
        """
        if time_left() < 10:
            return None, self.utility(game, maximizing_player)
        
        if depth == 0 or not game.get_legal_moves() :
            return None, self.utility(game, maximizing_player)

        best_move = None

        if maximizing_player:
            bestValue = float("-inf")
            for move in game.get_legal_moves():
                next_board, _, _ = game.forecast_move(move)
                # if time_left() <= 800:
                #     return best_move, bestValue
                _, value = self.alphabeta(next_board, time_left, depth - 1, alpha, beta, maximizing_player=False)
                if value > bestValue:
                    bestValue = value
                    best_move = move
                alpha = max(alpha, bestValue)
                if alpha >= beta:
                    break 
            return best_move, bestValue

        else:
            bestValue = float("inf")
            for move in game.get_legal_moves():
                next_board, _, _ = game.forecast_move(move)
                # if time_left() <= 800:
                #     return best_move, bestValue
                _, value = self.alphabeta(next_board, time_left, depth - 1, alpha, beta, maximizing_player=True)
                if value < bestValue:
                    bestValue = value
                    best_move = move
                beta = min(beta, bestValue)
                if alpha >= beta:
                    break
            return best_move, bestValue

        # TODO: finish this function!
        raise NotImplementedError
        
