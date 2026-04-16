# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 RUNE Contributors
"""Minimal Python module for CodeQL extraction.

The rune-docs tree is documentation-first; automation lives in **rune-ci**.
GitHub CodeQL's Python autobuild requires at least one extractable ``*.py``
file. This module intentionally does nothing beyond existing as source text.
"""


def codeql_python_present() -> bool:
    return True
