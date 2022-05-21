import logging
import copy

logger = logging.getLogger(__name__)


class ReturnData:
    def __init__(self, minions, success=False):
        if not minions:
            minions = []
        self.minions = minions
        # did every minion return without errors?
        self.success = success

    @classmethod
    def build_from_local(cls, data):
        input_data = copy.deepcopy(data)

        return_data = input_data["return"][0]
        if "data" in return_data:
            return_data = return_data["data"]

        success = True

        minions = []
        for minion_id, states in return_data.items():
            minion = MinionReturnData.build_from_dict(minion_id, states)
            if not minion.success:
                success = False
            minions.append(minion)
        return cls(minions, success)

    @classmethod
    def build_from_runner(cls, data):
        input_data = copy.deepcopy(data)

        return_data = input_data["return"][0]
        master, values = return_data.popitem()
        success = values.get("success", False)

        if not master.endswith("_master"):
            raise ReturnDataException(
                "Return data from runner does not"
                "contain the expected master as the only entry"
            )
        return_data = values["return"]["data"]

        minions = []
        for minion_id, states in return_data.items():
            minions.append(MinionReturnData.build_from_dict(minion_id, states))

        return cls(minions, success)

    @classmethod
    def get_builder_for_client(cls, client):
        if client.startswith("local"):
            return cls.build_from_local
        elif client.startswith("runner"):
            return cls.build_from_runner
        else:
            raise ReturnDataException(
                "ReturnData for client {} is not implemented".format(client)
            )

    def get_minion_ids(self):
        ids = []
        for minion in self.minions:
            ids.append(minion.minion_id)
        return ids

    def __str__(self):
        output = []
        for minion in self.minions:
            output.append(str(minion))
        return "\n".join(output)

    def __eq__(self, other):
        return (
            sorted(self.minions) == sorted(other.minions)
            and self.success == other.success
        )


class MinionReturnData:
    def __init__(self, minion_id, states, success=False):
        self.minion_id = minion_id
        self.states = states
        self.success = success

    @classmethod
    def build_from_dict(cls, minion_id, input_states):
        states = []
        success = True
        if isinstance(input_states, dict):
            for state_id, values in input_states.items():
                state = State.build_from_dict(state_id, values)
                if not state.result:
                    success = False
                states.append(state)
        else:
            states.append(input_states)
        return cls(minion_id, states, success)

    def __eq__(self, other):
        return (
            self.minion_id == other.minion_id
            and sorted(self.states) == sorted(other.states)
            and self.success == other.success
        )

    def __str__(self):
        output = []
        if self.success:
            output.append("+==> {}".format(self.minion_id))
        else:
            output.append("-==> {}".format(self.minion_id))
        for state in self.states:
            output.append("{}".format(state))
        return "\n".join(output)


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

    def __eq__(self, other):
        return (
            self.state_id == other.state_id
            and self.name == other.name
            and self.sls == other.sls
            and self.result == other.result
        )

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
        output = []
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
