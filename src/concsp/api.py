from concsp import salt, payload
from pepper import Pepper
import abc
import sys


class ConcourseApi(abc.ABC):
    def __init__(self, resource_payload, saltapi):
        self.resource_payload = resource_payload
        self.saltapi = saltapi

    def _execute(self):
        """
        Run resource specific api
        """

        pepper = Pepper(
            self.payload.uri,
            self.payload.debug_http,
            self.payload.verify_ssl)
        salt_pepper_api = self.saltapi(pepper, self.payload)
        pepper_payload = salt.get_api_payload(self.payload)
        salt_pepper_api.run(pepper_payload)

    def run(self):
        self._input()
        self._execute()
        self._output()

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
        pass

    def _output(self):
        pass


class ConcourseApiIn(ConcourseApiNoop):
    def _output(self):
        import json
        print(json.dumps({
            "version": {},
            }))


class ConcourseApiCheck(ConcourseApiNoop):
    def _output(self):
        print([])


class ConcourseApiOut(ConcourseApi):
    def _output(self):
        import json
        print(json.dumps({
            "version": {},
            }))


def build_check():
    return ConcourseApiCheck(
            payload.ResourcePayload,
            salt.SaltAPI)


def build_out():
    return ConcourseApiOut(
            payload.ResourcePayloadOut,
            salt.SaltAPI)


def build_in():
    return ConcourseApiIn()
