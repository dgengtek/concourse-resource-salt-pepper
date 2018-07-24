from pepper import PepperException
import time
import logging

logger = logging.getLogger(__name__)


class SaltAPI():
    def __init__(self, pepper, payload):
        self.pepper = pepper
        self.payload = payload

    def login(self):
        self.pepper.login(
                self.payload.username,
                self.payload.password,
                self.payload.eauth)

    def logout(self):
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
        exit_code = 1

        # keep trying until all expected nodes return
        total_time = 0
        start_time = time.time()
        exit_code = 0
        while True:
            logger.info("waiting for all expected nodes to return")
            total_time = time.time() - start_time
            if total_time > self.payload.timeout:
                exit_code = 1
                break

            logger.info("Runner jobs.lookup_jid for jid: {}".format(jid))
            jid_ret = self.pepper.low([{
                'client': 'runner',
                'fun': 'jobs.lookup_jid',
                'kwarg': {
                    'jid': jid,
                },
            }])

            responded = set(jid_ret['return'][0].keys()) ^ set(ret_nodes)
            logger.info("Nodes responded: {}".format(responded))
            for node in responded:
                yield None, "{{{}: {}}}".format(
                    node,
                    jid_ret['return'][0][node])
            ret_nodes = list(jid_ret['return'][0].keys())

            if set(ret_nodes) == set(nodes):
                logger.info("All nodes responded. Finishing.")
                exit_code = 0
                break
            else:
                logger.info("Not all nodes responded. Trying again...")
                time.sleep(self.payload.seconds_to_wait)

        if self.payload.fail_if_minions_dont_respond:
            exit_code = exit_code
        else:
            exit_code = 0

        yield exit_code, "{{Failed: {}}}".format(
            list(set(ret_nodes) ^ set(nodes)))

    def run(self, load):
        try:
            self.login()
        except PepperException as exc:
            logger.error(
                    "{}. Failed to login as {} using eauth: {}."
                    .format(exc, self.payload.username, self.payload.eauth))

        logger.info("Running pepper - {} {} - '{}' {} {} {} ".format(
            load.client,
            load.expr_form,
            load.tgt,
            load.fun,
            load.args,
            load.kwargs))

        for exit_code, result in self.poll_for_returns(load):
            print(exit_code, result)


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
