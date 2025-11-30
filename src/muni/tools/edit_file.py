import re
from typing import Optional, Tuple

from . import BaseTool


class EditFileTool(BaseTool):
    """
    Edits file contents by replacing lines in a specified range.
    
    ## EditFile
    
    Replaces content between start and end line numbers in a file.
    
    **IMPORTANT:** Before editing, you MUST first read the lines you intend to modify
    using ReadFile with the same start and end range. This ensures you have the current
    state of the file and can make accurate edits.
    
    **Workflow:**
    1. First, read the target lines: `<ReadFile file="path" start="X" end="Y" />`
    2. Review the content and plan your changes
    3. Then edit: `<EditFile file="path" start="X" end="Y">new content</EditFile>`
    
    **Usage:**
    
    ```
    <EditFile file="app/page.tsx" start="10" end="50">
    replacement content goes here
    </EditFile>
    
    <EditFile path="components/header.tsx" start="5" end="5">
    single line replacement
    </EditFile>
    ```
    
    **Attributes:**
    - file or path: Path to the file to edit (relative to project root)
    - start: Starting line number (1-based, inclusive)
    - end: Ending line number (1-based, inclusive)
    
    The content between the tags will replace lines from start to end (inclusive).
    """

    EDITFILE_RE = re.compile(
        r"<EditFile\b([^>]*)>(.*?)</EditFile>",
        re.IGNORECASE | re.DOTALL
    )

    def process(self, mdx: str) -> Optional[Tuple[str, str]]:
        """Process EditFile tags. Returns (full_results, summary) or None."""
        parts = []
        summaries = []
        
        for match in self.EDITFILE_RE.finditer(mdx):
            attrs = self._parse_attrs(match.group(1))
            content = match.group(2)
            
            file_path = attrs.get("file") or attrs.get("path")
            start = attrs.get("start")
            end = attrs.get("end")
            
            if not file_path:
                parts.append("=== EditFile Error ===\nMissing file/path attribute")
                summaries.append("❌ EditFile: missing file/path")
                continue
            
            if not start or not start.isdigit():
                parts.append(f"=== EditFile Error: {file_path} ===\nMissing or invalid start line")
                summaries.append(f"❌ EditFile {file_path}: invalid start")
                continue
            
            if not end or not end.isdigit():
                parts.append(f"=== EditFile Error: {file_path} ===\nMissing or invalid end line")
                summaries.append(f"❌ EditFile {file_path}: invalid end")
                continue
            
            start_line = int(start)
            end_line = int(end)
            
            # Strip the first newline if content starts with one (common formatting)
            if content.startswith("\n"):
                content = content[1:]
            
            result = self._edit_file(file_path, start_line, end_line, content)
            if result is True:
                parts.append(f"=== Edited: {file_path} (lines {start_line}-{end_line}) ===\nSuccessfully replaced content")
                summaries.append(f"✏️ EDITED {file_path} (lines {start_line}-{end_line})")
            else:
                parts.append(f"=== EditFile Error: {file_path} ===\n{result}")
                summaries.append(f"❌ {file_path}: {result}")
        
        if parts:
            return "\n\n".join(parts), "\n".join(summaries)
        return None

    def _edit_file(
        self, file_path: str, start: int, end: int, new_content: str
    ) -> bool | str:
        """
        Edit file by replacing lines from start to end with new_content.
        Returns True on success, or an error message string on failure.
        """
        target = self.base_dir / file_path
        
        if not target.exists():
            return "File not found"
        if not target.is_file():
            return "Path is not a file"
        
        if start < 1:
            return "Start line must be >= 1"
        if end < start:
            return "End line must be >= start line"
        
        try:
            original = target.read_text(encoding="utf-8")
            lines = original.splitlines(keepends=True)
            
            # Handle case where file doesn't end with newline
            if lines and not lines[-1].endswith("\n"):
                lines[-1] += "\n"
            
            total_lines = len(lines)
            if start > total_lines:
                return f"Start line {start} exceeds file length ({total_lines} lines)"
            if end > total_lines:
                return f"End line {end} exceeds file length ({total_lines} lines)"
            
            # Ensure new_content ends with newline for proper line handling
            if new_content and not new_content.endswith("\n"):
                new_content += "\n"
            
            # Convert 1-based to 0-based index
            start_idx = start - 1
            end_idx = end  # end is inclusive, so we slice up to end_idx
            
            # Build new content
            new_lines = lines[:start_idx]
            if new_content:
                new_lines.append(new_content)
            new_lines.extend(lines[end_idx:])
            
            # Write back
            result = "".join(new_lines)
            # Remove trailing newline if original didn't have one
            if not original.endswith("\n") and result.endswith("\n"):
                result = result[:-1]
            
            target.write_text(result, encoding="utf-8")
            return True
            
        except Exception as e:
            return f"Error: {e}"

