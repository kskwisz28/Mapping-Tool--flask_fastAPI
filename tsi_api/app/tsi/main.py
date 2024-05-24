from fastapi import FastAPI
from json import dumps
from pydantic import BaseModel
from pydantic import BaseSettings
from helpers import (
    get_neo4j_connection,
    get_page_range,
    get_sort_param,
    get_concept_location,
    intcomma,
)  # , get_db_connection

from queries import (
    RETURN_STMN,
    COUNT_STMN,
    LOWER_CONCEPTS_QUERY,
    HIGHER_CONCEPTS_QUERY,
    ALL_CONCEPTS_QUERY,
    COUNTRY_CONCEPTS_QUERY,
    REGION_CONCEPTS_QUERY,
    CITIES_CONCEPTS_QUERY,
    CONCEPT_LOCATION_QUERY,
    CONCEPTS_BY_NAME_QUERY,
)

# TODO:
# populating results should be unified and taken out into one function
#


class Settings(BaseSettings):
    """APP Settings should be set using env variables"""

    admin_email: str
    admin_password: str
    neo4j_host: str
    neo4j_port: int
    neo4j_username: str
    neo4j_password: str


settings = Settings()

app = FastAPI()

ITEMS_PER_PAGE = 100


@app.get("/api/health")
def health() -> dict:
    """Test endpoint, should always return status:ok"""
    return {"status": "ok"}


# Autocomplete API calls:
@app.get("/api/get/countries")
def countries_list(name: str = None, skip: int = 0, limit: int = 10) -> dict:
    """List all countries, or with name starts with 'name' param"""

    if name:
        regex = "(?i){name}.*".format(name=name)
    else:
        regex = ".*"
    # we build regex here, because neo4j breaks regex if name
    # param passed directly to neo4j driver

    q = (
        "MATCH(n:Country) WHERE n.country_id =~ $regex "
        "RETURN n.country_id as name SKIP $skip LIMIT $limit"
    )

    results = {}
    with get_neo4j_connection(settings) as db:
        result = db.run(q, {"regex": regex, "skip": skip, "limit": limit})
        results["data"] = []
        for r in result:
            results["data"].append(r.data())
    return results


@app.get("/api/get/regions")
def regions_list(
    country_id: str, name: str = None, skip: int = 0, limit: int = 10
) -> dict:
    """List all regions in selected country,
    filtered with 'name' param"""

    if name:
        regex = "(?i){name}.*".format(name=name)
    else:
        regex = ".*"

    q = (
        "MATCH(reg:Region)-[:HAS_REGION]-(l:Location)-[:HAS_COUNTRY]-(c:Country)"
        " WHERE c.country_id=$country_id and reg.region_id =~ $regex "
        "RETURN DISTINCT reg.region_id as name limit $limit"
    )

    results = {}
    with get_neo4j_connection(settings) as db:
        result = db.run(
            q, {"country_id": country_id, "regex": regex, "skip": skip, "limit": limit}
        )
        results["data"] = []
        for r in result:
            results["data"].append(r.data())
    return results


@app.get("/api/get/cities")
def cities_list(
    region_id: str, name: str = None, skip: int = 0, limit: int = 10
) -> dict:
    """List all Cities in selected Country,
    filtered with 'name' param is provided"""

    if name:
        regex = "(?i){name}.*".format(name=name)
    else:
        regex = ".*"

    q = (
        "MATCH(city:City)-[:HAS_CITY]-(l:Location)-[:HAS_REGION]-(reg:Region)"
        " WHERE reg.region_id=$region_id and city.city_id =~ $regex "
        "RETURN DISTINCT city.city_id as name skip $skip limit $limit"
    )

    results = {}
    with get_neo4j_connection(settings) as db:
        result = db.run(
            q, {"region_id": region_id, "regex": regex, "skip": skip, "limit": limit}
        )
        results["data"] = []
        for r in result:
            results["data"].append(r.data())
    return results


@app.get("/api/get/locations")
def locations_list(name: str, skip: int = 0, limit: int = 100) -> dict:
    """Search location by name for autocomplete
    and search results"""

    if limit > 100:
        limit = 100
    location_regex = "(?i).*{location_name}.*".format(location_name=name)
    q = (
        "MATCH(n:Location) WHERE n.location_id =~ $location_regex "
        "RETURN n.location_id as name SKIP $skip LIMIT $limit"
    )
    results = {}
    with get_neo4j_connection(settings) as db:
        result = db.run(
            q, {"location_regex": location_regex, "skip": skip, "limit": limit}
        )  #
        results["data"] = []
        for r in result:
            results["data"].append(r.data())
    return results


