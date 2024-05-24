"""This module contains all Queries"""

RETURN_STMN = "RETURN concept, location, state ORDER BY %s SKIP $skip LIMIT $limit"
COUNT_STMN = "RETURN COUNT(concept) as count"


CONCEPT_LOCATION_QUERY = """
CALL {
  MATCH (l:Location{location_id:$location_id})
  MATCH (cl:Concept)<-[:HAS_SEED_CONCEPT]-(l)
  RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state

  UNION
  MATCH (loc:Location{location_id:$location_id})
  MATCH (c:Concept)<-[:HAS_SEED_CONCEPT]-(loc)
  MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*1..5]->(c)
  MATCH (cl:Concept)-[:HAS_SEED_CONCEPT]-(l:Location)
  RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state


  UNION // level 1
  MATCH (loc:Location{location_id:$location_id})
  MATCH (c:Concept)<-[:HAS_SEED_CONCEPT]-(loc)
  MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*1..6]->(c)
  MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*1]->(:Concept)-[:HAS_SEED_CONCEPT]-(l:Location)
    WHERE size((cl)-[:HAS_SEED_CONCEPT]-(:Location)) = 0
        RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state



  UNION // level 2
  MATCH (loc:Location{location_id:$location_id})
  MATCH (c:Concept)<-[:HAS_SEED_CONCEPT]-(loc)
  MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*1..6]->(c)
  MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*2]->(:Concept)-[:HAS_SEED_CONCEPT]-(l:Location)
    WHERE size((cl)-[:HAS_SEED_CONCEPT]-(:Location)) = 0
      AND size((cl:Concept)-[:HAS_HIGHER_LOCATION*1]->(:Concept)-[:HAS_SEED_CONCEPT]-(:Location)) = 0
        RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state


  UNION // level 3
  MATCH (loc:Location{location_id:$location_id})
  MATCH (c:Concept)<-[:HAS_SEED_CONCEPT]-(loc)
  MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*1..6]->(c)
  MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*3]->(:Concept)-[:HAS_SEED_CONCEPT]-(l:Location)
    WHERE size((cl)-[:HAS_SEED_CONCEPT]-(:Location)) = 0
      AND size((cl:Concept)-[:HAS_HIGHER_LOCATION*1..2]->(:Concept)-[:HAS_SEED_CONCEPT]-(:Location)) = 0
        RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state


  UNION // level 4
  MATCH (loc:Location{location_id:$location_id})
  MATCH (c:Concept)<-[:HAS_SEED_CONCEPT]-(loc)
  MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*1..6]->(c)
  MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*4]->(:Concept)-[:HAS_SEED_CONCEPT]-(l:Location)
    WHERE size((cl)-[:HAS_SEED_CONCEPT]-(:Location)) = 0
      AND size((cl:Concept)-[:HAS_HIGHER_LOCATION*1..3]->(:Concept)-[:HAS_SEED_CONCEPT]-(:Location)) = 0
        RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state


  UNION // level 5
  MATCH (loc:Location{location_id:$location_id})
  MATCH (c:Concept)<-[:HAS_SEED_CONCEPT]-(loc)
  MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*1..6]->(c)
  MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*5]->(:Concept)-[:HAS_SEED_CONCEPT]-(l:Location)
    WHERE size((cl)-[:HAS_SEED_CONCEPT]-(:Location)) = 0
      AND size((cl:Concept)-[:HAS_HIGHER_LOCATION*1..4]->(:Concept)-[:HAS_SEED_CONCEPT]-(:Location)) = 0
        RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state

  UNION // level 6
  MATCH (loc:Location{location_id:$location_id})
  MATCH (c:Concept)<-[:HAS_SEED_CONCEPT]-(loc)
  MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*1..6]->(c)
  MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*6]->(:Concept)-[:HAS_SEED_CONCEPT]-(l:Location)
    WHERE size((cl)-[:HAS_SEED_CONCEPT]-(:Location)) = 0
      AND size((cl:Concept)-[:HAS_HIGHER_LOCATION*1..5]->(:Concept)-[:HAS_SEED_CONCEPT]-(:Location)) = 0
        RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state

}
"""

