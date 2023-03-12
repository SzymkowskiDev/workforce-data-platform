from tinydb import TinyDB, Query

# create a new database
db = TinyDB('research/sourced_data/document_db.json')

# insert some data
db.insert({'name': 'Alice', 'age': 25})
db.insert({'name': 'Bob', 'age': 30})
db.insert({'name': 'Charlie', 'age': 35})
