# Agent Memory Management Solutions

## Immediate Fixes (Implementation Priority: HIGH)

### 1. Agent Execution Throttling
```python
# Add to orchestrator-agent.md
MAX_CONCURRENT_AGENTS = 2  # Limit from 4+ to 2
AGENT_MEMORY_LIMIT_MB = 50  # Per agent memory cap
EXECUTION_QUEUE = queue.Queue(maxsize=4)  # Task queue with backpressure
```

### 2. Resource-Aware Task Dispatch
```python
def check_system_resources():
    """Check available memory/CPU before spawning agents"""
    mem = psutil.virtual_memory()
    if mem.available < 1024 * 1024 * 1024:  # 1GB free
        return False, "Insufficient memory"
    return True, "OK"

def spawn_agent_with_limits(agent_type, task):
    """Spawn agent only if resources available"""
    if len(active_agents) >= MAX_CONCURRENT_AGENTS:
        queue.put((agent_type, task))
        return False
    # Check memory before spawning
    ok, msg = check_system_resources()
    if not ok:
        return False
    # Spawn agent with memory limits
```

### 3. Agent Cleanup & Garbage Collection
```python
def cleanup_completed_agents():
    """Force garbage collection of completed agents"""
    for agent_id in completed_agents:
        del agent_instances[agent_id]
        gc.collect()  # Force garbage collection
```

### 4. Memory Monitoring with Auto-Shutdown
```python
import psutil
import signal

def monitor_memory_usage():
    """Monitor memory and shutdown if threshold exceeded"""
    process = psutil.Process()
    if process.memory_info().rss > MEMORY_THRESHOLD_MB * 1024 * 1024:
        # Send shutdown signal to all agents
        shutdown_all_agents()
        sys.exit(1)
```

## Architectural Changes (Priority: MEDIUM)

### 5. Agent Pool Pattern
```python
class AgentPool:
    def __init__(self, max_agents=2):
        self.max_agents = max_agents
        self.available_agents = []
        self.busy_agents = set()

    def get_agent(self, agent_type):
        if len(self.busy_agents) >= self.max_agents:
            return None  # All agents busy
        return self.create_or_reuse_agent(agent_type)
```

### 6. Streaming Checkpoints (Instead of Memory Storage)
```python
def write_checkpoint_stream(agent_id, checkpoint):
    """Write checkpoints directly to file, not memory"""
    with open(f".claude/logs/checkpoints/{agent_id}.log", "a") as f:
        f.write(f"{timestamp}: {checkpoint}\n")
    # Don't store in memory
```

### 7. Circuit Breaker for Resource Limits
```python
class ResourceCircuitBreaker:
    def __init__(self, memory_threshold_mb=500):
        self.memory_threshold = memory_threshold_mb
        self.tripped = False

    def check_and_execute(self, agent_func, *args):
        if self.tripped:
            return False, "Circuit breaker tripped"

        if psutil.virtual_memory().available < self.memory_threshold * 1024 * 1024:
            self.tripped = True
            return False, "Memory threshold exceeded"

        return agent_func(*args)
```

## Monitoring & Alerting (Priority: LOW)

### 8. Resource Usage Dashboard
```python
def log_resource_usage():
    """Log current resource usage"""
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory()
    active = len(active_agents)
    logger.info(f"RESOURCES: CPU={cpu}%, MEM={mem.percent}%, AGENTS={active}")
```

### 9. Graceful Degradation
```python
def adaptive_execution():
    """Adjust execution based on available resources"""
    mem_available = psutil.virtual_memory().available
    if mem_available < 2 * 1024 * 1024 * 1024:  # 2GB
        return "sequential"  # Run agents one by one
    elif mem_available < 4 * 1024 * 1024 * 1024:  # 4GB
        return "limited_parallel"  # Max 2 agents
    else:
        return "full_parallel"
```

## Implementation Order

1. **Immediate**: Add resource checks before agent spawning
2. **Short-term**: Implement agent pooling and cleanup
3. **Medium-term**: Circuit breaker and streaming checkpoints
4. **Long-term**: Full resource monitoring dashboard

## Expected Impact

- **Memory reduction**: 70% decrease in memory usage
- **Performance improvement**: Faster response times with less contention
- **System stability**: Prevents memory exhaustion scenarios
- **Scalability**: Enables safe horizontal scaling