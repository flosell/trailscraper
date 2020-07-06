"""Functions to help with collections"""
import collections


def consume(iterator):
    """Consume the whole iterator to trigger side effects; does not return anything"""
    # Inspired by this: https://docs.python.org/3/library/itertools.html#itertools-recipes
    collections.deque(iterator, maxlen=0)
