#########################################
# IMPORTS
import socket  # Communication
import numpy as np  # rng-enerator
import re  # Action Representation Etraction

# Command-Line launch support
from absl import app
from absl import flags


# pyspeil and components
import evaluator
import model
import interface
import mcts
from config import Config
import evaluator
import pyspiel
import uniform_random


def _init_bot(bot_type, game, player_id, config: Config):
    """Initializes a bot by type."""  # For now just random rollout, pending training
    # random
    rng = np.random.RandomState(config.seed) if config.seed is not None else config.seed
    """
  
    #az
    if bot_type == "az":
        model = az_model.Model.from_checkpoint(FLAGS.az_path)
        evaluator = az_evaluator.AlphaZeroEvaluator(game, model)
        return mcts.MCTSBot(
            game,
            FLAGS.uct_c,
            FLAGS.max_simulations,
            evaluator,
            random_state=rng,
            child_selection_fn=mcts.SearchNode.puct_value,
            solve=FLAGS.solve,
            verbose=FLAGS.verbose)

    """
    if bot_type == "mcts":
        evaluator = mcts.RandomRolloutEvaluator(config.max_simulations, rng)
        b = mcts.MCTSBot(
            game,
            uct_c=config.uct_c,
            max_simulations=config.max_simulations,
            evaluator=evaluator,
            random_state=rng,
            solve=config.solve,
            verbose=config.verbose,
        )
        b._player_id = player_id
    elif bot_type == "random":
        b = uniform_random.UniformRandomBot(player_id, rng)
    elif bot_type == "az":
        evaluator = evaluator.AlphaZeroEvaluator(config.max_simulations, rng)
        b = mcts.MCTSBot(
            game,
            uct_c=config.uct_c,
            max_simulations=config.max_simulations,
            evaluator=evaluator,
            random_state=rng,
            solve=config.solve,
            verbose=config.verbose,
        )
        b._player_id = player_id
    else:
        raise ValueError(f"Bot {bot_type} not valid.")

    return b


#####################
class GroupAgent56:

    HOST = "127.0.0.1"
    PORT = 1234

    def __init__(self, config: Config):
        self.config = config
        self._turn_count = 1
        self._verbose = config.verbose

    def run(self):
        """A finite-state machine that cycles through waiting for input
        and sending moves.
        """

        """Initialisation of Config from constants"""
        self.interface = interface.Interface(self.config)
        self._turn_count = 1

        states = {
            1: GroupAgent56._connect,
            2: GroupAgent56._wait_start,
            3: GroupAgent56._make_move,
            4: GroupAgent56._wait_message,
            5: GroupAgent56._close,
        }

        res = states[1](self)  ### nicee
        while res != 0:
            res = states[res](self)

    # 1
    def _connect(self):
        """Connects to the socket and jumps to waiting for the start
        message.
        """
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._s.connect((GroupAgent56.HOST, GroupAgent56.PORT))
        return 2

    # 2
    def _wait_start(self):
        """Initialises itself when receiving the start message, then
        answers if it is Red or waits if it is Blue.
        """
        # Recieve + Decode
        data = self._s.recv(1024).decode("utf-8").strip().split(";")

        if data[0] == "START":  # In the Money
            colour = data[2]
            # Initialise the game with player side
            if colour == "R":
                self.interface.initialise_game(0, colour)
                return 3  # Bot p1 with colour red
            else:
                self.interface.initialise_game(1, colour)
                return 4  # Bot p2 waits for next turn

        else:
            Exception("No START message received.")
            return 0

    # 3
    def _make_move(self):
        """Az bot to move, parse response for game engine"""

        # Query our agent to make a move
        action = self.interface.make_move()

        # Convert that move into a sendable message
        msg = self.parse_action_to_str(action)

        # if self._verbose:
        #     print(f"paresed action {action} as {msg}")

        # Send that message off
        self._s.sendall(bytes(msg, "utf-8"))

        return 4

    # 4
    def _wait_message(self):
        """Waits for a new message when it is not its turn.
        Parses and updates state for bot"""

        self._turn_count += 1

        # Receive and Decode
        data = self._s.recv(1024).decode("utf-8").strip().split(";")

        # Check for end
        if data[0] == "END" or data[-1] == "END":
            return 5
        else:
            # Parse the move ??
            # data = self.parse_move(data)

            if data[1] == "SWAP":
                # Swap the player states
                self.interface.swap_players()
                # exit()
            else:
                x, y = data[1].split(",")
                self.interface.inform_move(int(x), int(y))

            if data[-1] == self.interface.colour:
                return 3

        return 4

    # 5
    def _close(self):
        """Closes the socket."""
        self._s.close()
        return 0

    def parse_action_to_str(self, action: int):
        x = action // 11
        y = action % 11
        return f"{x},{y}\n"
