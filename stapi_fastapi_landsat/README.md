## Landsat backend

Start the server locally

```sh
poetry run landsat
```

GET all products
```sh
curl http://127.0.0.1:8000/products
```

POST to opportunities
```sh
curl -d '{"geometry": {"type": "Point", "coordinates": [13.4, 52.5]}, "product_id": "landsat:9", "datetime": "2024-05-01T00:00:00Z/2024-05-12T00:00:00Z"}' -H "Content-Type: application/json" -X POST http://127.0.0.1:8000/opportunities
```
