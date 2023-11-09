from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime


client = MongoClient()
db = client['DB3']


def test():
    #print(authorize_user('malaka', 123))
    #print(registrate_user('malaka', '123', 'Daniil', 'Azbukin', '897788011131'))
    #print(add_note('malaka', "NOTE3", "hello world4"))
    #get_notes("malaka")
    #delete_note('6543b9a2b6c9e1a5f8cd8649')
    #update_note('6543b9a6252046cd183e995c', "NEW TTITLE", "NEW TEXT")
    #search_note1('malaka', 'YEA')
    # db['notes'].create_index([('title', 'text'), ('text', 'text')])
    #search_note('malaka', 'Shop')
    pass


def add_user_to_note(username: str, note_id: str):
    user = db['users'].find_one({"username": username})
    if user is not None:
        user_id = user['_id']
        notes_coll = db['notes']
        notes_coll.update_one({"_id": ObjectId(note_id)},
                              {'$push': {'users': ObjectId(user_id)}})
        return 200
    else:
        return 404


def get_username_by_id(id):
    user_coll = db['users']
    username = user_coll.find_one({"_id": ObjectId(id)})['username']
    return username


def get_notes_last_edit(note_id):
    last_edit_coll = db['lastedit']
    result = last_edit_coll.find_one({'note': ObjectId(note_id)})
    return result


def search_note(username: str, text: str):
    user_coll = db['users']
    user_id = user_coll.find_one({"username": username})['_id']
    notes_coll = db['notes']
    result = notes_coll.find({
                    "users": ObjectId(user_id),
                     "$text": {
                         "$search": text
                     }
                     })
    search_arr = []
    for each in result:
        search_arr.append(each)
    return search_arr


def update_note_title(note_id: str, title: str, username: str) -> int:
    notes_collection = db['notes']
    last_edit_coll = db['lastedit']
    user_id = db['users'].find_one({"username": username})['_id']
    note = notes_collection.find_one({"_id": ObjectId(note_id)})
    post_note = {
        "title": title,
        "update_date": datetime.datetime.now(),
        "updated_by": ObjectId(user_id)
    }
    post_last_edit = {
        "note": ObjectId(note_id),
        "title": note['title'],
        "text": note['text'],
        "update_date": note['metadata']['update_date'],
        "updated_by": note['metadata']['updated_by']
    }
    try:
        notes_collection.update_one({"_id": ObjectId(note_id)}, {"$set": post_note})
        if check_history_existance(note_id):
            post_last_edit = {
                "title": note['title'],
                "text": note['text'],
                "update_date": note['metadata']['update_date'],
                "updated_by": note['metadata']['updated_by']
            }
            last_edit_coll.update_one({"note": ObjectId(note_id)}, {"$set": post_last_edit})
        else:
            last_edit_coll.insert_one(post_last_edit)

    except Exception as ex:
        print(ex)
        return 404
    return 200


def check_history_existance(note_id) -> bool:
    notes_collection = db['lastedit']
    if notes_collection.find_one({"note": ObjectId(note_id)}) is not None:
        return True
    else:
        return False


def update_note_text(note_id: str, text: str, username: str) -> int:
    notes_collection = db['notes']
    last_edit_coll = db['lastedit']
    user_id = db['users'].find_one({"username": username})['_id']
    note = notes_collection.find_one({"_id": ObjectId(note_id)})
    post_note = {
        "text": text,
        "update_date": datetime.datetime.now(),
        "updated_by": ObjectId(user_id)
    }
    post_last_edit = {
        "note": ObjectId(note_id),
        "title": note['title'],
        "text": note['text'],
        "update_date": note['metadata']['update_date'],
        "updated_by": note['metadata']['updated_by']
    }
    try:
        notes_collection.update_one({"_id": ObjectId(note_id)}, {"$set": post_note})
        if check_history_existance(note_id):
            post_last_edit = {
                "title": note['title'],
                "text": note['text'],
                "update_date": note['metadata']['update_date'],
                "updated_by": note['metadata']['updated_by']
            }
            last_edit_coll.update_one({"note": ObjectId(note_id)}, {"$set": post_last_edit})
        else:
            last_edit_coll.insert_one(post_last_edit)

    except Exception as ex:
        print(ex)
        return 404
    return 200


def delete_note(note_id: str) -> int:
    notes_collection = db['notes']
    try:
        notes_collection.find_one_and_delete({"_id": ObjectId(note_id)})
    except Exception as ex:
        print(ex)
        return 404
    return 200


def get_note_by_id(id):
    notes_collection = db['notes']
    return notes_collection.find_one({"_id": ObjectId(id)})


def get_notes(username: str):
    user_id = db['users'].find_one({"username": username})['_id']
    notes_collection = db['notes']
    arr_of_notes = []
    for note in notes_collection.find({'users': user_id}):
        arr_of_notes.append(note)
    return arr_of_notes


def add_note(username: str, title: str, text: str) -> int:
    user_collection = db['users']
    user_id = user_collection.find_one({"username": str(username)})['_id']
    post_note = {
        "title": title,
        "text": text,
        "users": [ObjectId(user_id)],
        "metadata": {
            "created_by": ObjectId(user_id),
            "creation_date": datetime.datetime.now(),
            "updated_by": ObjectId(user_id),
            "update_date": datetime.datetime.now(),
        }
    }
    notes_collection = db['notes']
    try:
        notes_collection.insert_one(post_note)
    except Exception as ex:
        return 404
    return 200


def registrate_user(username: str, first_name: str, last_name="") -> int:
    post = {
        "username": username,
        "first_name": first_name,
        "last_name": last_name,
    }

    collection = db['users']
    try:
        user_id = collection.insert_one(post).inserted_id
    except Exception as ex:
        return 404
    return 200


def authorize_user(username: str) -> int:
    collection = db['users']
    user = collection.find_one({"username": username})
    if user is not None:
        return 200
    return 404