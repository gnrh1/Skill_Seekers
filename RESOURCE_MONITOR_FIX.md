# Resource Monitor Fix Applied

**Date**: November 18, 2025  
**Issue**: False positive agent counting (reported 57 agents when none active)  
**Status**: **FIXED** ✅

---

## Root Cause Analysis

### **Mental Models Applied**

1. **First Principles**: What is the fundamental purpose of `get_active_agent_count()`?
   - **Answer**: Count OUR orchestrated agents, not system processes

2. **Systems Thinking**: How does false counting affect the entire system?
   - **Answer**: Circuit breaker ALWAYS open → blocks ALL agent execution

3. **Inversion**: What should we NOT count?
   - **Answer**: System agents, Adobe processes, macOS services

4. **Second-Order Effects**: What cascades from false counting?
   - **Answer**: Protection system becomes denial-of-service, blocks legitimate work

---

## The Bug

### **Problematic Code** (Before)
```python
def get_active_agent_count(self) -> int:
    """Count currently active agent processes"""
    agent_count = 0
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        cmdline = ' '.join(proc.info['cmdline'] or [])
        if 'agent' in cmdline.lower():  # ❌ TOO BROAD
            agent_count += 1
    return agent_count
```

### **Why It Failed**
This searched for ANY process with "agent" in the command line, matching:
- ❌ `searchpartyuseragent` (macOS Spotlight)
- ❌ `mbuseragent` (Setup Assistant)
- ❌ `nbagent` (Noticeboard)
- ❌ `containermanagerd --runmode=agent` (Container daemon)
- ❌ `trustd --agent` (Security daemon)
- ❌ `distnoted agent` (Distributed notifications, multiple instances)
- ❌ `gamecontrolleragentd` (Game controller)
- ❌ `UsageTrackingAgent` (Usage stats)
- ❌ Adobe Creative Cloud processes (10+ with "agent" in name)

**Result**: Reported 57-87 "agents" when zero orchestrated agents were running!

---

## The Fix

### **Corrected Code** (After)
```python
def get_active_agent_count(self) -> int:
    """Count currently active agent processes from registry only"""
    # FIXED: Only count agents we explicitly registered
    # Do NOT scan all processes (causes false positives)
    active_count = sum(
        1 for agent in self.agent_registry.values()
        if agent['status'] == 'active'
    )
    return active_count
```

### **Why It Works**
- ✅ Only counts agents in `agent_registry` (our agents)
- ✅ Ignores system processes completely
- ✅ Tracks actual orchestrated agent lifecycle
- ✅ Zero false positives

---

## Additional Fix: Threshold Logic

### **Semantic Bug**
Documentation said "Maximum 2 concurrent agents" but code checked `>= 2`, which only allowed 0 or 1.

### **Before**: Too Restrictive
```python
if active_agents >= self.MAX_CONCURRENT_AGENTS:  # Rejects at 2
    return False
```
- Allowed: 0, 1
- Rejected: 2, 3, 4...

### **After**: Correct Semantics
```python
if active_agents > self.MAX_CONCURRENT_AGENTS:  # Rejects at 3
    return False
```
- Allowed: 0, 1, 2
- Rejected: 3, 4, 5...

**Now matches documentation**: "Maximum 2 concurrent agents" = up to and including 2.

---

## Testing Results

### **Comprehensive Test Suite** ✅
Created `test_resource_monitor.py` with 9 tests:

1. ✅ System resource check (passes)
2. ✅ Agent count = 0 initially
3. ✅ Agent registration works
4. ✅ Resource check with 1 agent (passes)
5. ✅ Resource check with 2 agents (passes - at limit)
6. ✅ Resource check with 3 agents (fails - over limit)
7. ✅ Agent cleanup works
8. ✅ Memory monitoring operational
9. ✅ Helper function works

**All tests pass** 🎉

### **Before Fix**
```bash
$ python3 -c "from resource_monitor import get_resource_monitor; ..."
Active agents: 57  # ❌ FALSE POSITIVE
Resources OK: False
Message: Too many agents: 57 active
```

### **After Fix**
```bash
$ python3 -c "from resource_monitor import get_resource_monitor; ..."
Active agents: 0  # ✅ CORRECT
Resources OK: True
Message: Resources OK
```

---

## Impact Assessment

### **Before Fix** 💀
- **Agent spawning**: Blocked (circuit breaker always open)
- **Orchestration**: Completely disabled
- **Error message**: "Too many agents: 57 active"
- **User experience**: System appeared broken
- **Root cause**: Protection system became attack surface

### **After Fix** ✅
- **Agent spawning**: Works correctly
- **Orchestration**: Fully functional
- **Agent limits**: Properly enforced (0-2 allowed, 3+ rejected)
- **User experience**: System works as designed
- **Protection**: Active and accurate

