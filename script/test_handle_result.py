from tool.factory import get_tool_handle
import util

tool_handle = get_tool_handle("codeql")
project = "neomutt/neomutt"
commit_sha = "41b5f7640f7a5ac84b4893ad4cb09d4f96e42e06"

output_filename = util.get_output_filename(
    project=project, commit_sha=commit_sha
)

warnings = tool_handle.get_transaction_result(output_filename=output_filename)
