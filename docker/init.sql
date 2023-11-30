-- tool results
CREATE TABLE execution_log (
    id SERIAL PRIMARY KEY,

    trial_name varchar(255) NOT NULL,
    project varchar(255) NOT NULL,
    tool varchar(255) NOT NULL,
    tool_type varchar(255) NOT NULL,
    commit_sha varchar(255) NOT NULL,
    parent_commit_sha text,
    is_parent_commit boolean NOT NULL DEFAULT FALSE,
    result_location text,
    result_count integer NOT NULL DEFAULT 0,
    execution_status varchar(255),

    start_time timestamp,
    end_time timestamp,
    
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- extracted changes in vcc and fixing commits at file / function / and line level
-- to be used to create `relevant_vcc_changed_lines`
CREATE TABLE commit_changes (
    id SERIAL PRIMARY KEY,

    project varchar(255) NOT NULL,
    commit_sha varchar(255) NOT NULL,
    commit_type varchar(40) NOT NULL,
    
    file_name text NOT NULL,
    file_nloc integer NOT NULL DEFAULT -1,
    function_name text  NOT NULL,
    function_nloc integer NOT NULL DEFAULT -1,
    function_start_line integer NOT NULL DEFAULT -1,
    function_end_line integer NOT NULL DEFAULT -1,
    line_number integer NOT NULL DEFAULT -1,
    line_content text,

    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);

-- relevant changes in vcc, compared to fixing commits
CREATE TABLE relevant_vcc_changes (
    id SERIAL PRIMARY KEY,

    project varchar(255) NOT NULL,
    cve varchar(255) NOT NULL,
    commit_sha varchar(255) NOT NULL,
    fixing_commit_sha varchar(255) NOT NULL,
    
    is_vcc_blamed  boolean NOT NULL DEFAULT FALSE,
    is_changed_file_match boolean NOT NULL DEFAULT FALSE,
    is_changed_function_match boolean NOT NULL DEFAULT FALSE,
    is_changed_line_match boolean NOT NULL DEFAULT FALSE,

    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);
