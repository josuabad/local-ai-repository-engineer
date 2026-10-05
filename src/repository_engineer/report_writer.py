from pathlib import Path


class ReportWriter:
    """Writes repository analysis reports to disk."""

    def __init__(self, output_directory: str = "reports"):
        self.output_directory = Path(output_directory)

    def write(
        self,
        content: str,
        filename: str = "repository_analysis.md",
    ) -> Path:
        self.output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path = self.output_directory / filename

        output_path.write_text(
            content,
            encoding="utf-8",
        )

        return output_path
