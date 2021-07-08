// Create Symptome
LOAD CSV WITH HEADERS FROM 'file:///db_generation/symptoms.csv' AS line FIELDTERMINATOR '\t'
MERGE (m:Maladie {wikidata : line.diseaseWikidata})
WITH line, m
MERGE (s:Symptome {label : line.prefLabel, label_unified : line.prefLabel_processed, cui: line.CUI, wikidata: line.wikidata, synonyms: line.synonyms, synonyms_unified: line.synonyms_processed})
WITH s,m,line
MERGE (s)-[:IS_SYMPTOM_OF {weight : toFloat(line.weight)}]->(m);