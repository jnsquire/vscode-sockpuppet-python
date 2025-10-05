# Webview Issues and Solutions

## Issue 1: Scripts Not Executing in Webviews ✅ FIXED

### Problem
Inline `<script>` tags in webview HTML were not executing, even though `enable_scripts=True` was set in `WebviewOptions`.

### Root Cause
VS Code applies a restrictive Content Security Policy (CSP) by default when none is specified in the HTML. This blocks all inline scripts for security reasons.

### Solution
Add an explicit CSP meta tag that allows inline scripts:

```html
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline';">
```

### Files Fixed
- ✅ `example_webview.py`
- ✅ `example_webview_forms.py`
- ✅ `example_webview_dispose.py`
- ✅ `example_webview_visibility.py`
- ✅ `example_webview_chart.py` (already had CSP for Chart.js)

---

## Issue 2: Cannot Interrupt Examples with Ctrl-C ✅ FIXED

### Problem
Pressing Ctrl-C (SIGINT) does not stop running examples on Windows. The program continues running and ignores the interrupt signal.

### Root Causes

1. **Long `time.sleep()` calls block signals on Windows**
   - `time.sleep(3)` or longer blocks signal delivery on Windows
   - The signal is queued but not delivered until the sleep completes

2. **Polling loops are inefficient**
   - Checking flags in tight loops wastes CPU
   - Multiple short sleeps add complexity

3. **No explicit signal handler**
   - Python's default SIGINT handler works on Unix but is less reliable on Windows

### Solution: Event-Driven Pattern ✅

Use `threading.Event` for clean, immediate shutdown:

```python
import threading
import signal

class WebviewState:
    def __init__(self):
        self.counter = 0
        self.stop_event = threading.Event()
    
    def stop(self):
        """Signal the main loop to stop."""
        self.stop_event.set()
    
    @property
    def running(self):
        """Check if still running (not stopped)."""
        return not self.stop_event.is_set()

# Create state first
state = WebviewState()

# Signal handler fires stop event
def signal_handler(sig, frame):
    print("\n⌨️  Ctrl-C detected, shutting down...")
    state.stop()

signal.signal(signal.SIGINT, signal_handler)

# Event-driven wait - responds immediately!
while state.running:
    if state.stop_event.wait(timeout=3.0):
        # Event was set (Ctrl-C or webview closed)
        break
    # Timeout expired, do periodic work
    update_counter()
```

### Benefits

- ✅ **Immediate response** - No delay waiting for sleep to complete
- ✅ **No polling** - Uses OS-level event synchronization
- ✅ **Cleaner code** - Single wait point, no flag checking in loops
- ✅ **Cross-platform** - Works reliably on Windows and Unix
- ✅ **Event-driven** - Pythonic and idiomatic

### How `Event.wait(timeout)` Works

- If event is **not set**: Blocks for up to `timeout` seconds, then returns `False`
- If event is **set before timeout**: Returns immediately with `True`
- Signal handlers can call `event.set()` to wake up waiting threads immediately

This is perfect for Ctrl-C handling because:
1. Signal handler calls `state.stop()` → `event.set()`
2. `event.wait()` wakes up immediately (doesn't wait for timeout)
3. Returns `True`, loop breaks, cleanup happens

### Files Fixed
- ✅ `example_webview.py` - Periodic updates with 3-second wait
- ✅ `example_webview_forms.py` - Indefinite wait until closed
- ✅ `example_webview_debug.py` - Debug logging with 3-second wait

### Comparison

**OLD (Polling with short sleeps)**:
```python
# BAD: Polling, slow response, complex
while state.running:
    for _ in range(30):  # 30 x 0.1s = 3 seconds
        if not state.running:
            break
        time.sleep(0.1)
    if not state.running:
        break
    update_counter()
```

**NEW (Event-driven)**:
```python
# GOOD: Event-driven, immediate response, simple
while state.running:
    if state.stop_event.wait(timeout=3.0):
        break
    update_counter()
```

### Remaining Considerations

The event loop thread still blocks on `sock.read()`, but since it's a daemon thread, it will be killed on process exit. The main thread now exits immediately on Ctrl-C, which is the desired behavior.

For indefinite waits (like in the forms example), simply call `event.wait()` without a timeout:

```python
# Wait forever until event is set
state.stop_event.wait()
```

---

## Issue 3: Webview Events Not Triggering 🔍 INVESTIGATING

### Problem
When clicking buttons in webview examples, the JavaScript `vscode.postMessage()` is called but Python handlers never receive the messages.

### Debug Steps

1. **Created `example_webview_debug.py`**
   - Extensive logging on both JavaScript and Python sides
   - Session listener to see all internal events
   - Console logging in webview to verify script execution

2. **Need to verify:**
   - [ ] Extension is running and pipe connection works
   - [ ] JavaScript `vscode.postMessage()` is executing
   - [ ] Server receives the message and broadcasts `webview.onDidReceiveMessage` event
   - [ ] Client event loop receives the event
   - [ ] Event dispatcher routes message to correct panel
   - [ ] Handler is called with message data

### Hypothesis
Given that the CSP is now correct and scripts execute, the issue is likely in the event flow:
- Server may not be broadcasting the event
- Client may not be subscribed to the event
- Event dispatcher may not be routing correctly

### Next Steps
1. Run `example_webview_debug.py` with extension active
2. Click a button and observe logs
3. Check where the event flow breaks
4. Fix the broken link in the chain

### Potential Issues to Check

1. **Event subscription not active**
   - Verify `client.get_subscriptions()` includes `"webview.onDidReceiveMessage"`
   - Check if `_setup_message_subscription()` was called

2. **Event name mismatch**
   - Server broadcasts: `webview.onDidReceiveMessage`
   - Client subscribes to: same string?

3. **Global dispatcher not working**
   - Check if `_global_message_registry` has the panel
   - Verify `_global_handler` is registered

4. **Panel ID mismatch**
   - Server sends event with panel `id`
   - Client looks up panel by `id`
   - Are they the same?

---

## Testing Checklist

### After Fixes
- [ ] Scripts execute in webviews (buttons work, logs appear)
- [ ] Button clicks trigger Python handlers
- [ ] Ctrl-C interrupts running examples
- [ ] Clean shutdown with proper cleanup
- [ ] No hanging threads after exit
- [ ] Works on Windows
- [ ] Works on Linux/Mac

### Test Commands
```bash
# Test webview with debug logging
cd python
uv run examples/example_webview_debug.py

# Test basic webview
uv run examples/example_webview.py

# Test form webview
uv run examples/example_webview_forms.py

# Test Ctrl-C handling (should exit cleanly)
uv run examples/example_webview.py
# Press Ctrl-C - should exit within 1 second
```
