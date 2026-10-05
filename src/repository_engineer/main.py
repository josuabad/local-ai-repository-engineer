import sys

from crewai import Agent, LLM, Task

from repository_engineer.tools.repository_scanner import RepositoryScanner
from repository_engineer.tools.file_reader import FileReader
from repository_engineer.report_writer import ReportWriter


def main():
    if len(sys.argv) != 2:
        print("Usage: python -m repository_engineer.main <repository>")
        sys.exit(1)

    repository_path = sys.argv[1]

    llm = LLM(
        model="ollama/gemma4:e4b",
        base_url="http://localhost:11434",
    )

    scanner = RepositoryScanner()
    file_reader = FileReader(root_path=repository_path)

    agent = Agent(
        role="Senior Software Engineer",
        goal=(
            "Analyze software repositories and identify "
            "their architecture, technologies and structure."
        ),
        backstory=(
            "You are an experienced software engineer specialized "
            "in understanding existing codebases."
        ),
        llm=llm,
        tools=[
            scanner,
            file_reader,
        ],
        verbose=True,
    )

    task = Task(
        description=f"""
    Analyze the software repository located at:

    {repository_path}

    Your objective is to understand the repository and produce
    a useful technical analysis.

    Follow this process:

    1. Use the repository_scanner tool to understand the repository structure.
    2. Identify the most important source code files.
    3. Use the file_reader tool to inspect those files.
    4. Understand the main application components.
    5. Identify how the components interact.
    6. Analyze the testing structure.
    7. Analyze configuration and dependencies.
    8. Identify potential architectural or maintainability concerns.

    Do not modify any repository files.

    Produce the final answer as a Markdown technical report.

    The report MUST contain these sections:

    # Repository Analysis

    ## Overview

    ## Technologies

    ## Project Structure

    ## Architecture

    ## Main Components

    ## Data Flow

    ## Testing

    ## Configuration and Dependencies

    ## Potential Issues

    ## Recommendations
    """,
        expected_output=("A complete Markdown technical report about the repository."),
        agent=agent,
    )

    result = task.execute_sync()

    writer = ReportWriter()

    output_path = writer.write(
        content=str(result),
        filename="repository_analysis.md",
    )

    print("\n\n===== REPORT GENERATED =====\n")
    print(output_path)


if __name__ == "__main__":
    main()
