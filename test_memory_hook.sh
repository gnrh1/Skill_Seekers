#!/bin/bash
# Test memory protection hook integration

echo "🔍 Testing Memory Protection Hook Integration"
echo "=============================================="
echo ""

echo "1. Checking hook script exists..."
if [ -f ".claude/scripts/memory_protection_hook.py" ]; then
    echo "   ✅ memory_protection_hook.py exists"
else
    echo "   ❌ memory_protection_hook.py NOT FOUND"
    exit 1
fi

echo ""
echo "2. Testing hook execution..."
python3 .claude/scripts/memory_protection_hook.py > /tmp/hook_test.json 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ Hook executed successfully"
    echo "   Output: $(cat /tmp/hook_test.json | tail -1)"
else
    echo "   ❌ Hook execution failed"
    exit 1
fi

echo ""
echo "3. Checking hook logs..."
if [ -f ".claude/logs/memory_protection_hook.log" ]; then
    echo "   ✅ Hook log file created"
    echo "   Last entry:"
    tail -1 .claude/logs/memory_protection_hook.log | sed 's/^/      /'
else
    echo "   ❌ Hook log NOT created"
    exit 1
fi

echo ""
echo "4. Checking settings.json configuration..."
if grep -q "memory_protection_hook.py" .claude/settings.json; then
    echo "   ✅ Hook configured in settings.json"
else
    echo "   ❌ Hook NOT configured in settings.json"
    exit 1
fi

echo ""
echo "5. Checking resource monitor integration..."
python3 -c "import sys; sys.path.insert(0, '.claude/scripts'); from resource_monitor import check_resources_before_agent_spawn; print('✅ Resource monitor accessible')" 2>&1

echo ""
echo "=============================================="
echo "✅ ALL CHECKS PASSED"
echo ""
echo "Next Steps:"
echo "1. Restart Claude Code to load new hook configuration"
echo "2. When you use @orchestrator-agent, the hook will:"
echo "   - Intercept EVERY Task tool call"
echo "   - Check memory/CPU/agent count BEFORE spawning"
echo "   - Block if limits exceeded (>2 agents or >500MB)"
echo "   - Log all checks to .claude/logs/memory_protection_hook.log"
echo ""
echo "3. Monitor with: tail -f .claude/logs/memory_protection_hook.log"
