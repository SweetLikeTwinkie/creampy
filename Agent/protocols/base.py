"""
Agent.protocols.base

Defines the base communication interface for agent communication protocols.
All protocol-specific communication classes should inherit from this base class.
"""
#!/usr/bin/env python3

class BaseComm:
    """
    Base communication class defining a common interface for all communication protocols.
    """
    def send_message(self, message: str) -> str:
        """
        Sends a message via the specific communication method.

        Args:
            message (str): The message to send.

        Returns:
            str: The response message received.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError