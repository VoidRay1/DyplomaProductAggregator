from django.dispatch import receiver
from aggregator import signals

@receiver(signals.test_signal)
def handle_test_signal(test, **kwargs):
    print(test)