import re
from typing import Dict, Optional, Tuple
from pathlib import Path


class ReadFileTool:

    ATTRS_RE = re.compile(r'(\w+)="([^"]*)"')
    READFILE_RE = re.compile(r"<ReadFile\b([^>]*)/>", re.IGNORECASE)
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

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

    def _parse_attrs(self, attrs_str: str) -> Dict[str, str]:
        """Parse attributes string into a dictionary."""
        attrs = {}
        for match in self.ATTRS_RE.finditer(attrs_str):
            attrs[match.group(1)] = match.group(2)
        return attrs

    def _read_file(self, file_path: str) -> Optional[str]:
        """Read and return the contents of a file."""
        target = self.base_dir / file_path
        if not target.exists():
            return None
        if not target.is_file():
            return None
        return target.read_text(encoding="utf-8")

