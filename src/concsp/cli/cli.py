from concsp import api
import sys


def main():
    try:
        cmd = sys.argv[1]
    except IndexError:
        return
    concourse = None
    if cmd == "in":
        concourse = api.build_in()
    elif cmd == "out":
        concourse = api.build_out()
    elif cmd == "check":
        concourse = api.build_check()
    concourse.run()


if __name__ == "__main__":
    main()
