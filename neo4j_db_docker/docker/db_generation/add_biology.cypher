// Create Examen
LOAD CSV WITH HEADERS FROM 'file:///db_generation/biology.csv' AS line FIELDTERMINATOR '\t'
MERGE (m:Maladie {pmsi : line.CONCEPT_CD_PMSI})
WITH line, m
MERGE (b:Examen {label : line.NAME_CHAR, label_unified : line.NAME_CHAR_PROCESSED, type : line.type, concept_cd_dxcarenum : line.CONCEPT_CD_DXCARENUM})
WITH b,m,line
MERGE (m)-[:IS_DIAGNOSED_BY {weight : toFloat(line.value)}]->(b);