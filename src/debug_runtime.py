"""
Debug runtime for Frscript
Adds debugging capabilities to the interpreter
"""
import sys
import json
from typing import Any, Dict, Set, List, Optional
from parser import parse
from runtime import run, get_current_vars, funcs as runtime_funcs

class DebugRuntime:
    """Enhanced runtime with debugging support"""

    def __init__(self):
        self.breakpoints: Set[int] = set()
        self.current_line: int = 0
        self.last_paused_line: int = -1
        self.current_file: str = ''
        self.paused: bool = False
        self.step_mode: Optional[str] = None  # 'over', 'in', 'out', None
        self.call_stack: List[Dict[str, Any]] = []
        self.call_depth: int = 0
        self.step_depth: int = 0
        self.commands: List[str] = []
        self.stop_on_entry: bool = False
        self.started: bool = False

    def log_debug(self, message: str):
        """Send debug protocol message to debug adapter"""
        print(f"DEBUG:{message}", flush=True)

    def log_output(self, text: str):
        """Send regular output"""
        print(text, end='', flush=True)

    def add_breakpoint(self, file: str, line: int):
        """Add a breakpoint at the specified line"""
        self.breakpoints.add(line)
        self.log_debug(f"breakpoint_added:{file}:{line}")

    def remove_breakpoint(self, file: str, line: int):
        """Remove a breakpoint"""
        self.breakpoints.discard(line)

    def clear_breakpoints(self, file: str):
        """Clear all breakpoints for a file"""
        self.breakpoints.clear()

    def should_pause(self, line: int) -> bool:
        """Check if execution should pause at this line"""
        # Don't pause on the same line we just paused at (for stepping)
        if self.step_mode and line == self.last_paused_line:
            return False
            
        # Pause on entry at first line - but skip global scope (depth 0)
        # We want to pause at first line inside main function (depth 1)
        if self.stop_on_entry and not self.started:
            # Only pause if we're inside a function (depth > 0)
            if self.call_depth > 0:
                self.started = True
                self.log_debug(f"pausing_on_entry:{line}")
                return True
            # At global scope, don't pause yet
            return False
            
        # Always pause at breakpoints
        if line in self.breakpoints:
            self.log_debug(f"pausing_at_breakpoint:{line}")
            return True
            
        # Check step mode
        if self.step_mode == 'over':
            # Pause at next statement at same or shallower depth
            # Special case: if step_depth is 0 (global), allow depth 1 (main function)
            if self.call_depth <= self.step_depth or (self.step_depth == 0 and self.call_depth == 1):
                self.log_debug(f"pausing_on_step:{line}")
                return True
        elif self.step_mode == 'in':
            # Pause at next statement regardless of depth
            self.log_debug(f"pausing_on_step:{line}")
            return True
        elif self.step_mode == 'out':
            # Pause when we return to shallower depth
            if self.call_depth < self.step_depth:
                self.log_debug(f"pausing_on_step:{line}")
                return True

        return False

    def notify_line(self, line: int):
        """Notify that execution reached a line"""
        self.current_line = line
        self.log_debug(f"line:{line}:breakpoints:{sorted(self.breakpoints)}")
        
        # Send variables on every line update so Variables pane updates in real-time
        self.send_variables()

        if self.should_pause(line):
            self.pause_execution()

    def notify_call(self, func_name: str):
        """Notify that a function was called"""
        self.call_depth += 1
        self.log_debug(f"call:{func_name}")

    def notify_return(self):
        """Notify that a function returned"""
        self.call_depth -= 1
        self.log_debug("return")

    def send_variables(self):
        """Send current variable state"""
        local_vars = {}
        global_vars = {}

        # Get current variables from runtime
        current_vars = get_current_vars()
        
        for name, var_data in current_vars.items():
            value = var_data.get('value')
            # Serialize the value
            try:
                if isinstance(value, (int, float, str, bool, type(None))):
                    serialized = value
                elif isinstance(value, list):
                    serialized = [self.serialize_value(v) for v in value]
                elif isinstance(value, dict):
                    serialized = {k: self.serialize_value(v) for k, v in value.items()}
                else:
                    serialized = str(value)

                # Determine if variable is local or global based on call depth
                # Variables defined inside functions (depth > 0) are local
                if self.call_depth > 0:
                    local_vars[name] = serialized
                else:
                    global_vars[name] = serialized
            except Exception as e:
                if self.call_depth > 0:
                    local_vars[name] = f"<error: {e}>"
                else:
                    global_vars[name] = f"<error: {e}>"

        self.log_debug(f"vars:local:{json.dumps(local_vars)}")
        self.log_debug(f"vars:global:{json.dumps(global_vars)}")

    def serialize_value(self, value: Any) -> Any:
        """Serialize a value for JSON transmission"""
        if isinstance(value, (int, float, str, bool, type(None))):
            return value
        elif isinstance(value, list):
            return [self.serialize_value(v) for v in value]
        elif isinstance(value, dict):
            if 'type' in value and value.get('type') == 'struct_def':
                return '<struct definition>'
            return {k: self.serialize_value(v) for k, v in value.items()}
        else:
            return str(value)

    def pause_execution(self):
        """Pause execution and wait for command"""
        self.paused = True
        self.last_paused_line = self.current_line
        self.send_variables()

        # Read command from stdin (sent by debugger)
        import sys
        
        while self.paused:
            try:
                # Blocking read from stdin
                line = sys.stdin.readline()
                if line:
                    self.handle_command(line.strip())
                else:
                    # EOF - debugger disconnected, just continue
                    self.paused = False
                    break
            except (EOFError, KeyboardInterrupt):
                # Debugger disconnected or user interrupted
                self.paused = False
                break
            except Exception as e:
                self.log_debug(f"error:Failed to read command: {e}")
                self.paused = False
                break

    def handle_command(self, command: str):
        """Handle a debug command from the adapter"""
        self.log_debug(f"cmd:{command}")  # Log received command
        parts = command.split(':')
        cmd_type = parts[0]

        if cmd_type == 'stopOnEntry':
            self.stop_on_entry = True

        elif cmd_type == 'continue':
            self.paused = False
            self.step_mode = None

        elif cmd_type == 'step':
            self.paused = False
            self.step_mode = 'over'
            # Set step_depth to current depth so we'll pause at next line at same or shallower depth
            # BUT also allow stepping into the first function call
            self.step_depth = self.call_depth

        elif cmd_type == 'stepIn':
            self.paused = False
            self.step_mode = 'in'

        elif cmd_type == 'stepOut':
            self.paused = False
            self.step_mode = 'out'
            self.step_depth = self.call_depth

        elif cmd_type == 'pause':
            self.paused = True

        elif cmd_type == 'breakpoint':
            # breakpoint:file:line
            file = parts[1]
            line = int(parts[2])
            self.add_breakpoint(file, line)

        elif cmd_type == 'clearBreakpoints':
            file = parts[1]
            self.clear_breakpoints(file)

        elif cmd_type == 'evaluate':
            expr = ':'.join(parts[1:])
            try:
                # Try to evaluate in current context
                current_vars = get_current_vars()
                result = eval(expr, {'vars': current_vars, 'funcs': runtime_funcs})
                self.log_debug(f"evalResult:{json.dumps(result)}")
            except Exception as e:
                self.log_debug(f"evalError:{str(e)}")

        elif cmd_type == 'setVar':
            # setVar:scope:name:value
            scope = parts[1]
            name = parts[2]
            value = ':'.join(parts[3:])
            try:
                current_vars = get_current_vars()
                parsed_value = json.loads(value)
                if name in current_vars:
                    current_vars[name]['value'] = parsed_value
            except Exception as e:
                self.log_debug(f"error:Failed to set variable: {e}")


