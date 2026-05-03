"""Resolve retail CSV rows by Product ID, partial ID, Product Name, or Category."""

from __future__ import annotations


class AmbiguousProductError(Exception):
    """Multiple Product IDs match the query."""

    def __init__(self, product_ids: list[str]):
        super().__init__(f"ambiguous: {len(product_ids)} matches")
        self.product_ids = product_ids


class ProductNotFoundError(Exception):
    """No Product ID matches the query."""

    def __init__(self, query: str):
        super().__init__(f"not found: {query}")
        self.query = query


def display_label_for_product_id(df, product_id: str) -> str:
    pid = str(product_id).strip()
    sub = df[df["Product ID"].astype(str) == pid]
    if sub.empty:
        return pid
    row = sub.iloc[0]
    if "Product Name" in df.columns:
        name = row.get("Product Name")
        if name is not None and str(name).strip():
            return f"{str(name).strip()} ({pid})"
    cat = row.get("Category")
    if cat is not None and str(cat).strip():
        return f"{str(cat).strip()} ({pid})"
    return pid


def resolve_product_id(df, query: str) -> str:
    """Return canonical Product ID string for user input."""
    q = (query or "").strip()
    if not q:
        raise ProductNotFoundError(query or "")

    ids = sorted(df["Product ID"].astype(str).unique().tolist())
    q_fold = q.casefold()

    for pid in ids:
        if pid.casefold() == q_fold:
            return pid

    id_matches = [p for p in ids if q_fold in p.casefold()]
    if len(id_matches) == 1:
        return id_matches[0]
    if len(id_matches) > 1:
        raise AmbiguousProductError(id_matches)

    if "Product Name" in df.columns:
        mask = (
            df["Product Name"]
            .astype(str)
            .str.contains(q, case=False, na=False, regex=False)
        )
        u = df.loc[mask, "Product ID"].astype(str).unique().tolist()
        if len(u) == 1:
            return u[0]
        if len(u) > 1:
            raise AmbiguousProductError(sorted(u))

    if "Category" in df.columns:
        mask = (
            df["Category"].astype(str).str.contains(q, case=False, na=False, regex=False)
        )
        u = df.loc[mask, "Product ID"].astype(str).unique().tolist()
        if len(u) == 1:
            return u[0]
        if len(u) > 1:
            raise AmbiguousProductError(sorted(u))

    raise ProductNotFoundError(q)
