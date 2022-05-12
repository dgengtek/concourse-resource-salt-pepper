import json
import sys
import os
import logging
import copy

logger = logging.getLogger(__name__)


class ResourcePayload(object):
    ''' Payload class '''

    def __init__(self):
        self.payload = {}
        self.args = {}
        self.initialized = False

    def init(self, payload):
        if self.initialized:
            raise ResourcePayloadException(
                    "Payload has been initialized already.")
        self.initialized = True

        self.payload = self.get_payload(payload)
        try:
            self.source = self.payload["source"]
        except KeyError:
            raise ResourcePayloadException("Source not configured.")
        else:
            self.params = self.payload.get("params", {})
            self.parse_payload()
        # argument pass with dir
        # not required
        # self.working_dir = self._get_dir_from_argv()

    def get_payload(self, payload=sys.stdin):
        if not payload:
            raise ResourcePayloadException("Payload required.")
        if type(payload) == dict:
            return copy.deepcopy(payload)
        try:
            payload = json.load(payload)
        except ValueError as value_error:
            raise ResourcePayloadException(
                    "JSON Input error: {}".format(value_error))
        return payload

    def __getattribute__(self, name):
        if name in ("init", "initialized"):
            return super().__getattribute__(name)
        if not self.initialized:
            raise ResourcePayloadException(
                    "Payload is not initialized. Attribute access denied.")
        return super().__getattribute__(name)

    def reset(self):
        self.initialized = False
        del self.source
        del self.params
        del self.payload

    def _get_dir_from_argv(self):
        if len(sys.argv) < 2:
            return False

        if not os.path.isdir(sys.argv[1]):
            raise ResourcePayloadException(
                    "Invalid dir argument passed '{}'".format(sys.argv[1]))
        return sys.argv[1]

    def parse_payload(self):
        ''' Parse payload passed by concourse'''
        self.version = self.payload.get("version")
        if self.version is None:
            self.version = {}
        self.parse_payload_source(self.source)
        self.parse_payload_params(self.params)
        self._verify()

    def parse_payload_source(self, source):
        try:
            # Mandatory
            self.uri = source["uri"]
            self.username = source["username"]
            self.password = source["password"]
            self.eauth = source.get("eauth", "auto")
        except KeyError as value_error:
            raise ResourcePayloadSourceException(
                    "Source config '{}' required".format(value_error))
        # Optional
        self.debug_http = source.get("debug_http", False)
        self.verify_ssl = source.get("verify_ssl", True)
        self.outputter = source.get("outputter", True)
        self.timeout = source.get("timeout", 300)
        self.job_timeout = source.get("job_timeout", 120)
        self.retry = source.get("retry", 5)
        self.cache_token = source.get("cache_token", False)
        self.loglevel = source.get("loglevel", "warning")
        self.client = source.get("client", "local_async")
        self.expr_form = source.get("expr_form", "glob")
        self.fail_if_minions_dont_respond = source.get(
                "fail_if_minions_dont_respond", True)
        self.poll_lookup_jid = source.get(
                "poll_lookup_jid", True)
        self.sleep_time = source.get("sleep_time", 3)

    def parse_payload_params(self, params):
        # Optional
        self.client = params.get("client", self.client)
        self.expr_form = params.get("expr_form", self.expr_form)
        self.tgt = params.get("tgt", None)
        self.fun = params.get("fun", None)
        self.args = params.get("args", [])
        self.kwargs = params.get("kwargs", {})

    def _verify(self):
        if type(self.args) != list:
            raise ResourcePayloadParameterException("args is not a list")
        if type(self.kwargs) != dict:
            raise ResourcePayloadParameterException("kwargs is not a dict")

    def update(self, data):
        self.parse_payload_source(data.get("source", {}))
        self.parse_payload_params(data.get("params", {}))


class ResourcePayloadOut(ResourcePayload):
    def parse_payload_params(self, params):
        try:
            # Mandatory
            self.tgt = params["tgt"]
            self.fun = params["fun"]
        except KeyError as value_error:
            raise ResourcePayloadParameterException(
                    "Params config '{}' required".format(value_error))
        self.client = params.get("client", self.client)
        self.expr_form = params.get("expr_form", self.expr_form)
        self.args = params.get("args", [])
        self.kwargs = params.get("kwargs", {})

        self.fail_if_minions_dont_respond = params.get(
                "fail_if_minions_dont_respond",
                self.fail_if_minions_dont_respond)
        self.poll_lookup_jid = params.get(
                "poll_lookup_jid", self.poll_lookup_jid)
        self.sleep_time = params.get("sleep_time", self.sleep_time)
        self.timeout = params.get("timeout", self.timeout)
        self.job_timeout = params.get("job_timeout", self.job_timeout)
        self.retry = params.get("retry", self.retry)


class ResourcePayloadException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class ResourcePayloadSourceException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class ResourcePayloadParameterException(Exception):
    def __init__(self, msg):
        super().__init__(msg)
