from pathlib import Path

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class FileReaderInput(BaseModel):
    path: str = Field(..., description="Path to the file that should be read.")


class FileReader(BaseTool):
    name: str = "file_reader"
    description: str = "Reads text files inside the target repository."
    args_schema: type[BaseModel] = FileReaderInput
    root_path: str = ""
    max_file_size: int = 100_000

    def _run(self, path: str) -> str:
        root = Path(self.root_path).resolve()
        file_path = Path(path).resolve()

        try:
            file_path.relative_to(root)
        except ValueError:
            return f"Access denied. The file is outside " f"the repository: {file_path}"

        if not file_path.exists():
            return f"File does not exist: {file_path}"

        if not file_path.is_file():
            return f"Path is not a file: {file_path}"

        if file_path.stat().st_size > self.max_file_size:
            return (
                f"File is too large to read directly: {file_path} "
                f"({file_path.stat().st_size} bytes)"
            )

        try:
            content = file_path.read_text(
                encoding="utf-8",
                errors="replace",
            )
        except Exception as exc:
            return f"Could not read file: {exc}"

        return f"===== FILE: {file_path} =====\n\n" f"{content}"


# if __name__ == "__main__":
#     reader = FileReader()
#     result = reader._run("src/repository_engineer/main.py")
#     print(result)
