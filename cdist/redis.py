# -*- coding: utf-8 -*-
"""
Redis resource implementation.

The implemented lock mechanism is the historical way to use a ".lock"
tag to the configuration key. For example, if a configuration is named
"myconfig", its lock bit will be defined in the "myconfig.lock" key's
variable. This is a temporary solution and please give any suggestion if you
need something more robust.

Author:
    Andrea Cervesato <andrea.cervesato@mailbox.org>
"""
from __future__ import absolute_import
from redis import Redis
from redis import RedisError
from cdist.resource import Resource
from cdist.resource import ResourceError
from cdist.resource import ResourceConnectionError
from cdist.resource import ResourcePushError
from cdist.resource import ResourcePullError
from cdist.resource import ResourceLockError
from cdist.resource import ResourceUnlockError
from cdist.resource import ResourceNotExistError
from cdist.resource import ResourceDeleteError


class RedisResource(Resource):
    """
    Redis recourse implementation.
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

    def _set_status(self, key: str, locked: bool):
        """
        Set config locking status.
        """
        if not key:
            raise ValueError("key is empty")

        client = self._connect()
        try:
            if key not in client.keys():
                raise ResourceNotExistError("'%s' config is not defined" % key)

            value = "1" if locked else ""
            client.set(self._lock_name(key), value)
        except RedisError as err:
            if locked:
                raise ResourceLockError(err)
            else:
                raise ResourceUnlockError(err)

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
            if key not in client.keys():
                raise ResourceNotExistError("'%s' config is not defined" % key)

            config = client.hgetall(key)
        except RedisError as err:
            raise ResourcePullError(err)

        return config

    def lock(self, key: str):
        self._set_status(key, True)

    def unlock(self, key: str):
        self._set_status(key, False)

    def is_locked(self, key: str) -> bool:
        if not key:
            raise ValueError("key is empty")

        client = self._connect()
        locked = False
        try:
            if key not in client.keys():
                raise ResourceNotExistError("'%s' config is not defined" % key)

            locked = client.get(self._lock_name(key))
        except RedisError as err:
            raise ResourceError(err)

        return locked

    def keys(self) -> list:
        client = self._connect()
        data = list()
        try:
            data = client.keys()
        except RedisError as err:
            raise ResourceConnectionError(err)

        filtered = [item for item in data if not item.endswith(".lock")]
        return filtered

    def delete(self, key: str):
        if not key:
            raise ValueError("key is empty")

        client = self._connect()
        try:
            if key not in client.keys():
                raise ResourceNotExistError("'%s' config is not defined" % key)

            client.delete(key)
        except RedisError as err:
            raise ResourceDeleteError(err)
        finally:
            # always try to delete the locking variable
            try:
                client.delete(self._lock_name(key))
            except RedisError as err:
                raise ResourceDeleteError(err)
