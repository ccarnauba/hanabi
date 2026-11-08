# pyright: reportUnknownMemberType=false
from main import *
import statistics
import matplotlib.pyplot as plt
from multiprocessing import Pool
from collections.abc import Callable
import functools

import unambiguous_hinting_player
import random_player

DEFAULT_TEST_ITERATIONS = 10000

# Run 4 processes by default
DEFAULT_POOL_SIZE       = 4

def summarize(name: str, values: list[int]) -> str:
    mean = statistics.mean(values)
    median = statistics.median(values)
    std_dev = statistics.stdev(values)
    summary = f"{name}: mean={mean:.2f}, median={median:g}, std dev={std_dev:.2f}"
    print(summary)
    return summary

def play_one(create_player : Callable[[], Player], num_players : int, seed : int) -> GameInfo:
    return Game([create_player() for _ in range(num_players)], random_seed = seed).play()

def test_harness(create_player : Callable[[], Player], num_players : int):
    results : list[GameInfo] = []

    with Pool(processes=DEFAULT_POOL_SIZE) as pool:
        results = pool.map(functools.partial(play_one, create_player, num_players),\
                           range(DEFAULT_TEST_ITERATIONS))

    fig, (score_hist, rounds_hist, game_end_chart) = plt.subplots(nrows = 3)

    scores = [game_info.score for game_info in results]
    game_lengths = [game_info.game_length for game_info in results]
    end_reasons = [game_info.game_end_reason for game_info in results]
    loss_tally =  {reason_label:\
                   len([reason for reason in end_reasons if reason == reason_label])
                   for reason_label in GameEndReason}

    score_summary = summarize("Score", scores)
    rounds_summary = summarize("Rounds", game_lengths)
    print(f"The games ended due to: {loss_tally}")

    rounds_hist.hist(game_lengths)
    rounds_hist.set_title(f"Rounds hist\n{rounds_summary}")
    rounds_hist.set_xlabel("Rounds")
    rounds_hist.set_ylabel("Frequency")

    score_hist.hist(scores, bins = range(0, 25))
    score_hist.set_title(f"Score hist\n{score_summary}")
    score_hist.set_xlabel("Score")
    score_hist.set_ylabel("Frequency")


    game_end_chart.bar(loss_tally.keys(), loss_tally.values())
    game_end_chart.set_title("loss reasons")

    fig.tight_layout()

    plt.show()

if __name__ == "__main__":
    # test_harness(functools.partial(random_player.RandomPlayer), 4)
    test_harness(functools.partial(unambiguous_hinting_player.Unambiguous_Hinting_Player), 4)
