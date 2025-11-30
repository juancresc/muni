import re
from typing import Dict, Optional, List, Tuple
from pathlib import Path


class ListDirTool:

    ATTRS_RE = re.compile(r'(\w+)="([^"]*)"')
    LISTDIR_RE = re.compile(r"<ListDir\b([^>]*)/>", re.IGNORECASE)
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def process(self, mdx: str) -> Optional[Tuple[str, str]]:
        """Process ListDir tags. Returns (full_results, summary) or None."""
        parts: List[str] = []
        summaries: List[str] = []
        for match in self.LISTDIR_RE.finditer(mdx):
            attrs = self._parse_attrs(match.group(1))
            dir_path = attrs.get("path") or "."
            
            content, count = self._list_dir(dir_path)
            if content is not None:
                parts.append(f"=== Directory: {dir_path} ===\n{content}")
                summaries.append(f"📁 LISTED {dir_path}/ ({count} items)")
            else:
                parts.append(f"=== Directory: {dir_path} ===\n(Directory not found)")
                summaries.append(f"❌ {dir_path}/ (not found)")
        
        if parts:
            return "\n\n".join(parts), "\n".join(summaries)
        return None

    def _parse_attrs(self, attrs_str: str) -> Dict[str, str]:
        """Parse attributes string into a dictionary."""
        attrs: Dict[str, str] = {}
        for match in self.ATTRS_RE.finditer(attrs_str):
            attrs[match.group(1)] = match.group(2)
        return attrs

    def _list_dir(self, dir_path: str) -> Tuple[Optional[str], int]:
        """List contents of a directory. Returns (content, count)."""
        target = self.base_dir / dir_path
        if not target.exists():
            return None, 0
        if not target.is_dir():
            return None, 0
        
        entries: List[str] = []
        for item in sorted(target.iterdir()):
            if item.is_dir():
                entries.append(f"{item.name}/")
            else:
                entries.append(item.name)
        
        content = "\n".join(entries) if entries else "(empty)"
        return content, len(entries)

