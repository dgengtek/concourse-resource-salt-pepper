from concsp import salt, payload
from pepper import Pepper
import abc
import sys
import json
import logging
import sys

logger = logging.getLogger(__name__)


class ConcourseApi(abc.ABC):
    def __init__(self, context, resource_payload, saltapi):
        self.context = context
        self.resource_payload = resource_payload
        self.saltapi = saltapi
        self.payload = {}
        self.exit_code = 0

    def _execute(self):
        """
        Run resource specific api
        """
        pepper = Pepper(
            self.payload.uri, self.payload.debug_http, self.payload.verify_ssl
        )
        salt_pepper_api = self.saltapi(pepper, self.payload)
        pepper_payload = salt.get_api_payload(self.payload)
        logger.debug("Running salt pepper with payload:" "{}".format(pepper_payload))
        self.exit_code = salt_pepper_api.run(pepper_payload)

    def run(self):
        self._input()
        self._setup()
        self._execute()
        self._output()
        sys.exit(self.exit_code)

    def _setup(self):
        levels = {
            "debug": logging.DEBUG,
            "warning": logging.WARNING,
            "info": logging.INFO,
        }
        loglevel = self.context.get("loglevel")
        if not loglevel:
            loglevel = self.payload.loglevel
        logging.basicConfig(loglevel=levels.get(loglevel))

    def _input(self):
        self.payload = self.resource_payload()
        self.payload.init(sys.stdin)

    @abc.abstractmethod
    def _output(self):
        raise NotImplementedError()


class ConcourseApiNoop(ConcourseApi):
    def __init__(self, *args, **kwargs):
        pass

    def run(self):
        self._output()

    def _output(self):
        pass


class ConcourseApiIn(ConcourseApiNoop):
    def _output(self):
        print(json.dumps({"version": {}}, indent=4, sort_keys=True))


class ConcourseApiCheck(ConcourseApiNoop):
    def _output(self):
        print([])


class ConcourseApiOut(ConcourseApi):
    def _output(self):
        from datetime import datetime

        print(
            json.dumps(
                {
                    "version": {"version": datetime.isoformat(datetime.now())},
                    "metadata": [
                        {"name": "username", "value": self.payload.username},
                        {"name": "tgt", "value": self.payload.tgt},
                        {"name": "fun", "value": self.payload.fun},
                    ],
                },
                indent=4,
                sort_keys=True,
            )
        )


class ConcourseApiRun(ConcourseApiOut):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.disable_input = False

    def _setup(self):
        super()._setup()

        # override options from cli
        self.payload.update(self.context)

    def run(self):
        if not self.disable_input:
            self._input()
        else:
            self.payload = self.resource_payload()
            self.payload.init(self.context)
        self._setup()
        self._execute()
        self._output()


def build_check(context):
    return ConcourseApiCheck(context, payload.ResourcePayload, salt.SaltAPI)


def build_out(context):
    return ConcourseApiOut(context, payload.ResourcePayloadOut, salt.SaltAPI)


def build_in(context):
    return ConcourseApiIn(context, payload.ResourcePayload, salt.SaltAPI)


def build_run(context, disable_input=True):
    return ConcourseApiRun(context, payload.ResourcePayloadOut, salt.SaltAPI)
