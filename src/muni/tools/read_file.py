import re
from typing import Optional, Tuple

from . import BaseTool


class ReadFileTool(BaseTool):
    """
    Reads file contents from the project.
    
    ## ReadFile
    
    Reads file contents from the project.
    
    **Usage:**
    
    ```
    <ReadFile file="app/page.tsx" />
    <ReadFile path="components/header.tsx" />
    <ReadFile file="app/page.tsx" start="10" end="50" />
    <ReadFile file="app/page.tsx" start="100" />
    ```
    
    **Attributes:**
    - file or path: Path to the file to read (relative to project root)
    - start: (optional) Starting line number (1-based, inclusive)
    - end: (optional) Ending line number (1-based, inclusive)
    """

    READFILE_RE = re.compile(r"<ReadFile\b([^>]*)/>", re.IGNORECASE)

    def process(self, mdx: str) -> Optional[Tuple[str, str]]:
        """Process ReadFile tags. Returns (full_results, summary) or None."""
        parts = []
        summaries = []
        for match in self.READFILE_RE.finditer(mdx):
            attrs = self._parse_attrs(match.group(1))
            file_path = attrs.get("file") or attrs.get("path")
            if not file_path:
                continue
            
            start = attrs.get("start")
            end = attrs.get("end")
            start_line = int(start) if start and start.isdigit() else None
            end_line = int(end) if end and end.isdigit() else None
            
            content = self._read_file(file_path, start_line, end_line)
            if content is not None:
                line_info = ""
                if start_line or end_line:
                    line_info = f" (lines {start_line or 1}-{end_line or 'end'})"
                parts.append(f"=== File: {file_path}{line_info} ===\n{content}")
                summaries.append(f"📄 READ {file_path}{line_info}")
            else:
                parts.append(f"=== File: {file_path} ===\n(File not found)")
                summaries.append(f"❌ {file_path} (not found)")
        
        if parts:
            return "\n\n".join(parts), "\n".join(summaries)
        return None

    def _read_file(
        self, file_path: str, start: Optional[int] = None, end: Optional[int] = None
    ) -> Optional[str]:
        """Read and return the contents of a file, optionally filtered by line range."""
        target = self.base_dir / file_path
        if not target.exists():
            return None
        if not target.is_file():
            return None
        
        content = target.read_text(encoding="utf-8")
        
        if start is not None or end is not None:
            lines = content.splitlines(keepends=True)
            # Convert 1-based to 0-based index
            start_idx = (start - 1) if start else 0
            end_idx = end if end else len(lines)
            lines = lines[start_idx:end_idx]
            content = "".join(lines)
        
        return content
