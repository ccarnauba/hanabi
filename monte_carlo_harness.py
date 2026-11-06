from main import *
import matplotlib.pyplot as plt
import random_player

DEFAULT_TEST_ITERATIONS = 1000

def test_harness(player_list : list[Player]):
    results = [Game(player_list).play() for _ in range(DEFAULT_TEST_ITERATIONS)]

    fig, (score_hist, rounds_hist) = plt.subplots(nrows = 2)

    rounds_hist.hist([game_info.game_length for game_info in results] ) #pyright: ignore[reportUnknownMemberType]
    rounds_hist.set_title("Rounds hist") #pyright: ignore[reportUnknownMemberType]
    rounds_hist.set_xlabel("Rounds") #pyright: ignore[reportUnknownMemberType]
    rounds_hist.set_ylabel("Frequency") #pyright: ignore[reportUnknownMemberType]

    score_hist.hist([game_info.score for game_info in results] , bins = 25) #pyright: ignore[reportUnknownMemberType]
    score_hist.set_title("Score hist") #pyright: ignore[reportUnknownMemberType]
    score_hist.set_xlabel("Score") #pyright: ignore[reportUnknownMemberType]
    score_hist.set_ylabel("Frequency") #pyright: ignore[reportUnknownMemberType]

    fig.tight_layout()

    plt.show() #pyright: ignore[reportUnknownMemberType]


test_harness([random_player.RandomDiscarder() for _ in range(4)])
