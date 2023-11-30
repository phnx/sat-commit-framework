from .ToolClass import ToolClass
from .codechecker import handle as codechecker_handle
from .codeql import handle as codeql_handle
from .cppcheck import handle as cppcheck_handle
from .flawfinder import handle as flawfinder_handle
from .infer import handle as infer_handle


def get_tool_handle(name: str) -> ToolClass:
    if name == "codechecker":
        return codechecker_handle.handle()

    elif name == "codeql":
        return codeql_handle.handle()

    elif name == "cppcheck":
        return cppcheck_handle.handle()

    elif name == "flawfinder":
        return flawfinder_handle.handle()

    elif name == "infer":
        return infer_handle.handle()

    # TODO define other handles
