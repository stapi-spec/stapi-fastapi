from typing import Any, Callable

link_dict = dict[str, Any]


def find_link(links: list[link_dict], rel: str) -> link_dict | None:
    return next((link for link in links if link["rel"] == rel), None)


def assert_link(
    req: str,
    body: dict[str, Any],
    rel: str,
    path: str,
    url_for: Callable[[str], str],
    media_type: str = "application/json",
) -> None:
    link = find_link(body["links"], rel)
    assert link, f"{req} Link[rel={rel}] should exist"
    assert link["type"] == media_type
    assert link["href"] == url_for(path)
