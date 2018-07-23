import json
import sys
import os
import logging

logger = logging.getLogger(__name__)


class ConcoursePayloadException(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class ConcoursePayload(object):
    ''' Payload class '''

    def __init__(self):
        self.payload = {}
        self.args = {}
        self.initialized = False

    def init(self, payload=None):
        self.initialized = True
        self.payload = self.get_payload(payload)
        try:
            self.source = self.payload["source"]
        except KeyError:
            raise ConcoursePayloadException("Source not configured.")
        else:
            self.params = self.payload.get("params", {})
            self.parse_payload()
        # argument pass with dir
        # not required
        #self.working_dir = self._get_dir_from_argv()

    def get_payload(self, payload=sys.stdin):
        if type(payload) == dict:
            return payload
        try:
            payload = json.load(payload)
        except ValueError as value_error:
            raise ConcoursePayloadException("JSON Input error: {}".format(value_error))
        return payload

    def _get_dir_from_argv(self):
        if len(sys.argv) < 2:
            return False

        if not os.path.isdir(sys.argv[1]):
            raise ConcoursePayloadException("Invalid dir argument passed '{}'".format(sys.argv[1]))
        return sys.argv[1]

    def parse_payload(self):
        ''' Parse payload passed by concourse'''
        self.version = self.payload.get("version")
        if self.version is None:
            self.version = {}
        self.parse_payload_source()
        self.parse_payload_params()

    def parse_payload_source(self):
        try:
            # Mandatory
            self.uri = self.source["uri"]
            self.username = self.source["username"]
            self.password = self.source["password"]
            self.eauth = self.source.get("eauth", "pam")
        except KeyError as value_error:
            raise ConcoursePayloadException("Source config '{}' required".format(value_error))
        # Optional
        self.debug_http = self.source.get("debug_http", False)
        self.verify_ssl = self.source.get("verify_ssl", True)
        self.outputter = self.source.get("outputter", True)
        self.timeout = self.source.get("timeout", 60)
        self.cache_token = self.source.get("cache_token", False)
        self.loglevel = self.source.get("loglevel", "warning")
        self.client = self.source.get("client", "local_async")
        self.expr_form = self.source.get("expr_form", "glob")

    def parse_payload_params(self):
        # Optional
        self.client = self.params.get("client", self.client)
        self.expr_form = self.params.get("expr_form", self.expr_form)
        self.tgt = self.params.get("tgt", None)
        self.fun = self.params.get("fun", None)
        self.arg = self.params.get("arg", [])
        self.kwargs = self.params.get("kwargs", {})
