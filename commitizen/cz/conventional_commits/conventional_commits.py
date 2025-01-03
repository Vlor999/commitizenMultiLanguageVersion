import os
import re

from commitizen import defaults
from commitizen.cz.base import BaseCommitizen
from commitizen.cz.conventional_commits.translation_multilanguage import (
    translate_text_from_eng,
)
from commitizen.cz.utils import multiple_line_breaker, required_validator
from commitizen.defaults import Questions

__all__ = ["ConventionalCommitsCz"]


def parse_scope(text):
    if not text:
        return ""

    scope = text.strip().split()
    if len(scope) == 1:
        return scope[0]

    return "-".join(scope)


def parse_subject(text):
    if isinstance(text, str):
        text = text.strip(".").strip()

    return required_validator(text, msg="Subject is required.")


class ConventionalCommitsCz(BaseCommitizen):
    bump_pattern = defaults.bump_pattern
    bump_map = defaults.bump_map
    bump_map_major_version_zero = defaults.bump_map_major_version_zero
    commit_parser = r"^((?P<change_type>feat|fix|refactor|perf|BREAKING CHANGE)(?:\((?P<scope>[^()\r\n]*)\)|\()?(?P<breaking>!)?|\w+!):\s(?P<message>.*)?"  # noqa
    change_type_map = {
        "feat": "Feat",
        "fix": "Fix",
        "refactor": "Refactor",
        "perf": "Perf",
    }
    changelog_pattern = defaults.bump_pattern

    def questions(self, language: str) -> Questions:
        questions: Questions = [
            {
                "type": "list",
                "name": "prefix",
                "message": translate_text_from_eng(
                    "Select the type of change you are committing", language, "prefix"
                ),
                "choices": [
                    {
                        "value": "fix",
                        "name": "fix: "
                        + translate_text_from_eng(
                            "A bug fix. Correlates with PATCH in SemVer",
                            language,
                            "fix",
                        ),
                        "key": "x",
                    },
                    {
                        "value": "feat",
                        "name": "feat: "
                        + translate_text_from_eng(
                            "A new feature. Correlates with MINOR in SemVer",
                            language,
                            "feat",
                        ),
                        "key": "f",
                    },
                    {
                        "value": "docs",
                        "name": "docs: "
                        + translate_text_from_eng(
                            "Documentation only changes", language, "docs"
                        ),
                        "key": "d",
                    },
                    {
                        "value": "style",
                        "name": "style: "
                        + translate_text_from_eng(
                            """Changes that do not affect the meaning of the code (white-space, formatting,  missing semi-colons, etc)""",
                            language,
                            "style",
                        ),
                        "key": "s",
                    },
                    {
                        "value": "refactor",
                        "name": "refactor: "
                        + translate_text_from_eng(
                            """A code change that neither fixes a bug nor adds a feature""",
                            language,
                            "refactor",
                        ),
                        "key": "r",
                    },
                    {
                        "value": "perf",
                        "name": "perf: "
                        + translate_text_from_eng(
                            "A code change that improves performance", language, "perf"
                        ),
                        "key": "p",
                    },
                    {
                        "value": "test",
                        "name": "test: "
                        + translate_text_from_eng(
                            "Adding missing or correcting existing tests",
                            language,
                            "test",
                        ),
                        "key": "t",
                    },
                    {
                        "value": "build",
                        "name": "build: "
                        + translate_text_from_eng(
                            """Changes that affect the build system or external dependencies (example scopes: pip, docker, npm)""",
                            language,
                            "build",
                        ),
                        "key": "b",
                    },
                    {
                        "value": "ci",
                        "name": "ci: "
                        + translate_text_from_eng(
                            """Changes to CI configuration files and scripts (example scopes: GitLabCI)""",
                            language,
                            "ci",
                        ),
                        "key": "c",
                    },
                ],
            },
            {
                "type": "input",
                "name": "scope",
                "message": translate_text_from_eng(
                    "What is the scope of this change? (class or file name): (press [enter] to skip)\n",
                    language,
                    "scope",
                ),
                "filter": parse_scope,
            },
            {
                "type": "input",
                "name": "subject",
                "filter": parse_subject,
                "message": translate_text_from_eng(
                    "Write a short and imperative summary of the code changes: (lower case and no period)\n",
                    language, "subject"),
            },
            {
                "type": "input",
                "name": "body",
                "message": (
                    "Provide additional contextual information about the code changes: (press [enter] to skip)\n"
                ),
                "filter": multiple_line_breaker,
            },
            {
                "type": "confirm",
                "message": "Is this a BREAKING CHANGE? Correlates with MAJOR in SemVer",
                "name": "is_breaking_change",
                "default": False,
            },
            {
                "type": "input",
                "name": "footer",
                "message": (
                    "Footer. Information about Breaking Changes and "
                    "reference issues that this commit closes: (press [enter] to skip)\n"
                ),
            },
        ]
        return questions

    def message(self, answers: dict) -> str:
        prefix = answers["prefix"]
        scope = answers["scope"]
        subject = answers["subject"]
        body = answers["body"]
        footer = answers["footer"]
        is_breaking_change = answers["is_breaking_change"]

        if scope:
            scope = f"({scope})"
        if body:
            body = f"\n\n{body}"
        if is_breaking_change:
            footer = f"BREAKING CHANGE: {footer}"
        if footer:
            footer = f"\n\n{footer}"

        message = f"{prefix}{scope}: {subject}{body}{footer}"

        return message

    def example(self) -> str:
        return (
            "fix: correct minor typos in code\n"
            "\n"
            "see the issue for details on the typos fixed\n"
            "\n"
            "closes issue #12"
        )

    def schema(self) -> str:
        return (
            "<type>(<scope>): <subject>\n"
            "<BLANK LINE>\n"
            "<body>\n"
            "<BLANK LINE>\n"
            "(BREAKING CHANGE: )<footer>"
        )

    def schema_pattern(self) -> str:
        PATTERN = (
            r"(?s)"  # To explicitly make . match new line
            r"(build|ci|docs|feat|fix|perf|refactor|style|test|chore|revert|bump)"  # type
            r"(\(\S+\))?!?:"  # scope
            r"( [^\n\r]+)"  # subject
            r"((\n\n.*)|(\s*))?$"
        )
        return PATTERN

    def info(self) -> str:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        filepath = os.path.join(dir_path, "conventional_commits_info.txt")
        with open(filepath, encoding=self.config.settings["encoding"]) as f:
            content = f.read()
        return content

    def process_commit(self, commit: str) -> str:
        pat = re.compile(self.schema_pattern())
        m = re.match(pat, commit)
        if m is None:
            return ""
        return m.group(3).strip()
