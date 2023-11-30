from dataclasses import dataclass


@dataclass
class SATResult:
    location_hash: str
    location_file: str
    location_start_line: int
    location_start_column: int
    location_end_line: int
    location_end_column: int
    warning_rule_id: str
    warning_rule_name: str
    warning_message: str
    warning_weakness: str
    warning_severity: str

    def __init__(
        self,
        location_hash: str,
        location_file: str,
        location_start_line: int,
        location_start_column: int,
        location_end_line: int,
        location_end_column: int,
        warning_rule_id: str,
        warning_rule_name: str,
        warning_message: str,
        warning_weakness: str,
        warning_severity: str,
    ):
        self.location_hash = location_hash
        self.location_file = location_file
        self.location_start_line = location_start_line
        self.location_start_column = location_start_column
        self.location_end_line = location_end_line
        self.location_end_column = location_end_column
        self.warning_rule_id = warning_rule_id
        self.warning_rule_name = warning_rule_name
        self.warning_message = warning_message
        self.warning_weakness = warning_weakness
        self.warning_severity = warning_severity

    def __eq__(self, obj: object) -> bool:
        if not isinstance(obj, SATResult):
            return False

        # TODO - other comparision criteria e.g., weakness similarity, etc.
        return (
            self.location_hash == obj.location_hash
            and self.location_file == obj.location_file
            and self.warning_rule_id == obj.warning_rule_id
        )

    def __hash__(self) -> int:
        # TODO - other comparision criteria e.g., weakness similarity, etc.
        return hash(
            (self.location_hash, self.location_file, self.warning_rule_id)
        )

    def to_dict(self) -> dict:
        return {
            "location_hash": self.location_hash,
            "location_file": self.location_file,
            "location_start_line": self.location_start_line,
            "location_start_column": self.location_start_column,
            "location_end_line": self.location_end_line,
            "location_end_column": self.location_end_column,
            "warning_rule_id": self.warning_rule_id,
            "warning_rule_name": self.warning_rule_name,
            "warning_message": self.warning_message,
            "warning_weakness": self.warning_weakness,
            "warning_severity": self.warning_severity,
        }

    def __str__(self) -> str:
        return " ".join(
            [
                self.location_file,
                str(self.location_start_line),
                self.warning_weakness,
            ]
        )
