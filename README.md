# fastapi-mongodb-demo


## Development notes

### ports - `70xx`


| services                    | ports |
|-----------------------------|-------|
| backend                     | 7080  |
| \<docker-compose for test\> | --    |
| jupyter-lab                 | 7088  |
| MongoDB                     | 7017  |


## Development workflow

Start docker-compose:

```shell
$ docker-compose build backend
$ docker-compose up -d
```

Run test

```shell
$ docker-compose exec backend bash
(container)/app# pytest -v -x tests
...
```
