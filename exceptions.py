class MAIScheduleError(Exception):
    """
    Basic exception class of MAI schedule.
    """

    pass

class NoSuchGroupID(MAIScheduleError):
    """
    Raise when there is no group id.
    """

    def __init__(self, group_id):
        super().__init__(f"There is no group with that id: {group_id}")