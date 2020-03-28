# Czech Trainer

##Description
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
docker exec -it mongo-db -mongobackup --archive --gzip --db czech > db_backup.gz     
```

### Restore database
```
docker exec -it mongo-db mongorestore --archive --gzip < db_backup.gz
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
