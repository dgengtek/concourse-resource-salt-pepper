from pepper import PepperException
import time
import logging
import sys
import textwrap
import urllib

logger = logging.getLogger(__name__)


class SaltAPI():
    def __init__(self, pepper, payload):
        self.pepper = pepper
        self.payload = payload

    def login(self):
        logger.debug("Trying to log into salt {}".format(self.payload.uri))
        self.pepper.login(
            self.payload.username,
            self.payload.password,
            self.payload.eauth)
        logger.debug("Logged in via pepper.")

    def logout(self):
        logger.debug("Trying to log out of salt.")
        if self.pepper.auth \
                and 'token' in self.pepper.auth and self.pepper.auth['token']:
            return self.pepper.req("/logout", [])
        raise PepperException('You are not logged in.')

    def poll_for_returns(self, load):
        '''
        Run a command with the local_async client and periodically poll the job
        cache for returns for the job.
        '''
        load['client'] = 'local_async'
        logger.info("Running local_async low")
        async_ret = self.pepper.low(load)
        jid = async_ret['return'][0]['jid']
        logger.info("jid: {}".format(jid))
        nodes = async_ret['return'][0]['minions']
        logger.info("nodes: {}".format(nodes))
        ret_nodes = []

        # keep trying until all expected nodes return
        total_time = 0
        error_count = 0
        start_time = time.time()
        exit_code = 0
        while True:
            logger.info("waiting for all expected nodes to return")
            total_time = time.time() - start_time
            if total_time > self.payload.timeout:
                logger.error("Total timeout of {} exceeded. Stop waiting for job return.".format(self.payload.total_time))
                exit_code = 1
                break
            elif error_count >= self.payload.retry:
                logger.error("Error count exceed {} retries. Stop waiting for job return.".format(self.payload.retry))
                exit_code = 1
                break

            logger.info("Runner jobs.lookup_jid for jid: {}".format(jid))
            try:
                jid_ret = self.pepper.low([{
                    'client': 'runner',
                    'fun': 'jobs.lookup_jid',
                    'timeout': self.payload.job_timeout,
                    'kwarg': {
                        'jid': jid,
                    },
                }])
            except PepperException as exc:
                if "Authentication" in str(exc):
                    logger.info("Logging in again because of pepper authentication error")
                    self.login()
                logger.error(
                    "Retrying job lookup because of Pepper Error: {}."
                    .format(exc))
                error_count += 1
                time.sleep(self.payload.sleep_time)
                continue
            except urllib.error.HTTPError as exc:
                logger.error(
                    "Retrying job lookup because of HTTP Error: {}."
                    .format(exc))
                error_count += 1
                time.sleep(self.payload.sleep_time)
                continue

            error_count = 0
            responded = set(jid_ret['return'][0].keys()) ^ set(ret_nodes)
            logger.info("Nodes responded: {}".format(responded))
            for node in responded:
                yield None, {node: jid_ret['return'][0][node]}
            ret_nodes = list(jid_ret['return'][0].keys())

            if set(ret_nodes) == set(nodes):
                logger.info("All nodes responded. Finishing.")
                exit_code = 0
                break
            else:
                logger.info("Not all nodes responded. Trying again...")
                time.sleep(self.payload.sleep_time)

        if not self.payload.fail_if_minions_dont_respond:
            exit_code = 0

        yield exit_code, {"Failed": list(set(ret_nodes) ^ set(nodes))}

    def run(self, load):
        try:
            self.login()
        except PepperException as exc:
            logger.error(
                    "{}. Failed to login as user '{}' using eauth: {}."
                    .format(exc, self.payload.username, self.payload.eauth))
            logger.debug("password='{}'".format(self.payload.password))
            sys.exit(1)

        logger.info("Running pepper - {} {} - '{}' {} {} {} ".format(
            self.payload.client,
            self.payload.expr_form,
            self.payload.tgt,
            self.payload.fun,
            self.payload.args,
            self.payload.kwargs))

        for exit_code, result in self.poll_for_returns(load):
            print_result(exit_code, result)


def print_result(rc, result):
    from collections import OrderedDict
    minion, values = result.popitem()
    if not rc:
        rc = 0

    output = "{} ==> {}\n".format(minion, rc)
    if type(values) == dict:
        stack = [(k, v, 1) for k, v in OrderedDict(values).items()]
    else:
        output += "{}".format(_indent_char(values))
        print(output, file=sys.stderr)
        return
    while stack:
        key, items, nested = stack.pop(0)
        if type(items) == dict:
            output += "{}:\n".format(_indent_char(key, nested))
            for k, v in OrderedDict(items).items():
                stack.insert(0, (k, v, nested+1))
        else:
            output += "{}:\n".format(_indent_char(key, nested))
            output += "{}\n".format(_indent_char(items, nested+1))

    print(output, file=sys.stderr)


def _indent_char(s, count=1, spaces=4, character=" "):
    result = s if type(s) == str else str(s)
    for i in range(count):
        result = textwrap.indent(result, character*spaces)
    return result


def get_api_payload(payload):
    return build_load(
        payload.client,
        payload.tgt,
        payload.fun,
        payload.args,
        payload.kwargs,
        payload.expr_form,
        payload.timeout)


def build_load(
        client,
        tgt,
        fun,
        args=None,
        kwargs=None,
        expr_form="glob",
        timeout=None,
        ret=None):
    return {
        "client": client,
        "tgt": tgt,
        "fun": fun,
        "arg": args,
        "kwarg": kwargs,
        "expr_form": expr_form,
        "timeout": timeout,
        "ret": ret
        }
