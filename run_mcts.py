"""This is the script to run the bot."""

import Group56Agent
from config import Config


bot_types = ("mcts", "az", "random")
#########################################
# AGENT CONSTANTS -  Update with az bot
game = "hex"
bot_type = "mcts"
az_path = "."
uct_c = 1
max_simulations = 33
num_games = 1
seed = None
random_first = False
solve = True
verbose = False


if __name__ == "__main__":
    config = Config(
        game=game,
        bot_type=bot_type,
        az_path=az_path,
        uct_c=uct_c,
        max_simulations=max_simulations,
        num_games=num_games,
        random_first=random_first,
        solve=solve,
        seed=seed,
        verbose=verbose,
    )
    agent = Group56Agent.GroupAgent56(config)
    agent.run()