LOWER_CONCEPTS_QUERY = """
CALL {
  // first lets found concept's location
  // which can be higher at few levels:

  MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*1..5]->(c:Concept{concept_id:$concept_id})
    MATCH (cl)-[:HAS_SEED_CONCEPT]-(l:Location) 
      RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state

    UNION // level 1
  MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*1..5]->(c:Concept{concept_id:$concept_id})
    MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*1]->(:Concept)-[:HAS_SEED_CONCEPT]-(l:Location)
    WHERE size((cl)-[:HAS_SEED_CONCEPT]-(:Location)) = 0
        RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state


    UNION // level 2
  MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*1..5]->(c:Concept{concept_id:$concept_id})
    MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*2]->(:Concept)-[:HAS_SEED_CONCEPT]-(l:Location)
    WHERE size((cl)-[:HAS_SEED_CONCEPT]-(:Location)) = 0
      AND size((cl:Concept)-[:HAS_HIGHER_LOCATION*1]->(:Concept)-[:HAS_SEED_CONCEPT]-(:Location)) = 0   
        RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state


    UNION // level 3
  MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*1..5]->(c:Concept{concept_id:$concept_id})
    MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*3]->(:Concept)-[:HAS_SEED_CONCEPT]-(l:Location)
    WHERE size((cl)-[:HAS_SEED_CONCEPT]-(:Location)) = 0
      AND size((cl:Concept)-[:HAS_HIGHER_LOCATION*1..2]->(:Concept)-[:HAS_SEED_CONCEPT]-(:Location)) = 0   
        RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state


    UNION // level 4
  MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*1..5]->(c:Concept{concept_id:$concept_id})
    MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*4]->(:Concept)-[:HAS_SEED_CONCEPT]-(l:Location)
    WHERE size((cl)-[:HAS_SEED_CONCEPT]-(:Location)) = 0
      AND size((cl:Concept)-[:HAS_HIGHER_LOCATION*1..3]->(:Concept)-[:HAS_SEED_CONCEPT]-(:Location)) = 0   
        RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state

    UNION // level 5
  MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*1..5]->(c:Concept{concept_id:$concept_id})
    MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*5]->(:Concept)-[:HAS_SEED_CONCEPT]-(l:Location)
    WHERE size((cl)-[:HAS_SEED_CONCEPT]-(:Location)) = 0
      AND size((cl:Concept)-[:HAS_HIGHER_LOCATION*1..4]->(:Concept)-[:HAS_SEED_CONCEPT]-(:Location)) = 0   
        RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state


}
"""

#----------------------------------------------------------------------------

