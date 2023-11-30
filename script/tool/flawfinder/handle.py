from sarif import loader

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
            result = loader.load_sarif_file(f"../output/{output_filename}.sarif")
            return result.get_result_count()

        except Exception:
            # in any cases of failure - flag down the execution
            return -1

    def get_pre_analysis_commands(self) -> list:
        # these commands are to be called inside subject folder
        return []

    def does_analysis_use_shell(self) -> bool:
        return True

    def get_analysis_commands(self, output_filename: str) -> list:
        # these commands are to be called inside subject folder
        # Flawfinder uses shell pipe to store output file
        return [
            "python3 -u ../script/tool/flawfinder/convert_subject_encoding.py $PWD",
            f"flawfinder --sarif . > ../output/{output_filename}.sarif",
        ]

    def get_expected_analysis_commands_return_codes(self) -> list:
        return []

    def get_post_analysis_commands(self, output_filename: str) -> list:
        # these commands are to be called inside subject folder
        return []

    def get_transaction_result(self, output_filename: str) -> list:
        # TODO update target trial result location when analyzing data
        try:
            result = loader.load_sarif_file(
                f"../output/flawfinder-trial2/{output_filename}.sarif"
            )

            raw_results = result.get_results()

            # get rule for mappings
            rules = result.data["runs"][0]["tool"]["driver"]["rules"]
            rule_name = {r["id"]: r["name"] for r in rules}
            rule_weaknesses = {
                r["id"]: ",".join([w["target"]["id"] for w in r["relationships"]])
                for r in rules
            }

            # severity mapping
            severity_level = {
                "error": "HIGH",
                "warning": "MEDIUM",
                "note": "LOW",
            }

            standard_results = []
            for result in raw_results:
                # standardize tool's result

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

                # flawfinder artifactLocation url starts with './'
                standard_result = SATResult(
                    location_hash=result["fingerprints"]["contextHash/v1"],
                    location_file=result["locations"][0]["physicalLocation"][
                        "artifactLocation"
                    ]["uri"].lstrip("./"),
                    location_start_line=start_line,
                    location_start_column=start_column,
                    location_end_line=end_line,
                    location_end_column=end_column,
                    warning_rule_id=result["ruleId"],
                    warning_rule_name=rule_name[result["ruleId"]],
                    warning_message=result["message"]["text"],
                    warning_weakness=rule_weaknesses[result["ruleId"]],
                    warning_severity=severity_level[
                        str(result["level"]).lower()
                    ],  # convert error, warning, note to HIGH, MEDIUM, LOW
                )

                standard_results.append(standard_result)

            return standard_results

        except Exception as ex:
            # in any cases of failure - flag down the execution
            print("flawfinder handle exception", str(ex), result)
            return []
