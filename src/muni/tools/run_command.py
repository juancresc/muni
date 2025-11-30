import re
import subprocess
from typing import Optional, Tuple

from . import BaseTool


class RunCommandTool(BaseTool):
    """
    Runs a shell command and returns the output.
    
    ## RunCommand
    
    Runs a shell command and returns the output.
    
    **Usage:**
    
    ```
    <RunCommand command="ls -la" />
    <RunCommand command="git status" />
    <RunCommand command="npm test" />
    ```
    
    **Attributes:**
    - command or cmd: The shell command to execute
    
    **Notes:**
    - Commands run in the project root directory
    - Timeout: 60 seconds
    - Both stdout and stderr are captured
    """

    RUNCOMMAND_RE = re.compile(r"<RunCommand\b([^>]*)/>", re.IGNORECASE)

    def process(self, mdx: str) -> Optional[Tuple[str, str]]:
        """Process RunCommand tags. Returns (full_results, summary) or None."""
        parts = []
        summaries = []
        for match in self.RUNCOMMAND_RE.finditer(mdx):
            attrs = self._parse_attrs(match.group(1))
            command = attrs.get("command") or attrs.get("cmd")
            if not command:
                continue
            
            output, success = self._run_command(command)
            status = "✓" if success else "✗"
            parts.append(f"=== Command: {command} ===\n{output}")
            summaries.append(f"⚡ RUN `{command}` [{status}]")
        
        if parts:
            return "\n\n".join(parts), "\n".join(summaries)
        return None

    def _run_command(self, command: str) -> Tuple[str, bool]:
        """Run a shell command and return (output, success)."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                timeout=60,
            )
            output = result.stdout
            if result.stderr:
                output += f"\n[stderr]\n{result.stderr}"
            if result.returncode != 0:
                output += f"\n[exit code: {result.returncode}]"
            return output.strip() or "(no output)", result.returncode == 0
        except subprocess.TimeoutExpired:
            return "(command timed out after 60s)", False
        except Exception as e:
            return f"(error: {e})", False
