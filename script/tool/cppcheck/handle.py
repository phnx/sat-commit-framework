from xml.dom.minidom import parseString, Element
from typing import List

from ..ToolClass import ToolClass
from ..SATResult import SATResult


class handle(ToolClass):
    def __init__(self) -> None:
        super().__init__()

    def check_readiness(self) -> None:
        pass

    def get_tool_type(self) -> str:
        return "SAT"

    def is_compilation_required(self) -> bool:
        return False

    def get_supported_languages(self) -> list:
        return ["C", "C++"]

    def get_result_location(self) -> str:
        pass

    def count_result(self, output_filename: str) -> int:
        try:
            output_file = open(f"../output/{output_filename}.xml", "r")
            result = output_file.read()
            output_file.close()
            errors = parseString(result)

            return len(errors.getElementsByTagName("error"))

        except Exception:
            # in any cases of failure - flag down the execution
            return -1

    def get_pre_analysis_commands(self) -> list:
        # these commands are to be called inside subject folder
        return []

    def does_analysis_use_shell(self) -> bool:
        return False

    def get_analysis_commands(self, output_filename: str) -> list:
        # these commands are to be called inside subject folder
        return [
            [
                "cppcheck",
                "-j 8",
                ".",
                "--xml",
                f"--output-file=../output/{output_filename}.xml",
            ],
        ]

    def get_expected_analysis_commands_return_codes(self) -> list:
        return []

    def get_post_analysis_commands(self, output_filename: str) -> list:
        # these commands are to be called inside subject folder
        return []

    def get_transaction_result(self, output_filename: str) -> List[SATResult]:
        # TODO update target trial result location when analyzing data
        try:
            output_file = open(f"../output/cppcheck-trial1b/{output_filename}.xml", "r")
            results = output_file.read()
            output_file.close()

            errors = parseString(results).getElementsByTagName("error")

            # severity mapping
            severity_level = {
                "none": "LOW",
                "style": "LOW",
                "portability": "LOW",
                "information": "LOW",
                "debug": "LOW",
                "performance": "LOW",
                "warning": "MEDIUM",
                "error": "HIGH",
            }

            standard_results = []
            for result in errors:
                # standardize tool's result

                standard_result = SATResult(
                    location_hash=result.getAttribute("file0"),
                    location_file=result.getAttribute("file0"),
                    location_start_line=result.getElementsByTagName("location")[
                        0
                    ].getAttribute("line"),
                    location_start_column=result.getElementsByTagName("location")[
                        0
                    ].getAttribute("column"),
                    location_end_line=result.getElementsByTagName("location")[
                        0
                    ].getAttribute("line"),
                    location_end_column=result.getElementsByTagName("location")[
                        0
                    ].getAttribute("column"),
                    warning_rule_id=result.getAttribute("id"),
                    warning_rule_name=result.getAttribute("msg"),
                    warning_message=result.getAttribute("verbose"),
                    warning_weakness=(
                        ("CWE-" + result.getAttribute("cwe"))
                        if result.getAttribute("cwe") != ""
                        else ""
                    )
                    if result.getAttribute("id") != ""
                    else "",
                    warning_severity=severity_level[
                        str(result.getAttribute("severity")).lower()
                    ],  # convert none, error, warning, style, performance, portability, information, debug to HIGH, MEDIUM, LOW
                )

                standard_results.append(standard_result)

            return standard_results

        except Exception as ex:
            # in any cases of failure - flag down the execution
            print("cppcheck handle exception", str(ex))
            return []
