import pymongo

import gauss

schema = {
    str,
    str
}

uri = 'mongodb://admin:image112@host/image_processing'
print('Connecting to Mongo client...')
client = pymongo.MongoClient(uri)

db = client.get_database('image_processing')
users = db['users']

print('Connected')

while True:
    inp_select = int(input("1. Create a new account\n2. Login to an existing account\n"))
    if inp_select == 1:
        username = input("Enter a new username: ")
        pwd = gauss.grep('')
        if users.find_one({'uname': username}):
            print("A user with that name already exists........\n")
        else:
            print('Creating a new user')
            username = username.lower()
            ins = users.insert_one({
                'uname': username,
                'pwd': pwd
            })
            if ins.acknowledged:
                print("New user added :) \n")
            else:
                print("An error occurred \n\n\n")
    elif inp_select == 2:
        username = input("Enter username: ")
        username = username.lower()
        pwd = gauss.grep('')
        if users.find_one({
            'uname': username,
            'pwd': pwd
        }):
            print("Welcome " + username + '\n\n\n')
        else:
            print("A user with that credentials was not found......\n")
    else:
        break

client.close()
