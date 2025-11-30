from pathlib import Path
from typing import List, Optional, Tuple

from .read_file import ReadFileTool
from .list_dir import ListDirTool


class ToolsManager:
    """Manages all available tools and processes MDX content."""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self._tools = [
            ReadFileTool(base_dir),
            ListDirTool(base_dir),
        ]
    
    def process(self, mdx: str) -> Optional[Tuple[str, str]]:
        """
        Process MDX content and execute all matching tools.
        
        Returns (full_results, summary) or None if no tools matched.
        """
        full_parts: List[str] = []
        summary_parts: List[str] = []
        
        for tool in self._tools:
            result = tool.process(mdx)
            if result:
                full, summary = result
                full_parts.append(full)
                summary_parts.append(summary)
        
        if full_parts:
            return "\n\n".join(full_parts), "\n".join(summary_parts)
        return None


__all__ = ["ToolsManager", "ReadFileTool", "ListDirTool"]

