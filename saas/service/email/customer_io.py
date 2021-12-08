import dataclasses
from typing import Optional, Dict

import requests

from saas.core.config import configuration
from saas.domain.base import DomainEvent
from saas.domain.users import Profile
from .base import AbstractEmailSender


class CustomerIOEmailSender(AbstractEmailSender):
    CUSTOMER_IO_SITE_ID = configuration.CUSTOMER_IO_SITE_ID
    CUSTOMER_IO_API_KEY = configuration.CUSTOMER_IO_API_KEY
    AUTHENTICATION_CREDENTIALS = (CUSTOMER_IO_SITE_ID, CUSTOMER_IO_API_KEY)

    CUSTOMER_IO_DOMAIN = 'https://track.customer.io'
    CREATE_PERSON_URL = f'{CUSTOMER_IO_DOMAIN}/api/v1/customers'
    CREATE_ANONYMOUS_EVENT_URL = f'{CUSTOMER_IO_DOMAIN}/api/v1/events'

    def __init__(self, event: 'DomainEvent', profile: Optional['Profile'] = None):
        self.event = event
        self.profile = profile
        self.recipient = None
        self.person_payload: Dict = {}
        self.event_payload: Dict = {
            'name': self.event.name,
            'data': dataclasses.asdict(self.event),
        }

    def create_receiver(self, email_address: Optional[str] = None):
        if getattr(self.profile, 'user', None) is None:
            self.recipient = email_address
        else:
            self.person_payload = {
                'id': self.profile.reference,
                'email': self.profile.user.username,
                'enterprize': self.profile.enterprize.name,
                'enterprize_subdomain': self.profile.enterprize.subdomain,
                'created_at': self.profile.created.timestamp(),
            }
            self._send_person_request()

    def _send_person_request(self):
        requests.put(
            url=f'{self.CREATE_PERSON_URL}/{self.profile.reference}',
            json=self.person_payload,
            auth=self.AUTHENTICATION_CREDENTIALS,
            timeout=3,
        )

    def create_email_subject(self, subject: Optional[str] = None):
        pass

    def create_email_message(self, message: Optional[str] = None):
        if getattr(self.profile, 'user', None) is not None:
            self._create_person_email_message()
        else:
            self._create_anonymous_email_message()

    def _create_person_email_message(self):
        self.CREATE_EVENT_URL = f'{self.CREATE_PERSON_URL}/{self.profile.reference}/events'
        self.event_payload.update({'id': self.profile.reference})

    def _create_anonymous_email_message(self):
        self.CREATE_EVENT_URL = self.CREATE_ANONYMOUS_EVENT_URL
        self.event_payload['data'].update({'recipient': self.recipient})

    def send_email(self):
        requests.post(
            url=self.CREATE_EVENT_URL,
            json=self.event_payload,
            auth=self.AUTHENTICATION_CREDENTIALS,
            timeout=3,
        )
