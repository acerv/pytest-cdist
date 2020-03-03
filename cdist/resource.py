# -*- coding: utf-8 -*-
"""
API for resource services. A resource service is a service which stores
configurations for the pytest framework. I.e. a database.

Author:
    Andrea Cervesato <andrea.cervesato@mailbox.org>
"""


class ResourceError(Exception):
    """
    Generic error for cdist.
    """


class ResourceConnectionError(ResourceError):
    """
    Raised when an external resource has problems with connection.
    """


class ResourcePushError(ResourceError):
    """
    Raised when an external resource got errors while pushing.
    """


class ResourcePullError(ResourceError):
    """
    Raised when an external resource got errors while pulling.
    """


class ResourceLockError(ResourceError):
    """
    Raised when an external resource got errors while locking.
    """


class ResourceUnlockError(ResourceError):
    """
    Raised when an external resource got errors while unlocking.
    """


class ResourceNotExistError(ResourceError):
    """
    Raised when an external resource doesn't have a requested configuration.
    """


class ResourceDeleteError(ResourceError):
    """
    Raised when an external resource can't delete a requested configuration.
    """


class Resource:
    """
    A generic class to handle multiple pytest configurations via external
    resource. This is the case of a server which stores various pytest
    configurations.
    """

    def push(self, key: str, config: dict):
        """
        Push a pytest configuration tagging it with a specific key.

        Args:
            key (str): tag associated to ``config``.
            config (dict): dictionary representing a pytest configuration.

        Raises:
            ValueError: if one of the parameters is None or empty.
            ResourceConnectionError: if connection failed.
            ResourcePushError: if push failed.
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
            ResourceConnectionError: if connection failed.
            ResourcePullError: if pull failed.
        """
        raise NotImplementedError()

    def lock(self, key: str):
        """
        Lock a pytest configuration tagged with a specific key.

        Args:
            key (str): tag associated to a pytest configuration.

        Raises:
            ValueError: if one of the parameters is None or empty.
            ResourceConnectionError: if connection failed.
            ResourceLockError: if lock failed.
            ResourceNotExistError: if configuration doesn't exist.
        """
        raise NotImplementedError()

    def unlock(self, key: str):
        """
        Unlock a pytest configuration tagged with a specific key.

        Args:
            key (str): tag associated to a pytest configuration.

        Raises:
            ValueError: if one of the parameters is None or empty.
            ResourceConnectionError: if connection failed.
            ResourceUnlockError: if unlock failed.
            ResourceNotExistError: if configuration doesn't exist.
        """
        raise NotImplementedError()

    def is_locked(self, key: str) -> bool:
        """
        Check if a pytest configuration is locked.

        Args:
            key (str): tag associated to a pytest configuration.

        Returns:
            True if configuration is locked. False otherwise.

        Raises:
            ValueError: if one of the parameters is None or empty.
            ResourceConnectionError: if connection failed.
            ResourceNotExistError: if configuration doesn't exist.
        """
        raise NotImplementedError()

    def keys(self) -> list:
        """
        Fetch the list of available configurations.

        Returns:
            list(str): a list of strings rapresenting available configurations.

        Raises:
            ResourceConnectionError: if connection failed.
        """
        raise NotImplementedError()

    def delete(self, key: str):
        """
        Delete a pytest configuration.

        Args:
            key (str): tag associated to a pytest configuration.

        Raises:
            ValueError: if one of the parameters is None or empty.
            ResourceConnectionError: if connection failed.
            ResourceDeleteError: if configuration can't be deleted.
        """
        raise NotImplementedError()
