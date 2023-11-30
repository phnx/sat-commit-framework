from typing import List

import psycopg2
from psycopg2.extensions import connection, cursor

from tool.SATResult import SATResult
from util import _check_transaction_data


def connect_database(database: str = "auto_tool_investigation_db") -> any:
    conn = psycopg2.connect(
        host="localhost",
        port="5433",  # TODO switch port if needed
        database=database,
        user="postgres",
        password="password",
    )

    return conn, conn.cursor()


def find_execution_transaction(
    cur: cursor, trial_name: str, project: str, tool: str, commit_sha: str
) -> list:
    cur.execute(
        f"""
        SELECT * FROM execution_log 
        where 
        trial_name='{trial_name}' AND
        project='{project}' AND
        tool='{tool}' AND
        commit_sha='{commit_sha}';
    """
    )

    return cur.fetchall()


def add_execution_transaction(
    conn: connection,
    cur: cursor,
    transaction_data: dict,
) -> int:
    try:
        if _check_transaction_data(transaction_data=transaction_data):
            cur.execute(
                """
                INSERT INTO execution_log (
                    trial_name, project, tool, tool_type, 
                    commit_sha, parent_commit_sha, 
                    is_parent_commit, result_location, 
                    result_count, execution_status, 
                    start_time, end_time)
                VALUES (%(trial_name)s, %(project)s, %(tool)s, %(tool_type)s, 
                    %(commit_sha)s, %(parent_commit_sha)s, 
                    %(is_parent_commit)s, %(result_location)s,
                    %(result_count)s, %(execution_status)s,
                    %(start_time)s, %(end_time)s);
            """,
                transaction_data,
            )
            conn.commit()

            return True

    except (Exception, psycopg2.DatabaseError) as error:
        print(str(error))
        conn.rollback()

    return False


def get_execution_time(cur: cursor, trial_name: str):
    cur.execute(
        f"""
        select 
            trial_name,
            tool,
            project,
            commit_sha,
            execution_status,
            start_time,
            end_time,
            (end_time - start_time) as time_used
        from execution_log
        where 
            trial_name = '{trial_name}' 
            --- and execution_status = 'SUCCESS'
    """
    )

    column_names = [
        "trial_name",
        "tool",
        "project",
        "commit_sha",
        "execution_status",
        "start_time",
        "end_time",
        "time_used",
    ]

    named_results = []
    results = cur.fetchall()
    for result in results:
        d = dict.fromkeys(column_names)
        d.update(zip(column_names, result))
        named_results.append(d)

    return named_results
