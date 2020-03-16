"""Exceptions for Agent DVR."""


class AgentError(Exception):
    """Generic Agent DVR exception."""

    pass


class AgentConnectionError(AgentError):
    """Agent DVR connection exception."""

    pass