@app.get("/api/get/concepts-by-location")
def concepts_by_location(
    location_id: str, page_id: int = 1, sort: str = "pagerank"
) -> dict:
    """Search concepts by location_id"""

    sort_param = get_sort_param(sort)
    skip = (page_id - 1) * ITEMS_PER_PAGE
    limit = ITEMS_PER_PAGE

    q = (CONCEPT_LOCATION_QUERY + RETURN_STMN) % sort_param
    q_count = CONCEPT_LOCATION_QUERY + COUNT_STMN

    results = {}
    with get_neo4j_connection(settings) as db:
        concepts = db.run(q, {"location_id": location_id, "skip": skip, "limit": limit})
        concepts_count = db.run(q_count, {"location_id": location_id})
        count = int(concepts_count.single()["count"])

        total = count
        if total > 1:
            total += 1  # Assuming we did not count Concept which has_seed_concept

        results = {}
        results["data"] = []
        results["total"] = intcomma(total)
        results["found_by"] = "Location: {}".format(location_id)

        # now lets browse data
        for r in concepts:
            record = r.data()
            # print(record)
            record = {
                "concept": record["concept"],
                "state": record["state"],
                "locations": {"l": record["location"]},
            }
            results["data"].append(record)

    num_pages = total // ITEMS_PER_PAGE
    if (num_pages * ITEMS_PER_PAGE) < count:
        num_pages += 1

    page_range = get_page_range(num_pages, page_id, 10)
    results["pagination"] = page_range
    results["count"] = len(results["data"])

    results["skip"] = skip + 1
    if page_id < num_pages:
        next_page = page_id + 1
    else:
        next_page = False
    if page_id > 1:
        prev_page = page_id - 1
    else:
        prev_page = False
    results["next_page"] = next_page
    results["prev_page"] = prev_page
    results["page_id"] = page_id
    results["sort"] = sort

    return results


@app.get("/api/get/concepts-by-country")
def concepts_by_country(
    country_id: str, sort: str = "pagerank", page_id: int = 1
) -> dict:
    """Search concept by country name (country_id)"""

    skip = (page_id - 1) * ITEMS_PER_PAGE
    limit = ITEMS_PER_PAGE
    sort_param = get_sort_param(sort)

    q = (COUNTRY_CONCEPTS_QUERY + RETURN_STMN) % sort_param
    q_count = COUNTRY_CONCEPTS_QUERY + COUNT_STMN

    print(q)
    results = {}
    with get_neo4j_connection(settings) as db:
        concepts = db.run(
            q, {"country_id": country_id, "skip": skip, "limit": limit}
        )  #
        concepts_count = db.run(q_count, {"country_id": country_id})
        count = int(concepts_count.single()["count"])

        results = {}
        results["data"] = []
        results["total"] = intcomma(count)
        results["found_by"] = "Country {}".format(country_id)

        for r in concepts:
            record = r.data()
            record = {
                "concept": record["concept"],
                "state": record["state"],
                "locations": {"l": record["location"]},
            }
            results["data"].append(record)

    num_pages = count // ITEMS_PER_PAGE
    if (num_pages * ITEMS_PER_PAGE) < count:
        num_pages += 1

    if page_id < num_pages:
        next_page = page_id + 1
    else:
        next_page = False
    if page_id > 1:
        prev_page = page_id - 1
    else:
        prev_page = False
    results["next_page"] = next_page
    results["prev_page"] = prev_page
    results["page_id"] = page_id

    page_range = get_page_range(num_pages, page_id, 10)
    results["pagination"] = page_range
    results["count"] = len(results["data"])
    results["skip"] = skip + 1
    results["sort"] = sort

    return results


