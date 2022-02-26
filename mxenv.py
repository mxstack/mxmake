from mxdev import Hook
from mxdev import State


class MxEnv(Hook):

    def read(state: State) -> None:
        """Gets executed after mxdev read operation."""

    def write(state: State) -> None:
        """Gets executed after mxdev write operation."""
