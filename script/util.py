import typing
import os
from subprocess import run, TimeoutExpired

import clang.cindex
import lizard

import pandas as pd


def _is_c_or_cpp_file(filename: str):
    # Extract the file extension
    _, extension = os.path.splitext(filename)

    return extension.lower() in [
        ".c",
        ".cpp",
        ".cxx",
        ".cc",
        ".c++",
        ".h",
        ".hpp",
        ".hxx",
        ".hh",
        ".inl",
        ".cu",
        ".cuh",
    ]


def get_selected_vcc_from_file_df(input_file_name: str) -> pd.DataFrame:
    commit_df = pd.read_csv(f"../data-ref/{input_file_name}")

    return commit_df


def get_output_filename(project: str, commit_sha: str) -> str:
    project_name = project.replace("/", "-")
    return f"{project_name}-{commit_sha}"


def _check_transaction_data(transaction_data: dict) -> bool:
    try:
        assert "trial_name" in transaction_data
        assert "project" in transaction_data
        assert "tool" in transaction_data
        assert "tool_type" in transaction_data
        assert "commit_sha" in transaction_data
        assert "parent_commit_sha" in transaction_data
        assert "is_parent_commit" in transaction_data
        assert "result_location" in transaction_data
        assert "result_count" in transaction_data
        assert "execution_status" in transaction_data
        assert "start_time" in transaction_data
        assert "end_time" in transaction_data

        return True

    except Exception:
        return False


def run_command(
    command: typing.Union[str, list],
    shell_execution: bool = False,
    expected_return_code: int = 0,
) -> (bool, str):
    result = "SUCCESS"
    try:
        # allow maximum 5hr to execute a command
        # up to 5hr only for cppcheck
        if (
            run(command, timeout=60 * 60 * 5, shell=shell_execution).returncode
            == expected_return_code
        ):
            return (True, result)

        result = "FAILED"

    except TimeoutExpired:
        print("subprocess timeout, execution failed")
        result = "TIMEOUT"
        pass
    except Exception as ex:
        # in any failures, return false
        print(str(ex))
        result = "EXCEPTION"
        pass

    return (False, result)
