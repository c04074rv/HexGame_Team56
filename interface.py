import pyspiel
import numpy as np
from config import Config
import mcts
import uniform_random
import re
import model
import evaluator

bot_types = ("mcts", "az", "random")


def _init_bot(bot_type, game, player_id, config: Config):
    """Initializes a bot by type."""  # For now just random rollout, pending training
    # Random seed
    rng = np.random.RandomState(config.seed) if config.seed is not None else config.seed

    if bot_type == "mcts":
        eval = mcts.RandomRolloutEvaluator(config.max_simulations, rng)
        b = mcts.MCTSBot(
            game,
            uct_c=config.uct_c,
            max_simulations=config.max_simulations,
            evaluator=eval,
            random_state=rng,
            solve=config.solve,
            verbose=False,
        )
        b._player_id = player_id
    elif bot_type == "random":
        b = uniform_random.UniformRandomBot(player_id, rng)
    elif bot_type == "az":
        policy = model.Model.from_checkpoint(config.az_path, device="cpu")
        eval = evaluator.AlphaZeroEvaluator(game, policy)
        b = mcts.MCTSBot(
            game,
            uct_c=config.uct_c,
            max_simulations=config.max_simulations,
            evaluator=eval,
            child_selection_fn=mcts.SearchNode.puct_value,
            random_state=rng,
            solve=config.solve,
            verbose=False,
        )
        b._player_id = player_id
    else:
        raise ValueError(f"Bot {bot_type} not valid.")

    return b


class Interface(object):
    def __init__(self, config, colour=None) -> None:
        self.config = config
        self.bot_type = config.bot_type
        self.game = pyspiel.load_game(config.game, {"num_cols": 11, "num_rows": 11})
        self.state = None
        self.board_size = 11
        self.colour = colour
        self.verbose = config.verbose
        self.first_turn = ()  # x,y,p
        self.turn_count = 1
        self.history = []
        self.player = -1

    def initialise_game(self, player, colour):
        self.state = self.game.new_initial_state()
        self.bot = _init_bot(self.bot_type, self.game, player, self.config)
        self.player = player
        self.colour = colour
        if self.verbose:
            print(f"bot {self.bot} is player {player}")

    def inform_move(self, x, y=None):
        """Informs the state and player of the opponents move"""
        # Convert coordinate action to 1d index
        if y is not None:
            move = self._get_action(x, y)
            if move is None:
                return
        else:
            move = x

        # Inform our bot of the action
        # print(self.state)
        self.bot.inform_action(self.state, int(not self.player), move)

        self.history.append(move)

        # Make the move on our own board
        self.state.apply_action(move)

        if self.verbose:
            print(f"Player {self.player} received action: {move}")

    def make_move(self):
        """Queries the player for a move"""
        if not self.state.is_terminal():
            # Just for safety purposes
            if self.state.is_chance_node():
                raise ValueError("HEX game cannot have chance player.")
            elif self.state.is_simultaneous_node():
                raise ValueError("HEX game cannot have simultaneous nodes.")

        action = self.bot.step(self.state)

        self.history.append(action)

        self.state.apply_action(action)

        if self.verbose:
            print(f"Player makes move {action}")

        return action

    def swap_players(self):
        """swaps the board and initialises new players"""
        move = self.state.history()[0]
        self.initialise_game(int(not self.player), self.opp_colour())
        self.inform_move(move)

    def opp_colour(self):
        """Returns the char representation of the colour opposite to the
        current one.
        """
        if self.colour == "R":
            return "B"
        elif self.colour == "B":
            return "R"
        else:
            return "None"

    # Helper for working with action/action_str representation
    def _get_action(self, x: int, y: int):
        action = x * 11 + y
        actions = self.state.legal_actions()
        if action in actions:
            return action
        if action == self.history[-1]:
            return None
        raise ValueError("Something weird happened.")
