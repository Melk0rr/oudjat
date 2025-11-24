"""
A helper module to handle context.
"""

import inspect
from typing import TypedDict, override


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
    # Attributes & Constructor
    def __init__(self, skip: int = 1) -> None:
        """
        Create a new context.

        Args:
            skip (int): The number of context levels to skip
                        1 - Who called context
                        2 - Who called the caller. etc.
        """

        stack = inspect.stack()
        start = 0 + skip

        if len(stack) < start + 1:
            raise ValueError(f"{__class__.__name__}.caller_infos::Caller stack is {len(stack)}, you skipped {skip} levels")

        parent_f = stack[start][0]

        self.package: str | None = None
        self.module: str | None = None

        module_info = inspect.getmodule(parent_f)
        if module_info:
            mod = module_info.__name__.split(".")
            self.package = mod[0]
            self.module = mod[1] if len(mod) > 1 else None

        self.cls: str | None = None
        if "self" in parent_f.f_locals:
            self.cls = parent_f.f_locals["self"].__class__.__name__

        self.function: str | None = None
        self.qualname: str | None = None
        if parent_f.f_code.co_name != '<module>':
            self.function = parent_f.f_code.co_name
            self.qualname = parent_f.f_code.co_qualname

        self.file: str = parent_f.f_code.co_filename
        self.line: int = parent_f.f_lineno

    # ****************************************************************
    # Methods

    @override
    def __str__(self) -> str:
        """
        Convert the current context into a string.

        Returns:
            str: A string representation of the context
        """

        return self.qualname or ""

    def to_dict(self) -> "ContextCallerProps":
        """
        Convert the current context into a dictionary.

        Returns:
            ContextCallerProps: A dictionary representation of the context
        """

        return {
            "package": self.package,
            "module": self.module,
            "cls": self.cls,
            "function": self.function,
            "qualname": self.qualname,
            "file": self.file,
            "line": self.line
        }

    # ****************************************************************
    # Static methods

