from app.services.query_rewrite_service import QueryRewriteService


def test_parse_json_content_plain() -> None:
    service = QueryRewriteService()
    data = service._parse_json_content(
        '{"query":"\\"Сидни Суини\\"~1","changed":true,"note":"точное ФИО"}'
    )
    assert data["query"] == '"Сидни Суини"~1'
    assert data["changed"] is True


def test_parse_json_content_fenced() -> None:
    service = QueryRewriteService()
    data = service._parse_json_content(
        '```json\n{"query":"бренд*","changed":false,"note":""}\n```'
    )
    assert data["query"] == "бренд*"


def test_sanitize_collapses_whitespace() -> None:
    service = QueryRewriteService()
    assert service._sanitize("  футбол   ЦСКА  ") == "футбол ЦСКА"
