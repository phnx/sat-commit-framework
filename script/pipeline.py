# main pipeline / orchestrate tools and data
import os
import sys
import shutil
from datetime import datetime, timezone

import pandas as pd
from git import Repo

import util
import db_util
from tool.ToolClass import ToolClass
from tool.factory import get_tool_handle

test_sampling_size = 10


def verify_tool(tool: str) -> bool:
    available_tools = [
        d[0].split("/")[2] for d in os.walk("./tool") if len(d[0].split("/")) > 2
    ]

    return tool in available_tools


def checkout_target_commit(commit: str) -> bool:
    # TODO add delay before checkout - prevent untracked changes in large project
    repo = Repo("../subject")

    try:
        repo.git.checkout(commit)
        return True

    except Exception:
        print("error while checking out commit")
        return False


def get_local_repo_commit_parents(commit: str) -> list:
    repo = Repo("../subject")

    # ensure head commit
    assert repo.head.commit.hexsha == commit

    # return parent commits
    return [commit.hexsha for commit in repo.head.commit.parents]


# reset discard all changes - but keep subject repository
def reset_local_repository():
    repo = Repo("../subject")
    repo.git.reset("--hard")
    repo.git.clean("-xdf")


def _clean_path(root_path: str) -> None:
    if os.path.exists(root_path):
        for files in os.listdir(root_path):
            path = os.path.join(root_path, files)
            try:
                shutil.rmtree(path)
            except OSError:
                os.remove(path)


# use before cloning new project
def clean_local_repository() -> None:
    _clean_path(root_path="../subject")


# clean temporary directory (e.g., tool database)
def clean_temp_folder() -> None:
    _clean_path(root_path="../temp")


# clone new project tree
def clone_project(gh_repo: str) -> None:
    try:
        Repo.clone_from(
            gh_repo,
            "../subject/",
        )
        return True
    except Exception:
        # clone error, repository no longer exists
        return False


def analyze_commit(
    conn,
    cur,
    trial_name: str,
    project: str,
    commit_sha: str,
    parent_commits: list,
    tool: str,
    tool_handle: ToolClass,
    is_vcc_parent: bool = False,
    test: bool = True,
) -> None:
    clean_temp_folder()

    # switch to subject folder
    os.chdir("../subject")

    # state execution status
    execution_status = "SUCCESS"

    output_filename = util.get_output_filename(project=project, commit_sha=commit_sha)

    start_time = datetime.now(timezone.utc)

    # SAT flow
    if tool_handle.get_tool_type() == "SAT":
        # time.sleep(5)
        if tool_handle.is_compilation_required():
            compile_commands = tool_handle.get_pre_analysis_commands()
            for command in compile_commands:
                util.run_command(command)

        # run tool
        analysis_commands = tool_handle.get_analysis_commands(
            output_filename=output_filename
        )
        shell_execution = tool_handle.does_analysis_use_shell()
        expected_analysis_commands_return_codes = (
            tool_handle.get_expected_analysis_commands_return_codes()
        )

        print("analysis:", analysis_commands)
        for i, command in enumerate(analysis_commands):
            print("analysis step:", command)

            expected_return_code = 0
            if len(expected_analysis_commands_return_codes) > 0:
                expected_return_code = expected_analysis_commands_return_codes[i]

            run_result, result_text = util.run_command(
                command,
                shell_execution=shell_execution,
                expected_return_code=expected_return_code,
            )

            if not run_result:
                print("analysis failed in subprocess call", commit_sha)
                execution_status = result_text
                break

        post_analysis_commands = tool_handle.get_post_analysis_commands(
            output_filename=output_filename
        )

        if len(post_analysis_commands) > 0:
            print("post analysis:", post_analysis_commands)
            for command in post_analysis_commands:
                run_result, _ = util.run_command(
                    command, shell_execution=shell_execution
                )

    end_time = datetime.now(timezone.utc)

    output_result_counts = tool_handle.count_result(output_filename=output_filename)

    if not test:
        # register transaction log - VCC & parent
        db_util.add_execution_transaction(
            conn=conn,
            cur=cur,
            transaction_data={
                "trial_name": trial_name,
                "project": project,
                "tool": tool,
                "tool_type": tool_handle.get_tool_type(),
                "commit_sha": commit_sha,
                "parent_commit_sha": ",".join(parent_commits),
                "is_parent_commit": is_vcc_parent,
                "result_location": "TODO",
                "result_count": output_result_counts,
                "execution_status": execution_status,
                "start_time": start_time,
                "end_time": end_time,
            },
        )

    # return to script folder
    os.chdir("../script")


