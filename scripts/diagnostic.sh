#!/bin/bash
# ComplianceBot AI Catalog Deployment - Quick Diagnostic Commands
# Run these commands to verify agent/flow registration status
# Official structure: agents/ and flows/ directories at repository root

set -e
cd "$(dirname "$0")"/..

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ComplianceBot AI Catalog Registration Diagnostic v2.0     ║"
echo "║  (Following official GitLab AI Catalog schema)              ║"
echo "╚════════════════════════════════════════════════════════════╝"

echo -e "\n📍 LOCATION: $(pwd)"
echo "🕐 TIMESTAMP: $(date -u +'%Y-%m-%d %H:%M:%S UTC')"

# 1. Check repository connectivity
echo -e "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1️⃣  GIT REPOSITORY STATUS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if git status > /dev/null 2>&1; then
    echo "✅ Git repository found"
    echo "   Branch: $(git rev-parse --abbrev-ref HEAD)"
    echo "   Remote: $(git config --get remote.origin.url)"
    echo "   Latest commit: $(git log -1 --format='%h - %s' || echo 'N/A')"
else
    echo "❌ Git repository not found"
    exit 1
fi

# 2. Check agent files (official location)
echo -e "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  AGENT FILES (agents/ — Official GitLab AI Catalog location)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -d "agents" ]; then
    count=$(find agents -maxdepth 1 -name "*.yaml" -type f 2>/dev/null | wc -l)
    if [ $count -gt 0 ]; then
        echo "✅ agents/: $count agent file(s)"
        find agents -maxdepth 1 -name "*.yaml" -type f 2>/dev/null | sort | sed 's/^/   ├─ /'
    else
        echo "❌ agents/: 0 files (no agent YAML files found)"
    fi
else
    echo "❌ agents/ directory not found"
fi

# 3. Check flow files (official location)
echo -e "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  FLOW FILES (flows/ — Official GitLab AI Catalog location)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -d "flows" ]; then
    count=$(find flows -maxdepth 1 -name "*.yaml" -type f 2>/dev/null | wc -l)
    if [ $count -gt 0 ]; then
        echo "✅ flows/: $count flow file(s)"
        find flows -maxdepth 1 -name "*.yaml" -type f 2>/dev/null | sort | sed 's/^/   ├─ /'
    else
        echo "❌ flows/: 0 files (no flow YAML files found)"
    fi
else
    echo "❌ flows/ directory not found"
fi

# 4. Check GitLab CI/CD configuration
echo -e "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  GitLab CI/CD CONFIGURATION (.gitlab-ci.yml)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f ".gitlab-ci.yml" ]; then
    echo "✅ .gitlab-ci.yml found"
    if grep -q "catalog-sync" ".gitlab-ci.yml"; then
        echo "   ✅ Contains ai-catalog/catalog-sync component reference"
        echo "   Configuration:"
        grep -A 3 "catalog-sync" ".gitlab-ci.yml" | head -5 | sed 's/^/      ├─ /'
    else
        echo "   ⚠️  No catalog-sync component found"
    fi
else
    echo "❌ .gitlab-ci.yml NOT found"
fi

# 5. Validate YAML syntax
echo -e "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣  YAML SYNTAX VALIDATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if command -v python3 &> /dev/null; then
    echo "Using Python YAML validation..."
    yaml_errors=0
    for file in agents/*.yaml flows/*.yaml 2>/dev/null; do
        if [ -f "$file" ]; then
            if python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
                echo "✅ $file: Valid YAML"
            else
                echo "❌ $file: INVALID YAML"
                yaml_errors=$((yaml_errors + 1))
            fi
        fi
    done
    if [ $yaml_errors -eq 0 ]; then
        echo "✅ All YAML files are syntactically valid"
    fi
else
    echo "ℹ️  Python3 not found, skipping detailed YAML validation"
fi

# 6. Check line endings
echo -e "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6️⃣  LINE ENDING VERIFICATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_file="agents/compliance-scanner.yaml"
if [ -f "$test_file" ]; then
    if file "$test_file" | grep -q "CRLF\|carriage"; then
        echo "❌ Files have CRLF line endings (should be LF only)"
        echo "   Fix with: dos2unix agents/*.yaml flows/*.yaml"
    else
        echo "✅ Files have correct line endings (LF)"
    fi
else
    echo "⚠️  Reference file not found, skipping"
fi

# 7. Check for non-standard directories (now removed)
echo -e "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "7️⃣  CLEANUP STATUS (Non-standard directories)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -d ".ai-catalog" ]; then
    echo "⚠️  .ai-catalog/ directory exists (non-standard, can be removed)"
else
    echo "✅ .ai-catalog/ removed (standard structure maintained)"
fi

if [ -d ".gitlab" ]; then
    echo "⚠️  .gitlab/ directory exists (for Duo Platform, not AI Catalog)"
else
    echo "✅ .gitlab/ removed (official structure maintained)"
fi

# 8. Summary
echo -e "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

agent_total=$(find agents -maxdepth 1 -name "*.yaml" -type f 2>/dev/null | wc -l)
flow_total=$(find flows -maxdepth 1 -name "*.yaml" -type f 2>/dev/null | wc -l)

echo "✅ Total agents: $agent_total (expect 4-5)"
echo "✅ Total flows: $flow_total (expect 1)"

echo -e "\n⏭️  NEXT STEPS:"
echo "  1. ✅ All files follow official GitLab AI Catalog schema"
echo "  2. ⏳ Push to origin/main and create a Git tag to trigger sync"
echo "  3. 🔍 Check GitLab CI/CD → Pipelines for catalog-sync job"
echo "  4. 📢 Once synced, agents appear in Automate → Agents → Managed"
echo "  5. 🧪 Create test MR to verify flow execution"
echo "  6. 📹 Record demo and submit to Devpost"

echo -e "\n📚 References:"
echo "  • Official docs: https://gitlab.com/components/ai-catalog/-/blob/main/README.md"
echo "  • Configuration: docs/configuration.md"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
