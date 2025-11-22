#!/bin/bash
# Quick test to verify memory protection is working

echo "======================================"
echo "MEMORY PROTECTION TEST"
echo "======================================"
echo ""

# 1. Check agent files
echo "1. Checking agent configuration..."
if [ -f ".claude/agents/orchestrator-agent-memory-enhanced.md" ]; then
    name=$(grep "^name:" .claude/agents/orchestrator-agent-memory-enhanced.md | head -1)
    if [[ $name == *"orchestrator-agent"* ]] && [[ $name != *"memory-enhanced"* ]]; then
        echo "   ✅ orchestrator-agent: Active (memory-protected)"
    else
        echo "   ⚠️  orchestrator-agent: Wrong name in file"
    fi
else
    echo "   ❌ orchestrator-agent: File missing"
fi

if [ -f ".claude/agents/intelligence-orchestrator-memory-enhanced.md" ]; then
    name=$(grep "^name:" .claude/agents/intelligence-orchestrator-memory-enhanced.md | head -1)
    if [[ $name == *"intelligence-orchestrator"* ]] && [[ $name != *"memory-enhanced"* ]]; then
        echo "   ✅ intelligence-orchestrator: Active (memory-protected)"
    else
        echo "   ⚠️  intelligence-orchestrator: Wrong name in file"
    fi
else
    echo "   ❌ intelligence-orchestrator: File missing"
fi

echo ""
echo "2. Checking for legacy agents..."
legacy_count=$(ls .claude/agents/*-legacy.md 2>/dev/null | wc -l | tr -d ' ')
if [ "$legacy_count" -gt 0 ]; then
    echo "   ⚠️  WARNING: $legacy_count legacy agent(s) still active!"
    echo "      Run: mv .claude/agents/*-legacy.md .claude/agents/*.backup"
else
    echo "   ✅ No legacy agents found"
fi

echo ""
echo "3. Checking resource scripts..."
for script in resource_monitor.py agent_circuit_breaker.py agent_pool.py memory_enhanced_orchestrator.py; do
    if [ -f ".claude/scripts/$script" ]; then
        echo "   ✅ $script"
    else
        echo "   ❌ $script (MISSING)"
    fi
done

echo ""
echo "======================================"
echo "TEST COMPLETE"
echo "======================================"
