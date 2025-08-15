"""Module documentation for `app/services/chat_service.py`.

This module is part of an enterprise-grade, research-ready codebase.
Docstrings follow the Google Python style guide for consistency and clarity.

Generated on 2025-08-15.
"""

from app.domain.agent.impl.agent_impl import AgentImpl


class ChatService:
    """Summary of `ChatService`.

    Attributes:
        agent_impl: Description of `agent_impl`.
    """

    def __init__(self):
        """Summary of `__init__`.

        Args:
            self: Description of self.

        Returns:
            Any: Description of return value.

        """
        self.agent_impl = AgentImpl()

    def chat(self, user_input: str, session_id: str = None):
        """Summary of `chat`.

        Args:
            self: Description of self.
            user_input (str): Description of user_input.
            session_id (str): Description of session_id, default=None.

        Returns:
            Any: Description of return value.

        """
        return self.agent_impl.run(user_input, session_id)


chat_service = ChatService()
