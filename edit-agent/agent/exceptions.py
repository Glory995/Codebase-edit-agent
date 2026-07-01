"""
agent/exceptions.py

Custom exceptions for the agent.

Using specific exception types (instead of generic Exception)
means calling code can catch exactly what it expects and handle
each failure case differently.
"""


class AgentError(Exception):
    """Base class for all agent-specific errors."""

    pass


class ModelConnectionError(AgentError):
    """Raised when the agent cannot reach the LLM provider at all."""

    pass


class ModelTimeoutError(AgentError):
    """Raised when the LLM provider takes too long to respond."""

    pass


class ToolExecutionError(AgentError):
    """Raised when a tool fails to execute correctly."""

    pass


class MaxIterationsExceeded(AgentError):
    """Raised when the agent loop hits its iteration limit without finishing."""

    pass
