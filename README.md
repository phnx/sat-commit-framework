# Automated Pipeline for Large-Scale Experiment of Static Analysis Tools (SATs) on Code Commits

## Overview
This automated pipeline is developed for facilitating the large-scale experiments of C/C++ Static Analysis Tools on the target set of open-source code commits (i.e., GitHub commits). 
The pipeline consists of two major parts: the central database and the runners. Each runner is responsible for running a experiment trial i.e., executing a selected SAT on a set of target commits and storing the warnings or reports in a folder on host machine. The central database collects the execution results (i.e., succcess, failed, checkedout_failed, or timeout) and start-end timestamps of each commit from each trial.

In the current version, five widely-used C/C++ SATs i.e., CodeChecker, CodeQL, Cppcheck, Flawfinder, and Infer are integrated. Users can freely added the new SATs of choice or modify the existing pipeline components by following the instructions in [this section](#pipeline-customization). Technically, this pipeline should also support SATs and target commits of other programming languages (including the commits hosted on other platforms) as long as the commit is accessible via a certain URL and the SATs can run on command-line. However, it has neither been implemented nor tested.

With this pipeline, user can conduct various SAT experiment trials on a set of target commits and gather the results for further analyses such as the effectiveness of SATs to detect security issues in the early development process. All elements of the pipeline operate in the Docker environment for portability and scalability. To modify the runner's resources such as allocated memory or CPU cores, see [this section](#configure-runner-resource). To run a trial, user must prepare the list of target commits as described in [this section](#prepare-target-commits-for-sat-trial). Then start the trial following the instructions in [this section](#start-a-trial). 

## Future Work
We aim to develop this pipeline into a complete end-to-end SAT benchmark for evaluating the performance of *SAT-under-test* on the target commits that contain certain issues. To do so, we are working toward accomplishing the following tasks. 
- Define a standard format for test oracle of the target commits i.e., a) buggy files, buggy functions, or buggy lines in target commits and b) expected issue types such as CWE number
- Implement an analysis extension to systematically analyze and compare the SAT performance from multople trials i.e., detection effectiveness and computation time
- Implement a reporting module that automatically translates and visualizes the analysis results

## Pipeline Workflow
```plaintext
Start Central Database --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------->
Start Runner 1 --                                                                                                                                             ^
                 \                                                                                                                                            |
                  --> Install SAT --                                                                                                                          |
                                    \                                                                                                                  Execution Result
                                     --> Read Target Commits & Loop --                                                                                        |
                                                                      \                                                                                       |
                                                                       --> Clone Project & Checkout Commit --                                                 |
                                                                                       ^                     \                                                |
                                                                                       |                      --> Pre-compiliation (if required) / Execute --> --> Store warning files output/[trial_name]
                                                                                       |                                                                                     |
                                                                                        --------------------------------------------------------------------------------------                
Start Runner 2 ....
```

## System Requirement
The pipeline was tested on MacOS 14.1.1 (M1 chip) and Ubuntu 20.04. Make sure that following software is installed and working properly:
- Docker Engine version 24.0.6 or newer
- Or Docker Desktop version 4.25.1 or newer (this includes Docker Engine)

The runner and central database use the following Docker base images:
- Runner: ubuntu:22.04
- Central Database: postgres (latest version)

## Start Central Database
The status of each execution is stored in the central PostgreSQL database. To start the central database container, run the following command in root folder:

```console
docker-compose -f docker/database.yml up -d
```

Note that the database is independent of the runners. It can support multiple runners in simultaneously. To view the executed transactions in database, use the following command to access `psql` console:

```console
sudo docker exec -it auto-tool-investigation-db psql -U postgres
```

Then, enter the default password for PostgreSQL database: `postgresql`; select the target database using the following command before running SQL queries.

```console
\c auto_tool_investigation_db
select * from execution_log;
```

## Prepare Target Commits for SAT Trial
The list of target code commits for SAT analysis stored in CVS file in following format.
```text
project,cve,cwe,hash
memcached/memcached,CVE-2010-1152,707,32f382b605b4565bddfae5c9d082af3bfd30cf02
php/php-src,CVE-2016-3132,"710,664",f0168baecfb27e104e46fe914e5b5b6507ba8214
```
Column definition:
1. **project**: GitHub project's identity e.g., git/git or php/php-src
2. **cve**: CVE number of the commit, can be a dummy value if not available
3. **cwe**: CWE number that shows the vulnerability of commit, can be a dummy value if not available
4. **hash**: a valid commit identification (commit sha) which can be checked out

