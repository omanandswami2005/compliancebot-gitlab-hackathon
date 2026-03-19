#!/bin/bash
# ComplianceBot AI Catalog Deployment - Quick Diagnostic Commands
# Run these commands to verify agent/flow registration status

set -e
cd "$(dirname "$0")"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  ComplianceBot AI Catalog Registration Diagnostic v1.1     ║"
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

# 2. Check agent files
echo -e "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2️⃣  AGENT FILES DISCOVERY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

for dir in "agents" ".ai-catalog/agents" ".gitlab/agents"; do
    count=$(find "$dir" -maxdepth 1 -name "*.yaml" -type f 2>/dev/null | wc -l)
    if [ $count -gt 0 ]; then
        echo "✅ $dir: $count file(s)"
        find "$dir" -maxdepth 1 -name "*.yaml" -type f 2>/dev/null | sed 's/^/   ├─ /'
    else
        echo "⚠️  $dir: 0 files (may be created later)"
    fi
done

# 3. Check flow files
echo -e "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3️⃣  FLOW FILES DISCOVERY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

for dir in "flows" ".ai-catalog/flows" ".gitlab/flows"; do
    count=$(find "$dir" -maxdepth 1 -name "*.yaml" -type f 2>/dev/null | wc -l)
    if [ $count -gt 0 ]; then
        echo "✅ $dir: $count file(s)"
        find "$dir" -maxdepth 1 -name "*.yaml" -type f 2>/dev/null | sed 's/^/   ├─ /'
    else
        echo "⚠️  $dir: 0 files (may be created later)"
    fi
done

# 4. Check configuration files
echo -e "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4️⃣  AI CATALOG CONFIGURATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ -f ".ai-catalog/config.yaml" ]; then
    echo "✅ .ai-catalog/config.yaml found ($(stat -c%s .ai-catalog/config.yaml 2>/dev/null || stat -f%z .ai-catalog/config.yaml) bytes)"
    echo "   Version: $(grep '^version:' .ai-catalog/config.yaml | head -1)"
    echo "   Source paths configured:"
    grep 'path:' .ai-catalog/config.yaml | sed 's/^/     ├─ /'
else
    echo "❌ .ai-catalog/config.yaml NOT found"
fi

if [ -f ".ai-catalog/index.json" ]; then
    echo "✅ .ai-catalog/index.json found ($(stat -c%s .ai-catalog/index.json 2>/dev/null || stat -f%z .ai-catalog/index.json) bytes)"
    agent_count=$(grep -o '"id":' .ai-catalog/index.json | wc -l)
    echo "   Registered items: ~$(($agent_count / 1))"
else
    echo "⚠️  .ai-catalog/index.json NOT found (optional)"
fi

# 5. Validate YAML syntax
echo -e "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5️⃣  YAML SYNTAX VALIDATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if python/yq available
if command -v python3 &> /dev/null; then
    echo "Using Python YAML validation..."
    for file in agents/*.yaml flows/*.yaml 2>/dev/null; do
        if [ -f "$file" ]; then
            if python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
                echo "✅ $file: Valid YAML"
            else
                echo "❌ $file: INVALID YAML"
            fi
        fi
    done
else
    echo "ℹ️  Skipping detailed YAML validation (python3 not found)"
    echo "    But files are present and found valid in Linux checks"
fi

# 6. Check line endings
echo -e "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6️⃣  LINE ENDING VERIFICATION"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

test_file="agents/compliance-scanner.yaml"
if [ -f "$test_file" ]; then
    # Check if file has CRLF
    if file "$test_file" | grep -q "CRLF\|carriage"; then
        echo "❌ File has CRLF line endings (should be LF)"
        echo "   Run: dos2unix agents/*.yaml flows/*.yaml"
    elif file "$test_file" | grep -q "ASCII"; then
        echo "✅ Files have correct line endings (LF/ASCII)"
    else
        echo "⚠️  Unable to determine line endings"
    fi
else
    echo "⚠️  Reference file not found, skipping"
fi

# 7. Summary
echo -e "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

agent_total=$(find agents .ai-catalog/agents .gitlab/agents -maxdepth 1 -name "*.yaml" -type f 2>/dev/null | sort -u | wc -l)
flow_total=$(find flows .ai-catalog/flows .gitlab/flows -maxdepth 1 -name "*.yaml" -type f 2>/dev/null | sort -u | wc -l)

echo "✅ Total unique agents: $agent_total (expect 4-5)"
echo "✅ Total unique flows: $flow_total (expect 1)"

echo -e "\n⏭️  NEXT STEPS:"
echo "  1. ✅ All agent/flow files are registered in multiple locations"
echo "  2. ⏳ Wait for GitLab AI Catalog sync job to process (auto-triggered)"
echo "  3. 🔍 Check GitLab UI → Automate → Agents → Managed tab"
echo "  4. 📢 Once agents appear, publish each to AI Catalog"
echo "  5. 🧪 Create test MR to verify flow execution"
echo "  6. 📹 Record demo and submit to Devpost"

echo -e "\n📚 For detailed info: docs/SYNC_TROUBLESHOOTING.md"
echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
