"""
redis module tests.
"""
import os
import redis
import pytest
from cdist import RedisResource
from cdist import ResourceError
from cdist import ResourceConnectionError
from cdist import ResourcePushError
from cdist import ResourcePullError
from cdist import ResourceLockError
from cdist import ResourceUnlockError
from cdist import ResourceNotExistError
from cdist import ResourceDeleteError

# mock it's used to find bugs when redis server is not available, but tests
# should be always executed with a real environment. Use docker in this case.
MOCKED = os.environ.get("CDIST_MOCKED", None)


@pytest.fixture
def resource(request, mocker):
    """
    Resource to test.
    """
    if MOCKED:
        mocker.patch('redis.Redis.__init__', return_value=None)
        mocker.patch('redis.Redis.__del__')
        mocker.patch('redis.Redis.close')

    kwargs = dict(
        hostname="192.168.10.47",
        port="61324"
    )
    resource = RedisResource(**kwargs)
    return resource


def test_connection_error(mocker):
    """
    Test if connection raises an error when server is not available.
    """
    if not MOCKED:
        pytest.xfail("need mocking")

    if MOCKED:
        mocker.patch(
            'redis.Redis.__init__',
            return_value=None,
            side_effect=redis.RedisError())

    kwargs = dict(
        hostname="localhost",
        port="12345"  # i'm not expecting this port is used
    )
    resource = RedisResource(**kwargs)
    with pytest.raises(ResourceConnectionError):
        resource._connect()


def test_push_args_error(resource):
    """
    Test push method arguments when they are not valid.
    """
    with pytest.raises(ValueError):
        resource.push(None, None)

    with pytest.raises(ValueError):
        resource.push("test", None)

    with pytest.raises(ValueError):
        resource.push("test.lock", None)


def test_pull_args_error(resource):
    """
    Test pull method arguments when they are not valid.
    """
    with pytest.raises(ValueError):
        resource.pull(None)


def test_push_error(request, mocker, resource):
    """
    Test push method when it raises exceptions.

    Hard to test the behaviour without exceptions inside Redis. This
    test is expected to fail without mocking.
    """
    if not MOCKED:
        pytest.xfail("need mocking")

    key = request.node.name

    if MOCKED:
        mocker.patch('redis.Redis.hmset', side_effect=redis.RedisError())
        mocker.patch('redis.Redis.set')

    with pytest.raises(ResourcePushError):
        resource.push(key, dict())

    if MOCKED:
        mocker.patch('redis.Redis.hmset')
        mocker.patch('redis.Redis.set', side_effect=redis.RedisError())

    with pytest.raises(ResourcePushError):
        resource.push(key, dict())


def test_pull_error(request, mocker, resource):
    """
    Test pull method when it raises a ResourcePullError error.

    Hard to test the behaviour without exceptions inside Redis. This
    test is expected to fail without mocking.
    """
    if not MOCKED:
        pytest.xfail("need mocking")

    key = request.node.name

    if MOCKED:
        mocker.patch('redis.Redis.hgetall', side_effect=redis.RedisError())
        mocker.patch('redis.Redis.exists', return_value=True)

    with pytest.raises(ResourcePullError):
        resource.pull(key)

    if MOCKED:
        redis.Redis.hgetall.assert_called_with(key)
        redis.Redis.exists.assert_called()


def test_pull_resource_not_exist_error(request, mocker, resource):
    """
    Test pull method when it raises a ResourceNotExistError exception.

    Hard to test the behaviour without exceptions inside Redis. This
    test is expected to fail without mocking.
    """
    if not MOCKED:
        pytest.xfail("need mocking")

    key = request.node.name

    if MOCKED:
        mocker.patch('redis.Redis.hgetall')
        mocker.patch('redis.Redis.exists', return_value=False)

    with pytest.raises(ResourceNotExistError):
        resource.pull(key)

    if MOCKED:
        redis.Redis.hgetall.assert_not_called()
        redis.Redis.exists.assert_called()


