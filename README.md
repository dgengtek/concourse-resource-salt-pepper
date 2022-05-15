# Concourse resource salt pepper

Run commands on a remote salt-api instance with the help of [pepper](https://github.com/saltstack/pepper)


See [example](./ci/concourse.yml) usage of the resource in a concourse pipeline


Make sure to set the external_auth configuration on the salt-master and include
permission to run jobs.lookup_jid for the user concourse will be using. Eg:


    external_auth:
      ldap:
        admin_salt%:
          - "*":
            - test.echo
            - test.ping
        concourse:
          - "*":
            - test.ping
            - state.*
          - '@runner':
            - 'jobs.lookup_jid'


## Source configuration

* `uri`: *Required.* Uri to salt-api instance
* `username`: *Required.*
* `password`: *Required.*
* `eauth`: *Optional.* default: auto
* `client`: *Optional.* default: local_async, (only local_async, runner_async supported)
* `debug_http`: *Optional.* default: False
* `loglevel`: *Optional.* default: warning
* `verify_ssl`: *Optional.* default: True
* `outputter`: *Optional.* default: True, Currently only simple outputter added
* `timeout`: *Optional.* default: 300 (in seconds), total timeout for waiting on return
* `job_timeout`: *Optional.* default: 120 (in seconds), salt job timeout
* `retry`: *Optional.* default: 5, how often to retry on failure before exiting
* `tgt_type`: *Optional.* default: glob, can be set in source as default for resource use in put
* `fail_if_minions_dont_respond`: *Optional.* default: True. The resource will return an error result which will result in failure in the pipeline.
* `poll_lookup_jid`: *Optional.* default: True. The resource will poll for the result of the job. If disabled will return immediately
* `sleep_time`: *Optional.* default: 3 (in seconds). Define how long to sleep between each poll of results against the salt-api of the executed job


## Behaviour

[Targeting minions](https://docs.saltproject.io/en/latest/topics/targeting/index.html)

[Salt client](https://docs.saltproject.io/en/latest/ref/clients/)

### check

noop

### in

noop

### out

Runs commands via the salt pepper library

#### Parameters

* `client`: *Optional.* default: from source configuration
* `tgt`: *Required if the client does as well. See pepper* Saltstack targetting format of minions
* `fun`: *Required.* The salt function to run
* `args`: *Optional.* Arguments to the salt function ["test=True"]. Must be a list
* `kwargs`: *Optional.* Key value arguments to pass to the function.
* `timeout`: *Optional.* default: from source configuration
* `job_timeout`: *Optional.* default: from source configuration
* `retry`: *Optional.* default: from source configuration
* `tgt_type`: *Optional.* default: from source configuration
* `fail_if_minions_dont_respond`: *Optional.* default: from source configuration
* `poll_lookup_jid`: *Optional.* default: from source configuration
* `sleep_time`: *Optional.* default: from source configuration
