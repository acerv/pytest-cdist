# -*- coding: utf-8 -*-
"""
cdist-plugin implementation.

Author:
    Andrea Cervesato <andrea.cervesato@mailbox.org>
"""
import pytest
from cdist import __version__
from cdist.redis import RedisResource
from cdist.resource import ResourceError


def pytest_addoption(parser):
    """
    Plugin configurations.
    """
    parser.addini(
        "cdist_hostname",
        "cdist resource hostname (default: localhost)",
        default="localhost"
    )
    parser.addini(
        "cdist_port",
        "cdist resource port (default: 6379)",
        default="6379"
    )
    parser.addini(
        "cdist_autolock",
        "Enable/Disable configuration automatic lock (default: True)",
        default="True"
    )

    group = parser.getgroup("cdist")
    group.addoption(
        "--cdist-config",
        action="store",
        dest="cdist_config",
        default="",
        help="configuration key name"
    )


class Plugin:
    """
    cdist plugin definition, handling client and pytest hooks.
    """

    def __init__(self):
        self._client = None

    @staticmethod
    def _get_autolock(config):
        """
        Return autolock parameter.
        """
        autolock = config.getini("cdist_autolock").lower() == "true"
        return autolock

    def pytest_report_header(self, config):
        """
        Create the plugin report to be shown during the session.
        """
        config_name = config.option.cdist_config
        if not config_name:
            return None

        # fetch configuration data
        hostname = config.getini("cdist_hostname")
        port = config.getini("cdist_port")
        autolock = self._get_autolock(config)

        # create report lines
        lines = list()
        lines.append("cdist %s -- resource: %s:%s, configuration: %s, autolock: %s" %
                     (__version__, hostname, port, config_name, autolock))

        return lines

    def pytest_sessionstart(self, session):
        """
        Initialize client, fetch data and update pytest configuration.
        """
        config_name = session.config.option.cdist_config
        if not config_name:
            return None

        # fetch data
        hostname = session.config.getini("cdist_hostname")
        port = session.config.getini("cdist_port")
        autolock = self._get_autolock(session.config)

        # create client
        try:
            self._client = RedisResource(hostname=hostname, port=int(port))
            if autolock:
                self._client.lock(config_name)

            # pull configuration
            config = self._client.pull(config_name)
        except ResourceError as err:
            raise pytest.UsageError(err)

        # update pytest configuration
        for key, value in config.items():
            try:
                # check if key is available inside pytest configuration
                session.config.getini(key)
            except ValueError:
                continue

            session.config._inicache[key] = value

    def pytest_sessionfinish(self, session, exitstatus):
        """
        Unlock configuration when session finish.
        """
        config_name = session.config.option.cdist_config
        if not config_name:
            return None

        autolock = self._get_autolock(session.config)
        if autolock:
            self._client.unlock(config_name)


def pytest_configure(config):
    """
    Print out some session informations.
    """
    config.pluginmanager.register(Plugin(), "plugin.cdist")