@app.get("/api/get/concepts-by-region")
def concepts_by_region(
    region_id: str, country_id: str, sort: str = "pagerank", page_id: int = 1
) -> dict:
    """Search concepts by region name (region_id)"""

    skip = (page_id - 1) * ITEMS_PER_PAGE
    limit = ITEMS_PER_PAGE
    sort_param = get_sort_param(sort)

    q = (REGION_CONCEPTS_QUERY + RETURN_STMN) % sort_param
    q_count = REGION_CONCEPTS_QUERY + COUNT_STMN

    results = {}
    with get_neo4j_connection(settings) as db:
        concepts = db.run(
            q,
            {
                "region_id": region_id,
                "country_id": country_id,
                "skip": skip,
                "limit": limit,
            },
        )  #
        concepts_count = db.run(
            q_count, {"region_id": region_id, "country_id": country_id}
        )

        count = int(concepts_count.single()["count"])

        results = {}
        results["data"] = []
        results["total"] = intcomma(count)
        results["found_by"] = "Country {}, Region {}".format(country_id, region_id)

        for r in concepts:
            record = r.data()
            record = {
                "concept": record["concept"],
                "state": record["state"],
                "locations": {"l": record["location"]},
            }
            results["data"].append(record)

    num_pages = count // ITEMS_PER_PAGE
    if (num_pages * ITEMS_PER_PAGE) < count:
        num_pages += 1

    page_range = get_page_range(num_pages, page_id, 10)
    if page_id < num_pages:
        next_page = page_id + 1
    else:
        next_page = False
    if page_id > 1:
        prev_page = page_id - 1
    else:
        prev_page = False
    results["next_page"] = next_page
    results["prev_page"] = prev_page
    results["page_id"] = page_id
    results["pagination"] = page_range
    results["count"] = len(results["data"])
    results["skip"] = skip + 1
    results["sort"] = sort

    return results


@app.get("/api/get/concepts-by-city")
def concepts_by_city(
    country_id: str,
    region_id: str,
    city_id: str,
    sort: str = "pagerank",
    page_id: int = 1,
) -> dict:
    """Search concept by country_id, region_id, city_id"""

    skip = (page_id - 1) * ITEMS_PER_PAGE
    limit = ITEMS_PER_PAGE
    sort_param = get_sort_param(sort)

    q = (CITIES_CONCEPTS_QUERY + RETURN_STMN) % sort_param
    q_count = CITIES_CONCEPTS_QUERY + COUNT_STMN

    results = {}
    with get_neo4j_connection(settings) as db:
        concepts = db.run(
            q,
            {
                "country_id": country_id,
                "region_id": region_id,
                "city_id": city_id,
                "skip": skip,
                "limit": limit,
            },
        )  #

        concepts_count = db.run(
            q_count,
            {
                "country_id": country_id,
                "region_id": region_id,
                "city_id": city_id,
                "skip": skip,
                "limit": limit,
            },
        )

        results = {}
        results["data"] = []

        count = int(concepts_count.single()["count"])

        results["total"] = intcomma(count)
        results["found_by"] = "{}, {}, {}".format(country_id, region_id, city_id)

        for r in concepts:
            record = r.data()
            record = {
                "concept": record["concept"],
                "state": record["state"],
                "locations": {"l": record["location"]},
            }
            results["data"].append(record)

    num_pages = count // ITEMS_PER_PAGE
    if (num_pages * ITEMS_PER_PAGE) < count:
        num_pages += 1

    page_range = get_page_range(num_pages, page_id, 10)
    if page_id < num_pages:
        next_page = page_id + 1
    else:
        next_page = False
    if page_id > 1:
        prev_page = page_id - 1
    else:
        prev_page = False
    results["next_page"] = next_page
    results["prev_page"] = prev_page
    results["page_id"] = page_id
    results["pagination"] = page_range
    results["count"] = len(results["data"])
    results["skip"] = skip + 1
    results["sort"] = sort

    return results


@app.get("/api/list/concepts")
def concepts_list(page_id: int = 1, sort: str = "pagerank") -> dict:
    """list all concepts by rank"""

    skip = (page_id - 1) * ITEMS_PER_PAGE
    limit = ITEMS_PER_PAGE
    sort_param = get_sort_param(sort)

    q = (ALL_CONCEPTS_QUERY + RETURN_STMN) % sort_param
    q_count = ALL_CONCEPTS_QUERY + COUNT_STMN

    results = {}
    with get_neo4j_connection(settings) as db:

        count_result = db.run(q_count)  #
        count = int(count_result.single()["count"])

        num_pages = count // ITEMS_PER_PAGE
        if (num_pages * ITEMS_PER_PAGE) < count:
            num_pages += 1

        concepts = db.run(q, {"skip": skip, "limit": limit})  #
        results["data"] = []
        results["total"] = intcomma(int(count))
        results["found_by"] = " All Concepts"
        for r in concepts:
            record = r.data()
            record = {
                "concept": record["concept"],
                "state": record["state"],
                "locations": {"l": record["location"]},
            }
            results["data"].append(record)

    results["count"] = len(results["data"])

    page_range = get_page_range(num_pages, page_id, 10)

    if page_id < num_pages:
        next_page = page_id + 1
    else:
        next_page = False
    if page_id > 1:
        prev_page = page_id - 1
    else:
        prev_page = False
    results["next_page"] = next_page
    results["prev_page"] = prev_page
    results["page_id"] = page_id

    results["pagination"] = page_range
    results["skip"] = skip + 1
    results["sort"] = sort

    # print(results)
    return results


