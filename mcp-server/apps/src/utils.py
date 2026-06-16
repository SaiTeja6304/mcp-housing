from datetime import date, datetime
from typing import Optional

def format_move_in(start_date: str | None) -> str:
    if not start_date:
        return "None"

    move_in_date = date.fromisoformat(start_date)

    if move_in_date < date.today():
        return "Available now"

    return f"{move_in_date:%b} {move_in_date.day}, {move_in_date:%Y}"

def format_posted(posted_at: int | None) -> str:
    if not posted_at:
        return ""

    posted_date = datetime.fromtimestamp(posted_at)

    return f"{posted_date:%b} {posted_date.day}, {posted_date:%Y}"

def clean_text(text: str) -> str:
    return " ".join(text.split())

def build_response(records: list, total: int, limit: Optional[int]) -> dict:
    """Wrap results in metadata so the host LLM knows the full picture.
 
    The metadata is always returned even when results are not truncated so the
    LLM has a consistent schema to parse regardless of the limit value.
    """
    returned = len(records)
    truncated = total > returned
 
    metadata: dict = {
        "total_records": total,
        "returned_records": returned,
        "truncated": truncated,
    }
 
    if truncated:
        metadata["warning"] = (
            f"Only {returned} of {total} records are returned "
            f"(limit={returned}). Re-call this tool with a higher `limit` "
            f"or apply additional filters to narrow the results."
        )
    else:
        metadata["warning"] = None
 
    return {"metadata": metadata, "records": records}