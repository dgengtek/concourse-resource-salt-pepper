import click
# http://click.pocoo.org/5/options/
from concsp import api
import logging
import sys
from pepper import PepperException

logger = logging.getLogger(__name__)


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


@main.command("run")
@click.argument(
    "tgt",
    required=True)
@click.argument(
    "fun",
    required=True)
@click.argument(
    "args",
    nargs=-1,
    required=False)
@click.option("--username")
@click.option("--password")
@click.option(
    "--eauth",
    default="auto")
@click.option(
    "--uri",
    default="https://salt:8000")
@click.pass_context
def main_run(ctx, username, password, tgt, fun, args, uri, eauth):
    ctx.obj["source"] = {}
    ctx.obj["params"] = {}
    ctx.obj["source"]["username"] = username
    ctx.obj["source"]["password"] = password
    ctx.obj["source"]["eauth"] = eauth
    ctx.obj["source"]["uri"] = uri
    ctx.obj["params"]["tgt"] = tgt
    ctx.obj["params"]["fun"] = fun
    if args:
        ctx.obj["params"]["args"] = list(args)
    concourse = api.build_run(ctx.obj)
    concourse.disable_input = True
    concourse.run()


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
        logger.error(exc)
        sys.exit(1)
