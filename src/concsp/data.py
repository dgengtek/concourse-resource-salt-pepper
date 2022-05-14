import logging

logger = logging.getLogger(__name__)


class ReturnData:
    def __init__(self, minions, success=False):
        if not minions:
            minions = {}
        self.minions = minions
        self.success = success

    @classmethod
    def build_from_local(cls, input_data):
        return_data = input_data["return"][0]["data"]
        success = input_data.get("success", False)
        minions = get_data(return_data)

        return cls(minions, success)

    @classmethod
    def build_from_runner(cls, input_data):
        return_data = input_data["return"][0]
        master, values = return_data.popitem()
        if not master.endswith("_master"):
            raise ReturnDataException(
                "Return data from runner does not"
                "contain the expected master as the only entry"
            )
        return_data = values["return"]["data"]

        success = values.get("success", False)
        minions = get_data(return_data)

        return cls(minions, success)

    def __str__(self):
        output = list()
        for minion_id, states in self.minions.items():
            output.append("==> {}".format(minion_id))
            for state in states:
                output.append("{}".format(state))
        return "\n".join(output)

    @classmethod
    def args_to_string(cls, args):
        funargs = []
        for arg in args:
            if isinstance(arg, dict):
                for i, v in arg.items():
                    if isinstance(v, dict):
                        v = str(v)
                    funargs.append("{}={}".format(i, v))
            else:
                funargs.append(arg)
        return " ".join(funargs)

    def get_command(self, limit_args=15):
        return "{} {}".format(self.module, self.args_to_string(self.args)[:limit_args])


class State:
    def __init__(
        self,
        state_id,
        run_nr,
        result,
        comment,
        sls="",
        name="",
        ident="",
        duration=0,
        start_time=0,
        state_ran=True,
    ):
        self.state_id = state_id
        self.nr = run_nr
        self.result = result
        self.comment = comment
        self.changes = False
        self.pchanges = False
        self.duration = duration
        self.start_time = start_time
        self.state_ran = state_ran
        self.sls = sls
        self.name = name
        self.id = ident

    def __lt__(self, other):
        return self.nr < other.nr

    @classmethod
    def build_from_dict(cls, state_id, input_data):
        comment = input_data.get("comment", "")
        run_nr = input_data.get("__run_num__", 0)
        result = input_data["result"]
        sls = input_data["__sls__"]
        state_ran = input_data.get("__state_ran__", True)
        ident = input_data.get("__id__", "")
        name = input_data.get("name", "")
        duration = input_data.get("duration")
        start_time = input_data.get("start_time")
        changes = False
        pchanges = False
        if input_data.get("changes", ""):
            changes = input_data["changes"]
        if input_data.get("pchanges", ""):
            pchanges = input_data["pchanges"]

        state = cls(
            state_id,
            run_nr,
            result,
            comment,
            duration=duration,
            sls=sls,
            name=name,
            ident=ident,
            start_time=start_time,
            state_ran=state_ran,
        )
        state.changes = changes
        state.pchanges = pchanges
        return state

    @classmethod
    def build_from_str(cls, fun, input_data):
        comment = "State undefined - single state return?"
        run_nr = "single return"
        result = input_data
        ident = "state return id undefined"
        changes = False
        pchanges = False
        changes = False
        pchanges = False
        state_id = "{}: {}".format(fun, type(result))

        state = cls(state_id, ident, run_nr, result, comment)
        state.changes = changes
        state.pchanges = pchanges
        return state

    def __str__(self):
        output = list()
        if self.result:
            output.append("+{}:".format(self.state_id))
        else:
            output.append("-{}:".format(self.state_id))
        if self.id:
            output.append("  id: {}".format(self.id))
        if self.name:
            output.append("  name: {}".format(self.name))
        if self.sls:
            output.append("  sls: {}".format(self.sls))
        output.append("  run_num: {}".format(self.nr))
        if self.start_time:
            output.append("  start_time: {}".format(self.start_time))
        if self.duration:
            output.append("  duration: {}".format(self.duration))
        output.append("  result: {}".format(self.result))
        output.append("  state_ran: {}".format(self.state_ran))
        output.append("  comment: {}".format(self.comment))
        output.append("  changes: {}".format(self.changes))
        output.append("  pchanges: {}".format(self.pchanges))
        return "\n".join(output)


class ReturnDataException(Exception):
    pass


def get_data(return_data):
    data = {}
    for minion_id, values in return_data.items():
        states = []
        for state_id, state_values in values.items():
            states.append(State.build_from_dict(state_id, state_values))
            data.update({minion_id: states})
    return data
