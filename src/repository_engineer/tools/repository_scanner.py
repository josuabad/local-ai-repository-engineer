from pathlib import Path
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class RepositoryScannerInput(BaseModel):
    path: str = Field(
        ..., description="Absolute or relative path to the repository to analyze."
    )


class RepositoryScanner(BaseTool):
    name: str = "repository_scanner"
    description: str = (
        "Scans a software repository and returns its structure, "
        "files, directories, detected languages and test files."
    )
    args_schema: type[BaseModel] = RepositoryScannerInput

    ignored_directories: set[str] = {
        ".git",
        ".venv",
        "venv",
        "node_modules",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".idea",
        ".vscode",
        "dist",
        "build",
    }

    def _run(self, path: str) -> str:
        repository = Path(path).resolve()

        if not repository.exists():
            return f"Repository does not exist: {repository}"

        if not repository.is_dir():
            return f"Path is not a directory: {repository}"

        files = []
        directories = []
        test_files = []

        for current_path in repository.rglob("*"):
            relative_path = current_path.relative_to(repository)

            if any(part in self.ignored_directories for part in relative_path.parts):
                continue

            if current_path.is_dir():
                directories.append(str(relative_path))

            elif current_path.is_file():
                files.append(str(relative_path))

                if (
                    "test" in current_path.name.lower()
                    or "tests" in relative_path.parts
                ):
                    test_files.append(str(relative_path))

        languages = self._detect_languages(files)

        result = [
            f"Repository: {repository}",
            "",
            f"Total files: {len(files)}",
            f"Total directories: {len(directories)}",
            "",
            "Languages:",
        ]

        for language, count in sorted(languages.items()):
            result.append(f"- {language}: {count}")

        result.extend(
            [
                "",
                "Directories:",
            ]
        )

        for directory in sorted(directories):
            result.append(f"- {directory}")

        result.extend(
            [
                "",
                "Files:",
            ]
        )

        for file in sorted(files):
            result.append(f"- {file}")

        result.extend(
            [
                "",
                "Test files:",
            ]
        )

        if test_files:
            for test_file in sorted(test_files):
                result.append(f"- {test_file}")
        else:
            result.append("- None detected")

        return "\n".join(result)

    @staticmethod
    def _detect_languages(files: list[str]) -> dict[str, int]:
        extensions = {
            ".py": "Python",
            ".js": "JavaScript",
            ".jsx": "JavaScript/React",
            ".ts": "TypeScript",
            ".tsx": "TypeScript/React",
            ".java": "Java",
            ".kt": "Kotlin",
            ".go": "Go",
            ".rs": "Rust",
            ".c": "C",
            ".cpp": "C++",
            ".h": "C/C++",
            ".cs": "C#",
            ".rb": "Ruby",
            ".php": "PHP",
            ".swift": "Swift",
            ".sql": "SQL",
            ".sh": "Shell",
            ".ps1": "PowerShell",
            ".html": "HTML",
            ".css": "CSS",
            ".md": "Markdown",
            ".json": "JSON",
            ".yaml": "YAML",
            ".yml": "YAML",
            ".xml": "XML",
        }

        languages: dict[str, int] = {}

        for file in files:
            extension = Path(file).suffix.lower()

            if extension in extensions:
                language = extensions[extension]
                languages[language] = languages.get(language, 0) + 1

        return languages


# if __name__ == "__main__":
#     scanner = RepositoryScanner()
#     result = scanner._run(".")
#     print(result)
