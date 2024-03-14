# Build a Site Using Django, Vue, and GraphQL

## Starting the back-end Django application

In a new terminal tab:

1. Install the back-end requirements in the environment of your choice:
  ```shell
  MacOS: source .venv/bin/activate
  Windows: .venv/Scripts/activate
  python3 -m pip install -r requirements.txt
  # отключаем создание .pyc файлов
  MacOS: export PYTHONDONTWRITEBYTECODE=True
  Windows: SET PYTHONDONTWRITEBYTECODE=True
  ```
2. Start Django project
  ```shell
  django-admin startproject backend
  ```
3. Create the app Django:
  ```shell
  cd backend/
  python manage.py startapp aggregator
  ```
4. Create the initial Django database by running migrations:
  ```shell
  cd backend/
  python manage.py migrate
  ```
5. Create a Django superuser:
  ```shell
  cd backend/
  python manage.py createsuperuser
  ```
6. Run the Django project (by default on port 8000):
  ```shell
  cd backend/
  python manage.py runserver
  ```
7. Make migrations
  ```shell
  cd backend/
  python manage.py makemigrations
  python manage.py migrate
  ```
8. Make messages
  ```shell
  cd backend/
  django-admin makemessages --all
  ```
9. Compile messages
  ```shell
  cd backend/
  django-admin compilemessages
  ```
10. Archive DB
  ```shell
  python -Xutf8 manage.py dumpdata --indent=2 --output=fixtures/db.json
  ```
11. Restore DB
  ```shell
  python manage.py loaddata fixtures/db.json
  ```

## Starting Celery

1. Start Celery Beat
  ```shell
  celery -A backend beat --loglevel=INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
  ```

2. Start Celery worker
  ```shell
  celery -A backend worker --loglevel=INFO
  ```

## Starting Docker
  ```shell
  docker-compose --project-name="product-aggregator" up -d
  ```

## Starting the front-end Vue application

In a new terminal tab:

1. Install the front-end requirements:
  ```shell
  vue create frontend
  ```
2. Run the Vue project (by default on port 8080):
  ```shell
  cd frontend
  npm run serve
  ```
3. Install Apollo
  ```shell
  cd frontend
  npm install --save @vue/apollo-option
  npm install --save @apollo/client
  npm install --save graphql
  npm install --save graphql-tag
  ```

## Admin

1. Visit [the Django admin](http://localhost:8000/admin)
2. Log in using the superuser you created earlier
3. Admin area

## View the app

1. Visit [the app homepage](http://localhost:8080)
2. Browse product aggregator

## Try the GraphQL API yourself

1. Visit [the GraphiQL interface](http://localhost:8000/graphql)
2. View the *Docs* panel on the top right
3. Create some queries&mdash;the available information should auto-populate!
