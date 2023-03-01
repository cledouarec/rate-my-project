# Rate my project

[![Lint](https://github.com/cledouarec/rate_my_project/actions/workflows/lint.yaml/badge.svg)](https://github.com/cledouarec/rate_my_project/actions/workflows/lint.yaml)
[![Unit tests](https://github.com/cledouarec/rate_my_project/actions/workflows/test.yaml/badge.svg)](https://github.com/cledouarec/rate_my_project/actions/workflows/test.yaml)

**Table of Contents**
* [Overview](#Overview)
* [Installation](#Installation)
* [Usage](#Usage)
* [Configuration](#Configuration)
    * [Server configuration](#Server-configuration)
    * [Project configuration](#Project-configuration)

## Overview

**rate my project** is a tool designed to help analyze and improve the
efficiency of a project and the team working on it. It does this by integrating
with Jira, a popular project management tool from Atlassian, to retrieve data
and statistics about the project's progress and the team's performance.

![Demo](https://github.com/cledouarec/rate_my_project/raw/main/examples/demo.png)

By collecting this data from Jira, **rate my project** can provide an objective
view of the project's status and help identify areas for improvement. This can
include metrics such as how long tasks take to complete, how many tasks are
being completed on time, and how much work is being done by each team member.

In addition to analyzing the data, **rate my project** also offers the ability
to produce reports in Confluence, another popular collaboration tool in
Atlassian suite. These reports can help visualize the data collected by
**rate my project** and communicate it to stakeholders, team members, and other
interested parties.

Overall, **rate my project** is a useful tool for project managers and team
leaders who want to improve their team's efficiency and effectiveness. By using
data to gain an objective view of the project's progress, they can make
informed decisions and take actions that lead to better outcomes.

## Installation

### From PyPI (Recommended)

You can install easily with the following command or insert into your
requirements file :
```
pip install rate-my-project
```

### From sources

It is recommended to use a virtual environment :
```
python -m venv venv
```
To install the module and the main script, simply do :
```
pip install .
```
For the developers, it is useful to install extra tools like :
* [pre-commit](https://pre-commit.com)
* [pytest](http://docs.pytest.org)
* [commitizen](https://commitizen-tools.github.io/commitizen/)

These tools can be installed with the following command :
```
pip install '.[dev]'
```
The Git hooks can be installed with :
```
pre-commit install
```
The hooks can be run manually at any time :
```
pre-commit run --all-file
```

## Usage

The full list of arguments supported can be displayed with the following
helper :
```
./rate_my_project -h
Usage: rate_my_project [OPTIONS] COMMAND [ARGS]...

  Swiss knife for measuring project efficiency.

Options:
  -v, --verbose  Enables verbose mode.
  -h, --help     Show this message and exit.

Commands:
  explore  Explore efficiency metrics with web interface from CONFIG file.
  report   Generate report from CONFIG file.

```

### Exploration mode

The first command is used to create a dynamic dashboard to explore the metrics.
The dashboard is a simple webapp which let the user entered a JQL query and 
interact with the results.

This mode can be started by executing the following command :
```
./rate_my_project explore my_config.yaml
```
The dashboard will be accessible at : http://127.0.0.1:8050

### Report mode

The second command is used to create a report on Confluence for every project
in the config file.
The objective of this mode is to automate the reporting after finding the 
right query in exploration mode.

This mode can be started by executing the following command :
```
./rate_my_project report my_config.yaml
```

## Configuration

The configuration file support 2 formats :
- [YAML format](https://yaml.org) (Recommended format)
- [JSON format](https://www.json.org)

In the configuration file, there are 3 main sections required :
- Server
- Fields
- Projects

Some fields could use double quotes to preserve space in their names. The YAML
syntax provides a solution by replacing with simple quote or escaping like
JSON :

**_In Yaml :_**
```yaml
JQL: 'project = "MY TEST"'
```
**_In Json :_**
```json
{
  "JQL": "project = \"MY TEST\""
}
```

### Server configuration

The `Server` node will configure the URL of the Jira and Confluence server.
The credentials could be defined with environment variables or `.env` file.
For the moment, only the username/token authentication is supported.

```
ATLASSIAN_USER=<your login>
ATLASSIAN_TOKEN=<your token>
```

**_In Yaml :_**
```yaml
Server:
  Jira: "https://my.jira.server.com"
  Confluence: "https://my.confluence.server.com"
```
**_In Json :_**
```json
{
  "Server": {
    "Jira": "https://my.jira.server.com",
    "Confluence": "https://my.confluence.server.com"
  }
}
```

| Attribute  | Required | Description                                      |
|------------|:--------:|--------------------------------------------------|
| Server     |    ✅     | Main configuration node for server.              |
| Jira       |    ✅     | Jira server URL to retrieve tickets information. |
| Confluence |    ✅     | Confluence server URL to publish the report      |

### Fields configuration

The `Fields` node will configure the field name to use since it could be custom
fields.

**_In Yaml :_**
```yaml
Fields:
  Sprint: "customfield_10001"
  Story points: "customfield_10002"
```
**_In Json :_**
```json
{
  "Fields": {
    "Sprint": "customfield_10001",
    "Story points": "customfield_10002"
  }
}
```

| Attribute    | Required | Description                                                    |
|--------------|:--------:|----------------------------------------------------------------|
| Fields       |    ✅     | Main configuration node for fields.                            |
| Sprint       |    ✅     | Field to store the current sprint                              |
| Story points |    ✅     | Field to store the estimation in story points of a development |

### Project configuration

The `Projects` node will provide the configuration for each project.

**_In Yaml :_**
```yaml
Projects:
  <Project name>:
    JQL: "project = TEST"
    Report:
      Space: "SPACE"
      Parent page: "My Parent Page"
```
**_In Json :_**
```json
{
  "Projects": {
    "<Project name>": {
      "JQL": "project = TEST",
      "Report": {
        "Space": "SPACE",
        "Parent page": "My Parent Page"
      }
    }
  }
}
```

| Attribute        | Required | Description                                                                                                                           |
|------------------|:--------:|---------------------------------------------------------------------------------------------------------------------------------------|
| Projects         |    ✅     | Main configuration node for all projects.                                                                                             |
| \<Project name\> |    ✅     | Must be replaced by the name of the project.<br/>This name will be used as a title of the report.                                     |
| JQL              |    ✅     | [JQL](https://www.atlassian.com/blog/jira-software/jql-the-most-flexible-way-to-search-jira-14) query to retrieve the list of tickets |
| Report           |    ✅     | Configuration node for all attributes related to report generation                                                                    |
| Space            |    ✅     | Confluence destination space.<br/>                                                                                                    |
| Parent page      |    ✅     | Confluence parent page of the report page.                                                                                            |
| Template         |    ❌     | Path to Jinja2 template used to produce the report page.                                                                              |
