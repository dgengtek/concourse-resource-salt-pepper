import click
# http://click.pocoo.org/5/options/
from concsp import api
import logging


@click.group("concsp")
@click.option(
    "-l",
    "--loglevel",
    type=click.Choice(["info", "debug", "warning"]),
    default="info")
@click.pass_context
def main(ctx, loglevel):
    levels = {
        "info": logging.INFO,
        "debug": logging.DEBUG,
        "warning": logging.WARNING,
        }
    logging.basicConfig(level=levels.get(loglevel))
    d = dict()
    ctx.obj = d


@main.command("check")
@click.pass_context
def main_check(ctx, args=None):
    concourse = api.build_check()
    concourse.run()


@main.command("in")
@click.argument("destination", required=True)
@click.pass_context
def main_in(ctx, destination):
    concourse = api.build_in()
    concourse.run()


@main.command("out")
@click.argument("source", required=True)
@click.pass_context
def main_out(ctx, source):
    concourse = api.build_out()
    concourse.run()


if __name__ == "__main__":
    main()
