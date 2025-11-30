import re
from typing import Optional, List, Tuple

from . import BaseTool


class ListDirTool(BaseTool):
    """
    Lists contents of a directory.
    
    ## ListDir
    
    Lists contents of a directory.
    
    **Usage:**
    
    ```
    <ListDir path="." />
    <ListDir path="src/components" />
    ```
    
    **Attributes:**
    - path: Directory path to list (relative to project root, defaults to ".")
    """

    LISTDIR_RE = re.compile(r"<ListDir\b([^>]*)/>", re.IGNORECASE)

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