---

## Verification Commands

### Check Agent Count
```bash
# Should return 0 when no agents running
python3 -c "
import sys
sys.path.insert(0, '.claude/scripts')
from resource_monitor import get_resource_monitor
monitor = get_resource_monitor()
print(f'Active agents: {monitor.get_active_agent_count()}')
"
```

### Check Resource Status
```bash
# Should return True when system ready
python3 -c "
import sys
sys.path.insert(0, '.claude/scripts')
from resource_monitor import check_resources_before_agent_spawn
ok, msg = check_resources_before_agent_spawn()
print(f'Resources OK: {ok}')
print(f'Message: {msg}')
"
```

### Run Full Test Suite
```bash
python3 .claude/scripts/test_resource_monitor.py
```

### Pre-Flight Check
```bash
./check_before_agents.sh
```

---

## Technical Details

### **Agent Registry Design**
The fix relies on the agent registry pattern:

```python
# When agent starts
monitor.register_agent(agent_id, agent_type)
# → Adds to registry with status='active'

# When agent completes
monitor.update_agent_status(agent_id, 'completed')
# → Updates status in registry

# Periodic cleanup
monitor.cleanup_completed_agents()
# → Removes completed agents from registry

# Count active agents
count = monitor.get_active_agent_count()
# → Counts only agents with status='active' in registry
```

### **Why This Is Better**
1. **Explicit tracking**: We control what counts as an agent
2. **No process scanning**: Avoids false positives entirely
3. **Lifecycle aware**: Knows when agents start, run, complete
4. **Memory efficient**: Registry is lightweight (just metadata)
5. **Testable**: Can mock and verify behavior

---

## Files Modified

### Changed
- ✅ `.claude/scripts/resource_monitor.py`
  - Fixed `get_active_agent_count()` to use registry
  - Fixed threshold check from `>=` to `>`
  - Added clearer error messages

### Created
- ✅ `.claude/scripts/test_resource_monitor.py`
  - Comprehensive test suite (9 tests)
  - Validates all resource monitor functionality
  - Includes regression tests for false positive bug

- ✅ `RESOURCE_MONITOR_FIX.md` (this file)
  - Complete root cause analysis
  - Fix documentation
  - Verification procedures

---

## Lessons Learned

### **Anti-Pattern**: Process Name Grep
```python
# ❌ NEVER DO THIS
for proc in all_processes:
    if 'agent' in proc.name:  # Too many false positives
        count += 1
```

### **Best Practice**: Explicit Registration
```python
# ✅ ALWAYS DO THIS
registry = {}
def register(agent_id): registry[agent_id] = {'status': 'active'}
def count_active(): return sum(1 for a in registry.values() if a['status'] == 'active')
```

### **Mental Model**: Own Your State
- Don't infer system state from external observations
- Maintain explicit state through registration
- Use process scanning only as validation, not source of truth

---

## Related Issues Fixed

This fix also resolves:
1. ✅ Circuit breaker stuck open
2. ✅ "Too many agents" when none running
3. ✅ Orchestrator unable to spawn any agents
4. ✅ False resource exhaustion errors
5. ✅ Semantic mismatch in MAX_CONCURRENT_AGENTS

---

## Prevention: How to Avoid This

### **Code Review Checklist**
- [ ] Does process scanning have specific, unique identifiers?
- [ ] Could system processes match the search pattern?
- [ ] Is there a more explicit way to track state?
- [ ] Are thresholds clearly documented (inclusive vs exclusive)?
- [ ] Are there tests for boundary conditions?

### **Testing Checklist**
- [ ] Test with zero entities (agents, processes, etc.)
- [ ] Test at exactly the limit (n = MAX)
- [ ] Test just over the limit (n = MAX + 1)
- [ ] Test with system noise (other processes running)
- [ ] Test cleanup and state reset

---

## Status

✅ **ALL FIXED AND TESTED**

The resource monitor now:
- Correctly counts only orchestrated agents (no false positives)
- Allows up to 2 concurrent agents (inclusive)
- Rejects 3 or more agents (protective)
- Passes all 9 comprehensive tests
- Works correctly with system processes running

**Your orchestrator agents will now work properly!** 🎉

---

## Next Steps

1. ✅ Fix applied and tested
2. ✅ Test suite created for regression prevention
3. **→ Restart Claude Code to load changes**
4. **→ Test agent execution to verify fix**
5. **→ Monitor first few executions**

Run the pre-flight check before using agents:
```bash
./check_before_agents.sh
```

If all checks pass, you're ready to use orchestrator agents safely!
