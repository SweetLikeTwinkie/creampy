class BaseComm:
    """
    Base communication class to define a common interface for all communication methods.
    """
    def send_message(self, message: str) -> str:
        raise NotImplementedError