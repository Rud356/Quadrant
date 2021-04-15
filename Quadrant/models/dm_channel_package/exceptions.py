class UserIsNotAMemberException(PermissionError):
    pass


class BlockedByOtherParticipantException(PermissionError):
    pass
