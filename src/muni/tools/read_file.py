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
    ```
    
    **Attributes:**
    - file or path: Path to the file to read (relative to project root)
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
            content = self._read_file(file_path)
            if content is not None:
                parts.append(f"=== File: {file_path} ===\n{content}")
                summaries.append(f"📄 READ {file_path}")
            else:
                parts.append(f"=== File: {file_path} ===\n(File not found)")
                summaries.append(f"❌ {file_path} (not found)")
        
        if parts:
            return "\n\n".join(parts), "\n".join(summaries)
        return None

    def _read_file(self, file_path: str) -> Optional[str]:
        """Read and return the contents of a file."""
        target = self.base_dir / file_path
        if not target.exists():
            return None
        if not target.is_file():
            return None
        return target.read_text(encoding="utf-8")
