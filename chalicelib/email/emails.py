import boto3
import re
import os
from json import dumps
from botocore.exceptions import ClientError

AWS_REGION = "eu-west-1"
EMAIL_SENDER = f"Trading Bot <{os.environ.get('SENDER_EMAIL_ADDRESS')}>"
CHARSET = "UTF-8"


def format_json_to_html(json) -> list:
    lines = json.splitlines()
    formatted_lines = []

    for line in lines:
        line = re.sub(r'$', '<br>', line)
        if line.__contains__('\"'):
            line = re.sub(r'^', '<font color=brown>', line)
            line = re.sub(r'\":', '\"<font color=black>:', line)
            if line.__contains__(':'):
                line = re.sub(r':', ':<font color=mediumblue>', line)
                line = re.sub(r',<br>$', '<font color=black>,<br>', line)
        else:
            line = re.sub(r'^', '<font color=black>', line)
        # Ensure any brackets of opening blocks are black
        line = line.replace('[', '<font color=black>[').replace('{', '<font color=black>{')
        formatted_lines.append(line)
    return formatted_lines


def send_trade_placed_email(email_recipient, trade_response):
    email_subject = "Order Placed"
    trade_response = dict(trade_response)
    ticker = trade_response.get('body', {}).get('ticker', '')
    side = trade_response.get('body', {}).get('position', {}).get('side', '')
    interval = trade_response.get('body', {}).get('interval', '')
    trade_response_json = dumps(trade_response, indent=2)
    formatted_html = format_json_to_html(trade_response_json)

    html_json = ''.join(formatted_html)
    body_html = """
            <html>
            <head></head>
            <body>
              <h2>{} {} Position Opened ({}m)</h2>
              <div>
              <p style="font-family:Courier New";>
                <pre>{}</pre>
              </p>
              </div>
            </body>
            </html>
            """.format(ticker, side, interval, html_json)
    send_email(email_address=email_recipient, subject=email_subject, body=body_html)


def send_error_email(email_recipient, heading, err_msg, ticker, order_side):
    email_subject = "Order Failed"
    body_html = """
                <html>
                <head></head>
                <body>
                  <h2>{} {} {}</h2>
                  <div>
                  <p style="font-family:Courier New";>
                    <pre>{}</pre>
                  </p>
                  </div>
                </body>
                </html>
                """.format(ticker, order_side, heading, err_msg)
    send_email(email_address=email_recipient, subject=email_subject, body=body_html)


def send_email(email_address, subject, body):
    client = boto3.client('ses', region_name=AWS_REGION)

    try:
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    email_address,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': body,
                    }
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': subject,
                },
            },
            Source=EMAIL_SENDER,
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])
