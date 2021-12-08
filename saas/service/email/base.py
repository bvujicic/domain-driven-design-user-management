import abc


class AbstractEmailSender(abc.ABC):
    @abc.abstractmethod
    def create_receiver(self, email_address: str):
        pass

    @abc.abstractmethod
    def create_email_subject(self, subject: str):
        raise NotImplementedError

    @abc.abstractmethod
    def create_email_message(self, message: str):
        raise NotImplementedError

    @abc.abstractmethod
    def send_email(self):
        raise NotImplementedError