# execute tool on a selected subject
def execute(
    tool: str,
    trial_name: str,
    input_file_name: str = "",
    test: bool = True,
) -> None:
    print(f"Execute: {tool}")

    selected_vcc_df = pd.DataFrame()

    print(f"input_file_name: {input_file_name}")

    # get selected_vcc
    selected_vcc_df = util.get_selected_vcc_from_file_df(
        input_file_name=input_file_name
    )
    print(f"target commits: {selected_vcc_df.shape[0]}")

    conn = None
    cur = None
    if not test:
        # transaction database
        conn, cur = db_util.connect_database()

    # initiate tool handle
    tool_handle = get_tool_handle(name=tool)
    print(f"Initiate tool handle: {tool_handle.get_tool_type()}")

    # PART 1 - run tool, iterate through commits
    previous_project = ""
    for _, vcc in selected_vcc_df.iterrows():
        project = vcc["project"].lower()

        if project != previous_project:
            print("new project, clone repository")
            # clean repository before project switching
            clean_local_repository()

            # clone new repository
            repo_url = "/".join(["https://github.com", project])
            clone_project(gh_repo=repo_url)

            previous_project = project

        print(f"Assess VCC: {vcc['cve']}, {vcc['cwe']}, {vcc['hash']}")

        if vcc["hash"].strip() == "":
            print("invalid commit sha, skip")
            continue

        commit_sha = vcc["hash"].strip()

        existing_transaction = []

        if not test:
            # check transaction log of commit - tool
            existing_transaction = db_util.find_execution_transaction(
                cur=cur,
                trial_name=trial_name,
                project=project,
                tool=tool,
                commit_sha=commit_sha,
            )

        # get vcc
        if len(existing_transaction) != 0:
            print("already analyzed commit, skip")
            continue

        parent_commits = []
        # new vcc
        print("running analysis")

        # reset repository - pre-cleanup
        reset_local_repository()

        # checkout target commit, get parent commits
        if checkout_target_commit(commit=commit_sha):
            parent_commits = get_local_repo_commit_parents(commit=commit_sha)

            # analyze vcc
            analyze_commit(
                conn,
                cur,
                trial_name=trial_name,
                project=project,
                commit_sha=commit_sha,
                parent_commits=parent_commits,
                tool=tool,
                tool_handle=tool_handle,
                is_vcc_parent=False,
                test=test,
            )

            # reset repository - post-cleanup
            reset_local_repository()

        else:
            # record failed checkout
            if not test:
                db_util.add_execution_transaction(
                    conn=conn,
                    cur=cur,
                    transaction_data={
                        "trial_name": trial_name,
                        "project": project,
                        "tool": tool,
                        "tool_type": tool_handle.get_tool_type(),
                        "commit_sha": commit_sha,
                        "parent_commit_sha": "",
                        "is_parent_commit": False,
                        "result_location": "TODO",
                        "result_count": -1,
                        "execution_status": "CHECKOUT_FAILED",
                        "start_time": None,
                        "end_time": None,
                    },
                )


# accept parameters to select tool, unique trial_name,
# [optional: input_file_name (in ../data-ref)]
if __name__ == "__main__":
    args = sys.argv[1:]

    tool = args[0]
    trial_name = None
    input_file_name = ""
    use_database = ""

    if len(args) > 1:
        trial_name = args[1]

    if len(args) > 2:
        input_file_name = args[2]

    if len(args) > 3:
        use_database = args[3]

    # verify tool
    if not verify_tool(tool=tool):
        sys.exit("selected tool does not exist")

    test = True
    if use_database == "yes":
        test = False

    # tool execution
    execute(
        tool=tool,
        trial_name=trial_name,
        input_file_name=input_file_name,
        test=test,
    )
