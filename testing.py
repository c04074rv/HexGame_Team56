"""This is the script to run the bot."""

from absl import flags

import Group56Agent
from config import Config

bot_types = ("mcts", "az", "random")

#########################################
# AGENT CONSTANTS -  Update with az bot
_GAME = "hex"
_BOT = "mcts"
# flags.DEFINE_string("az_path", None,"Path to an alpha_zero checkpoint. Needed by an az player.")
_UCT = 2
_ROLLOUT_COUNT = 1
_MAX_SIMS = 1000
_SEED = 69
# flags.DEFINE_bool("random_first", True, "Play the first move randomly.")
_SOLVE = True
# flags.DEFINE_bool("quiet", False, "Don't show the moves as they're played.")
_VERBOSE = True

# Need tweeking + decide if need 2 bots for represenation; fingers crossed
flags.DEFINE_string("game", "tic_tac_toe", "Name of the game.")
flags.DEFINE_enum("bot_type", "mcts", 1, "Who controls player 1.")
flags.DEFINE_string("gtp_path", None, "Where to find a binary for gtp.")
flags.DEFINE_multi_string("gtp_cmd", [], "GTP commands to run at init.")
flags.DEFINE_string(
    "az_path", None, "Path to an alpha_zero checkpoint. Needed by an az player."
)
flags.DEFINE_integer("uct_c", 2, "UCT's exploration constant.")
flags.DEFINE_integer("rollout_count", 1, "How many rollouts to do.")
flags.DEFINE_integer("max_simulations", 1000, "How many simulations to run.")
flags.DEFINE_integer("num_games", 1, "How many games to play.")
flags.DEFINE_integer("seed", None, "Seed for the random number generator.")
flags.DEFINE_bool("random_first", False, "Play the first move randomly.")
flags.DEFINE_bool("solve", True, "Whether to use MCTS-Solver.")
flags.DEFINE_bool("quiet", False, "Don't show the moves as they're played.")
flags.DEFINE_bool("verbose", False, "Show the MCTS stats of possible moves.")
FLAGS = flags.FLAGS


if __name__ == "__main__":
    bot = FLAGS.bot_type
    if bot not in bot_types:
        raise ValueError(f"Bot value must be one of {bot_types}")

    config = Config(
        game=FLAGS.game,
        bot_type=bot,
        gtp_path=FLAGS.gtp_path,
        gtp_cmd=FLAGS.alpha_zero_mcts,
        az_path=FLAGS.az_path,
        uct_c=FLAGS.uct_c,
        max_simulations=FLAGS.max_simulations,
        num_games=FLAGS.num_games,
        random_first=FLAGS.random_first,
        solve=FLAGS.solve,
        quiet=FLAGS.quiet,
        verbose=FLAGS.verbose,
    )
    agent = Group56Agent.GroupAgent56(config)
    agent.run()
