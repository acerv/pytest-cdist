# -*- coding: utf-8 -*-
"""
cdist library implementation.

Author:
    Andrea Cervesato <andrea.cervesato@mailbox.org>
"""


class ResourceError(Exception):
    """
    Raised when an external resource doesn't work as expected.
    """


class ResourceLockedError(Exception):
    """
    Raised when an external resource is locked and it can't be pulled.
    """


class ExternalResource:
    """
    A generic class to handle multiple pytest configurations via external
    resource. This is the case of a server which stores various pytest
    configurations.
    """

    def push(self, key: str, config: dict) -> bool:
        """
        Push a pytest configuration tagging it with a specific key.

        Args:
            key (str): tag associated to ``config``.
            config (dict): dictionary representing a pytest configuration.

        Returns:
            bool: True if successful, False otherwise.

        Raises:
            ValueError: if one of the parameters is None or empty.
            ResourceError: if connection failed or pushing failed.
        """
        raise NotImplementedError()

    def pull(self, key: str) -> dict:
        """
        Pull a pytest configuration tagged with a specific key.

        Args:
            key (str): tag associated to a pytest configuration.

        Returns:
            dict: dictionary representing a pytest configuration.

        Raises:
            ValueError: if one of the parameters is None or empty.
            ResourceError: if connection failed.
            ResourceLockedError: if pytest configuration tagged with ``key``
                is locked.
        """
        raise NotImplementedError()

    def lock(self, key: str) -> bool:
        """
        Lock a pytest configuration tagged with a specific key.

        Args:
            key (str): tag associated to a pytest configuration.

        Returns:
            bool: True if successful, False otherwise.

        Raises:
            ValueError: if one of the parameters is None or empty.
            ResourceError: if connection failed or locking failed.
        """
        raise NotImplementedError()

    def unlock(self, key: str) -> bool:
        """
        Unlock a pytest configuration tagged with a specific key.

        Args:
            key (str): tag associated to a pytest configuration.

        Returns:
            bool: True if successful, False otherwise.

        Raises:
            ValueError: if one of the parameters is None or empty.
            ResourceError: if connection failed or unlocking failed.
        """
        raise NotImplementedError()