# Global debug runtime instance
debug_runtime: Optional[DebugRuntime] = None

def init_debug_runtime():
    """Initialize the debug runtime"""
    global debug_runtime
    debug_runtime = DebugRuntime()
    
    # Register with runtime module
    import runtime
    runtime.set_debug_runtime(debug_runtime)
    
    return debug_runtime

def run_with_debug(ast: list, file: str = '<stdin>'):
    """Run AST with debugging enabled"""
    global debug_runtime

    if debug_runtime is None:
        debug_runtime = init_debug_runtime()

    debug_runtime.current_file = file

    # Wait for initial commands (breakpoints, stopOnEntry, etc.)
    # Read commands until we get a signal to start or timeout
    import sys
    import select
    
    # Read initial setup commands (non-blocking with timeout)
    while True:
        # Check if there's input available (with 100ms timeout)
        if sys.stdin in select.select([sys.stdin], [], [], 0.1)[0]:
            line = sys.stdin.readline().strip()
            if line:
                # Process setup commands
                if line in ['stopOnEntry', 'breakpoint:', 'clearBreakpoints:'] or line.startswith('breakpoint:') or line.startswith('clearBreakpoints:'):
                    debug_runtime.handle_command(line)
                else:
                    # Non-setup command, put it back somehow or just ignore for now
                    # For now, we'll assume any other command means "start execution"
                    break
            else:
                break
        else:
            # No more input available, start execution
            break

    # Inject debug hooks into the runtime
    # This is a simplified version - you'll need to integrate this with runtime.py
    try:
        # Run the program - debug hooks in runtime.py will handle line notifications
        run(ast)

    except Exception as e:
        debug_runtime.log_debug(f"error:{str(e)}")
        raise
