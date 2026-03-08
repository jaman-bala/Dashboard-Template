# AUTODOSTUK 🚙

## Applications 💻

A program that allows students to test their knowledge by passing a test. And track your achievements.


## Getting started

```
uv sync
```


ab -k -c 5 -n 20000 'http://localhost:8080/' & \
ab -k -c 5 -n 2000 'http://0.0.0.0:8080/auth/login' & \
ab -k -c 5 -n 3000 'http://0.0.0.0:8080/auth/me' & \
ab -k -c 5 -n 5000 'http://0.0.0.0:8080/questions' & \
ab -k -c 5 -n 5000 'http://0.0.0.0:8080/tickets' & \
ab -k -c 50 -n 5000 'http://0.0.0.0:8080/questions/200?seconds_sleep=1' & \
ab -k -c 50 -n 2000 'http://0.0.0.0:8080/questions/200?seconds_sleep=2'


```aiignore
docker exec -it backend uv run alembic revision --autogenerate -m "update orm"
docker exec -it backend uv run alembic upgrade head
```
