fundamental
===========

Money 20/20 Project

# Setup
=========
To set Mongo HQ URL, do:

```
heroku config:set MONGOHQ_URL="mongodb://<dbuser>:<dbpassword>@ds047940.mongolab.com:47940/fundamental"

heroku config:set VENMO_CLIENT_ID="<client_id>"

heroku config:set VENMO_CLIENT_SECRET="<client_id>"

heroku config:set VENMO_ACCESS_TOKEN="<access_token>"
```

For local development, add to your ~/.bashrc:

```
export MONGOHQ_URL="mongodb://<dbuser>:<dbpassword>@ds047940.mongolab.com:47940/fundamental"
```

See google doc for the dbuser and dbpassword

