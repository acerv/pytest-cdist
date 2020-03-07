"""
cdist plugin tests.
"""
import pytest
import cdist

pytest_plugins = ["pytester"]


@pytest.fixture(autouse=True)
def _setup(testdir, mocker):
    """
    Click runner client.
    """
    testdir.makeconftest(
        """
        def pytest_addoption(parser):
            parser.addini(
                "test_param0",
                "test parameter 0",
                default="empty"
            )
            parser.addini(
                "test_param1",
                "test parameter 1",
                default="empty"
            )
    """)

    config_dict = dict(
        test_param0="empty",
        test_param1="full",
    )

    mocker.patch('cdist.RedisResource.__init__', return_value=None)
    mocker.patch("cdist.RedisResource.pull", return_value=config_dict)
    mocker.patch("cdist.RedisResource.lock")
    mocker.patch("cdist.RedisResource.unlock")


def test_pull_config(testdir, mocker):
    """
    Test if parameters will be overwritten correctly.
    """
    testdir.makepyfile(
        """
        def test_parameter(pytestconfig):
            assert pytestconfig.getini("test_param0") == "empty"
            assert pytestconfig.getini("test_param1") == "full"
    """)

    result = testdir.runpytest("--cdist-config=test")
    result.assert_outcomes(passed=1)

    cdist.RedisResource.pull.assert_called_with("test")
    cdist.RedisResource.lock.assert_called_with("test")
    cdist.RedisResource.unlock.assert_called_with("test")


def test_parameters(testdir, mocker):
    """
    Test cdist parameters setup.
    """
    testdir.makeini(
        """
        [pytest]
        cdist_hostname = 192.168.1.1
        cdist_port = 2244
        cdist_autolock = False
    """)

    result = testdir.runpytest("--cdist-config=test")

    cdist.RedisResource.__init__.assert_called_with(
        hostname="192.168.1.1", port=2244)
    cdist.RedisResource.pull.assert_called_with("test")
    cdist.RedisResource.lock.assert_not_called()
    cdist.RedisResource.unlock.assert_not_called()
