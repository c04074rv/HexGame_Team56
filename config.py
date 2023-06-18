import collections


class Config(
    collections.namedtuple(
        "Config",
        [
            "game",
            "bot_type",
            "az_path",
            "uct_c",
            "max_simulations",
            "num_games",
            "seed",
            "random_first",
            "solve",
            "verbose",
        ],
    )
):
    """A config for the model/experiment."""

    pass
