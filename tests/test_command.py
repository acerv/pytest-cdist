"""
command module tests.
"""
import os
import pytest
from click.testing import CliRunner
import cdist
import cdist.command
import redis

# mock it's used to find bugs when resource server is not available, but tests
# should be always executed with a real environment. Use docker in this case.
MOCKED = os.environ.get("CDIST_MOCKED", None)


@pytest.fixture
def runner(mocker):
    """
    Click runner client.
    """
    if MOCKED:
        mocker.patch('cdist.RedisResource.__init__', return_value=None)

    runner = CliRunner()
    with runner.isolated_filesystem():
        def _callback(cmd, hostname="localhost", port="61324"):
            ret = runner.invoke(cdist.command.cli, [
                "-h",
                hostname,
                "-p",
                port,
            ] + cmd)

            return ret

        yield _callback


def test_cli_help(runner):
    """
    Test for --help option
    """
    ret = runner(['--help'])
    assert not ret.exception
    assert ret.exit_code == 0


def test_push_config_type_error(request, runner):
    """
    A pytest configuration must be a ini file with a single "[pytest]" section.
    This test check if pushing non-pytest configuration will raise an exception.
    """
    key = request.node.name

    with open("other.ini", "w") as config:
        config.write("[mysection]\ndata = test")

    # push configuration file
    ret = runner(['push', key, 'other.ini'])
    assert ret.exception
    assert ret.exit_code == 1


def test_push_config_not_exist_error(request, runner):
    """
    This test check if pushing non existing configuration will raise
    an exception.
    """
    key = request.node.name

    # configuration doesn't exist
    ret = runner(['push', key, 'other.ini'])
    assert ret.exception
    assert ret.exit_code == 1


def test_push_error(request, mocker, runner):
    """
    Push a configuration and check for exceptions when redis fails.
    """
    if not MOCKED:
        pytest.xfail("need mocking")

    key = request.node.name

    with open("pytest.ini", "w") as config:
        config.write("[pytest]\naddopts = --setup-only")

    config_dict = dict(addopts="--setup-only")

    if MOCKED:
        mocker.patch("cdist.RedisResource.push",
                     side_effect=cdist.ResourceError())

    # push configuration file
    ret = runner(['push', key, 'pytest.ini'])
    assert ret.exception
    assert ret.exit_code == 1

    if MOCKED:
        cdist.RedisResource.push.assert_called_with(key, config_dict)


def test_show_config_not_exist_error(request, runner):
    """
    This test check if showing non existing configuration will raise
    an exception.
    """
    key = request.node.name

    # configuration is not pushed
    ret = runner(['show', key])
    assert ret.exception
    assert ret.exit_code == 1


def test_show_error(request, mocker, runner):
    """
    Pull a configuration and check for exceptions when redis fails.
    """
    if not MOCKED:
        pytest.xfail("need mocking")

    key = request.node.name

    with open("pytest.ini", "w") as config:
        config.write("[pytest]\naddopts = --setup-only")

    if MOCKED:
        mocker.patch("cdist.RedisResource.pull",
                     side_effect=cdist.ResourceError())

    # push configuration file
    ret = runner(['show', key])
    assert ret.exception
    assert ret.exit_code == 1

    if MOCKED:
        cdist.RedisResource.pull.assert_called_with(key)


def test_push_and_show(request, mocker, runner):
    """
    Push a configuration and read it back.
    """
    key = request.node.name

    with open("pytest.ini", "w") as config:
        config.write("[pytest]\naddopts = --setup-only")

    config_dict = dict(addopts="--setup-only")

    if MOCKED:
        mocker.patch("cdist.RedisResource.push")
        mocker.patch("cdist.RedisResource.pull", return_value=config_dict)

    # push configuration file
    ret = runner(['push', key, 'pytest.ini'])
    assert not ret.exception
    assert ret.exit_code == 0

    # pull configuration file
    ret = runner(['show', key])
    assert not ret.exception
    assert ret.exit_code == 0

    if MOCKED:
        cdist.RedisResource.push.assert_called_with(key, config_dict)
        cdist.RedisResource.pull.assert_called_with(key)


def test_lock_config_not_exist_error(request, runner):
    """
    This test check if locking non existing configuration will raise
    an exception.
    """
    key = request.node.name

    # configuration is not pushed
    ret = runner(['lock', key])
    assert ret.exception
    assert ret.exit_code == 1


def test_lock_error(request, mocker, runner):
    """
    Lock a configuration and check for exceptions when redis fails.
    """
    if not MOCKED:
        pytest.xfail("need mocking")

    key = request.node.name

    with open("pytest.ini", "w") as config:
        config.write("[pytest]\naddopts = --setup-only")

    if MOCKED:
        mocker.patch("cdist.RedisResource.lock",
                     side_effect=cdist.ResourceError())

    # push configuration file
    ret = runner(['lock', key])
    assert ret.exception
    assert ret.exit_code == 1

    if MOCKED:
        cdist.RedisResource.lock.assert_called_with(key)


def test_unlock_config_not_exist_error(request, runner):
    """
    This test check if unlocking non existing configuration will raise
    an exception.
    """
    key = request.node.name

    # configuration is not pushed
    ret = runner(['unlock', key])
    assert ret.exception
    assert ret.exit_code == 1


def test_unlock_error(request, mocker, runner):
    """
    Unlock a configuration and check for exceptions when redis fails.
    """
    if not MOCKED:
        pytest.xfail("need mocking")

    key = request.node.name

    with open("pytest.ini", "w") as config:
        config.write("[pytest]\naddopts = --setup-only")

    if MOCKED:
        mocker.patch("cdist.RedisResource.unlock",
                     side_effect=cdist.ResourceError())

    # push configuration file
    ret = runner(['unlock', key])
    assert ret.exception
    assert ret.exit_code == 1

    if MOCKED:
        cdist.RedisResource.unlock.assert_called_with(key)


