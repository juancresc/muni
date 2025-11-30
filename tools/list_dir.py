import re
from typing import Dict, Optional, List
from pathlib import Path


class ListDirTool:

    ATTRS_RE = re.compile(r'(\w+)="([^"]*)"')
    LISTDIR_RE = re.compile(r"<ListDir\b([^>]*)/>", re.IGNORECASE)
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def process(self, mdx: str) -> Optional[str]:
        """Process ListDir tags and return formatted results."""
        parts: List[str] = []
        for match in self.LISTDIR_RE.finditer(mdx):
            attrs = self._parse_attrs(match.group(1))
            dir_path = attrs.get("path") or "."
            
            content = self._list_dir(dir_path)
            if content is not None:
                parts.append(f"=== Directory: {dir_path} ===\n{content}")
            else:
                parts.append(f"=== Directory: {dir_path} ===\n(Directory not found)")
        return "\n\n".join(parts) if parts else None

    def _parse_attrs(self, attrs_str: str) -> Dict[str, str]:
        """Parse attributes string into a dictionary."""
        attrs: Dict[str, str] = {}
        for match in self.ATTRS_RE.finditer(attrs_str):
            attrs[match.group(1)] = match.group(2)
        return attrs

    def _list_dir(self, dir_path: str) -> Optional[str]:
        """List contents of a directory."""
        target = self.base_dir / dir_path
        if not target.exists():
            print(f"[LISTDIR] {target} (directory does not exist)")
            return None
        if not target.is_dir():
            print(f"[LISTDIR] {target} (not a directory)")
            return None
        
        print(f"[LISTDIR] {target}")
        
        entries: List[str] = []
        for item in sorted(target.iterdir()):
            if item.is_dir():
                entries.append(f"{item.name}/")
            else:
                entries.append(item.name)
        
        return "\n".join(entries) if entries else "(empty)"