CONCEPTS_BY_NAME_QUERY = """
  // this query found concept by it name and all lower concepts.
CALL {
  // first lets found concept's location
  // which can be higher at few levels:

  MATCH (cl:Concept{concept_id:$concept_id})-[:HAS_SEED_CONCEPT]-(l:Location)
      RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state
   UNION 

  MATCH (cl:Concept{concept_id:$concept_id})-[:HAS_HIGHER_LOCATION*1]->(c:Concept)<-[:HAS_SEED_CONCEPT]-(l:Location)
     WHERE size ((cl)-[:HAS_SEED_CONCEPT]-(:Location)) = 0
      RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state
   UNION 

  MATCH (cl:Concept{concept_id:$concept_id})-[:HAS_HIGHER_LOCATION*2]->(c:Concept)<-[:HAS_SEED_CONCEPT]-(l:Location)
     WHERE size ((cl)-[:HAS_SEED_CONCEPT]-(:Location)) = 0
       AND size ((cl)-[:HAS_HIGHER_LOCATION*1]->(:Concept)<-[:HAS_SEED_CONCEPT]-(:Location)) = 0
      RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state
   UNION 

  MATCH (cl:Concept{concept_id:$concept_id})-[:HAS_HIGHER_LOCATION*3]->(c:Concept)<-[:HAS_SEED_CONCEPT]-(l:Location)
     WHERE size ((cl)-[:HAS_SEED_CONCEPT]-(:Location)) = 0
       AND size ((cl)-[:HAS_HIGHER_LOCATION*1..2]->(:Concept)<-[:HAS_SEED_CONCEPT]-(:Location)) = 0
      RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state
   UNION 

  MATCH (cl:Concept{concept_id:$concept_id})-[:HAS_HIGHER_LOCATION*4]->(c:Concept)<-[:HAS_SEED_CONCEPT]-(l:Location)
     WHERE size ((cl)-[:HAS_SEED_CONCEPT]-(:Location)) = 0
       AND size ((cl)-[:HAS_HIGHER_LOCATION*1..3]->(:Concept)<-[:HAS_SEED_CONCEPT]-(:Location)) = 0
      RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state
  // now lets go through lower locations:

   UNION // level 5

  MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*1..5]->(c:Concept{concept_id:$concept_id})
    MATCH (cl)-[:HAS_SEED_CONCEPT]-(l:Location) 
      RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state

    UNION // level 1
  MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*1..6]->(c:Concept{concept_id:$concept_id})
    MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*1]->(:Concept)-[:HAS_SEED_CONCEPT]-(l:Location)
    WHERE size((cl)-[:HAS_SEED_CONCEPT]->(:Location)) = 0
        RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state


    UNION // level 2
  MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*1..6]->(c:Concept{concept_id:$concept_id})
    MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*2]->(:Concept)-[:HAS_SEED_CONCEPT]-(l:Location)
    WHERE size((cl)-[:HAS_SEED_CONCEPT]->(:Location)) = 0
      AND size((cl:Concept)-[:HAS_HIGHER_LOCATION*1]->(:Concept)-[:HAS_SEED_CONCEPT]-(:Location)) = 0   
        RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state


    UNION // level 3
  MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*1..6]->(c:Concept{concept_id:$concept_id})
    MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*3]->(:Concept)-[:HAS_SEED_CONCEPT]-(l:Location)
    WHERE size((cl)-[:HAS_SEED_CONCEPT]->(:Location)) = 0
      AND size((cl:Concept)-[:HAS_HIGHER_LOCATION*1..2]->(:Concept)-[:HAS_SEED_CONCEPT]-(:Location)) = 0   
        RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state


    UNION // level 4
  MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*1..6]->(c:Concept{concept_id:$concept_id})
    MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*4]->(:Concept)-[:HAS_SEED_CONCEPT]-(l:Location)
    WHERE size((cl)-[:HAS_SEED_CONCEPT]->(:Location)) = 0
      AND size((cl:Concept)-[:HAS_HIGHER_LOCATION*1..3]->(:Concept)-[:HAS_SEED_CONCEPT]-(:Location)) = 0   
        RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state

    UNION // level 5
  MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*1..6]->(c:Concept{concept_id:$concept_id})
    MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*5]->(:Concept)-[:HAS_SEED_CONCEPT]-(l:Location)
    WHERE size((cl)-[:HAS_SEED_CONCEPT]->(:Location)) = 0
      AND size((cl:Concept)-[:HAS_HIGHER_LOCATION*1..4]->(:Concept)-[:HAS_SEED_CONCEPT]-(:Location)) = 0   
        RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state


    UNION // level 6
  MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*1..6]->(c:Concept{concept_id:$concept_id})
    MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*6]->(:Concept)-[:HAS_SEED_CONCEPT]-(l:Location)
    WHERE size((cl)-[:HAS_SEED_CONCEPT]->(:Location)) = 0
      AND size((cl:Concept)-[:HAS_HIGHER_LOCATION*1..5]->(:Concept)-[:HAS_SEED_CONCEPT]-(:Location)) = 0   
        RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state



}
"""


#----------------------------------------------------------------------------

