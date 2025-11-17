"""
A helper module to handle context.
"""

import inspect
from typing import TypedDict


class ContextCallerProps(TypedDict):
    """
    A helper class to handle Context caller infos properly.

    Attributes:
        package (str | None) : The caller package
        module (str | None)  : The caller module
        cls (str | None)     : The caller class name if any
        function (str | None): The caller function or method name
        qualname (str | None): The caller qualname
        file (str)           : The caller file name
        line (int)           : The line number of the call
    """

    package: str | None
    module: str | None
    cls: str | None
    function: str | None
    qualname: str | None
    file: str
    line: int


class Context:
    """
    A helper class to wrap context functions.
    """

    # ****************************************************************
    # Static methods

    @staticmethod
    def caller_infos(skip: int = 1) -> "ContextCallerProps":
        """
        Return caller context infos.

        Args:
            skip (int): Levels of stack to skip

        Returns:
            ContextCallerProps: Caller infos as a dictionary
        """


        stack = inspect.stack()
        start = 0 + skip

        if len(stack) < start + 1:
            raise ValueError(f"{__class__.__name__}.caller_infos::Caller stack is {len(stack)}, you skipped {skip} levels")

        infos = {}
        parent_f = stack[start][0]

        module_info = inspect.getmodule(parent_f)
        if module_info:
            mod = module_info.__name__.split(".")
            infos["package"] = mod[0]
            infos["module"] = mod[1] if len(mod) > 1 else None

        infos["cls"] = None
        if "self" in parent_f.f_locals:
            infos["cls"] = parent_f.f_locals["self"].__class__.__name__

        infos["function"] = None
        infos["qualname"] = None
        if parent_f.f_code.co_name != '<module>':
            infos["function"] = parent_f.f_code.co_name
            infos["qualname"] = parent_f.f_code.co_qualname

        infos["file"] = parent_f.f_code.co_filename
        infos["line"] = parent_f.f_lineno

        return ContextCallerProps(**infos)
