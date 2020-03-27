# -*- coding: utf-8 -*-
"""
cdist-cli command implementation.

Author:
    Andrea Cervesato <andrea.cervesato@mailbox.org>
"""
import sys
import configparser
import click
from cdist.redis import RedisResource
from cdist.resource import ResourceError


class Arguments:
    """
    Default program arguments.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self):
        self.resource = None


# pylint: disable=invalid-name
pass_arguments = click.make_pass_decorator(Arguments, ensure=True)


class CatchAllExceptions(click.Group):
    """
    Class created to catch all exceptions coming from the application.
    """

    def __call__(self, *args, **kwargs):
        try:
            return self.main(*args, **kwargs)
        except Exception as exc:
            click.secho(str(exc), fg="red")


@click.group(cls=CatchAllExceptions)
@click.option(
    '--hostname',
    '-h',
    default="localhost",
    help="resource server storing configurations (default: localhost)")
@click.option(
    '--port',
    '-p',
    default="61324",
    type=click.INT,
    help="port of the resource server (default: 6379)")
@pass_arguments
def cli(args, hostname, port):
    """
    cdist client for pytest distributed configuration.
    """
    kwargs = dict(
        hostname=hostname,
        port=port
    )
    args.resource = RedisResource(**kwargs)


@cli.command()
@click.argument("config_name")
@click.argument("config_file")
@pass_arguments
def push(args, config_name, config_file):
    """
    push a new configuration.
    """
    config = configparser.ConfigParser()
    config.read(config_file)

    if 'pytest' not in config.sections():
        raise ResourceError("not a pytest configuration.")

    click.echo("pushing '%s': " % config_name, nl=False)

    # pytest section to dict
    pytest_dict = dict()
    for option in config.options('pytest'):
        pytest_dict[option] = config.get('pytest', option)

    # push pytest configuration
    args.resource.push(config_name, pytest_dict)

    click.secho("done", fg="green")


@cli.command()
@click.argument("config_name")
@pass_arguments
def show(args, config_name):
    """
    show a configuration.
    """
    config = args.resource.pull(config_name)

    click.echo("\n[pytest]")
    for key, value in config.items():
        click.echo("%s = %s" % (key, value))


@cli.command()
@click.argument("config_name")
@pass_arguments
def lock(args, config_name):
    """
    lock a configuration.
    """
    args.resource.lock(config_name)


@cli.command()
@click.argument("config_name")
@pass_arguments
def unlock(args, config_name):
    """
    unlock a configuration.
    """
    args.resource.unlock(config_name)


@cli.command(name="list")
@pass_arguments
def _list(args):
    """
    list all saved configurations.
    """
    keys = args.resource.keys()

    click.echo("Available configurations:")
    if not keys:
        click.echo("- No configurations.")
        return

    for key in keys:
        click.echo("- %s: " % key, nl=False)

        if args.resource.is_locked(key):
            click.secho("Locked", fg="red")
        else:
            click.secho("Not locked", fg="green")


@cli.command()
@click.argument("config_name")
@pass_arguments
def delete(args, config_name):
    """
    delete a configuration.
    """
    args.resource.delete(config_name)
