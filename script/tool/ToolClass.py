from abc import ABC, abstractmethod


# abstract class for tool
class ToolClass(ABC):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def check_readiness(self) -> None:
        """
        Future work

        Params: None
        Returns: None
        """
        pass

    @abstractmethod
    def get_tool_type(self) -> str:
        """
        Constant function to indicate the type of tool

        Params: None
        Returns: string "SAT"
        """
        pass

    @abstractmethod
    def is_compilation_required(self) -> bool:
        """
        Inform pipeline whether the pre-analysis step is needed

        Params: None
        Returns: boolean
        """
        pass

    @abstractmethod
    def get_supported_languages(self) -> list:
        """
        Tool's information on the supported languages

        Params: None
        Returns: list
        """
        pass

    @abstractmethod
    def get_result_location(self) -> str:
        """
        Future work

        Params: None
        Returns: None
        """
        pass

    @abstractmethod
    def count_result(self, output_filename: str) -> int:
        """
        Called after the execution to count the warnings on each commit for a quick execution summary

        Params: output_filename of the commit as specified by the pipeline
        Returns: integer
        """
        pass

    @abstractmethod
    def get_pre_analysis_commands(self) -> list:
        """
        Mandatory commands that must be run before the actual SAT execution i.e., the pre-compilation script

        Params: None
        Returns: None
        """
        pass

    @abstractmethod
    def does_analysis_use_shell(self) -> bool:
        """
        Passing Shell flag to python subprocess command https://docs.python.org/3/library/subprocess.html#subprocess.run

        Params: None
        Returns: bool
        """
        pass

    @abstractmethod
    def get_analysis_commands(self, output_filename: str) -> list:
        """
        Main SAT execution commands, either single ot multiple sets of commands

        Params: output_filename of the commit as specified by the pipeline
        Returns: list
        """
        pass

    @abstractmethod
    def get_expected_analysis_commands_return_codes(self) -> list:
        """
        Normally the successful execution should return thecode 0, but some SATs may return different returncodes

        Params: None
        Returns: list of returncodes that are considered successful for the command, when the list is empty pipeline expects returncode 0
        """
        pass

    @abstractmethod
    def get_post_analysis_commands(self, output_filename: str) -> list:
        """
        Final commands that should be run after the main SAT execution. For example, deleting the unnecessary outputs that may take up diskspace. Not that the pipeline already takes care of commit checkout process. This script should not manage the commit clean up.

        Params: output_filename of the commit as specified by the pipeline
        Returns: list
        """
        pass

    @abstractmethod
    def get_transaction_result(self, output_filename: str) -> list:
        """
        Get the list of warnings in a common format, containing the essential information i.e., location_hash, location_file, location_start_line, location_start_column, location_end_line, location_end_column, warning_rule_id, warning_rule_name, warning_message, warning_weakness, and warning_severity. This function should read and extract information from the warning file and prepare SATResult objects with all necessary information, especially warning_weakness and warning_severity, mapped.

        Params: output_filename of the commit as specified by the pipeline
        Returns: list of objects in SATResult class
        """
        pass