The sample target commit input file can be found [here](./data-ref/test-selected-commit.csv).

## Start a Trial
In root directory, run the following command with four parameters:
```console
bash ./start-execution.sh [runner_type] [tool_name] [instance_name] [input_csv_in_data_ref_folder]
```

1. **runner_type**: select the type of runner that is suitable for the selected SAT. 
   1. `custom` runner has all the dependencies (See [this section](#manage-target-commit-dependency)) installed to support SAT that requires compilation of the test subject
   2. `clean` runner has only fundamental dependencies to run SATs that do not require the compilation
2. **tool_name**: a name of SAT integrated in the pipeline, by default five SATs are available: `codechecker`, `codeql`, `cppcheck`, `infer`, and `flawfinder`.
3. **instance_name**: a unique name that can identify the trial. This name will be used in central database and as the result folder.
4. **input_csv_in_data_ref_folder**: file name of a csv file in foler [`data-ref`](./data-ref/) (with .csv extension) that contain list of target commits (See [this section](#prepare-target-commits-for-sat-trial)).

The SAT warnings or outputs from each trial will be stored in folder `./output/[instance_name]`, in the original format that the tool produces which can be configured following the instructions in [this section](#customize-sat-execution).

To monitor the runner, use following command to print real-time logs:
```bash
docker container logs -f [instance_name]
```

## Pipeline Customization
The pipeline is designed for flexibility. User can modify various components of the pipeline to meet the specific requirements. 

### Configure Runner Resource
Allocated resources for the runner can be modified in [`start-execution.sh`](start-execution.sh) in the following command:
```bash
docker run -d --network=host \
    --cpus=4 \
    --name $INSTANCE_NAME \
    --log-driver json-file --log-opt max-size=5m --log-opt max-file=10 \
    ...
```

The available parameters can be seen [here](https://docs.docker.com/engine/reference/commandline/run/).

### Manage Target Commit Dependency
For the runner of type `custom` that supports SATs which compiles the target commits during execution, the required dependencies of the target commits must be installed in the container to enable the compilation process. These dependencies are listed in `Dockerfile` in the following location [`./script/tool/Dockerfile-Base`](./script/tool/Dockerfile-Base).
User can add or remove the dependencies in the following command:
```text
RUN apt-get -y update && \
    apt-get -y install --no-install-recommends sudo \
    apt-utils \
    build-essential \
    openssl \
    clang \
    clang-tidy \
    git \
    autoconf \
    libgnutls28-dev \
    ...
```

Delete docker containers (existing runners) and image; then, rebuild the image (or simply start the new trial) to let the change take effect.

### Target Commit Pre-Compilation Process
Currently, the pipeline only supports target commits that use [GNU Automake](https://www.gnu.org/software/automake/manual/automake.html) build process. For each commit, [`./script/tool/pre-compile.sh`](./script/tool/pre-compile.sh) is run prior to SAT execution if the selected SAT requires compilation in the execution process. This script can be modified to cover other build processes such as [cmake](https://cmake.org/cmake/help/latest/guide/tutorial/index.html) or [Bazel](https://bazel.build/).

### Modify Time Limit
All shell commands in pipeline are executed through function `run_command` in [./script/util.py](./script/util.py). Modify following condition to set the new time limit:
```python
run(..., timeout=60 * 60 * 5, ...)
```
By default, the time limit of a command is 5 hours. Note that the pre-compilation process may also cause a timeout failure if it takes longer time than the limit.

### Add New SATs
#### Prepare SAT Directory
The pipeline can recognize an integrated SAT by looking up the folders inside `./script/tool/`. The most convenient approach to add a new SAT is to duplicate the template folder [`./script/tool/sat_template`](script/tool/sat_template) and rename it for the new tool. Each SAT has two required components: `entrypoint.sh` (for installing the tool inside the runner and starting the pipeline) and `handle.py` (for pipeline interactions such as the execution commands and pre/post execution commands).

#### Prepare Runner Entrypoint
The *entrypoint script* is the first bash script executed inside the runner when the container is started. It is meant to prepare the SAT inside the container by installing the selected version of SAT in the runner and ensure that SAT can be launched from any paths. As the entrypoint is called by `start-execution.sh`, it should accept two parameters: 1) instance_name and 2) input_file. The sample structure of an entrypoint can be seen in [`./script/tool/sat_template/entrypoint.sh`](./script/tool/sat_template/entrypoint.sh).

#### Prepare Tool Handle
Tool handle manages how pipeline interacts with each tool. To streamline the interactions, each tool handle is the child class of [`script/tool/ToolClass.py`](./script/tool/ToolClass.py). See the following snippet for the docstrings of the mandatory functions.

```python
    def check_readiness(self) -> None:
        """
        Future work

        Params: None
        Returns: None
        """
        ...

    def get_tool_type(self) -> str:
        """
        Constant function to indicate the type of tool

        Params: None
        Returns: string "SAT"
        """
        ...

    def is_compilation_required(self) -> bool:
        """
        Inform pipeline whether the pre-analysis step is needed

        Params: None
        Returns: boolean
        """
        ...

    def get_supported_languages(self) -> list:
        """
        Tool's information on the supported languages

        Params: None
        Returns: list
        """
        ...

    def get_result_location(self) -> str:
        """
        Future work

        Params: None
        Returns: None
        """
        ...

    def count_result(self, output_filename: str) -> int:
        """
        Called after the execution to count the warnings on each commit for a quick execution summary

        Params: output_filename of the commit as specified by the pipeline
        Returns: integer
        """
        ...

    def get_pre_analysis_commands(self) -> list:
        """
        Mandatory commands that must be run before the actual SAT execution i.e., the pre-compilation script

        Params: None
        Returns: None
        """
        ...

    def does_analysis_use_shell(self) -> bool:
        """
        Passing Shell flag to python subprocess command https://docs.python.org/3/library/subprocess.html#subprocess.run

        Params: None
        Returns: bool
        """
        ...

    def get_analysis_commands(self, output_filename: str) -> list:
        """
        Main SAT execution commands, either single ot multiple sets of commands

        Params: output_filename of the commit as specified by the pipeline
        Returns: list
        """
        ...

    def get_expected_analysis_commands_return_codes(self) -> list:
        """
        Normally the successful execution should return code 0, but some SATs may return different returncodes

        Params: None
        Returns: list of returncodes that are considered successful for the command; when the list is empty, pipeline expects returncode 0
        """
        ...

    def get_post_analysis_commands(self, output_filename: str) -> list:
        """
        Final commands that should be run after the main SAT execution. For example, deleting the unnecessary outputs that may take up diskspace. Not that the pipeline already takes care of commit checkout process. This script should not manage the commit clean up.

        Params: output_filename of the commit as specified by the pipeline
        Returns: list
        """
        ...

    def get_transaction_result(self, output_filename: str) -> list:
        """
        Get the list of warnings in a common format, containing the essential information i.e., location_hash, location_file, location_start_line, location_start_column, location_end_line, location_end_column, warning_rule_id, warning_rule_name, warning_message, warning_weakness, and warning_severity. This function should read and extract information from the warning file and prepare SATResult objects with all necessary information, especially warning_weakness and warning_severity, mapped.

        Params: output_filename of the commit as specified by the pipeline
        Returns: list of objects in SATResult class
        """
        ...
```

When a new handle is created, it must be added to [`./script/tool/factory.py`](./script/tool/factory.py) so that the pipeline can initiate the tool handle correctly.

### Customize SAT Execution
The tool handle (`./script/tool/tool_name/handle.py`) controls parameters used in SAT execution, which are unique for different SATs. For instance, the build commands, the output format and location, and activated checking rules. These parameters of the existing tools can be modified. See the following examples:

Single step (Cppcheck):
```python
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
```

Multiple steps (CodeQL):
```python
def get_analysis_commands(self, output_filename: str) -> list:
        # these commands are to be called inside subject folder
        return [
            [
                "codeql",
                "database",
                "create",
                "../temp",
                "--language=cpp",
                "--command=make -j8 -i",    # create database with make command
                "--source-root=./",
                "--threads=16",
                "--ram=65536",
            ],
            [
                "codeql",
                "database",
                "analyze",
                "--threads=16",
                "--ram=65536",
                "--format=sarif-latest",    # set output format
                f"--output=../output/{output_filename}.sarif", 
                "../temp",
                "codeql/cpp-queries:codeql-suites/cpp-lgtm-full.qls",   # select query suite
            ],
        ]
```