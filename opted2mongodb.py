import os
from bs4 import BeautifulSoup
from pymongo import MongoClient

""" Parameters """
port_number = 27017
db_name = 'dictionary'
collection_name = 'definitions'
words = set([])


def main():
    client = MongoClient('localhost', port_number)
    db = client[db_name]
    collection = db[collection_name]
    collection.create_index([('word', 1)], unique=True)

    counter = 1

    for file_name in os.listdir(os.getcwd() + '/data'):
        with open('data/' + file_name, encoding='macintosh') as f:
            soup = BeautifulSoup(f, 'lxml')
        body = soup.body
        for child in body.children:
            if child.name == 'p':
                word = child.b.text.lower()
                pos = child.i.text # part of speech
                definition = child.text.split(')', 1)[1].strip()
                definition_entry = {
                    'parts_of_speech': pos,
                    'definition': definition
                }
                # print('word: {}, part of speech: {}, definition: {}'.format(word, pos, definition))

                if word in words:
                    document = collection.find_one({'word': word})
                    document['definitions_list'].append(definition_entry)
                    collection.replace_one({'word': word}, document, upsert=False)
                else:
                    document = {
                        'word': word,
                        'definitions_list': [definition_entry]
                    }
                    collection.insert_one(document)
                    words.add(word)

                    if counter % 1000 == 0:
                        print('Inserted {} entries'.format(counter))
                    counter += 1
        print("total count: {}".format(counter - 1))


if __name__ == '__main__':
    # execute only if run as a script
    main()

