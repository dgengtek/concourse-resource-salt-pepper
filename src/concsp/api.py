import abc

class ConcourseApi(abc.ABC):
    def __init__(self):
        pass


class ConcourseCheck(ConcourseApi):
    pass


class ConcourseIn(ConcourseApi):
    pass


class ConcourseOut(ConcourseApi):
    pass
