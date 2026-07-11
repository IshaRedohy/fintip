from abc import ABC, abstractmethod


class Notifier(ABC):
    @abstractmethod
    def notify(self, alert):
        """Deliver one price alert or raise an exception."""


def format_alert(alert):
    return (
        "{ticker} {target_type} target alert: current ${current_price:.2f}, "
        "target ${target_price:.2f}, distance {distance_percent:.2f}% "
        "(threshold {threshold_percent:.2f}%), checked {checked_at}"
    ).format(**alert)


class ConsoleNotifier(Notifier):
    def __init__(self, output=print):
        self.output = output

    def notify(self, alert):
        self.output(format_alert(alert))