HIGHER_CONCEPTS_QUERY = """
CALL {
  MATCH (c:Concept{concept_id:$concept_id})-[:HAS_HIGHER_LOCATION*1..5]->(cl:Concept)
    MATCH (cl)-[:HAS_SEED_CONCEPT]-(l:Location) 
      RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state

    UNION
      MATCH (c:Concept{concept_id:$concept_id})-[:HAS_HIGHER_LOCATION*1..5]->(cl:Concept)
          MATCH (cl)-[:HAS_HIGHER_LOCATION*1]->(con:Concept)<-[:HAS_SEED_CONCEPT]-(l:Location) 
           WHERE NOT EXISTS 
            {
               MATCH (cl)-[:HAS_SEED_CONCEPT]-()
            } // exclude has_seed_concepts
        RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state

    UNION
      MATCH (c:Concept{concept_id:$concept_id})-[:HAS_HIGHER_LOCATION*1..5]->(cl:Concept)
      MATCH (cl)-[:HAS_HIGHER_LOCATION*2]->(con:Concept)<-[:HAS_SEED_CONCEPT]-(l:Location) 
         WHERE NOT EXISTS 
          {
            MATCH (cl)-[:HAS_SEED_CONCEPT]-() // exclude has_seed_concepts
          } 
         AND NOT EXISTS {
           MATCH (cl)-[:HAS_HIGHER_LOCATION*1]->(c:Concept)<-[:HAS_SEED_CONCEPT]-()
           // exclude 1 level concepts
         }
        RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state

    UNION // third level
    MATCH (c:Concept{concept_id:$concept_id})-[:HAS_HIGHER_LOCATION*1..5]->(cl:Concept)
      MATCH (cl)-[:HAS_HIGHER_LOCATION*3]->(con:Concept)<-[:HAS_SEED_CONCEPT]-(l:Location) 
         WHERE NOT EXISTS 
          {       
            MATCH (cl)-[:HAS_SEED_CONCEPT]-()} // exclude has_seed_concepts
         AND NOT EXISTS {           
           MATCH (cl)-[:HAS_HIGHER_LOCATION*1..2]->(c:Concept)<-[:HAS_SEED_CONCEPT]-(Location)
         }
        RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state

    UNION // fourth level
    MATCH (c:Concept{concept_id:$concept_id})-[:HAS_HIGHER_LOCATION*1..5]->(cl:Concept)
      // WITH cl
      MATCH (cl)-[:HAS_HIGHER_LOCATION*4]->(con:Concept)<-[:HAS_SEED_CONCEPT]-(l:Location) 
         WHERE NOT EXISTS 
          {       
            MATCH (cl)-[:HAS_SEED_CONCEPT]-()
          } // exclude seed_concepts

         AND NOT EXISTS {           
           MATCH (cl)-[:HAS_HIGHER_LOCATION*1..3]->(c:Concept)<-[:HAS_SEED_CONCEPT]-(Location)
         } // we only need concepts/locations here which does not has
           // has_seed concepts through higher level concepts.

        RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state
}
"""

#----------------------------------------------------------------------------



