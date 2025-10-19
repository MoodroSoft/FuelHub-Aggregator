import enum


class EnumWithAttrs(str, enum.Enum):
    """
    Enum class that allows to add attributes

    Example:
    >>> class UserRoles(EnumWithAttrs):
    ...     ADMIN = 'ADMIN', 'Admin user'
    ... 
    ... UserRoles.ADMIN
    ...     <UserRoles.ADMIN: UserRoles>
    ... UserRoles.ADMIN.description
    ...     'Admin user'
    """

    def __new__(cls, *args, **kwargs):
        obj = str.__new__(cls, args[0])
        obj._value_ = args[0]

        if len(args) > 1 and args[1]:
            obj.__doc__ = args[1]
        return obj

    def __init__(self, _: str, description: str | None = None):
        """
        Args:
            description: human-readable description for field
        """
        self._description_ = description

    def __str__(self):
        return self.value

    # this makes sure that the description is read-only
    @property
    def description(self):
        return self._description_