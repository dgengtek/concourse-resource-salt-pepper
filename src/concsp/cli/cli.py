import click
# http://click.pocoo.org/5/options/
from concsp import api


@click.group("concsp")
@click.pass_context
def main(ctx, args=None):
    d = dict()
    ctx.obj = d


@main.command("check")
@click.pass_context
def main_check(ctx, args=None):
    concourse = api.build_check()
    concourse.run()


@main.command("in")
@click.pass_context
def main_in(ctx, args=None):
    concourse = api.build_in()
    concourse.run()


@main.command("out")
@click.pass_context
def main_out(ctx, args=None):
    concourse = api.build_out()
    concourse.run()


if __name__ == "__main__":
    main()
