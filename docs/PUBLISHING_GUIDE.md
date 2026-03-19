# ComplianceBot: Publishing Agents to GitLab AI Catalog

## Overview

This guide walks you through publishing your ComplianceBot agents and flow to the GitLab AI Catalog from VS Code. This is **required** for hackathon submission.

---

## Prerequisites

✅ **Completed Before Starting:**
- All 4 agents created (`.gitlab/agents/*.yaml`)
- Flow orchestration created (`.gitlab/flows/compliance-flow.yaml`)
- Repository pushed to GitLab AI Hackathon group
- GitLab PAT token with `api`, `read_api`, `write_repository` scopes
- GitLab extension installed in VS Code

---

## Step 1: Set Up GitLab PAT Extension in VS Code

### 1.1 Install GitLab Extension (if not already installed)
```
1. Press Ctrl+Shift+X (or Cmd+Shift+X on Mac)
2. Search for "GitLab" 
3. Install "GitLab Workflow" by GitLab
4. Reload VS Code
```

### 1.2 Create GitLab Personal Access Token
**In GitLab Web UI:**
```
1. Go to gitlab.com
2. Click your profile icon (top right) → Settings
3. Left sidebar → Access Tokens
4. Click "Add new token"
5. Fill in:
   - Name: "ComplianceBot-VSCode-PAT"
   - Scopes: ✅ api, ✅ read_api, ✅ write_repository
   - Expiry: 30 days minimum (for hackathon duration)
6. Click "Create personal access token"
7. COPY the token (you won't see it again!)
```

### 1.3 Configure PAT in VS Code
```
1. Press Ctrl+Shift+P (or Cmd+Shift+P on Mac)
2. Type: "GitLab: Add GitLab Instance"
3. Enter your instance: https://gitlab.com
4. Paste the PAT token when prompted
5. VS Code will verify the connection
```

### 1.4 Verify Setup
```
1. Press Ctrl+Shift+P
2. Type: "GitLab: Connect"
3. You should see your GitLab username and current project
```

---

## Step 2: Prepare Repository for AI Catalog

### 2.1 Ensure Files are Committed
Before publishing, commit all agent and flow files:

```bash
cd c:\Users\omana\Projects\compliancebot-gitlab-hackathon

# Check git status
git status

# Stage all changes
git add .

# Commit with message
git commit -m "feat: prepare agents and flow for AI Catalog publication"

# Push to GitLab
git push origin main
```

### 2.2 Verify Repository is Public
```
In GitLab Web UI:
1. Go to https://gitlab.com/gitlab-ai-hackathon/YOUR-PROJECT-NAME
2. Click Settings → General
3. Scroll to Visibility
4. Ensure "Public" is selected (not Private/Internal)
5. Click Save
```

### 2.3 Verify MIT License is Visible
```
1. Go to project homepage
2. Check that LICENSE file is visible in repo root
3. GitLab should show "MIT" badge on project page
```

---

## Step 3: Enable Duo Agent Platform in Project

### 3.1 Enable in GitLab Web UI
```
1. Go to your project: https://gitlab.com/gitlab-ai-hackathon/YOUR-PROJECT-NAME
2. Click Settings → Integrations
3. Look for "GitLab Duo" or "Agent Platform"
4. Enable any available toggles
5. Scroll to bottom → Click "Save"
```

### 3.2 Verify Agent Configuration Files
```bash
# Check that all agent files exist and have correct format
ls -la .gitlab/agents/

# Should show:
# - compliance-scanner.yaml
# - compliance-mapper.yaml
# - evidence-collector.yaml
# - compliance-reporter.yaml

# Check flow file exists
ls -la .gitlab/flows/

# Should show:
# - compliance-flow.yaml
```

---

## Step 4: Publish Agents to AI Catalog

### Method A: Via GitLab Web UI (Recommended for Hackathon)

#### 4.1 Publish First Agent (Scanner)
```
1. Go to: https://gitlab.com/gitlab-ai-hackathon/YOUR-PROJECT-NAME
2. Navigate to: Automate → Agents
3. Look for "compliance-scanner" in list
4. Click the agent name
5. Click "..." (three dots menu)
6. Select "Publish to AI Catalog"
7. Fill form:
   - Name: "ComplianceBot Scanner"
   - Description: "Detects security findings in MRs and pipelines (Auth, Encryption, Dependencies)"
   - Visibility: PUBLIC ⭐ (required for hackathon)
   - Tags: security, compliance, automation
8. Click "Publish"
9. ✅ Agent is now in AI Catalog!
```

