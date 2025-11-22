#!/bin/bash
# Quick pre-flight check before using agents
# Run this before important agent work to verify protection is active

cd /Users/docravikumar/Code/skill-test/Skill_Seekers

echo ""
echo "🔍 PRE-FLIGHT SAFETY CHECK"
echo "=================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

overall_safe=true

# Check 1: Memory-enhanced agents are primary
echo "1. Agent Configuration:"
orchestrator_name=$(grep "^name:" .claude/agents/orchestrator-agent-memory-enhanced.md | head -1 | cut -d: -f2 | tr -d ' ')
intel_name=$(grep "^name:" .claude/agents/intelligence-orchestrator-memory-enhanced.md | head -1 | cut -d: -f2 | tr -d ' ')

if [ "$orchestrator_name" = "orchestrator-agent" ]; then
    echo -e "   ${GREEN}✅${NC} orchestrator-agent (memory-protected)"
else
    echo -e "   ${RED}❌${NC} orchestrator-agent (WRONG NAME: $orchestrator_name)"
    overall_safe=false
fi

if [ "$intel_name" = "intelligence-orchestrator" ]; then
    echo -e "   ${GREEN}✅${NC} intelligence-orchestrator (memory-protected)"
else
    echo -e "   ${RED}❌${NC} intelligence-orchestrator (WRONG NAME: $intel_name)"
    overall_safe=false
fi

# Check 2: No legacy agents active
echo ""
echo "2. Legacy Agent Check:"
legacy_count=$(find .claude/agents -name "*-legacy.md" ! -name "*.backup" 2>/dev/null | wc -l | tr -d ' ')
if [ "$legacy_count" -eq 0 ]; then
    echo -e "   ${GREEN}✅${NC} No unsafe legacy agents active"
else
    echo -e "   ${RED}❌${NC} WARNING: $legacy_count legacy agent(s) still active!"
    find .claude/agents -name "*-legacy.md" ! -name "*.backup" | while read file; do
        echo -e "      ${RED}→${NC} $file"
    done
    overall_safe=false
fi

# Check 3: Resource monitoring scripts
echo ""
echo "3. Protection Scripts:"
all_scripts_present=true
for script in resource_monitor.py agent_circuit_breaker.py agent_pool.py memory_enhanced_orchestrator.py; do
    if [ -f ".claude/scripts/$script" ]; then
        echo -e "   ${GREEN}✅${NC} $script"
    else
        echo -e "   ${RED}❌${NC} $script (MISSING)"
        all_scripts_present=false
        overall_safe=false
    fi
done

# Check 4: Current memory usage
echo ""
echo "4. Current System Memory:"
if command -v python3 &> /dev/null; then
    mem_usage=$(python3 -c "import psutil; print(f'{psutil.virtual_memory().percent:.1f}')" 2>/dev/null)
    mem_available=$(python3 -c "import psutil; print(f'{psutil.virtual_memory().available / (1024**3):.1f}')" 2>/dev/null)
    
    if [ -n "$mem_usage" ]; then
        echo -e "   Memory usage: ${mem_usage}%"
        echo -e "   Available: ${mem_available}GB"
        
        mem_usage_int=${mem_usage%.*}
        if [ "$mem_usage_int" -gt 80 ]; then
            echo -e "   ${YELLOW}⚠️${NC}  High memory usage - consider freeing memory first"
        else
            echo -e "   ${GREEN}✅${NC} Memory looks good"
        fi
    fi
else
    echo -e "   ${YELLOW}⚠️${NC}  Python not available for memory check"
fi

# Check 5: Claude Code processes
echo ""
echo "5. Claude Code Processes:"
claude_count=$(ps aux | grep -i claude | grep -v grep | wc -l | tr -d ' ')
if [ "$claude_count" -gt 0 ]; then
    echo -e "   ${GREEN}✅${NC} $claude_count Claude process(es) running"
    
    # Check if any are using excessive memory
    high_mem=$(ps aux | grep -i claude | grep -v grep | awk '{if ($4 > 20) print $0}' | wc -l | tr -d ' ')
    if [ "$high_mem" -gt 0 ]; then
        echo -e "   ${YELLOW}⚠️${NC}  $high_mem process(es) using >20% memory"
        echo -e "      Consider restarting Claude Code"
    fi
else
    echo -e "   ${YELLOW}ℹ️${NC}  No Claude processes detected"
fi

# Final verdict
echo ""
echo "=================================="
if [ "$overall_safe" = true ]; then
    echo -e "${GREEN}✅ ALL CHECKS PASSED${NC}"
    echo ""
    echo "Your system is protected against memory explosions."
    echo "Safe to use orchestrator agents."
    echo ""
    exit 0
else
    echo -e "${RED}❌ SAFETY CHECKS FAILED${NC}"
    echo ""
    echo "DO NOT use orchestrator agents until issues are fixed!"
    echo ""
    echo "Fix commands:"
    echo "  1. Run verification: python3 .claude/scripts/verify_memory_protection.py"
    echo "  2. Check documentation: cat MEMORY_FIX_APPLIED.md"
    echo ""
    exit 1
fi