def test_lock_and_unlock(request, mocker, runner):
    """
    Push a configuration and read it back.
    """
    key = request.node.name

    with open("pytest.ini", "w") as config:
        config.write("[pytest]\naddopts = --setup-only")

    config_dict = dict(addopts="--setup-only")

    if MOCKED:
        mocker.patch("cdist.RedisResource.push")
        mocker.patch("cdist.RedisResource.lock")
        mocker.patch("cdist.RedisResource.unlock")

    # push configuration file
    ret = runner(['push', key, 'pytest.ini'])
    assert not ret.exception
    assert ret.exit_code == 0

    # lock configuration file
    ret = runner(['lock', key])
    assert not ret.exception
    assert ret.exit_code == 0

    # unlock configuration file
    ret = runner(['unlock', key])
    assert not ret.exception
    assert ret.exit_code == 0

    if MOCKED:
        cdist.RedisResource.push.assert_called_with(key, config_dict)
        cdist.RedisResource.lock.assert_called_with(key)
        cdist.RedisResource.unlock.assert_called_with(key)


def test_list_error(request, mocker, runner):
    """
    List configurations and check for exceptions when redis fails.
    """
    if not MOCKED:
        pytest.xfail("need mocking")

    key = request.node.name

    with open("pytest.ini", "w") as config:
        config.write("[pytest]\naddopts = --setup-only")

    if MOCKED:
        mocker.patch("cdist.RedisResource.keys",
                     side_effect=cdist.ResourceError())

    # list configurations
    ret = runner(['list'])
    assert ret.exception
    assert ret.exit_code == 1

    if MOCKED:
        cdist.RedisResource.keys.assert_called_with()


def test_list_locked_check_error(request, mocker, runner):
    """
    List configurations and check for exceptions when looking for a locked
    configuration.
    """
    if not MOCKED:
        pytest.xfail("need mocking")

    key = request.node.name

    with open("pytest.ini", "w") as config:
        config.write("[pytest]\naddopts = --setup-only")

    config_dict = dict(addopts="--setup-only")

    if MOCKED:
        mocker.patch("cdist.RedisResource.push")
        mocker.patch("cdist.RedisResource.keys", return_value=[key])
        mocker.patch("cdist.RedisResource.is_locked",
                     side_effect=cdist.ResourceError())

    # push configuration file
    ret = runner(['push', key, 'pytest.ini'])
    assert not ret.exception
    assert ret.exit_code == 0

    # list configurations
    ret = runner(['list'])
    assert ret.exception
    assert ret.exit_code == 1

    if MOCKED:
        cdist.RedisResource.push.assert_called_with(key, config_dict)
        cdist.RedisResource.is_locked.assert_called_with(key)
        cdist.RedisResource.keys.assert_called()


def test_push_and_list(request, mocker, runner):
    """
    List configurations and check for exceptions when redis fails.
    """
    if not MOCKED:
        pytest.xfail("need mocking")

    key = request.node.name

    with open("pytest.ini", "w") as config:
        config.write("[pytest]\naddopts = --setup-only")

    config_dict = dict(addopts="--setup-only")

    if MOCKED:
        mocker.patch("cdist.RedisResource.push")
        mocker.patch("cdist.RedisResource.keys", return_value=[key])
        mocker.patch("cdist.RedisResource.is_locked", return_value=False)

    # push configuration file
    ret = runner(['push', key, 'pytest.ini'])
    assert not ret.exception
    assert ret.exit_code == 0

    # list configurations
    ret = runner(['list'])
    assert not ret.exception
    assert ret.exit_code == 0
    assert key in ret.output

    if MOCKED:
        cdist.RedisResource.push.assert_called_with(key, config_dict)
        cdist.RedisResource.keys.assert_called()
        cdist.RedisResource.is_locked.assert_called_with(key)


def test_delete_config_not_exist_error(request, runner):
    """
    This test check if deleting non existing configuration will raise
    an exception.
    """
    key = request.node.name

    # configuration is not pushed
    ret = runner(['delete', key])
    assert ret.exception
    assert ret.exit_code == 1


def test_delete_error(request, mocker, runner):
    """
    Delete a configuration and check for exceptions when redis fails.
    """
    if not MOCKED:
        pytest.xfail("need mocking")

    key = request.node.name

    with open("pytest.ini", "w") as config:
        config.write("[pytest]\naddopts = --setup-only")

    if MOCKED:
        mocker.patch("cdist.RedisResource.delete",
                     side_effect=cdist.ResourceError())

    # push configuration file
    ret = runner(['delete', key])
    assert ret.exception
    assert ret.exit_code == 1

    if MOCKED:
        cdist.RedisResource.delete.assert_called_with(key)


def test_push_and_delete(request, mocker, runner):
    """
    Push a configuration and delete it.
    """
    key = request.node.name

    with open("pytest.ini", "w") as config:
        config.write("[pytest]\naddopts = --setup-only")

    config_dict = dict(addopts="--setup-only")

    if MOCKED:
        mocker.patch("cdist.RedisResource.push")
        mocker.patch("cdist.RedisResource.delete")

    # push configuration file
    ret = runner(['push', key, 'pytest.ini'])
    assert not ret.exception
    assert ret.exit_code == 0

    # pull configuration file
    ret = runner(['delete', key])
    assert not ret.exception
    assert ret.exit_code == 0

    if MOCKED:
        cdist.RedisResource.push.assert_called_with(key, config_dict)
        cdist.RedisResource.delete.assert_called_with(key)
