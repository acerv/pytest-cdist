# -*- coding: utf-8 -*-
"""
cdist-cli command implementation.

Author:
    Andrea Cervesato <andrea.cervesato@mailbox.org>
"""
import sys
import configparser
import click
from cdist import RedisResource
from cdist import ResourceError


class Arguments:
    """
    Default program arguments.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self):
        self.resource = None


# pylint: disable=invalid-name
pass_arguments = click.make_pass_decorator(Arguments, ensure=True)


def print_error(msg):
    """
    print error message and exit.
    """
    click.secho(msg, err=True, fg="red")
    sys.exit(1)


@click.group()
@click.option(
    '--hostname',
    '-h',
    default="localhost",
    help="resource server storing configurations (default: localhost)")
@click.option(
    '--port',
    '-p',
    default="6379",
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
@click.argument("config_name", nargs=1)
@click.argument("config_file", nargs=1)
@pass_arguments
def push(args, config_name, config_file):
    """
    push a new configuration.
    """
    config = configparser.ConfigParser()
    config.read(config_file)

    if 'pytest' not in config.sections():
        print_error("ERROR: not a pytest configuration.")

    click.echo("pushing '%s': ", nl=False)

    try:
        args.resource.push(config_name, config['pytest'])
    except ResourceError as err:
        print_error("ERROR: %s." % str(err))

    click.secho("done", fg="green")


@cli.command()
@click.argument("config_name", nargs=1)
@pass_arguments
def show(args, config_name):
    """
    show a configuration.
    """
    keys = list()
    try:
        keys = args.resource.keys()
    except ResourceError as err:
        print_error("ERROR: %s." % str(err))

    if config_name not in keys:
        print_error("ERROR: can't find the requested configuration.")

    config = None
    try:
        config = args.resource.pull(config_name)
    except ResourceError as err:
        print_error("ERROR: %s." % str(err))

    click.echo("\n[pytest]")
    for key, value in config.items():
        click.echo("%s = %s" % (key, value))


@cli.command()
@click.argument("config_name", nargs=1)
@pass_arguments
def lock(args, config_name):
    """
    lock a configuration.
    """
    keys = list()
    try:
        keys = args.resource.keys()
    except ResourceError as err:
        print_error("ERROR: %s." % str(err))

    if config_name not in keys:
        print_error("ERROR: can't find the requested configuration.")

    try:
        args.resource.lock(config_name)
    except ResourceError as err:
        print_error("ERROR: %s." % err)


@cli.command()
@click.argument("config_name", nargs=1)
@pass_arguments
def unlock(args, config_name):
    """
    unlock a configuration.
    """
    keys = list()
    try:
        keys = args.resource.keys()
    except ResourceError as err:
        print_error("ERROR: %s." % str(err))

    if config_name not in keys:
        print_error("ERROR: can't find the requested configuration.")

    try:
        args.resource.unlock(config_name)
    except ResourceError as err:
        print_error("ERROR: %s." % err)
