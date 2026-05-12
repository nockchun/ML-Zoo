from __future__ import annotations

import os
import re
from typing import List, Tuple

DOC_DIR = os.path.join(os.path.dirname(__file__), "..", "docs")

def load_docs() -> List[Tuple[str, str]]:
    docs = []
    for fn in sorted(os.listdir(DOC_DIR)):
        if fn.endswith(".md"):
            with open(os.path.join(DOC_DIR, fn), "r", encoding="utf-8") as f:
                docs.append((fn, f.read()))
    return docs

def simple_retrieve(query: str, k: int = 3) -> List[str]:
    """Very small lexical retriever (teaching only).

    We score docs by overlap between query tokens and document text so that
    queries like "홍길동 전화번호" tend to retrieve the user profile doc.
    """
    docs = load_docs()
    toks = [t.strip() for t in re.split(r"\s+", query) if len(t.strip()) >= 2]

    scored: List[Tuple[int, str]] = []
    for fn, txt in docs:
        score = 0
        for t in toks:
            if t in txt:
                score += 1
        scored.append((score, fn))

    # Higher score first; stable tie-breaker by filename
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [fn for score, fn in scored[:k]]

def get_doc_text(filenames: List[str]) -> str:
    docs = dict(load_docs())
    return "\n\n---\n\n".join([docs.get(fn, "") for fn in filenames])
