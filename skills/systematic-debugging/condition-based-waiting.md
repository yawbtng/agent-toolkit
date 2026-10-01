# Condition-Based Waiting

## Overview

Flaky tests often guess at timing with arbitrary delays. This creates race conditions where tests pass on fast machines but fail under load or in CI.

The same guessing shows up outside tests too: waiting on a long-running shell process (a build, a dev server, a background job) by repeatedly sending an empty keystroke or re-checking output every few seconds on a fixed short interval. It wastes tool calls the same way a flaky `setTimeout` wastes test time.

**Core principle:** Wait for the actual condition you care about, not a guess about how long it takes.

## When to Use

```dot
digraph when_to_use {
    "Test uses setTimeout/sleep?" [shape=diamond];
    "Testing timing behavior?" [shape=diamond];
    "Document WHY timeout needed" [shape=box];
    "Use condition-based waiting" [shape=box];

    "Test uses setTimeout/sleep?" -> "Testing timing behavior?" [label="yes"];
    "Testing timing behavior?" -> "Document WHY timeout needed" [label="yes"];
    "Testing timing behavior?" -> "Use condition-based waiting" [label="no"];
}
```

**Use when:**
- Tests have arbitrary delays (`setTimeout`, `sleep`, `time.sleep()`)
- Tests are flaky (pass sometimes, fail under load)
- Tests timeout when run in parallel
- Waiting for async operations to complete
- Watching a shell command, build, or dev server for completion (see "Shell / Long-Running Process Monitoring" below)

**Don't use when:**
- Testing actual timing behavior (debounce, throttle intervals)
- Always document WHY if using arbitrary timeout

## Core Pattern

```typescript
// ❌ BEFORE: Guessing at timing
await new Promise(r => setTimeout(r, 50));
const result = getResult();
expect(result).toBeDefined();

// ✅ AFTER: Waiting for condition
await waitFor(() => getResult() !== undefined);
const result = getResult();
expect(result).toBeDefined();
```

## Quick Patterns

| Scenario | Pattern |
|----------|---------|
| Wait for event | `waitFor(() => events.find(e => e.type === 'DONE'))` |
| Wait for state | `waitFor(() => machine.state === 'ready')` |
| Wait for count | `waitFor(() => items.length >= 5)` |
| Wait for file | `waitFor(() => fs.existsSync(path))` |
| Complex condition | `waitFor(() => obj.ready && obj.value > 10)` |

## Shell / Long-Running Process Monitoring

The polling mistake also shows up at the shell level: sending a blank `write_stdin`/keystroke every 5 seconds to "flush" output, or looping `sleep 5` a dozen-plus times to watch a build or dev server, instead of waiting on the condition that actually matters (the process exiting, or a marker string appearing in its output).

**❌ BEFORE: Manual poll loop**
```bash
# repeated every few seconds, by hand, for a dozen+ iterations
sleep 5 && tail -n 20 build.log
```

**✅ AFTER: One bounded wait on the real condition**
```bash
# background the job, then block on it directly instead of polling
some_long_build > build.log 2>&1 &
pid=$!
wait "$pid"
echo "exit code: $?"
```

```bash
# or: block until a marker appears, with a real timeout
timeout 300 bash -c 'until grep -q "Build succeeded" build.log; do sleep 2; done'
```

**Requirements:**
1. Background the process once, then wait/poll on its actual exit or a log marker — not a fixed cadence of manual checks
2. Always bound it with a real timeout (`timeout N ...`), never an unbounded loop
3. If the harness provides a native watch/monitor primitive for background output, prefer it over a hand-rolled shell loop

## Implementation

Generic polling function:
```typescript
async function waitFor<T>(
  condition: () => T | undefined | null | false,
  description: string,
  timeoutMs = 5000
): Promise<T> {
  const startTime = Date.now();

  while (true) {
    const result = condition();
    if (result) return result;

    if (Date.now() - startTime > timeoutMs) {
      throw new Error(`Timeout waiting for ${description} after ${timeoutMs}ms`);
    }

    await new Promise(r => setTimeout(r, 10)); // Poll every 10ms
  }
}
```

See `condition-based-waiting-example.ts` in this directory for complete implementation with domain-specific helpers (`waitForEvent`, `waitForEventCount`, `waitForEventMatch`) from actual debugging session.

## Common Mistakes

**❌ Polling too fast:** `setTimeout(check, 1)` - wastes CPU
**✅ Fix:** Poll every 10ms

**❌ No timeout:** Loop forever if condition never met
**✅ Fix:** Always include timeout with clear error

**❌ Stale data:** Cache state before loop
**✅ Fix:** Call getter inside loop for fresh data

**❌ Manual re-checking on a fixed cadence:** repeated `sleep N && check` by hand, or blank keystrokes sent just to "flush" a process's output
**✅ Fix:** background the process and `wait` on it, or block on a log marker with a single bounded `timeout`

## When Arbitrary Timeout IS Correct

```typescript
// Tool ticks every 100ms - need 2 ticks to verify partial output
await waitForEvent(manager, 'TOOL_STARTED'); // First: wait for condition
await new Promise(r => setTimeout(r, 200));   // Then: wait for timed behavior
// 200ms = 2 ticks at 100ms intervals - documented and justified
```

**Requirements:**
1. First wait for triggering condition
2. Based on known timing (not guessing)
3. Comment explaining WHY

## Real-World Impact

From debugging session (2025-10-03):
- Fixed 15 flaky tests across 3 files
- Pass rate: 60% → 100%
- Execution time: 40% faster
- No more race conditions
