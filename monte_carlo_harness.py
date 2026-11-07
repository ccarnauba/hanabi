# pyright: reportUnknownMemberType=false
from main import *
import statistics
import matplotlib.pyplot as plt
import unambiguous_hinting_player
import random_player

DEFAULT_TEST_ITERATIONS = 100


def summarize(name: str, values: list[int]) -> str:
    mean = statistics.mean(values)
    median = statistics.median(values)
    std_dev = statistics.stdev(values)
    summary = f"{name}: mean={mean:.2f}, median={median:g}, std dev={std_dev:.2f}"
    print(summary)
    return summary

def test_harness(player_list : list[Player]):
    game_iteration = 0
    results = [Game(player_list).play() for _ in range(DEFAULT_TEST_ITERATIONS) if print((game_iteration := game_iteration + 1)) or True]
    fig, (score_hist, rounds_hist) = plt.subplots(nrows = 2)

    scores = [game_info.score for game_info in results]
    game_lengths = [game_info.game_length for game_info in results]
    score_summary = summarize("Score", scores)
    rounds_summary = summarize("Rounds", game_lengths)

    rounds_hist.hist(game_lengths)
    rounds_hist.set_title(f"Rounds hist\n{rounds_summary}")
    rounds_hist.set_xlabel("Rounds")
    rounds_hist.set_ylabel("Frequency")

    score_hist.hist(scores, bins = 25)
    score_hist.set_title(f"Score hist\n{score_summary}")
    score_hist.set_xlabel("Score")
    score_hist.set_ylabel("Frequency")

    fig.tight_layout()

    plt.show()


# test_harness([random_player.RandomPlayer() for _ in range(4)])
test_harness([unambiguous_hinting_player.Unambiguous_Hinting_Player() for _ in range(4)])
