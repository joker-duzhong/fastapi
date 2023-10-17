mongo -- "$MONGO_INITDB_DATABASE" <<EOF
    var port = '$DB_PORT';
    var username = '$DB_USERNAME';
    var password = '$DB_PASSWORD';
    var database = '$DB_DATABASE';

    db.createUser(
        {
            user: username,
            pwd: password,
            roles: [ { role: "readWrite", db: database} ],
            passwordDigestor: "server",
        }
    )

    var uri = "mongodb://" + username + ":" + password + "@localhost:" + port + "/" + database
    var db = connect(uri);
    db = db.getSiblingDB(database);

    let res = [
        db.test.insert({ title: 'setup-db', description: 'initialize when mongo container up' }),
        db.test.insert({ title: 'hello', description: 'testing' }),
        db.test.insert({ title: 'fuzzbuzz', description: 'eggspam' })
    ]
    printjson(res)
EOF
