from .quadrant_exception import QuadrantException


class UserProfileNotFound(QuadrantException):
    """
    User wasn't found in database.
    """