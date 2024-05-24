import re
from neo4j import GraphDatabase, basic_auth


def intcomma(orig: int) -> str:
    """Add commas to long ints for readability"""
    new = re.sub(r"^(-?\d+)(\d{3})", r"\g<1>,\g<2>", str(orig))
    if orig == new:
        return new
    else:
        return intcomma(new)


def get_neo4j_connection(settings):

    bolt_url = "bolt://{}:{}".format(settings.neo4j_host, settings.neo4j_port)
    print(bolt_url)
    driver = GraphDatabase.driver(
        bolt_url,
        auth=basic_auth(settings.neo4j_username, settings.neo4j_password),
    )
    db = driver.session()
    return db


def get_page_range(num_pages, page, page_links=15) -> list:
    """Generate page range"""

    _PAGE_LINKS = page_links
    page_range = []
    if page < _PAGE_LINKS // 2:
        if num_pages > _PAGE_LINKS:
            page_range = [p for p in range(1, _PAGE_LINKS + 1)]
        else:
            page_range = [p for p in range(1, num_pages + 1)]
    else:
        for p in range(1, num_pages + 1):
            if p < page:
                if page - p < (_PAGE_LINKS) // 2:
                    page_range.append(p)
            if p >= page:
                if p - page < (_PAGE_LINKS) // 2:
                    page_range.append(p)

        if len(page_range) > _PAGE_LINKS and page > (_PAGE_LINKS) // 2:
            page_range = page_range[:-1]
    # transform to dict so it easy to render with mustache
    dict_page_range = []
    for p in page_range:
        if p == page:
            dict_page_range.append({"page": p, "active": True})
        else:
            dict_page_range.append({"page": p, "active": False})
    return dict_page_range


def get_sort_param(sort: str) -> str:
    """Simple SWITCH/CASE helpers to process sort param
    to actual sort value for query"""

    sort_param = False

    if sort == "pagerank":
        sort_param = "COALESCE(concept.pagerank, 0) desc"
    elif sort == "-pagerank":
        sort_param = "COALESCE(concept.pagerank, 0) asc"
    elif sort == "name":
        sort_param = "concept.concept_id"
    elif sort == "-name":
        sort_param = "concept.concept_id desc"
    elif sort == "state":
        sort_param = "state"
    elif sort == "-state":
        sort_param = "state desc"

    if not sort_param:  # default value
        sort_param = "COALESCE(concept.pagerank, 0) desc"
    return sort_param


def get_concept_location(settings, concept_id: str) -> dict:
    """Find location for concept"""
    q = (
        "MATCH(n:Concept{concept_id:$concept_id})-[:HAS_SEED_CONCEPT]-(l:Location)"
        "RETURN n as concept, l as location, NOT EXISTS((n)-[:DEACTIVATES]-(l)) as state"
    ) # seed concept
    location = None
    results = []
    with get_neo4j_connection(settings) as db:
        result = db.run(q, {"concept_id": concept_id})
        # we expect 1 seed location or less
        location = result.single()
        level = 1
        while level < 6 and not location:
            q = (
                "MATCH "
                "(l:Location)-[:HAS_SEED_CONCEPT]->(c2:Concept)"
                "<-[:HAS_HIGHER_LOCATION*1..%s]-(n:Concept{concept_id:$concept_id}) "
                "RETURN l as location, n as concept NOT EXISTS((l)-[:DEACTIVATES]-(c2)) as state"
            ) % level
            level += 1
            # print(q)
            result = db.run(q, {"concept_id": concept_id})
            for r in result:
                rec = r.data()
                results.append(
                    {
                        "location": rec["l"],
                        "concept_id": concept_id,
                        "state": rec["state"],
                    }
                )
    return results
