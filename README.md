# Market Orders Steaming to YugabyteDB with Django

This application subscribes to the [PubNub Market Orders Stream](https://www.pubnub.com/developers/realtime-data-streams/financial-securities-market-orders/) via Python [Django](https://docs.djangoproject.com/en/4.1/) with an optional support to ingest data as a [celery](https://docs.celeryq.dev/en/latest/index.html) task and stores the market trades in YugabyteDB.


Check [this blog post](https://www.yugabyte.com/blog/building-simple-application-yugabytedb-prisma/) for a quick app overview.

**How the application ingests the PubNub Market Orders stream data:**

- **Method 1:** : Subscribe to the data stream via API endpoint (inside View) and then store the data in YugabyteDB.
- **Method 2:** : Subscribe to the data stream by creating Celery task (running it in background) to store the data in YugabyteDB. For long running tasks like storing the realtime data stream to database, it's recommended to use the tasks queues.

## Run using YugabyteDB Managed

1. [Sign up for YugabyteDB Managed](https://docs.yugabyte.com/preview/yugabyte-cloud/cloud-quickstart/) and create a free cluster.  Additionally, follow this [guide](https://docs.yugabyte.com/preview/yugabyte-cloud/cloud-quickstart/cloud-build-apps/cloud-add-ip/#download-your-cluster-certificate) to download your cluster CA certificate and set up your cluster IP allow list.

2. Run the following to create [virtual environment](https://docs.python.org/3/glossary.html#term-virtual-environment) for app and install application dependencies (first time only):

```bash
$ python3 -m venv market_order_app_venv  # create the virtual environment
$ source market_order_app_venv/bin/activate  # activate the virtual environment
$ cd market-orders-app-django/
$ pip install -r requirements.txt
```

3. Configure your environment variables in the .env file ( create a .env file if it doesn't exist, check `.env_example` ):

```bash
DATABASE_URL=postgresql://yuagbyte:yuagbyte@usxx.ybdb.io:5433/yugabyte
```

4. Run the following to initialize the database with model schema:

```bash
$ python manage.py makemigrations
$ python manage.py sqlmigrate market_orders 0001_initial # or your  migratino fiile name
$ python manage.py migrate
```

This will create the tables for the models as written in the `market_orders/models.py`

5. Seed the user data in the `User` model. Run the following to insert the default user data for User table:

```bash
$python manage.py runscript seed_user_data
```

`seed_user_data.py` will create user data using the [`faker`](https://github.com/joke2k/faker) module and inserts it into the `User` model table. But for the best practice it's recommended to use [fixtures](https://docs.djangoproject.com/en/2.2/howto/initial-data/).

6. Run the application:

- **Method 1:** Using views to store the market order data

    ```bash
        $ python manage.py runserver
    ```
    You can see the app running on [http://127.0.0.1:8000](http://127.0.0.1:8000).

    ![market order application home page](/Docs/images/market_order_home_d.png)

    Test the application (You can use [Postman](https://www.postman.com/downloads/) or cURL to send the requests)

    - Subscribe to a channel - `curl --location --request GET 'http://127.0.0.1:8000/subscription/add?channel=pubnub-market-orders'`
    - Unsubscribe from a channel - `curl --location --request GET 'http://127.0.0.1:5001/subscription/remove?channel=pubnub-market-orders'`
    - Get subscribed channels - `curl --location --request GET 'http://127.0.0.1:5001/subscription/list'`
    - Ingest the market order stream to YugabyteDB - `curl --location --request GET 'http://127.0.0.1:8000/ingeststreamdata?channel=pubnub-market-orders'`
    - Get Trade stats - `curl --location --request GET 'http://127.0.0.1:5001/tradestats'`

    Here is the screenshot of how to call the API request in Postman.
    - Subscribe to a channel
    ![Subscribe to the channel](/Docs/images/add_subscription_d.png)
    - Ingest data request
    ![Ingest data request response](/Docs/images/ingest_data_d.png)
    - Get Trade stats
    ![Get Trade stats](/Docs/images/trade_stats_d.png)


    ---

- **Method 2:** Running the Celery task with  the application to ingest the data
    - [Install redis](https://redis.io/docs/getting-started/installation/), to use it as a broker and backed tp store the task results. For  backend you can also use YugabyteDB, by twealking the celery backed configuration in the `market_order_app/settings.py` file.
    - Open 3 terminal windows to run -`redis-server`, `celery worker` (in Django project directory) and Django app server to run respectively.
        - terminal 1: `redis-server`
        - terminal 2: `celery -A market_order_app worker --loglevel=info --concurrency 3`  # starts the celery worker to take tasks from the redis queue
        - terminal 3: `$ python manage.py runserver`

    - **Celery worker receiving task request**
    ![Celery worker receiving task request](/Docs/images/celery_worker_ingest_data_request.png)
    - **Celery worker task output**
    ![celery worker task output showing channel subscription](/Docs/images/celery_worker_ingest_data_op.png)
    You can see the app running on [http://127.0.0.1:8000](http://127.0.0.1:8000).
    Test the application (You can use [Postman](https://www.postman.com/downloads/) or cURL to send the requests)

    - Subscribe & ingest data:
    ```bash
    curl --location --request POST 'http://127.0.0.1:8000/ingeststreamdata/task/' \
    --form 'channel="pubnub-market-orders"' \
    --form 'task_type="start"'
    ```
    - Unsubscribe & stop the data ingestion task (it will stop the celery workers execution):
    ```bash
    curl --location --request POST 'http://127.0.0.1:8000/ingeststreamdata/task/' \
    --form 'channel="pubnub-market-orders"' --form 'task_type="stop"'
    ```

    Here is the screenshot of how to call the API request in Postman.
    -Subscribe & ingest data from channel
    ![Subscribe & ingest data from the channel response](/Docs/images/ingest_data_celery_task_id.png)
    - Get Trade stats
    ![Get Trade stats](/Docs/images/trade_stats_d.png)

## Run using YugabyteDB locally

1. [Install YugabyteDB locally](https://docs.yugabyte.com/quick-start/install/).

2. Follow the same instructions as above (from step 2)