@app.get("/api/get/concepts-by-name")
def concepts_list_by_name(concept_id: str, page_id: int = 1, sort="pagerank") -> dict:
    """list all concepts connected to selected concept
    and searching concept"""

    skip = (page_id - 1) * ITEMS_PER_PAGE
    limit = ITEMS_PER_PAGE
    sort_param = get_sort_param(sort)

    # select all lower concepts
    # we expect all lower concepts have location
    # at least from one higher concept
    q = (CONCEPTS_BY_NAME_QUERY + RETURN_STMN) % sort_param
    q_count = CONCEPTS_BY_NAME_QUERY + COUNT_STMN

    results = {}
    with get_neo4j_connection(settings) as db:
        result = db.run(q_count, {"concept_id": concept_id})
        count = int(result.single()["count"])

        num_pages = count // ITEMS_PER_PAGE
        if (num_pages * ITEMS_PER_PAGE) < count:
            num_pages += 1

        result = db.run(q, {"concept_id": concept_id, "skip": skip, "limit": limit})  #
        results["data"] = []
        results["total"] = intcomma(count)
        results["found_by"] = "Concept: {}".format(concept_id)

        for r in result:
            record = r.data()
            record = {
                "concept": record["concept"],
                "state": record["state"],
                "locations": {"l": record["location"]},
            }
            results["data"].append(record)

    results["count"] = len(results["data"])

    page_range = get_page_range(num_pages, page_id, 10)

    results["pagination"] = page_range
    results["skip"] = skip + 1
    if page_id < num_pages:
        next_page = page_id + 1
    else:
        next_page = False
    if page_id > 1:
        prev_page = page_id - 1
    else:
        prev_page = False
    results["next_page"] = next_page
    results["prev_page"] = prev_page
    results["page_id"] = page_id

    # print(results)
    return results


@app.get("/api/get/lower-higher-concepts")
def lower_higher_concepts(
    concept_id: str, page_id: int = 1, lower: bool = True, sort="pagerank"
) -> dict:
    """list all concepts connected to selected concept
    By default app show all lower concepts,
    to list higher concepts set lower=False"""

    skip = (page_id - 1) * ITEMS_PER_PAGE
    limit = ITEMS_PER_PAGE
    sort_param = get_sort_param(sort)

    # first lets found location related to this concept
    # concept_locations = get_concept_location(settings, concept_id)
    # print("Location:", concept_locations)

    if lower:
        # select all lower concepts
        # we expect all lower concepts have location
        # at least from one higher concept
        q = (LOWER_CONCEPTS_QUERY + RETURN_STMN) % sort_param
        q_count = LOWER_CONCEPTS_QUERY + COUNT_STMN

    else:
        # select all higher concepts
        q = (HIGHER_CONCEPTS_QUERY + RETURN_STMN) % sort_param
        q_count = HIGHER_CONCEPTS_QUERY + COUNT_STMN

    results = {}
    with get_neo4j_connection(settings) as db:
        result = db.run(q_count, {"concept_id": concept_id})
        count = int(result.single()["count"])

        num_pages = count // ITEMS_PER_PAGE
        if (num_pages * ITEMS_PER_PAGE) < count:
            num_pages += 1

        result = db.run(q, {"concept_id": concept_id, "skip": skip, "limit": limit})  #
        results["data"] = []
        results["total"] = intcomma(count)
        if lower:
            results["found_by"] = "Concept: {} (lower Concepts)".format(concept_id)
        else:
            results["found_by"] = "Concept: {} (higher Concepts)".format(concept_id)

        for r in result:
            record = r.data()
            record = {
                "concept": record["concept"],
                "state": record["state"],
                "locations": {"l": record["location"]},
            }
            results["data"].append(record)

    results["count"] = len(results["data"])

    page_range = get_page_range(num_pages, page_id, 10)

    results["pagination"] = page_range
    results["skip"] = skip + 1
    if page_id < num_pages:
        next_page = page_id + 1
    else:
        next_page = False
    if page_id > 1:
        prev_page = page_id - 1
    else:
        prev_page = False
    results["next_page"] = next_page
    results["prev_page"] = prev_page
    results["page_id"] = page_id

    # print(results)
    return results


