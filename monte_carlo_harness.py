# pyright: reportUnknownMemberType=false
from main import *
import statistics
import matplotlib.pyplot as plt
import better_player

DEFAULT_TEST_ITERATIONS = 10


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


test_harness([better_player.BetterPlayer() for _ in range(4)])
