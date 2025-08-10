from app.lib.agent.agent_runner import AgentRunner


class ChatService:
    """
    Thin service layer that wraps the core agent runner.
    Provides both standard and streaming interfaces for use in API or CLI.

    Methods:
        chat(user_input, session_id): Synchronously get agent response.
        stream_chat(user_input, session_id): Get streaming response from agent.
    """

    def __init__(self):
        self.runner = AgentRunner()

    def chat(self, user_input: str, session_id: str = None):
        """
        Streams the agent's response for real-time interfaces.

        Args:
            user_input (str): The user's input.
            session_id (str, optional): The session ID to use.

        Returns:
            Generator[str]: Streamed output from the model.
        """
        return self.runner.run(user_input, session_id)


# Singleton instance
chat_service = ChatService()