@app.get("/api/get-higher-location")
def concept_higher_location(concept_id: str) -> dict:
    """Hit db for higher location for Concept"""

    q = (
        "MATCH(n:Concept{concept_id:$concept_id})-[:HAS_HIGHER_LOCATION]->(c:Concept)"
        "WHERE c.banned = False RETURN c"
    )
    with get_neo4j_connection(settings) as db:
        rec = db.run(q, {"concept_id": concept_id})  #
        results = rec.single()[0]
    return results


@app.get("/api/get/concepts")
def concepts_autocomplete(name: str, skip: int = 0, limit: int = 0) -> dict:
    """Hit db for concepts names"""

    if name:
        name = name.replace(" ", "_")
        regex = "(?i){name}.*".format(name=name)
    else:
        regex = ".*"

    # q = (
    #     "MATCH(n:Concept) WHERE n.concept_id =~ $regex "
    #     "RETURN n.concept_id as name SKIP $skip LIMIT  $limit"
    # )

    q = (
        'CALL db.index.fulltext.queryNodes("conceptIdFullText", $name) '
        "YIELD node, score RETURN node.concept_id as name order by score desc "
        "SKIP $skip LIMIT $limit"
    )
    results = {}
    with get_neo4j_connection(settings) as db:
        result = db.run(q, {"name": name, "skip": skip, "limit": limit})
        results["data"] = []
        for r in result:
            results["data"].append(r.data())
    return results


@app.get("/api/concept-info/")
def concept_info(concept_id: str) -> dict:
    """Return concept information:
    How many releted concepts in upper lever and lower level
    returning dict with these fields:
    "higher_concepts": int ,
    "lower_concepts": int,
    "types": list of types attached to concept
    """

    q = "match (t:Type)<-[:HAS_TYPE]-(c:Concept{concept_id:$concept_id}) return t, c;"

    results = {}
    with get_neo4j_connection(settings) as db:
        records = db.run(q, {"concept_id": concept_id})
        if not records:
            return {"error": "No such Concept in database"}

        concept_types = []
        for r in records:
            c_type = r.data()["t"]
            # print(c_type)
            concept_types.append(c_type["label"])

        q_higher = HIGHER_CONCEPTS_QUERY + COUNT_STMN

        q_lower = LOWER_CONCEPTS_QUERY + COUNT_STMN

        rec = db.run(q_higher, {"concept_id": concept_id})
        higher_concepts = rec.single()[0]
        rec = db.run(q_lower, {"concept_id": concept_id})
        lower_concepts = rec.single()[0]
        # print(lower_concepts)
        results["higher_concepts"] = higher_concepts
        results["lower_concepts"] = lower_concepts
        results["types"] = concept_types
    return results


def deactivate_concept(concept_id: str, location_id: str):
    """Helper function which add DEACTIVATES relationship
    beetwen selected concept and location"""
    print("Deactivating: {} - {}".format(concept_id, location_id))
    with get_neo4j_connection(settings) as db:
        q = (
            "MATCH(l:Location {location_id:$location_id}), "
            " (c:Concept {concept_id:$concept_id})"
            " MERGE (l)-[r:DEACTIVATES]->(c)"
        )
        result = db.run(
            q,
            {
                "location_id": location_id,
                "concept_id": concept_id,
            },
        )
        record = result.single()
    return record


def activate_concept(concept_id: str, location_id: str):
    """Helper function which add ACTIVATES relationship
    beetwen selected concept and location"""
    print("Activating: {} -> {}".format(location_id, concept_id))
    with get_neo4j_connection(settings) as db:
        q = (
            "MATCH(l:Location {location_id:$location_id})-[r:DEACTIVATES]"
            "->(c:Concept {concept_id:$concept_id}) DELETE r"
        )
        result = db.run(
            q,
            {
                "location_id": location_id,
                "concept_id": concept_id,
            },
        )

        record = result.single()
    return record


