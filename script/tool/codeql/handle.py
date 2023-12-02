from sarif import loader
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
        return True

    def get_supported_languages(self) -> list:
        return ["C", "C++"]

    def get_result_location(self) -> str:
        pass

    def count_result(self, output_filename: str) -> list:
        try:
            result = loader.load_sarif_file(f"../output/{output_filename}.sarif")
            return result.get_result_count()

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
                "codeql",
                "database",
                "create",
                "../temp",
                "--language=cpp",
                "--command=make -j1 -i",
                "--source-root=./",
                # "--threads=16",
                # "--ram=65536",
            ],
            [
                "codeql",
                "database",
                "analyze",
                # "--threads=16",
                # "--ram=65536",
                "--format=sarif-latest",
                f"--output=../output/{output_filename}.sarif",
                "../temp",
                "codeql/cpp-queries:codeql-suites/cpp-lgtm-full.qls",
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
            result = loader.load_sarif_file(
                f"../output/codeql-trial4/{output_filename}.sarif"
            )

            raw_results = result.get_results()

            rules = result.data["runs"][0]["tool"]["driver"]["rules"]
            rule_name = {r["id"]: r["shortDescription"]["text"] for r in rules}
            rule_weaknesses = {
                r["id"]: ",".join(
                    [
                        (t.split("/")[-1]).upper()
                        for t in r["properties"]["tags"]
                        if "/cwe/" in t
                    ]
                )
                for r in rules
            }
            rule_severity = {r["id"]: r["defaultConfiguration"]["level"] for r in rules}

            # severity mapping
            severity_level = {
                "error": "HIGH",
                "warning": "MEDIUM",
                "note": "LOW",
            }

            standard_results = []
            for result in raw_results:
                # standardize tool's result
                # get right results from SARIF - ensure that columns exist
                start_line = (
                    result["locations"][0]["physicalLocation"]
                    .get("region", {})
                    .get("startLine", -1)
                )

                start_column = (
                    result["locations"][0]["physicalLocation"]
                    .get("region", {})
                    .get("startColumn", -1)
                )
                end_line = (
                    result["locations"][0]["physicalLocation"]
                    .get("region", {})
                    .get("endLine", -1)
                )
                end_column = (
                    result["locations"][0]["physicalLocation"]
                    .get("region", {})
                    .get("endColumn", -1)
                )

                standard_result = SATResult(
                    location_hash=result["partialFingerprints"][
                        "primaryLocationLineHash"
                    ],
                    location_file=result["locations"][0]["physicalLocation"][
                        "artifactLocation"
                    ]["uri"],
                    location_start_line=start_line,
                    location_start_column=start_column,
                    location_end_line=end_line,
                    location_end_column=end_column,
                    warning_rule_id=result["ruleId"],
                    warning_rule_name=rule_name[result["ruleId"]],
                    warning_message=result["message"]["text"],
                    warning_weakness=rule_weaknesses[result["ruleId"]],
                    warning_severity=severity_level[
                        str(rule_severity[result["ruleId"]]).lower()
                    ],  # convert error, warning, note to HIGH, MEDIUM, LOW
                )

                standard_results.append(standard_result)

            return standard_results

        except Exception as ex:
            # in any cases of failure - flag down the execution
            print("codeql handle exception", str(ex), result)
            return []
