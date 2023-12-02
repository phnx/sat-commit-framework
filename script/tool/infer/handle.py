import json
from typing import List
import pathlib
import os

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
        return True

    def get_supported_languages(self) -> list:
        return ["C", "C++"]

    def get_result_location(self) -> str:
        pass

    def count_result(self, output_filename: str) -> int:
        try:
            report_path = f"../output/{output_filename}/report.json"
            with open(report_path) as report_file:
                report = json.load(report_file)
                return len(report)

        except Exception:
            # in any cases of failure - flag down the execution
            return -1

    def get_pre_analysis_commands(self) -> list:
        # these commands are to be called inside subject folder
        return [["bash", "../script/tool/pre-compile.sh"]]

    def does_analysis_use_shell(self) -> bool:
        return False

    def get_analysis_commands(self, output_filename: str) -> list:
        # these commands are to be called inside subject folder
        return [
            [
                "infer",
                "-j",
                "1",  # tested on Apple M1 host, only #job=1 works
                "-o",
                f"../output/{output_filename}",
                "run",
                # "--annotation-reachability",  # NOTE non-default checker
                # "--bufferoverrun",  # NOTE non-default checker
                # "--bo-field-depth-limit",  # NOTE prevent OOM, cont.
                # "3",  # NOTE prevent OOM
                # "--loop-hoisting",  # NOTE non-default checker
                # "--pulse",  # NOTE non-default checker
                # "--quandary",  # NOTE non-default checker
                "--",
                "make",
                "-i",
            ]
        ]

    def get_expected_analysis_commands_return_codes(self) -> list:
        return []

    def get_post_analysis_commands(self, output_filename: str) -> list:
        # these commands are to be called inside subject folder
        return [
            [
                "rm",
                f"../output/{output_filename}/results.db",
            ]
        ]

    def get_transaction_result(self, output_filename: str) -> List[SATResult]:
        # TODO update target trial result location when analyzing data
        try:
            report_path = f"../output/infer-trial3/{output_filename}/report.json"

            # lookup warning_rule_id mapping file
            weakness_mapping_path = (
                pathlib.Path(__file__).parent.resolve() / "weakness-mapping.json"
            )
            weakness_mapping = {}
            if os.path.isfile(weakness_mapping_path):
                mapping_file = open(weakness_mapping_path)
                weakness_mapping = json.load(mapping_file)
                mapping_file.close()

            # severity mapping
            severity_level = {
                "info": "LOW",
                "like": "LOW",
                "advice": "MEDIUM",
                "warning": "MEDIUM",
                "error": "HIGH",
            }

            with open(report_path) as report_file:
                report = json.load(report_file)

                standard_results = []
                for result in report:
                    # standardize tool's result
                    weakness_rule_id = ""
                    if result["bug_type"] in weakness_mapping.keys():
                        weakness_rule_id = ",".join(
                            weakness_mapping[result["bug_type"]]
                        )
                    else:
                        print("unmapped weakness:", result["bug_type"])

                    standard_result = SATResult(
                        location_hash=result["key"],
                        location_file=result["file"],
                        location_start_line=result["line"],
                        location_start_column=result["column"],
                        location_end_line=result["line"],
                        location_end_column=result["column"],
                        warning_rule_id=result["bug_type"],
                        warning_rule_name=result["bug_type_hum"],
                        warning_message=result["qualifier"],
                        warning_weakness=weakness_rule_id,
                        warning_severity=severity_level[
                            str(result["severity"]).lower()
                        ],  # convert info, like, advice, warning, error to HIGH, MEDIUM, LOW
                    )

                    standard_results.append(standard_result)

                return standard_results

        except Exception as ex:
            # in any cases of failure - flag down the execution
            print("infer handle exception", str(ex))
            return []
