# asyncio_chat

This is my try to create some chat app server using Quart and Mongodb  
There's some problems like delivering updates of nicknames and lack of functionallity yet, but you may help me fix it or I'll fix it some time soon  

## TODO list

- [ ] Write new tests
- [ ] More efficient paged channels receiving
- [ ] Add pagination get methods of listed data
- [ ] Changing passwords
- [ ] Specifying for what channel type we are looking for
- [ ] Group dms ownership transfering
- [ ] Servers, roles, emojis, etc.
- [ ] Voice calls
- [x] Add clearer way to init routes
- [x] Group DMs
- [x] Bot users and their managment
- [x] Updates notification
- [x] Better files uploading
- [x] Optmizate logging in
- [x] Add autocleaner of inactive users
- [x] Add some users updates notification system

## Install guide

Steps:

- Firstly you should get python 3.7 and above cause of used modules

- Install all mudiles required to work with: `pip install -r requirements.txt` while being inside working dir in console (might need to put `pip3` for linux users)

- Install [MongoDB](https://www.mongodb.com/try/download/community)

- Run app for the first time to generate `config.ini`

- Change settings you need (likely these will be: `debug`, `host`, `port` and `db_conn_string`)

To see more about [connection string](https://docs.mongodb.com/manual/reference/connection-string/) for mongodb

- Also you might need to add encryption so go and change `priv_key`, `pub_key` and maybe `ca_certs`

## Documentation:

See [documenatation file](/Docs.md) and [docs formatting](/Docs_format.md)
