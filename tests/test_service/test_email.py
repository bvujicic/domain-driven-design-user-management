from saas.service.email import AbstractEmailSender


class FakeEmailSender(AbstractEmailSender):
    receiver: str
    subject: str
    message: str

    def create_receiver(self, email_address: str):
        self.receiver = email_address

    def create_email_subject(self, subject: str):
        self.subject = subject

    def create_email_message(self, message: str):
        self.message = message

    def send_email(self) -> str:
        return self.receiver


class TestEmailService:
    email_sender = FakeEmailSender()
    email_address = 'test@mail.com'
    subject = 'test'
    message = 'test'

    def test_can_create_receiver(self):
        self.email_sender.create_receiver(email_address=self.email_address)

        assert self.email_sender.receiver is not None

    def test_can_create_subject(self):
        self.email_sender.create_email_subject(subject=self.subject)

        assert self.email_sender.subject is not None

    def test_can_create_message(self):
        self.email_sender.create_email_message(message=self.message)

        assert self.email_sender.message is not None

    def test_can_send_email(self):
        self.email_sender.create_receiver(email_address=self.email_address)

        assert self.email_sender.send_email() == self.email_address
