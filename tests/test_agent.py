"""Tests to verify the agent module."""

import unittest

from agent import a


class TestAgent(unittest.TestCase):
    """Tests to verify the Agent class."""

    def test_build_server_url_no_trailing_slash(self):
        """Verifies that server_url is correct with a trailing slash."""
        host = 'http://agent.com:8090'
        self.assertEqual(
            'http://agent.com/agent/',
            a.Agent._build_server_url(host)
        )
