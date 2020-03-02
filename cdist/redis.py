# -*- coding: utf-8 -*-
"""
ExternalResource class implementation for Redis services.

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

        client = self._connect()
        try:
            result = client.hmset(key, config)
            if not result:
                raise ResourcePushError("cannot push '%s' configuration" % key)
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
            client.hset(key, "cdist_locked", "1")
        except RedisError as err:
            raise ResourceLockError(err)

    def unlock(self, key: str):
        if not key:
            raise ValueError("key is empty")

        client = self._connect()
        try:
            client.hset(key, "cdist_locked", "0")
        except RedisError as err:
            raise ResourceUnlockError(err)
