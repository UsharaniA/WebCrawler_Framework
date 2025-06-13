import time 
import random


def random_sleep(min_seconds=2, max_seconds=5):
    delay = random.uniform(min_seconds, max_seconds)
    print(f"Sleeping for {delay:.2f} seconds...")  # optional, for debugging
    time.sleep(delay)