#### 4.2 Publish Second Agent (Mapper)
```
Repeat same steps for:
- Name: "ComplianceBot Mapper"
- Description: "Maps security findings to SOC 2, ISO 27001, PCI-DSS, HIPAA controls"
- Tags: compliance, mapping, controls
```

#### 4.3 Publish Third Agent (Evidence Collector)
```
Repeat for:
- Name: "ComplianceBot Evidence Collector"
- Description: "Collects audit trails, approvals, and pipeline results with SHA-256 hashing"
- Tags: evidence, audit, compliance
```

#### 4.4 Publish Fourth Agent (Reporter)
```
Repeat for:
- Name: "ComplianceBot Reporter"
- Description: "Generates compliance narratives and PDF reports using Vertex AI"
- Tags: reporting, audit-ready, PDF
```

### Method B: Via VS Code Extension (Alternative)

If you want to use the GitLab extension in VS Code:

```
1. Press Ctrl+Shift+P
2. Type: "GitLab: Create Agent"
3. This will open creation wizard in GitLab UI
4. For existing agents, look for "Publish" button in extension

Note: The Web UI method is more straightforward for hackathon.
```

---

## Step 5: Publish Flow to AI Catalog

### 5.1 Publish Flow
```
1. Go to: https://gitlab.com/gitlab-ai-hackathon/YOUR-PROJECT-NAME
2. Navigate to: Automate → Flows
3. Find "compliance-flow" in list
4. Click the flow name
5. Click "..." menu
6. Select "Publish to AI Catalog"
7. Fill form:
   - Name: "ComplianceBot Flow"
   - Description: "Multi-agent compliance assessment flow triggered on MRs, pipelines, and schedule"
   - Visibility: PUBLIC ⭐ (required!)
   - Tags: compliance, automation, multi-agent, devops
8. Click "Publish"
9. ✅ Flow is now in AI Catalog!
```

---

## Step 6: Verify Publication

### 6.1 Check AI Catalog
```
1. Go to: https://gitlab.com/explore/groups
2. Search for your agents and flow by name
3. Or go to: https://gitlab.com/-/duo/catalog
4. Verify your items appear as PUBLIC
```

### 6.2 Verify in Project
```
1. Go to project page
2. Should show badge: "X agents published to AI Catalog"
```

### 6.3 Test Agent Works
```
1. In your project:
   - Create a test MR with code changes
   - Trigger the flow manually (if available)
2. Go to Automate → Sessions
3. Should see flow execution logs
4. Verify scanner detected findings
```

---

## Step 7: Complete Hackathon Submission

### 7.1 Prepare Devpost Submission
```
When submitting to Devpost (https://gitlab.devpost.com):

Project URL: https://gitlab.com/gitlab-ai-hackathon/YOUR-PROJECT-NAME
```

Ensure these are ready:
- ✅ Public repository
- ✅ MIT license visible
- ✅ README.md with clear description
- ✅ At least 1 agent published (you have 4!)
- ✅ Flow published
- ✅ Demo video (3 min max) on YouTube/Vimeo

### 7.2 Create Demo Video
```
Show in demo:
1. (0:00-0:30) Repository overview - show agents and flow files
2. (0:30-1:30) Trigger MR → Scanner finds compliance issues → Screenshot
3. (1:30-2:00) Show Mapper mapped controls → Score calculated
4. (2:00-2:30) Show Evidence collected → PDF report generated in GCS
5. (2:30-3:00) Show agents in AI Catalog (published status)
```

### 7.3 Submit to Devpost
```
1. Go to: https://gitlab.devpost.com
2. Click "Register" (join hackathon if not already)
3. Click "Submit" 
4. Fill form with:
   - Project URL
   - Description (copy from README)
   - Demo video YouTube link
   - Opt in: Google Cloud + GitLab Prize, Anthropic + GitLab Prize
   - Team members
5. Click "Submit"
6. ✅ You're done!
```

