import pepper
import time
import logging

logger = logging.getLogger(__name__)


class Options():
    def __init__(self):
        self.debug_http = False
        self.ignore_ssl_errors = False
        self.seconds_to_wait = 3
        self.fail_if_minions_dont_respond = True
        self.timeout = 30

    @classmethod
    def build(
            cls,
            url):
        options = cls()
        options.url = url
        return options


class SaltAPI(pepper.Pepper):
    def __init__(self, options):
        super().__init__(
                options.url,
                options.debug_http,
                options.ignore_ssl_errors)
        self.options = options

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
            if total_time > self.options.timeout:
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
                time.sleep(self.options.seconds_to_wait)

        exit_code = exit_code if self.options.fail_if_minions_dont_respond else 0
        yield exit_code, "{{Failed: {}}}".format(
            list(set(ret_nodes) ^ set(nodes)))

    def run(self, load):
        load = {}
        for exit_code, result in self.poll_for_returns(load):
            print(exit_code, result)


def build_load(
        client,
        tgt,
        fun,
        arg=None,
        kwarg=None,
        expr_form="glob",
        timeout=None,
        ret=None):
    return {
            "client": client,
            "tgt": tgt,
            "fun": fun,
            "arg": arg,
            "kwarg": kwarg,
            "expr_form": expr_form,
            "timeout": timeout,
            "ret": ret
            }