ALL_CONCEPTS_QUERY = """

CALL {
    MATCH (cl:Concept)-[s:HAS_SEED_CONCEPT]-(l:Location) 
      RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state

    UNION
      MATCH (cl)-[:HAS_HIGHER_LOCATION*1]->(con:Concept)<-[:HAS_SEED_CONCEPT]-(l:Location)
         WHERE size( (cl)-[:HAS_SEED_CONCEPT]-(:Location) ) = 0
      RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state


    UNION // level 2
      MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*2]->(con:Concept)<-[:HAS_SEED_CONCEPT]-(l:Location) 
           WHERE size((cl)-[:HAS_HIGHER_LOCATION*1]->(:Concept)<-[:HAS_SEED_CONCEPT]-(:Location)) = 0
           AND size((cl)-[:HAS_SEED_CONCEPT]-(:Location)) = 0
      RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state

    UNION // level 3
      MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*3]->(con:Concept)<-[:HAS_SEED_CONCEPT]-(l:Location) 
           WHERE size((cl)-[:HAS_HIGHER_LOCATION*1..2]->(:Concept)<-[:HAS_SEED_CONCEPT]-(:Location)) = 0
           AND size((cl)-[:HAS_SEED_CONCEPT]-(:Location)) = 0
      RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state

    UNION // level 4
      MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*4]->(con:Concept)<-[:HAS_SEED_CONCEPT]-(l:Location) 
           WHERE size((cl)-[:HAS_HIGHER_LOCATION*1..3]->(:Concept)<-[:HAS_SEED_CONCEPT]-(:Location)) = 0
           AND size((cl)-[:HAS_SEED_CONCEPT]-(:Location)) = 0
      RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state

  UNION // level 5
      MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*5]->(con:Concept)<-[:HAS_SEED_CONCEPT]-(l:Location) 
           WHERE size((cl)-[:HAS_HIGHER_LOCATION*1..4]->(:Concept)<-[:HAS_SEED_CONCEPT]-(:Location)) = 0
           AND size((cl)-[:HAS_SEED_CONCEPT]-(:Location)) = 0
      RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state

}
"""

#----------------------------------------------------------------------------


COUNTRY_CONCEPTS_QUERY = """

CALL {
    MATCH (l:Location)-[:HAS_COUNTRY]-(country:Country{country_id:$country_id})
    MATCH (cl:Concept)<-[:HAS_SEED_CONCEPT]-(l:Location) 
      RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state
    UNION
      MATCH (l:Location)-[:HAS_COUNTRY]-(country:Country{country_id:$country_id})
      MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*1]->(con:Concept)<-[:HAS_SEED_CONCEPT]-(l) 
         WHERE size((cl)-[:HAS_SEED_CONCEPT]-(:Location)) = 0
        RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state

    UNION // level 2
      MATCH (l:Location)-[:HAS_COUNTRY]-(country:Country{country_id:$country_id})
      MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*2]->(con:Concept)<-[:HAS_SEED_CONCEPT]-(l) 
           WHERE size((cl)-[:HAS_HIGHER_LOCATION*1]->(:Concept)<-[:HAS_SEED_CONCEPT]-(:Location)) = 0
           AND size((cl)-[:HAS_SEED_CONCEPT]-(:Location)) = 0
        RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state


    UNION // level 3
      MATCH (l:Location)-[:HAS_COUNTRY]-(country:Country{country_id:$country_id})
      MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*3]->(con:Concept)<-[:HAS_SEED_CONCEPT]-(l) 
           WHERE size((cl)-[:HAS_HIGHER_LOCATION*1..2]->(:Concept)<-[:HAS_SEED_CONCEPT]-(:Location)) = 0
           AND size((cl)-[:HAS_SEED_CONCEPT]-(:Location)) = 0
        RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state

    UNION // level 4
      MATCH (l:Location)-[:HAS_COUNTRY]-(country:Country{country_id:$country_id})
      MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*4]->(con:Concept)<-[:HAS_SEED_CONCEPT]-(l) 
           WHERE size((cl)-[:HAS_HIGHER_LOCATION*1..3]->(:Concept)<-[:HAS_SEED_CONCEPT]-(:Location)) = 0
           AND size((cl)-[:HAS_SEED_CONCEPT]-(:Location)) = 0
        RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state

    UNION // level 5
      MATCH (l:Location)-[:HAS_COUNTRY]-(country:Country{country_id:$country_id})
      MATCH (cl:Concept)-[:HAS_HIGHER_LOCATION*5]->(con:Concept)<-[:HAS_SEED_CONCEPT]-(l) 
           WHERE size((cl)-[:HAS_HIGHER_LOCATION*1..4]->(:Concept)<-[:HAS_SEED_CONCEPT]-(:Location)) = 0
           AND size((cl)-[:HAS_SEED_CONCEPT]-(:Location)) = 0
        RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state

}
"""

#----------------------------------------------------------------------------



