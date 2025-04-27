import re
from typing import List, Union, Any
from _pytest.capture import CaptureFixture
import pytest


def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences from text."""
    ansi_escape = re.compile(r"\x1b\[[0-9;]*[mK]")
    return ansi_escape.sub("", text)


class OutputChecker:
    """Helper for checking CLI output with flexible matching options."""

    def __init__(self, capsys: CaptureFixture[Any]):
        self.capsys = capsys
        self._captured = None
        self._clean_out = None
        self._clean_err = None

    def capture(self) -> "OutputChecker":
        """Capture and process stdout/stderr."""
        self._captured = self.capsys.readouterr()  # type: ignore [assignment]
        self._clean_out = strip_ansi(self._captured.out)  # type: ignore [assignment, attr-defined]
        self._clean_err = strip_ansi(self._captured.err)  # type: ignore [assignment, attr-defined]
        return self

    @property
    def out(self) -> str | None:
        """Get clean stdout output."""
        if self._clean_out is None:
            self.capture()
        return self._clean_out

    @property
    def err(self) -> str | None:
        """Get clean stderr output."""
        if self._clean_err is None:
            self.capture()
        return self._clean_err

    @property
    def raw_out(self) -> str:
        """Get raw stdout output with ANSI codes."""
        if self._captured is None:
            self.capture()
        return str(self._captured.out)  # type: ignore [attr-defined]

    @property
    def raw_err(self) -> str:
        """Get raw stderr output with ANSI codes."""
        if self._captured is None:
            self.capture()
        return str(self._captured.err)  # type: ignore [attr-defined]

    def contains(
        self,
        patterns: Union[str, List[str]],
        where: str = "out",
        exact: bool = False,
        regex: bool = False,
    ) -> bool:
        """
        Check if output contains specified patterns.

        Args:
            patterns: String or list of strings to search for
            where: 'out' for stdout, 'err' for stderr, 'both' for either
            exact: If True, require exact string match (default: False)
            regex: If True, treat patterns as regex (default: False)

        Returns:
            True if all patterns are found, False otherwise
        """
        if isinstance(patterns, str):
            patterns = [patterns]

        text = ""
        if where in ("out", "both"):
            text += self.out or ""
        if where in ("err", "both"):
            text += self.err or ""

        for pattern in patterns:
            if exact:
                if pattern not in text:
                    return False
            elif regex:
                if not re.search(pattern, text):
                    return False
            else:
                # Smart matching - use regex for patterns with special chars
                if any(c in pattern for c in ".*+?()[]{}|^$"):
                    if not re.search(pattern, text):
                        return False
                elif pattern not in text:
                    return False

        return True

    def assert_contains(
        self,
        patterns: Union[str, List[str]],
        where: str = "out",
        exact: bool = False,
        regex: bool = False,
    ) -> None:
        """Assert that output contains all specified patterns."""
        if not self.contains(patterns, where, exact, regex):
            if isinstance(patterns, str):
                patterns = [patterns]

            # Find which pattern(s) failed
            failed = []
            text = ""
            if where in ("out", "both"):
                text += self.out or ""
            if where in ("err", "both"):
                text += self.err or ""

            for pattern in patterns:
                if exact and pattern not in text:
                    failed.append(f"'{pattern}'")
                elif regex and not re.search(pattern, text):
                    failed.append(f"/{pattern}/")
                elif not exact and not regex:
                    if any(c in pattern for c in ".*+?()[]{}|^$"):
                        if not re.search(pattern, text):
                            failed.append(f"/{pattern}/")
                    elif pattern not in text:
                        failed.append(f"'{pattern}'")

            output_excerpt = text[:200] + ("..." if len(text) > 200 else "")
            where_str = (
                "stdout" if where == "out" else "stderr" if where == "err" else "output"
            )

            pytest.fail(
                f"Pattern(s) {', '.join(failed)} not found in {where_str}.\n"
                f"Actual output (excerpt): {output_excerpt}"
            )

    def assert_not_contains(
        self,
        patterns: Union[str, List[str]],
        where: str = "out",
        exact: bool = False,
        regex: bool = False,
    ) -> None:
        """Assert that output does NOT contain any of the specified patterns."""
        if isinstance(patterns, str):
            patterns = [patterns]

        text = ""
        if where in ("out", "both"):
            text += self.out or ""
        if where in ("err", "both"):
            text += self.err or ""

        for pattern in patterns:
            if exact and pattern in text:
                pytest.fail(
                    f"Pattern '{pattern}' should NOT be in {where}, but was found."
                )
            elif regex and re.search(pattern, text):
                pytest.fail(
                    f"Pattern /{pattern}/ should NOT be in {where}, but was found."
                )
            elif not exact and not regex:
                if any(c in pattern for c in ".*+?()[]{}|^$"):
                    if re.search(pattern, text):
                        pytest.fail(
                            f"Pattern /{pattern}/ should NOT be in {where}, but was found."
                        )
                elif pattern in text:
                    pytest.fail(
                        f"Pattern '{pattern}' should NOT be in {where}, but was found."
                    )