@app.put("/api/concept-change-state/")
def change_concept_state(concept_id: str, location_id: str, action: str) -> dict:
    """Return Ok if no errors appear"""
    if action not in ["activate", "deactivate"]:
        return {"error": "Action should be either activate or deactivate"}

    # lower concepts which should be deactivated too:
    q = (
        "MATCH (n:Concept)-[:HAS_HIGHER_LOCATION]->(c:Concept{concept_id:$concept_id}) "
        "RETURN n as concept"
    )
    if action == "deactivate":  # FIRST deactivate concept
        deactivate_concept(concept_id, location_id)
    else:
        activate_concept(concept_id, location_id)

    results = {}
    with get_neo4j_connection(settings) as db:
        lower_concepts = db.run(q, {"concept_id": concept_id})
        for lc in lower_concepts:
            # print('Concept, Location >> ', loc.data())
            if action == "deactivate":
                deactivate_concept(lc["concept"]["concept_id"], location_id)
            else:
                activate_concept(lc["concept"]["concept_id"], location_id)

        return {"result": "ok"}


@app.put("/api/check-map-concept/")
def check_map_concept(
    concept_id: str,
    location_id: str = "",
    country_id: str = "",
    region_id: str = "",
    city_id: str = "",
) -> dict:

    # check for concept:

    q = (
        "MATCH (c:Concept{concept_id:$concept_id}) "
        "OPTIONAL MATCH (c)-[:HAS_TYPE]-(t:Type)"
        "RETURN c, t"
    )

    results = {}
    with get_neo4j_connection(settings) as db:
        records = db.run(q, {"concept_id": concept_id})
        concept_types = []
        for r in records:
            results["concept"] = r.data()["c"]
            c_type = r.data()["t"]
            concept_types.append(c_type["label"])
        if not results["concept"]:
            return {"error": "No such Concept in database"}

        results["types"] = concept_types

        q_lower = (
            "MATCH (c:Concept{concept_id:$concept_id})<-"
            "[:HAS_HIGHER_LOCATION*]-(c2:Concept)"
            " RETURN c2 as concept"
        )
        q_lower_count = (
            "MATCH (c:Concept{concept_id:$concept_id})<-"
            "[:HAS_HIGHER_LOCATION*]-(c2:Concept)"
            " RETURN count(c) as count"
        )
        count_lower = db.run(q_lower_count, {"concept_id": concept_id})
        results["count_lower"] = count_lower.single()["count"]
        if results["count_lower"] > 4:
            results["more"] = results["count_lower"] - 4
        else:
            results["more"] = False
        records = db.run(q_lower, {"concept_id": concept_id})
        lower_concepts = []
        i = 0
        for r in records:
            i += 1
            lower_concepts.append(r.data())
            if i > 3:  # show only 4 lower concepts
                break
        results["lower_concepts"] = lower_concepts
        results["validated"] = False

        # now lets check for Location:

        if location_id != "":
            q = (
                "MATCH (l:Location{location_id:$location_id}) "
                "OPTIONAL MATCH (l)-[:HAS_COUNTRY]-(country:Country)"
                "OPTIONAL MATCH (l)-[:HAS_REGION]-(region:Region)"
                "OPTIONAL MATCH (l)-[:HAS_CITY]-(city:City) "
                "RETURN l, country, region, city"
            )
            records = db.run(q, {"location_id": location_id})
            location = records.single()
            results["location"] = location.data()
            results["validated"] = True

        elif city_id != "":
            q = (
                "MATCH (l:Location)-[:HAS_CITY]-(city:City{city_id:$city_id}) "
                "WITH l, city MATCH (l)-[:HAS_REGION]-(region:Region{region_id:$region_id}) "
                "WITH l, city, region MATCH (l)-[:HAS_COUNTRY]-(country:Country{country_id:$country_id})"
                "RETURN l, country, region, city"
            )
            records = db.run(
                q,
                {"country_id": country_id, "region_id": region_id, "city_id": city_id},
            )
            location = records.single()
            results["location"] = location.data()
            results["validated"] = True

        return results


@app.put("/api/map-new-concept/")
def map_new_concept(concept_id: str, location_id: str) -> dict:

    q = (
        "MATCH(l:Location {location_id:$location_id}) "
        " MATCH(c:Concept {concept_id:$concept_id})"
        " MERGE (l)-[r:HAS_SEED_CONCEPT]->(c) "
        " RETURN r"
    )
    with get_neo4j_connection(settings) as db:
        result = db.run(
            q,
            {
                "location_id": location_id,
                "concept_id": concept_id,
            },
        )
        record = result.single()
    return record.data()
