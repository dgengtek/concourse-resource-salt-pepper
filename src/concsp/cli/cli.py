import click
# http://click.pocoo.org/5/options/


@click.group("concsp")
@click.pass_context
def main(ctx, args=None):
    d = dict()
    ctx.obj = d


@main.command("check")
@click.pass_context
def main_check(ctx, args=None):
    d = dict()
    ctx.obj = d


@main.command("in")
@click.pass_context
def main_in(ctx, args=None):
    d = dict()
    ctx.obj = d


@main.command("out")
@click.pass_context
def main_out(ctx, args=None):
    d = dict()
    ctx.obj = d


if __name__ == "__main__":
    main()