def test_push_and_pull(request, mocker, resource):
    """
    Push and pull data, then check if worked fine.
    """
    key = request.node.name

    data = dict(
        test0="data0",
        test1="data1",
        test2="data2"
    )

    if MOCKED:
        mocker.patch('redis.Redis.hmset')
        mocker.patch('redis.Redis.keys', return_value=[key])
        mocker.patch('redis.Redis.get', return_value="")
        mocker.patch('redis.Redis.set')
        mocker.patch('redis.Redis.hgetall', return_value=data)
        mocker.patch('redis.Redis.exists', return_value=True)

    # push data
    resource.push(key, data)
    assert key in resource.keys()
    assert not resource.is_locked(key)

    # pull data
    data0 = resource.pull(key)
    assert data == data0

    if MOCKED:
        redis.Redis.hmset.assert_called_with(key, data)
        redis.Redis.keys.assert_called()
        redis.Redis.get.assert_called()
        redis.Redis.hgetall.assert_called_with(key)
        redis.Redis.exists.assert_called()


def test_lock_args_error(resource):
    """
    Test lock method arguments when they are not valid.
    """
    with pytest.raises(ValueError):
        resource.lock(None)


def test_unlock_args_error(resource):
    """
    Test unlock method arguments when they are not valid.
    """
    with pytest.raises(ValueError):
        resource.unlock(None)


def test_lock_resource_not_exist_error(request, mocker, resource):
    """
    Test lock method when it raises a ResourceNotExistError exception.

    Hard to test the behaviour without exceptions inside Redis. This
    test is expected to fail without mocking.
    """
    if not MOCKED:
        pytest.xfail("need mocking")

    key = request.node.name

    if MOCKED:
        mocker.patch('redis.Redis.exists', return_value=False)
        mocker.patch('redis.Redis.set')

    with pytest.raises(ResourceNotExistError):
        resource.lock(key)

    if MOCKED:
        redis.Redis.set.assert_not_called()
        redis.Redis.exists.assert_called()


def test_lock_error(request, mocker, resource):
    """
    Test lock method when it raises a ResourceLockError exceptions.

    Hard to test the behaviour without exceptions inside Redis. This
    test is expected to fail without mocking.
    """
    if not MOCKED:
        pytest.xfail("need mocking")

    key = request.node.name

    if MOCKED:
        mocker.patch('redis.Redis.exists', return_value=True)
        mocker.patch('redis.Redis.set', side_effect=redis.RedisError())

    with pytest.raises(ResourceLockError):
        resource.lock(key)

    if MOCKED:
        redis.Redis.set.assert_called()
        redis.Redis.exists.assert_called()


def test_unlock_resource_not_exist_error(request, mocker, resource):
    """
    Test unlock method when it raises a ResourceNotExistError exception.

    Hard to test the behaviour without exceptions inside Redis. This
    test is expected to fail without mocking.
    """
    if not MOCKED:
        pytest.xfail("need mocking")

    key = request.node.name

    if MOCKED:
        mocker.patch('redis.Redis.exists', return_value=False)
        mocker.patch('redis.Redis.set')

    with pytest.raises(ResourceNotExistError):
        resource.unlock(key)

    if MOCKED:
        redis.Redis.set.assert_not_called()
        redis.Redis.exists.assert_called()


def test_unlock_error(request, mocker, resource):
    """
    Test unlock method when it raises a ResourceUnlockError exception.

    Hard to test the behaviour without exceptions inside Redis. This
    test is expected to fail without mocking.
    """
    if not MOCKED:
        pytest.xfail("need mocking")

    key = request.node.name

    if MOCKED:
        mocker.patch('redis.Redis.exists', return_value=True)
        mocker.patch('redis.Redis.set', side_effect=redis.RedisError())

    with pytest.raises(ResourceUnlockError):
        resource.unlock(key)

    if MOCKED:
        redis.Redis.set.assert_called()
        redis.Redis.exists.assert_called()


def test_is_locked_resource_not_exist_error(request, mocker, resource):
    """
    Test is_locked method when it raises a ResourceNotExistError exception.

    Hard to test the behaviour without exceptions inside Redis. This
    test is expected to fail without mocking.
    """
    if not MOCKED:
        pytest.xfail("need mocking")

    key = request.node.name

    if MOCKED:
        mocker.patch('redis.Redis.exists', return_value=False)
        mocker.patch('redis.Redis.get')

    with pytest.raises(ResourceNotExistError):
        resource.is_locked(key)

    if MOCKED:
        redis.Redis.get.assert_not_called()
        redis.Redis.exists.assert_called()


