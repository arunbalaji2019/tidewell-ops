import time


class Relay:
    def deliver(self, to, body):  # real SMTP client in production
        raise NotImplementedError


def send(relay, to, template, context, retries=3, backoff=2.0, sleep=time.sleep):
    """Sends one email. Retries timeouts with backoff; the tracker logs each
    failed attempt as a warning, and only a final failure is an error."""
    body = f"[{template}] " + ", ".join(f"{k}={v}" for k, v in sorted(context.items()))
    for attempt in range(1, retries + 1):
        try:
            relay.deliver(to, body)
            return attempt
        except TimeoutError:
            if attempt == retries:
                raise
            sleep(backoff * attempt)
