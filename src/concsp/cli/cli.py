import click
# http://click.pocoo.org/5/options/
from concsp import api
import logging
import sys


@click.group("concsp")
@click.option(
    "-l",
    "--loglevel",
    type=click.Choice(["info", "debug", "warning"]))
@click.pass_context
def main(ctx, loglevel):
    levels = {
        "info": logging.INFO,
        "debug": logging.DEBUG,
        "warning": logging.WARNING,
        }
    logging.basicConfig(level=levels.get(loglevel, logging.WARNING))
    d = dict()
    d["loglevel"] = loglevel
    ctx.obj = d


@main.command("check")
@click.pass_context
def main_check(ctx):
    concourse = api.build_check(ctx.obj)
    concourse.run()


@main.command("in")
@click.argument("destination", required=True)
@click.pass_context
def main_in(ctx, destination):
    concourse = api.build_in(ctx.obj)
    concourse.run()


@main.command("out")
@click.argument("source", required=True)
@click.pass_context
def main_out(ctx, source):
    concourse = api.build_out(ctx.obj)
    try:
        concourse.run()
    except PepperException as exc:
        log.error(exc)
        sys.exit(1)
