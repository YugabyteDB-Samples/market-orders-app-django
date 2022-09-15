# Market Orders Steaming to YugabyteDB with Django

This application subscribes to the [PubNub Market Orders Stream](https://www.pubnub.com/developers/realtime-data-streams/financial-securities-market-orders/) via Python client and stores the market trades in YugabyteDB.

## WIP - don't consider this readme as a final release.

Check [this blog post](https://www.yugabyte.com/blog/building-simple-application-yugabytedb-prisma/) for a quick app overview.

## Run using YugabyteDB Managed

1. [Sign up for YugabyteDB Managed](https://docs.yugabyte.com/preview/yugabyte-cloud/cloud-quickstart/) and create a free cluster.  Additionally, follow this [guide](https://docs.yugabyte.com/preview/yugabyte-cloud/cloud-quickstart/cloud-build-apps/cloud-add-ip/#download-your-cluster-certificate) to download your cluster CA certificate and set up your cluster IP allow list.

2. Run the following to create [virtual environment](https://docs.python.org/3/glossary.html#term-virtual-environment) for app and install application dependencies (first time only):

```bash
$ python3 -m venv market_order_app_venv  # create the virtual environment
$ source market_order_app_venv/bin/activate  # activate the virtual environment
$ cd market-orders-app-django/app/
$ pip install -r ../requirements.txt
```

3. Configure your environment variables in the .env file (create a .env file if it doesn't exist):

```bash
DB_HOST=127.0.0.1
PORT=5433
DB_NAME=yugabyte
USERNAME=username
PASSWORD=password
```

4. Run the following to initialize the database with schema:

```bash
$ python db.py
```

`db.py` will create tables and relations using [`schema/default_schema.sql`](schema/default_schema.sql)

5. Seed the user data in the `User` table. Run the following to insert the default user data for User table:

```bash
$ python seed_user_data.py
```

`seed_user_data.py` will create user data using the [`faker`](https://github.com/joke2k/faker) module and inserts it into the `User` table.

6. Run the application:

```bash
$ python manage.py runserver
```

You can see the app running on [http://127.0.0.1:8000](http://127.0.0.1:8000)

7. Test the application (You can use [Postman](https://www.postman.com/downloads/) or cURL to send the requests)

    - Subscribe to a channel - `curl --location --request GET 'http://127.0.0.1:5001/subscription/add?channel=pubnub-market-orders'`
    - Unsubscribe from a channel - `curl --location --request GET 'http://127.0.0.1:5001/subscription/remove?channel=pubnub-market-orders'`
    - Get subscribed channels - `curl --location --request GET 'http://127.0.0.1:5001/subscription/list'`
    - Ingest the market order stream to YugabyteDB - `curl --location --request GET 'http://127.0.0.1:5001/ingeststreamdata'`
    - Get Trade stats - `curl --location --request GET 'http://127.0.0.1:5001/tradestats'`

    Here is the screenshot of how to call the API request in Postman.
    - Subscribe to a channel
    ![Subscribe to the channel](/Docs/images/add_subscription.png)
    - Get Trade stats
    ![Get Trade stats](/Docs/images/trade_stats.png)


## Run using YugabyteDB locally

1. [Install YugabyteDB locally](https://docs.yugabyte.com/quick-start/install/).

2. Follow the same instructions as above (from step 2)
