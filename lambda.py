import boto3
import datetime

import requests


def add_to_dynamodb(price):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('BTC_Prices')
    table.put_item(
    Item={
    'timestamp': str(datetime.now()),
    'id': 'xyz',
    'btc_price': price})


def get_from_dynamodb():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('BTC_Prices')
    response = table.get_item(
    Key={
    'id': 'xyz'}, ProjectionExpression='btc_price')
    return response['Item']


def get_current_price():
    url = 'https://api.coindesk.com/v1/bpi/currentprice/BTC.json'
    response = requests.get(url)
    price = response.json()['bpi']['USD']['rate']

    # Call the function to save this response to a Dynamo DB
    add_to_dynamodb(float(price))
    return float(price)



def lambda_handler(event, context):
    last_price = get_from_dynamodb()

    # Get the current price of BTC
    current_price = get_current_price()
    # Check if the price has gone up by 5%
    if current_price >= 1.05 * last_price:
        # Send an email
        send_email(to="your_email@example.com",
                   subject="BTC price alert",
                   body="The price of BTC has gone up by 5%!")

    return current_price

def send_email(to, subject, body):
    # Create a new SES client
    client = boto3.client("ses")

    # Send the email
    client.send_email(
        Destination={
            "ToAddresses": [
                to,
            ]
        },
        Message={
            "Subject": {
                "Data": subject
            },
            "Body": {
                "Text": {
                    "Data": body
                }
            }
        }
    )