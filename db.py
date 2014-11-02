import pymongo
import os

DB_NAME = 'fundamental'

def get_connection():
    conn = pymongo.Connection(os.getenv('MONGOHQ_URL'))

    return conn

def get_database():
    conn = get_connection()
    return conn[DB_NAME]

def get_collection(coll_name):
    db = get_database()
    return db[coll_name]

def test_connection():
    coll = get_collection('test')
    coll.insert({"name":"testing1"})
    res = find_one('test', {'name':'testing1'})
    return res

#### PUBLIC FUNCTIONS

def find_one(coll_name, query):
    coll = get_collection(coll_name)
    return coll.find_one(query)
