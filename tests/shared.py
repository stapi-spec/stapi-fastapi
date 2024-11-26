from typing import Any

type link_dict = dict[str, Any]


def find_link(links: list[link_dict], rel: str) -> link_dict | None:
    return next((link for link in links if link["rel"] == rel), None)
