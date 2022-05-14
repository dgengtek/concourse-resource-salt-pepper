from pepper import PepperException
import time
import logging
import sys
import textwrap
import urllib
from .data import ReturnData

logger = logging.getLogger(__name__)


class SaltAPI:
    def __init__(self, pepper, payload):
        self.pepper = pepper
        self.payload = payload

    def login(self):
        logger.debug("Trying to log into salt {}".format(self.payload.uri))
        self.pepper.login(
            self.payload.username, self.payload.password, self.payload.eauth
        )
        logger.debug("Logged in via pepper.")

    def logout(self):
        logger.debug("Trying to log out of salt.")
        if (
            self.pepper.auth
            and "token" in self.pepper.auth
            and self.pepper.auth["token"]
        ):
            return self.pepper.req("/logout", [])
        raise PepperException("You are not logged in.")

    def poll_for_returns(self, load):
        """
        Run a command with the local_async client and periodically poll the job
        cache for returns for the job.
        """

        if not self.payload.client.startswith(
            "local"
        ) and not self.payload.client.startswith("runner"):
            raise PepperException(
                "The client '{}' is not supported".format(self.payload.client)
            )

        logger.info("Running pepper.low with payload")
        async_ret = self.pepper.low(load)
        jid = async_ret["return"][0]["jid"]
        logger.info("jid: {}".format(jid))
        minions = async_ret["return"][0]["minions"]
        logger.info("job running on minions: {}".format(minions))
        returned_minions = []

        print("jid: {}".format(jid), file=sys.stderr)
        if not self.payload.poll_lookup_jid:
            yield 0, None, minions

        # keep trying until all expected minions return
        total_time = 0
        error_count = 0
        start_time = time.time()
        exit_code = 0
        while True:
            logger.info("waiting for all expected minions to return")
            total_time = time.time() - start_time
            if total_time > self.payload.timeout:
                logger.error(
                    "Total timeout of {} exceeded. Stop waiting for job return.".format(
                        self.payload.total_time
                    )
                )
                exit_code = 1
                break
            elif error_count >= self.payload.retry:
                logger.error(
                    "Error count exceed {} retries. Stop waiting for job return.".format(
                        self.payload.retry
                    )
                )
                exit_code = 1
                break

            logger.info("Runner jobs.lookup_jid for jid: {}".format(jid))
            try:
                jid_ret = self.pepper.low(
                    [
                        {
                            "client": "runner",
                            "fun": "jobs.lookup_jid",
                            "timeout": self.payload.job_timeout,
                            "kwarg": {
                                "jid": jid,
                            },
                        }
                    ]
                )
                logger.debug(jid_ret)
            except PepperException as exc:
                if "Authentication" in str(exc):
                    logger.info(
                        "Logging in again because of pepper authentication error"
                    )
                    self.login()
                logger.error(
                    "Retrying job lookup because of Pepper Error: {}.".format(exc)
                )
                error_count += 1
                time.sleep(self.payload.sleep_time)
                continue
            except urllib.error.HTTPError as exc:
                logger.error(
                    "Retrying job lookup because of HTTP Error: {}.".format(exc)
                )
                error_count += 1
                time.sleep(self.payload.sleep_time)
                continue

            error_count = 0

            if not jid_ret["return"][0]:
                logger.info("Return was empty. Waiting for result")
                time.sleep(self.payload.sleep_time)
                continue

            builder = ReturnData.get_builder_for_client(self.payload.client)
            return_data = builder(jid_ret)
            returned_minions = return_data.get_minion_ids()

            responded = set(minions) ^ set(returned_minions)
            logger.info("Minions responded: {}".format(responded))

            if set(returned_minions) == set(minions):
                logger.info("All minions responded. Finishing.")
                return 0, return_data, minions

        return exit_code, None, minions

    def run(self, load):
        try:
            self.login()
        except PepperException as exc:
            logger.error(
                "{}. Failed to login as user '{}' using eauth: {}.".format(
                    exc, self.payload.username, self.payload.eauth
                )
            )
            logger.debug("password='{}'".format(self.payload.password))
            sys.exit(1)

        logger.info(
            "Running pepper - {} {} - '{}' {} {} {} ".format(
                self.payload.client,
                self.payload.tgt_type,
                self.payload.tgt,
                self.payload.fun,
                self.payload.args,
                self.payload.kwargs,
            )
        )

        exit_code, return_data, minions = self.poll_for_returns(load)
        print(minions)

        if not self.payload.fail_if_minions_dont_respond:
            exit_code = 0

        # nothing was returned
        if not return_data:
            sys.exit(exit_code)

        print(str(return_data))
        if return_data.success and exit_code == 0:
            sys.exit(0)
        elif not return_data.success:
            sys.exit(1)

        sys.exit(exit_code)


def _indent_char(s, count=1, spaces=4, character=" "):
    result = s if type(s) == str else str(s)
    for i in range(count):
        result = textwrap.indent(result, character * spaces)
    return result


def get_api_payload(payload):
    return build_load(
        payload.client,
        payload.tgt,
        payload.fun,
        payload.args,
        payload.kwargs,
        payload.tgt_type,
        payload.timeout,
    )


def build_load(
    client, tgt, fun, args=None, kwargs=None, tgt_type="glob", timeout=None, ret=None
):
    return {
        "client": client,
        "tgt": tgt,
        "fun": fun,
        "arg": args,
        "kwarg": kwargs,
        "tgt_type": tgt_type,
        "timeout": timeout,
        "ret": ret,
    }
