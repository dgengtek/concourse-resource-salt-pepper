from concsp import salt, payload
import abc
import sys


class ConcourseApi(abc.ABC):
    def __init__(self, payloadapi, saltpepperapi):
        self.payloadapi = payloadapi
        self.saltpepperapi = saltpepperapi

    def _execute(self):
        """
        Run resource specific api
        """
        pepper = self.saltpepperapi(self.payload)
        pepper_payload = salt.get_api_payload(self.payload)
        pepper.run(pepper_payload)

    def run(self):
        self._input()
        self._execute()
        self._output()

    def _input(self):
        self.payload = self.payloadapi()
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


class ConcourseApiCheck(ConcourseApi):
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
