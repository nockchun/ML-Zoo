"""Backward-compatible wrapper for notebooks.

Some notebooks import `load_model_and_tokenizer` from `src.modeling`.
The actual implementation lives in `src.llm`.
"""

from __future__ import annotations

from .llm import load_model_and_tokenizer  # re-export

__all__ = ["load_model_and_tokenizer"]