REGION_CONCEPTS_QUERY = """

CALL {
    MATCH (l:Location)-[:HAS_COUNTRY]-(country:Country{country_id:$country_id})
    MATCH (l:Location)-[:HAS_REGION]-(region:Region{region_id:$region_id})
    MATCH (cl:Concept)-[s:HAS_SEED_CONCEPT]-(l:Location) 
      RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state

    UNION
      MATCH (l:Location)-[:HAS_COUNTRY]-(country:Country{country_id:$country_id})
      MATCH (l:Location)-[:HAS_REGION]-(region:Region{region_id:$region_id})
      MATCH (cl)-[:HAS_HIGHER_LOCATION*1]->(con:Concept)<-[:HAS_SEED_CONCEPT]-(l:Location) 
         WHERE size( (cl)-[:HAS_SEED_CONCEPT]-(:Location) ) = 0
        RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state

    UNION // level 2
      MATCH (l:Location)-[:HAS_COUNTRY]-(country:Country{country_id:$country_id})
      MATCH (l:Location)-[:HAS_REGION]-(region:Region{region_id:$region_id})
      MATCH (cl)-[:HAS_HIGHER_LOCATION*2]->(con:Concept)<-[:HAS_SEED_CONCEPT]-(l:Location) 
           WHERE size((cl)-[:HAS_HIGHER_LOCATION*1]->(:Concept)<-[:HAS_SEED_CONCEPT]-(:Location)) = 0
           AND size((cl)-[:HAS_SEED_CONCEPT]-(:Location)) = 0
        RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state

    UNION // level 3
      MATCH (l:Location)-[:HAS_COUNTRY]-(country:Country{country_id:$country_id})
      MATCH (l:Location)-[:HAS_REGION]-(region:Region{region_id:$region_id})
      MATCH (cl)-[:HAS_HIGHER_LOCATION*3]->(con:Concept)<-[:HAS_SEED_CONCEPT]-(l:Location) 
           WHERE size((cl)-[:HAS_HIGHER_LOCATION*1..2]->(:Concept)<-[:HAS_SEED_CONCEPT]-(:Location)) = 0
           AND size((cl)-[:HAS_SEED_CONCEPT]-(:Location)) = 0
        RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state

    UNION // level 4
      MATCH (l:Location)-[:HAS_COUNTRY]-(country:Country{country_id:$country_id})
      MATCH (l:Location)-[:HAS_REGION]-(region:Region{region_id:$region_id})
      MATCH (cl)-[:HAS_HIGHER_LOCATION*4]->(con:Concept)<-[:HAS_SEED_CONCEPT]-(l:Location) 
           WHERE size((cl)-[:HAS_HIGHER_LOCATION*1..3]->(:Concept)<-[:HAS_SEED_CONCEPT]-(:Location)) = 0
           AND size((cl)-[:HAS_SEED_CONCEPT]-(:Location)) = 0
        RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state

    UNION // level 5
      MATCH (l:Location)-[:HAS_COUNTRY]-(country:Country{country_id:$country_id})
      MATCH (l:Location)-[:HAS_REGION]-(region:Region{region_id:$region_id})
      MATCH (cl)-[:HAS_HIGHER_LOCATION*5]->(con:Concept)<-[:HAS_SEED_CONCEPT]-(l:Location) 
           WHERE size((cl)-[:HAS_HIGHER_LOCATION*1..4]->(:Concept)<-[:HAS_SEED_CONCEPT]-(:Location)) = 0
           AND size((cl)-[:HAS_SEED_CONCEPT]-(:Location)) = 0
        RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state

}
"""

#----------------------------------------------------------------------------


