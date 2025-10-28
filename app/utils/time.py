from datetime import date, timedelta

def parse_date(d: str | None) -> date:
    if d in (None, "", "today"):
        return date.today()
    if d == "yesterday":
        return date.today() - timedelta(days=1)
    return date.fromisoformat(d)
