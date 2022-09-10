# Mountain Pass API (SF 09.2022)

API for submitting mountain pass data

* FastAPI
* BeanieODM
* MongoDB
* Motor

## Setup

Edit `compose.yaml` to set mongo credentials

```shell
docker-compose -f compose.yaml up
```

Edit `.env` file or set `FSTR_MONGO_URI`, `FSTR_UPLOAD_DIR` environment variables

```shell
uvicorn main:app --port 8089 --reload
```

## API Methods

`GET '/submitData/{id}'`

Returns mountain pass data by its ID

`GET /submitData?user__email={email}`

Return list of mountain pass data submitted by user with given email

`POST /submitData`

Save new mountain pass data to DB

`PATCH /submitData/{id}` 

Edit existing mountain pass data

### Swagger doc

Swagger docs also available at `http://localhost:8089/docs`