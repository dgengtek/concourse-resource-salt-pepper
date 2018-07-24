import pepper
import time
import logging

logger = logging.getLogger(__name__)


class SaltAPI(pepper.Pepper):
    def __init__(self, payload):
        super().__init__(
                payload.uri,
                payload.debug_http,
                payload.verify_ssl)
        self.payload = payload

    def logout(self):
        if self.auth and 'token' in self.auth and self.auth['token']:
            return self.req("/logout", [])
        raise pepper.PepperException('You are not logged in.')

    def poll_for_returns(self, load):
        '''
        Run a command with the local_async client and periodically poll the job
        cache for returns for the job.
        '''
        load[0]['client'] = 'local_async'
        async_ret = self.low(load)
        jid = async_ret['return'][0]['jid']
        nodes = async_ret['return'][0]['minions']
        ret_nodes = []
        exit_code = 1

        # keep trying until all expected nodes return
        total_time = 0
        start_time = time.time()
        exit_code = 0
        while True:
            total_time = time.time() - start_time
            if total_time > self.payload.timeout:
                exit_code = 1
                break

            jid_ret = self.low([{
                'client': 'runner',
                'fun': 'jobs.lookup_jid',
                'kwarg': {
                    'jid': jid,
                },
            }])

            responded = set(jid_ret['return'][0].keys()) ^ set(ret_nodes)
            for node in responded:
                yield None, "{{{}: {}}}".format(
                    node,
                    jid_ret['return'][0][node])
            ret_nodes = list(jid_ret['return'][0].keys())

            if set(ret_nodes) == set(nodes):
                exit_code = 0
                break
            else:
                time.sleep(self.payload.seconds_to_wait)

        if self.payload.fail_if_minions_dont_respond:
            exit_code = exit_code
        else:
            exit_code = 0

        yield exit_code, "{{Failed: {}}}".format(
            list(set(ret_nodes) ^ set(nodes)))

    def run(self, load):
        load = {}
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
