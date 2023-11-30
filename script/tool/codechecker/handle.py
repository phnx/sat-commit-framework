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

    def count_result(self, output_filename: str) -> list:
        try:
            report_path = f"../output/{output_filename}.json"
            with open(report_path) as report_file:
                report = json.load(report_file)
                return len(report["reports"])

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
                "CodeChecker",
                "check",
                "-j8",
                "--build",
                "make -j8 -i",
                "--enable-all",  # NOTE non-default checker
                "-o=./reports",
                "--clean",
            ],
            [
                "CodeChecker",
                "parse",
                "./reports",
                "--trim-path-prefix=/home/ubuntu/workspace/subject",
                "-e=json",
                f"-o=../output/{output_filename}.json",
            ],
        ]

    def get_expected_analysis_commands_return_codes(self) -> list:
        # for verifying status of subprocess.call(), leave blank for default--0
        # must have the same size as analysis commands
        return [2, 2]

    def get_post_analysis_commands(self, output_filename: str) -> list:
        # these commands are to be called inside subject folder
        return []

    def get_transaction_result(self, output_filename: str) -> List[SATResult]:
        # TODO update target trial result location when analyzing data
        try:
            report_path = f"../output/codechecker-trial4/{output_filename}.json"

            # lookup warning_rule_id mapping file
            weakness_mapping_path = (
                pathlib.Path(__file__).parent.resolve() / "weakness-mapping.json"
            )
            weakness_mapping = {}
            if os.path.isfile(weakness_mapping_path):
                mapping_file = open(weakness_mapping_path)
                weakness_mapping = json.load(mapping_file)
                mapping_file.close()

            with open(report_path) as report_file:
                report = json.load(report_file)

                standard_results = []
                for result in report["reports"]:
                    # standardize tool's result

                    weakness_rule_id = ""
                    if result["checker_name"] in weakness_mapping.keys():
                        weakness_rule_id = ",".join(
                            weakness_mapping[result["checker_name"]]
                        )
                    else:
                        print("unmapped weakness:", result["checker_name"])

                    # TODO map CodeChecker checker to weakness
                    standard_result = SATResult(
                        location_hash=result["report_hash"],
                        location_file=result["file"]["path"],
                        location_start_line=result["line"],
                        location_start_column=result["column"],
                        location_end_line=result["line"],
                        location_end_column=result["column"],
                        warning_rule_id=result["checker_name"],
                        warning_rule_name=result["checker_name"],
                        warning_message=result["message"],
                        warning_weakness=weakness_rule_id,
                        warning_severity=result["severity"],  # MEDIUM, HIGH, LOW
                    )

                    standard_results.append(standard_result)

                return standard_results

        except Exception as ex:
            # in any cases of failure - flag down the execution
            print("codechecker handle exception", str(ex), result)
            return []