def test_is_locked_error(request, mocker, resource):
    """
    Test is_locked method when it raises a ResourceError exception.

    Hard to test the behaviour without exceptions inside Redis. This
    test is expected to fail without mocking.
    """
    if not MOCKED:
        pytest.xfail("need mocking")

    key = request.node.name

    if MOCKED:
        mocker.patch('redis.Redis.exists', return_value=True)
        mocker.patch('redis.Redis.get', side_effect=redis.RedisError())

    with pytest.raises(ResourceError):
        resource.is_locked(key)

    if MOCKED:
        redis.Redis.get.assert_called()
        redis.Redis.exists.assert_called()


def test_keys_error(request, mocker, resource):
    """
    Test keys method when it raises exceptions.

    Hard to test the behaviour without exceptions inside Redis. This
    test is expected to fail without mocking.
    """
    if not MOCKED:
        pytest.xfail("need mocking")

    if MOCKED:
        mocker.patch('redis.Redis.keys', side_effect=redis.RedisError())

    with pytest.raises(ResourceConnectionError):
        resource.keys()

    if MOCKED:
        redis.Redis.keys.assert_called()


def test_lock_and_unlock(request, mocker, resource):
    """
    Lock and unlock a key, then check if worked fine.
    """
    key = request.node.name

    data = dict(
        test0="data0",
        test1="data1",
        test2="data2"
    )

    if MOCKED:
        mocker.patch('redis.Redis.get', return_value="1")
        mocker.patch('redis.Redis.set')
        mocker.patch('redis.Redis.hmset')
        mocker.patch('redis.Redis.exists', return_value=True)

    # lock data
    resource.push(key, data)
    resource.lock(key)
    assert resource.is_locked(key)  # useless without a real case

    if MOCKED:
        mocker.patch('redis.Redis.get', return_value="")

    # unlock data
    resource.unlock(key)
    assert not resource.is_locked(key)  # useless without a real case

    if MOCKED:
        redis.Redis.set.assert_called_with(key + ".lock", "")
        redis.Redis.get.assert_called_with(key + ".lock")
        redis.Redis.exists.assert_called()


def test_delete_args_error(resource):
    """
    Test delete method arguments when they are not valid.
    """
    with pytest.raises(ValueError):
        resource.delete(None)


def test_delete_error(request, mocker, resource):
    """
    Test delete method when it raises exceptions.

    Hard to test the behaviour without exceptions inside Redis. This
    test is expected to fail without mocking.
    """
    if not MOCKED:
        pytest.xfail("need mocking")

    key = request.node.name

    if MOCKED:
        mocker.patch('redis.Redis.delete', side_effect=redis.RedisError())
        mocker.patch('redis.Redis.keys', return_value=[key])
        mocker.patch('redis.Redis.exists', return_value=True)

    with pytest.raises(ResourceDeleteError):
        resource.delete(key)

    if MOCKED:
        redis.Redis.delete.assert_called()
        redis.Redis.exists.assert_called()


def test_push_and_delete(request, mocker, resource):
    """
    Push a configuration and then it deletes it.
    """
    key = request.node.name

    data = dict(
        test0="data0",
        test1="data1",
        test2="data2"
    )

    if MOCKED:
        mocker.patch('redis.Redis.hmset')
        mocker.patch('redis.Redis.keys', return_value=[key])
        mocker.patch('redis.Redis.set')
        mocker.patch('redis.Redis.delete')
        mocker.patch('redis.Redis.exists', return_value=True)

    # push data
    resource.push(key, data)
    assert key in resource.keys()

    # delete data
    resource.delete(key)

    if MOCKED:
        mocker.patch('redis.Redis.keys', return_value=[])

    assert key not in resource.keys()

    if MOCKED:
        redis.Redis.hmset.assert_called_with(key, data)
        redis.Redis.keys.assert_called()
        redis.Redis.set.assert_called()
        redis.Redis.delete.assert_called()
        redis.Redis.exists.assert_called()
