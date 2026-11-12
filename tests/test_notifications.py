import pytest

from services.notifications.sender import send


class Flaky:
    def __init__(self, fails):
        self.fails = fails
        self.calls = 0

    def deliver(self, to, body):
        self.calls += 1
        if self.calls <= self.fails:
            raise TimeoutError("relay timed out")


def test_retries_then_succeeds():
    assert send(Flaky(2), "a@example.com", "t", {}, sleep=lambda s: None) == 3


def test_gives_up_after_retries():
    with pytest.raises(TimeoutError):
        send(Flaky(5), "a@example.com", "t", {}, sleep=lambda s: None)