CITIES_CONCEPTS_QUERY = """

CALL {
    MATCH (l:Location)-[:HAS_COUNTRY]-(country:Country{country_id:$country_id})
    MATCH (l:Location)-[:HAS_REGION]-(region:Region{region_id:$region_id})
    MATCH (l:Location)-[:HAS_CITY]-(city:City{city_id:$city_id})
    MATCH (cl:Concept)-[s:HAS_SEED_CONCEPT]-(l:Location) 
      RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state

    UNION
      MATCH (l:Location)-[:HAS_COUNTRY]-(country:Country{country_id:$country_id})
      MATCH (l:Location)-[:HAS_REGION]-(region:Region{region_id:$region_id})
      MATCH (l:Location)-[:HAS_CITY]-(city:City{city_id:$city_id})
      MATCH (cl)-[:HAS_HIGHER_LOCATION*1]->(con:Concept)<-[:HAS_SEED_CONCEPT]-(l:Location) 
         WHERE size( (cl)-[:HAS_SEED_CONCEPT]-(:Location) ) = 0
        RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state

    UNION // level 2
      MATCH (l:Location)-[:HAS_COUNTRY]-(country:Country{country_id:$country_id})
      MATCH (l:Location)-[:HAS_REGION]-(region:Region{region_id:$region_id})
      MATCH (l:Location)-[:HAS_CITY]-(city:City{city_id:$city_id})
      MATCH (cl)-[:HAS_HIGHER_LOCATION*2]->(con:Concept)<-[:HAS_SEED_CONCEPT]-(l:Location) 
           WHERE size((cl)-[:HAS_HIGHER_LOCATION*1]->(:Concept)<-[:HAS_SEED_CONCEPT]-(:Location)) = 0
           AND size((cl)-[:HAS_SEED_CONCEPT]-(:Location)) = 0
        RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state

    UNION // level 3
      MATCH (l:Location)-[:HAS_COUNTRY]-(country:Country{country_id:$country_id})
      MATCH (l:Location)-[:HAS_REGION]-(region:Region{region_id:$region_id})
      MATCH (l:Location)-[:HAS_CITY]-(city:City{city_id:$city_id})
      MATCH (cl)-[:HAS_HIGHER_LOCATION*3]->(con:Concept)<-[:HAS_SEED_CONCEPT]-(l:Location) 
           WHERE size((cl)-[:HAS_HIGHER_LOCATION*1..2]->(:Concept)<-[:HAS_SEED_CONCEPT]-(:Location)) = 0
           AND size((cl)-[:HAS_SEED_CONCEPT]-(:Location)) = 0
        RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state

    UNION // level 4
      MATCH (l:Location)-[:HAS_COUNTRY]-(country:Country{country_id:$country_id})
      MATCH (l:Location)-[:HAS_REGION]-(region:Region{region_id:$region_id})
      MATCH (l:Location)-[:HAS_CITY]-(city:City{city_id:$city_id})
      MATCH (cl)-[:HAS_HIGHER_LOCATION*4]->(con:Concept)<-[:HAS_SEED_CONCEPT]-(l:Location) 
           WHERE size((cl)-[:HAS_HIGHER_LOCATION*1..3]->(:Concept)<-[:HAS_SEED_CONCEPT]-(:Location)) = 0
           AND size((cl)-[:HAS_SEED_CONCEPT]-(:Location)) = 0
        RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state

    UNION // level 5
      MATCH (l:Location)-[:HAS_COUNTRY]-(country:Country{country_id:$country_id})
      MATCH (l:Location)-[:HAS_REGION]-(region:Region{region_id:$region_id})
      MATCH (l:Location)-[:HAS_CITY]-(city:City{city_id:$city_id})
      MATCH (cl)-[:HAS_HIGHER_LOCATION*5]->(con:Concept)<-[:HAS_SEED_CONCEPT]-(l:Location) 
           WHERE size((cl)-[:HAS_HIGHER_LOCATION*1..4]->(:Concept)<-[:HAS_SEED_CONCEPT]-(:Location)) = 0
           AND size((cl)-[:HAS_SEED_CONCEPT]-(:Location)) = 0
        RETURN cl as concept, l as location, NOT EXISTS((cl)-[:DEACTIVATES]-(l)) as state
}
"""

#----------------------------------------------------------------------------
