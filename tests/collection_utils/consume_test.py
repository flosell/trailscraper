import pytest

from trailscraper.collection_utils import consume


def test_should_trigger_side_effects_of_collection():

    def some_iterator():
        for i in range(100):
            if i == 50:
                raise RuntimeError("omg")
            yield i

    with pytest.raises(RuntimeError):
        consume(some_iterator())

