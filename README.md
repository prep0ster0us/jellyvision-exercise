# jellyvision-exercise
Take Home Programming Exercise for Jellyvision|Centric


# GitHub Activity Exercise

Analyzes a GitHub user's recent public activity and shows their three most common contribution types for each repository.
The program also identifies whether each repository is directly owned by the requested GitHub user.

## Requirements

- Python 3.10+

## Setup

Clone the repository, install the required dependencies and move into the project directory.

```bash
pip install -r requirements.txt
```

Optionally, create a virtual environment:

```bash
python -m venv .venv
```

## Usage

Run the program by providing a GitHub username as a positional argument:

```bash
python github_activity.py ge0ffrey
```

## Tests
Run the unit test suite with:
```bash
pytest
```

For more detailed output:
```bash
pytest -v
```