---

## Troubleshooting

### Issue: Agent Not Appearing in AI Catalog
```
Solution:
1. Ensure agent file in .gitlab/agents/YOUR-AGENT.yaml
2. Verify YAML syntax is correct (use online validator)
3. Check project is PUBLIC (not private)
4. Check Duo Agent Platform is enabled
5. Try refreshing browser cache (Ctrl+Shift+R)
```

### Issue: VS Code GitLab Extension Won't Connect
```
Solution:
1. Verify PAT token has 'api' and 'write_repository' scopes
2. Check token is not expired (create new one if needed)
3. Try: Ctrl+Shift+P → "GitLab: Disconnect" → "GitLab: Connect"
4. Restart VS Code
```

### Issue: Flow Not Executing
```
Solution:
1. Verify flow.yaml syntax (check against .gitlab/flows/compliance-flow.yaml)
2. Ensure all 4 component agents are published
3. Check trigger conditions match your test scenario
4. View logs: Automate → Sessions → Click flow run
```

### Issue: Agents Showing as Private in Catalog
```
Solution:
1. Go to each agent's publish settings
2. Change visibility to "Public" (not "Internal" or "Private")
3. Ensure repository visibility is Public
```

---

## Git Operations Quick Reference

### Committing Changes
```bash
# Check what changed
git status

# Stage all files
git add .

# Commit with descriptive message
git commit -m "feat: add ComplianceBot agents and flows"

# Push to GitLab
git push origin main

# View git log
git log --oneline -10
```

### Working with Branches (Optional)
```bash
# Create new branch
git checkout -b feature/agent-updates

# Make changes, commit as above
git commit -m "..."

# Push branch
git push origin feature/agent-updates

# Open MR in GitLab Web UI (will show prompt after push)
```

### Syncing with Remote
```bash
# Pull latest changes
git pull origin main

# Check remote URL
git remote -v

# Update remote if needed
git remote set-url origin https://gitlab.com/gitlab-ai-hackathon/YOUR-PROJECT.git
```

---

## GitLab PAT Extension Features

### View Project Info
```
Press Ctrl+Shift+P → "GitLab: View Project"
Shows:
- Project name and URL
- Branch info
- Merge request status
```

### Create Issues from VS Code
```
Press Ctrl+Shift+P → "GitLab: Create Issue"
Useful for documenting agent behavior or creating bugs
```

### View Agent Sessions
```
Press Ctrl+Shift+P → "GitLab: View Sessions"
Shows logs of agent and flow executions
```

---

## Key Hackathon Requirements Checklist

- [ ] At least 1 custom PUBLIC agent ✅ (you have 4!)
- [ ] At least 1 custom PUBLIC flow ✅ (you have 1!)
- [ ] Repository is PUBLIC
- [ ] MIT license visible at top of repo page
- [ ] README explains features and functionality
- [ ] Demo video (3 min max) on YouTube/Vimeo (PUBLIC)
- [ ] All source code in [gitlab.com/gitlab-ai-hackathon](https://gitlab.com/gitlab-ai-hackathon) group
- [ ] Text description for Devpost
- [ ] Team members listed (if applicable)

---

## Additional Resources

- [GitLab Duo Agent Platform Getting Started](https://about.gitlab.com/blog/gitlab-duo-agent-platform-complete-getting-started-guide/)
- [GitLab Agents Documentation](https://docs.gitlab.com/ee/user/gitlab_duo/agents/)
- [AI Catalog Documentation](https://docs.gitlab.com/ee/user/gitlab_duo/agents/agent-catalog.html)
- [Hackathon Submission Guide](https://gitlab.devpost.com)
- [GitLab Workflow Extension](https://marketplace.visualstudio.com/items?itemName=GitLab.gitlab-workflow)

---

## Next Steps After Publishing

1. **Test End-to-End**: Create a real MR, verify flow executes
2. **Record Demo**: Show agents + flow in action (3 min video)
3. **Deploy Cloud Run**: Run `bash cloud/cloud_run/deploy.sh $GCP_PROJECT_ID`
4. **Submit**: Fill out Devpost form with project URL
5. **Wait**: Judging happens after March 25, 2 PM EDT

---

Good luck! 🚀
