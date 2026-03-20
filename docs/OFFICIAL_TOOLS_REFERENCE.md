# GitLab Official Tools Reference

**Source**: [GitLab built_in_tool_definitions.rb](https://gitlab.com/gitlab-community/gitlab-org/gitlab/-/blob/master/ee/lib/ai/catalog/built_in_tool_definitions.rb)

This reference documents **all 89 official GitLab tools** available for agents. Only these tools can be used in agent YAML definitions—custom tools are not supported.

---

## ComplianceBot Tool Usage Summary

### ✅ ComplianceBot Scanner (`agents/compliance-scanner.yml`)
**Purpose**: Analyze MRs and pipelines for compliance signals

| Tool | Purpose | Required |
|------|---------|----------|
| `read_file` | Read individual files from repository | ✅ |
| `read_files` | Read multiple files in one operation | ✅ |

**Why these tools**: Scanner needs to read MR diffs and configuration files to detect auth changes, encryption configs, and dependency updates.

---

### ✅ ComplianceBot Mapper (`agents/compliance-mapper.yml`)
**Purpose**: Map findings to compliance framework controls

| Tool | Purpose | Required |
|------|---------|----------|
| `read_file` | Read framework control definitions | ✅ |
| `get_vulnerability_details` | Fetch detailed vulnerability info | ✅ |
| `list_vulnerabilities` | Get all vulnerabilities in project | ✅ |
| `get_issue` | Retrieve issue details | ✅ |
| `get_repository_file` | Get file from remote repository | ✅ |
| `gitlab_blob_search` | Search for code patterns | ✅ |

**Why these tools**: Mapper needs to analyze security findings and cross-reference them with compliance controls defined in framework JSON files.

---

### ✅ ComplianceBot Evidence Collector (`agents/evidence-collector.yml`)
**Purpose**: Collect and archive audit trail evidence

| Tool | Purpose | Required |
|------|---------|----------|
| `read_file` | Read file manifests | ✅ |
| `get_repository_file` | Retrieve repository files | ✅ |
| `list_project_audit_events` | Fetch project audit logs | ✅ |
| `list_group_audit_events` | Fetch group audit logs | ✅ |
| `gitlab_api_get` | Make REST API calls | ✅ |
| `gitlab_graphql` | Execute GraphQL queries | ✅ |

**Why these tools**: Evidence collector needs access to audit trails, MR approvals, pipeline results, and deployment records for compliance documentation.

---

### ✅ ComplianceBot Reporter (`agents/compliance-reporter.yml`)
**Purpose**: Generate audit-ready compliance reports

| Tool | Purpose | Required |
|------|---------|----------|
| `read_file` | Read evidence and findings | ✅ |
| `create_issue` | Create GitLab issue for findings | ✅ |
| `create_issue_note` | Post comments on issues | ✅ |
| `get_issue` | Retrieve issue details | ✅ |
| `list_issues` | List existing issues | ✅ |

**Why these tools**: Reporter needs to create issues, post comments, and link to existing issues for compliance findings communication.

---

## Complete Tool Reference (89 tools)

### 1. File & Repository Operations (14 tools)

| ID | Tool | Purpose |
|----|------|---------|
| 39 | `read_file` | Read contents of a single file |
| 52 | `read_files` | Read multiple files in one operation |
| 10 | `edit_file` | Edit an existing file |
| 47 | `create_file_with_contents` | Create a new file with content |
| 72 | `create_commit` | Create a commit with multiple file actions |
| 37 | `mkdir` | Create a new directory |
| 23 | `get_repository_file` | Get file contents from remote repository |
| 11 | `find_files` | Find files with names matching a pattern |
| 59 | `list_repository_tree` | List files and directories in repository |
| 3 | `run_git_command` | Run a git command in repository |
| 24 | `grep` | Search for text patterns in files |
| 29 | `list_dir` | List files in given directory |
| 40 | `run_command` | Run a bash command in working directory |
| 83 | `extract_lines_from_text` | Extract specific lines from text content |

### 2. Issue Operations (7 tools)

| ID | Tool | Purpose |
|----|------|---------|
| 6 | `create_issue` | Create a new issue in a project |
| 17 | `get_issue` | Get a single issue |
| 33 | `list_issues` | List issues in a project |
| 43 | `update_issue` | Update an existing issue |
| 7 | `create_issue_note` | Create a comment on an issue |
| 18 | `get_issue_note` | Get a single issue comment |
| 32 | `list_issue_notes` | Get all comments for an issue |

### 3. Merge Request Operations (9 tools)

| ID | Tool | Purpose |
|----|------|---------|
| 8 | `create_merge_request` | Create a new merge request |
| 20 | `get_merge_request` | Fetch merge request details |
| 44 | `update_merge_request` | Update an existing merge request |
| 9 | `create_merge_request_note` | Create a comment on a merge request |
| 27 | `list_all_merge_request_notes` | List all comments on an MR |
| 34 | `list_merge_request_diffs` | Fetch diffs of files changed in an MR |
| 89 | `get_merge_request_conflicts` | Get raw merge conflict content |
| 81 | `get_pipeline_failing_jobs` | Get IDs for failed jobs in a pipeline |
| 85 | `build_review_merge_request_context` | Build comprehensive MR context for code review |

### 4. Epic Operations (5 tools)

| ID | Tool | Purpose |
|----|------|---------|
| 5 | `create_epic` | Create a new epic in a group |
| 15 | `get_epic` | Get a single epic |
| 31 | `list_epics` | Get all epics in a group |
| 42 | `update_epic` | Update an existing epic |
| 16 | `get_epic_note` | Get a comment from an epic |

### 5. Work Item Operations (8 tools)

| ID | Tool | Purpose |
|----|------|---------|
| 53 | `get_work_item` | Get a single work item |
| 71 | `list_work_items` | List work items in project/group |
| 75 | `create_work_item` | Create a new work item |
| 70 | `update_work_item` | Update an existing work item |
| 60 | `create_work_item_note` | Create a comment on a work item |
| 74 | `get_work_item_notes` | Get all comments for a work item |
| 30 | `list_epic_notes` | Get all comments for an epic |
| 76 | `get_wiki_page` | Get a wiki page from a project/group |

### 6. Commit & History Operations (6 tools)

| ID | Tool | Purpose |
|----|------|---------|
| 12 | `get_commit` | Get a single commit from repository |
| 13 | `get_commit_comments` | Get comments on a specific commit |
| 14 | `get_commit_diff` | Get the diff of a specific commit |
| 28 | `list_commits` | List commits in a repository |
| 3 | `run_git_command` | Run a git command in repository |
| 72 | `create_commit` | Create a commit with file actions |

### 7. Security & Vulnerability Operations (13 tools)

| ID | Tool | Purpose |
|----|------|---------|
| 73 | `list_vulnerabilities` | List security vulnerabilities in a project |
| 67 | `get_vulnerability_details` | Get detailed info about a vulnerability |
| 68 | `dismiss_vulnerability` | Dismiss a security vulnerability |
| 69 | `confirm_vulnerability` | Confirm a security vulnerability |
| 62 | `update_vulnerability_severity` | Update severity of vulnerabilities |
| 57 | `revert_to_detected_vulnerability` | Revert vulnerability to 'detected' status |
| 51 | `create_vulnerability_issue` | Create GitLab issue linked to vulnerabilities |
| 65 | `link_vulnerability_to_issue` | Link an issue to security vulnerabilities |
| 80 | `link_vulnerability_to_merge_request` | Link vulnerability to a merge request |
| 84 | `list_security_findings` | List ephemeral findings from pipeline scan |
| 77 | `get_security_finding_details` | Get details for a specific security finding |
| 86 | `post_sast_fp_analysis_to_gitlab` | Post SAST false positive analysis |

### 8. Audit & Compliance Operations (3 tools)

| ID | Tool | Purpose |
|----|------|---------|
| 63 | `list_project_audit_events` | List audit events for a project |
| 64 | `list_group_audit_events` | List audit events for a group |
| 66 | `list_instance_audit_events` | List instance-level audit events |

### 9. Search Operations (14 tools)

| ID | Tool | Purpose |
|----|------|---------|
| 1 | `gitlab_blob_search` | Search for blobs (file content) in projects/groups |
| 25 | `gitlab_group_project_search` | Search for projects within a GitLab group |
| 26 | `gitlab_issue_search` | Search for issues in projects/groups |
| 35 | `gitlab_merge_request_search` | Search for merge requests in projects/groups |
| 36 | `gitlab_milestone_search` | Search for milestones in projects/groups |
| 38 | `gitlab_note_search` | Search for notes in GitLab projects |
| 45 | `gitlab__user_search` | Search for users in projects/groups |
| 46 | `gitlab_wiki_blob_search` | Search for wiki blobs in projects/groups |
| 48 | `gitlab_documentation_search` | Find GitLab documentation on features |
| 4 | `gitlab_commit_search` | Search for commits in projects/groups |
| 24 | `grep` | Search for text patterns in files |
| 11 | `find_files` | Find files with names matching a pattern |
| 88 | `run_glql_query` | Execute GLQL queries on work items, epics, MRs |

### 10. Pipeline & Job Operations (7 tools)

| ID | Tool | Purpose |
|----|------|---------|
| 19 | `get_job_logs` | Get the trace for a job |
| 21 | `get_pipeline_errors` | Get logs for failed jobs in latest pipeline |
| 81 | `get_pipeline_failing_jobs` | Get IDs for failed jobs in a pipeline |
| 2 | `ci_linter` | Validate CI/CD YAML configuration |
| 82 | `run_tests` | Execute test commands for any language |
| 86 | `post_sast_fp_analysis_to_gitlab` | Post SAST false positive analysis |
| 87 | `post_duo_code_review` | Post Duo Code Review to MR |

### 11. Workflow & Planning Operations (6 tools)

| ID | Tool | Purpose |
|----|------|---------|
| 50 | `add_new_task` | Add a task to a plan |
| 54 | `create_plan` | Create a list of tasks for a plan |
| 55 | `get_plan` | Fetch a list of tasks for a workflow |
| 61 | `remove_task` | Remove a task from a plan |
| 41 | `set_task_status` | Set the status of a task |
| 56 | `update_task_description` | Update description of a task |

### 12. API & System Operations (7 tools)

| ID | Tool | Purpose |
|----|------|---------|
| 78 | `gitlab_api_get` | Make read-only GET requests to GitLab REST API |
| 79 | `gitlab_graphql` | Execute read-only GraphQL queries |
| 40 | `run_command` | Run a bash command in working directory |
| 83 | `extract_lines_from_text` | Extract specific lines from text content |
| 49 | `get_current_user` | Get current user information |
| 58 | `get_previous_session_context` | Get context from a previously run session |
| 22 | `get_project` | Fetch details about a project |

---

## Important Notes

1. **Official Tools Only**: Only the 89 tools listed above can be used in agent definitions. Custom tools are not supported.

2. **Read-Only Operations**: All tools are read-only except where explicitly documented as write operations:
   - Write: `create_*`, `edit_file`, `update_*`, `delete_*`, `dismiss_vulnerability`, `confirm_vulnerability`, `revert_to_detected_vulnerability`, `add_new_task`, `remove_task`, `set_task_status`, `update_task_description`

3. **GraphQL Limitations**: GraphQL queries are limited to read-only operations; mutations are not supported.

4. **Tool Validation**: The ai-catalog-sync validator in GitLab CI/CD will reject any agent that uses tools outside this official list.

5. **ComplianceBot Compliance**: All tools used in ComplianceBot agents are officially supported and validated.

---

## How to Use This Reference

1. **Check Agent Tools**: Before modifying agent YAML files, verify that all tools are listed in this reference.
2. **Add New Functionality**: When adding features to agents, search this document for the appropriate tool.
3. **Validation**: Run `ACTION=validate node /tmp/ai-catalog-sync/index.js` in your CI/CD to validate agent YAML against official tools.
4. **Updates**: If tools are added or deprecated in GitLab, update this reference by fetching the latest from the official source.

---

## References

- [GitLab official built_in_tool_definitions.rb](https://gitlab.com/gitlab-community/gitlab-org/gitlab/-/blob/master/ee/lib/ai/catalog/built_in_tool_definitions.rb)
- [GitLab AI Catalog Documentation](https://docs.gitlab.com/ee/user/ai/ai_catalog.html)
- [ComplianceBot AGENTS.md](../AGENTS.md)
