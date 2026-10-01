# GitHub CLI / API Notes For `babysit-prs`

## Primary commands used

### PR metadata

- `gh pr view --json number,url,state,mergedAt,closedAt,headRefName,headRefOid,headRepository,headRepositoryOwner,mergeable,mergeStateStatus,reviewDecision`

### PR checks summary

- `gh pr checks --json name,state,bucket,link,workflow,event,startedAt,completedAt`

### Workflow runs for head SHA

- `gh api repos/{owner}/{repo}/actions/runs -X GET -f head_sha=<sha> -f per_page=100`

### Failed log inspection

- `gh run view <run-id> --json jobs,name,workflowName,conclusion,status,url,headSha`
- `gh run view <run-id> --log-failed`

### Retry failed jobs only

- `gh run rerun <run-id> --failed`

## Review-related endpoints

- Issue comments: `gh api repos/{owner}/{repo}/issues/<pr_number>/comments?per_page=100`
- Inline PR review comments: `gh api repos/{owner}/{repo}/pulls/<pr_number>/comments?per_page=100`
- Review submissions: `gh api repos/{owner}/{repo}/pulls/<pr_number>/reviews?per_page=100`
