# Czech Trainer

## Description
Web application helps to learn Czech language.

## How to

### Deploy
```
git pull
docker build . -t czech-trainer:<version> --no-cache
docker-compose stop
docker-compose up -d
```

### Debug
```
docker logs <container-name> -f
docker exec -it <command> <container-name>
```

### Backup database
```
mongodump --db czech --gzip --archive=/path/to/archive
```

### Restore database
```
mongorestore --archive=/path/to/archive
```

### Update user role
Inside mongo-db container:
```
use czech
db.users.updateOne({"login":'Ellesmera'}, {$set: {'role': 2}})
```

## Authors
* Karpeeva Victoria
* Maslov Alexander
