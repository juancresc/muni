from pathlib import Path
from typing import List

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
    
    def process(self, mdx: str) -> List[str]:
        """
        Process MDX content and execute all matching tools.
        
        Returns a list of formatted result strings.
        """
        results = []
        for tool in self._tools:
            result = tool.process(mdx)
            if result:
                results.append(result)
        return results
    
    def format_results(self, results: List[str]) -> str:
        """Join all tool results into a single string."""
        return "\n\n".join(results)


__all__ = ["ToolsManager", "ReadFileTool", "ListDirTool"]
