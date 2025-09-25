from rpadatabase.core import IDatabaseCore


class DatabaseCore(IDatabaseCore):
    @staticmethod
    def print(msg: str = "") -> str:
        return "linux {}".format(msg)
