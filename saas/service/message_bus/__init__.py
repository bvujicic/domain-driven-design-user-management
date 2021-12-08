from saas.domain.base import DomainEvent
from .handlers import HANDLERS
from saas.core.config import configuration


def handle(event: DomainEvent):
    if configuration.DEBUG:
        from colorama import Fore, Style

        print(f'{Fore.GREEN}{vars(event)}{Style.RESET_ALL}')
        return

    for handler in HANDLERS[type(event)]:
        handler(event=event)  # type: ignore
