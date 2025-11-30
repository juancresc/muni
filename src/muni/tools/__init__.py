import importlib
import inspect
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class BaseTool(ABC):
    """Base class for all tools."""
    
    ATTRS_RE = re.compile(r'(\w+)="([^"]*)"')
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
    
    @abstractmethod
    def process(self, mdx: str) -> Optional[Tuple[str, str]]:
        """
        Process MDX content and execute the tool if matching tags are found.
        
        Returns (full_results, summary) or None if no matching tags.
        """
        pass
    
    def _parse_attrs(self, attrs_str: str) -> Dict[str, str]:
        """Parse attributes string into a dictionary."""
        attrs = {}
        for match in self.ATTRS_RE.finditer(attrs_str):
            attrs[match.group(1)] = match.group(2)
        return attrs


class ToolsManager:
    """Manages all available tools and processes MDX content."""
    
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self._tools: List[BaseTool] = []
        self._discover_tools()
    
    def _discover_tools(self) -> None:
        """Dynamically discover and register all tools in the tools directory."""
        tools_dir = Path(__file__).parent
        
        for file in tools_dir.glob("*.py"):
            if file.name.startswith("_"):
                continue
            
            module_name = f".{file.stem}"
            module = importlib.import_module(module_name, package=__package__)
            
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, BaseTool) and obj is not BaseTool:
                    self._tools.append(obj(self.base_dir))
    
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


__all__ = ["BaseTool", "ToolsManager"]
