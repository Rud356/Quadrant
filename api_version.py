class APIVersion:
    """
    First two numbers are always ints
    but third may have characters and not
    used to compare versions
    """
    def __init__(self, major: int, minor: int, micro: str):
        self.major = major
        self.minor = minor
        self.micro = micro

    @classmethod
    def from_str(cls, version: str):
        major, minor, micro = version.split('.', 3)
        return cls(int(major), int(minor), micro)

    def __repr__(self):
        return f"API version {self.major}.{self.minor}.{self.micro}"

    def __str__(self):
        return f"{self.major}.{self.minor}.{self.micro}"

    def __lt__(self, other):
        return self.major < other.major

    def __gt__(self, other):
        return self.major > other.major

    def __eq__(self, other):
        return self.major == other.major

    def __ge__(self, other):
        return self > other or self == other

    def __le__(self, other):
        return self < other or self == other