# -*- coding: utf-8 -*-
"""
ExternalResource class implementation for Redis services.

The implemented locking mechanism is the historical way to use a ".locking"
tag to the configuration key. For example, if a configuration is named
"myconfig", its locking bit will be defined in the "myconfig.locking" key's
variable. This is a temporary solution and please give any suggestion if you
need something more robust.

Author:
    Andrea Cervesato <andrea.cervesato@mailbox.org>
"""
from __future__ import absolute_import
from redis import Redis
from redis import RedisError
from cdist import ExternalResource
from cdist import ResourceConnectionError
from cdist import ResourcePushError
from cdist import ResourcePullError
from cdist import ResourceLockError
from cdist import ResourceUnlockError
from cdist import ResourceNotExistError


class RedisExternalResource(ExternalResource):
    """
    ExternalResource implementation for Redis DB.
    """

    def __init__(self, **kwargs: dict):
        """
        Args:
            hostname (str): Redis server hostname (default: localhost).
            port (int): Redis server port (default: 6379).
        """
        self._hostname = kwargs.get("hostname", "localhost")
        self._port = int(kwargs.get("port", 6379))

    @staticmethod
    def _lock_name(name):
        """
        Return the name used to recognize if a configuration is locked.
        """
        return "%s.lock" % name

    def _connect(self):
        """
        Connect to the Redis server.
        """
        client = None
        try:
            client = Redis(
                host=self._hostname,
                port=self._port
            )
        except RedisError as err:
            raise ResourceConnectionError(err)

        return client

    def push(self, key: str, config: dict):
        if not key:
            raise ValueError("key is empty")

        if config is None:
            raise ValueError("config is None")

        if key.endswith(".lock"):
            raise ValueError("key can't end with '.lock' suffix")

        client = self._connect()
        try:
            client.hmset(key, config)
            client.set(
                self._lock_name(key),
                ""
            )
        except RedisError as err:
            raise ResourcePushError(err)

    def pull(self, key: str) -> dict:
        if not key:
            raise ValueError("key is empty")

        client = self._connect()
        config = None
        try:
            config = client.hgetall(key)
        except RedisError as err:
            raise ResourcePullError(err)

        return config

    def lock(self, key: str):
        if not key:
            raise ValueError("key is empty")

        client = self._connect()
        try:
            if key not in client.keys():
                raise ResourceNotExistError("'%s' config is not defined" % key)

            client.set(
                self._lock_name(key),
                "1"
            )
        except RedisError as err:
            raise ResourceLockError(err)

    def unlock(self, key: str):
        if not key:
            raise ValueError("key is empty")

        client = self._connect()
        try:
            if key not in client.keys():
                raise ResourceNotExistError("'%s' config is not defined" % key)

            client.set(
                self._lock_name(key),
                ""
            )
        except RedisError as err:
            raise ResourceUnlockError(err)

    def is_locked(self, key: str) -> bool:
        if not key:
            raise ValueError("key is empty")

        client = self._connect()
        try:
            if key not in client.keys():
                raise ResourceNotExistError("'%s' config is not defined" % key)

            client.set(
                self._lock_name(key),
                ""
            )
        except RedisError as err:
            raise ResourceUnlockError(err)

    def keys(self) -> list:
        client = self._connect()
        data = list()
        try:
            data = client.keys()
        except RedisError as err:
            raise ResourceConnectionError(err)

        filtered = [item for item in data if not data.endswith(".lock")]
        return filtered
