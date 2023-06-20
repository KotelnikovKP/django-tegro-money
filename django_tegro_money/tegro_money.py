"""
    API connector for Tegro Money API
    https://tegro.money/docs/api/api/
"""

import hashlib
import hmac
import json
import time
from datetime import datetime, timezone

import requests
from django.db import transaction
from requests import JSONDecodeError

from django_tegro_money.exceptions import FailedRequestError
from django_tegro_money.loggers import get_logger
from django_tegro_money.models import TegroMoneyOrder, TegroMoneyOrderFields, TegroMoneyOrderReceipt
from django_tegro_money.settings import TEGRO_MONEY_SHOP_ID, TEGRO_MONEY_API_KEY
from django_tegro_money.utils import ftod

HTTP_URL = "https://tegro.money/api/"


class TegroMoney:
    __object = None

    def __new__(cls, *args, **kwargs):
        if cls.__object is None:
            cls.__object = super().__new__(cls)
        return cls.__object

    def __init__(self,
                 log_requests: bool = False,
                 timeout: int = 10,
                 max_retries: int = 3,
                 retry_delay: int = 3):

        if hasattr(self, 'api_key'):
            return

        self.shop_id = TEGRO_MONEY_SHOP_ID
        self.api_key = TEGRO_MONEY_API_KEY
        self.log_requests = log_requests
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.endpoint = HTTP_URL

        self.client = requests.Session()
        self.client.headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

        self.logger = get_logger()
        self.logger.debug("Initializing HTTP session")

    def prepare_data(self, data: dict) -> str:
        """
            Prepares the request data and validates parameter value types.
        """

        string_params = ['shop_id', 'currency', 'order_id', 'email', 'phone', 'name', 'phone', 'account', 'payment_id']
        integer_params = ['nonce', 'payment_system', 'page', 'order_id']
        number_params = ['amount', 'count', 'price']

        if not data.get('shop_id', False):
            data['shop_id'] = self.shop_id

        if not data.get('nonce', False):
            data['nonce'] = int(datetime.now(timezone.utc).timestamp() * 1000)

        for key, value in data.items():
            if key in string_params:
                if type(value) != str:
                    data[key] = str(value)
            elif key in integer_params:
                if type(value) != int:
                    data[key] = int(value)
            elif key in number_params:
                if type(value) not in (int, float):
                    data[key] = float(value)
                    if data[key] == int(data[key]):
                        data[key] = int(data[key])

        return json.dumps(data)

    def _auth(self, data):
        """
            Generates authentication signature.
        """

        if self.api_key is None:
            raise PermissionError("Authenticated endpoints require keys")

        hash_hmac = hmac.new(
            bytes(self.api_key, "utf-8"),
            data.encode("utf-8"),
            hashlib.sha256,
        )
        return hash_hmac.hexdigest()

    def _submit_request(self, path: str = None, data: dict = None) -> dict:
        """
            Submits the request to the API.
        """

        if data is None:
            data = {}

        data = self.prepare_data(data)

        # Prepare signature.
        signature = self._auth(data)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {signature}",
        }

        retries_attempted = self.max_retries

        while True:
            retries_attempted -= 1
            if retries_attempted < 0:
                raise FailedRequestError(
                    request=f"POST {path}: {data}",
                    message="Bad request. Retries exceeded maximum.",
                    status_code=400,
                    time=datetime.now(timezone.utc).strftime("%H:%M:%S"),
                    resp_headers=None,
                )

            retries_remaining = f"{retries_attempted} retries remain."

            # Log the request.
            if self.log_requests:
                self.logger.debug(f"Request -> POST {path}. Body: {data}. Headers: {headers}")

            request = self.client.prepare_request(
                requests.Request('POST', path, data=data, headers=headers)
            )

            # Attempt the request.
            try:
                response = self.client.send(request, timeout=self.timeout)

            # If requests fires an error, retry.
            except (
                requests.exceptions.ReadTimeout,
                requests.exceptions.SSLError,
                requests.exceptions.ConnectionError,
            ) as e:
                self.logger.error(f"{e}. {retries_remaining}")
                time.sleep(self.retry_delay)
                continue

            # Check HTTP status code before trying to decode JSON.
            if response.status_code != 200:
                if response.status_code == 403:
                    error_msg = "Access to the requested resource is forbidden."
                else:
                    error_msg = "HTTP status code is not 200."
                self.logger.error(f"Response status code: {response.status_code}. Response text: {response.text}. "
                                  f"Error message: {error_msg}")
                raise FailedRequestError(
                    request=f"POST {path}: {data}",
                    message=error_msg,
                    status_code=response.status_code,
                    time=datetime.now(timezone.utc).strftime("%H:%M:%S"),
                    resp_headers=response.headers,
                )

            # Convert response to dictionary, or raise if requests error.
            try:
                response_json = response.json()

            # If we have trouble converting, handle the error and retry.
            except JSONDecodeError as e:
                self.logger.error(f"{e}. {retries_remaining}")
                time.sleep(self.retry_delay)
                continue

            ret_code = "type"
            ret_msg = "desc"

            # If Tegro returns an error, loop.
            if response_json[ret_code] != 'success':
                self.logger.error(f"{response_json[ret_msg]} (Type: {response_json[ret_code]}). "
                                  f"{retries_remaining}")
                time.sleep(self.retry_delay)
                continue

            else:
                if self.log_requests:
                    self.logger.debug(f"Response elapsed: {response.elapsed}. "
                                      f"Response json: {response_json}. "
                                      f"Response headers: {response.headers}")

                return response_json

    def create_order(self, **kwargs) -> dict:
        """
            Method for obtaining a direct link to pay for an order
            Required args:
                currency (string): Payment currency, RUB/USD/EUR etc
                amount (number): Payment amount
                order_id (string): Order number in your store
                payment_system (integer): Payment system ID
                fields (dict(email, phone)): Customers data
                receipt (dict(name, count, price)): Receipt data
            Returns parameters for request:
                response_json (dict):
                    type (string): "success"
                    desc (string): ""
                    data (dict):
                        id (int): Order number in tegro.money
                        url (str): Direct link to pay for an order
            Additional information:
                https://tegro.money/docs/api/info/create-order/
        """

        with transaction.atomic():
            order = TegroMoneyOrder()
            order.shop_id = TEGRO_MONEY_SHOP_ID
            order.date_created = datetime.now(timezone.utc)
            for key, value in kwargs.items():
                if key == 'currency':
                    order.currency = str(value)
                elif key == 'amount':
                    order.amount = ftod(value)
                elif key == 'payment_system':
                    order.payment_system = int(value)
                elif key == 'order_id':
                    order.payment_id = str(value)
                elif key == 'test_order':
                    order.test_order = int(value)
            order.save()

            kwargs_fields = kwargs.get('fields', None)
            if kwargs_fields:
                for fields_key, fields_value in kwargs_fields.items():
                    order_fields = TegroMoneyOrderFields()
                    order_fields.order = order
                    order_fields.field_name = str(fields_key)
                    order_fields.field_value = str(fields_value)
                    order_fields.save()

            kwargs_receipt = kwargs.get('receipt', None)
            if kwargs_receipt:
                receipt_items = kwargs_receipt.get('items', None)
                if receipt_items:
                    for receipt_item in receipt_items:
                        order_receipt = TegroMoneyOrderReceipt()
                        for receipt_key, receipt_value in receipt_item.items():
                            order_receipt.order = order
                            if receipt_key == 'name':
                                order_receipt.name = str(receipt_value)
                            elif receipt_key == 'count':
                                order_receipt.count = ftod(receipt_value)
                            elif receipt_key == 'price':
                                order_receipt.price = ftod(receipt_value)
                        order_receipt.save()

        result = self._submit_request(
            path=f'{self.endpoint}createOrder/',
            data=kwargs,
        )

        with transaction.atomic():
            order.status = 0
            if result.get('data', False):
                order_id = result['data'].get('id', None)
                if order_id:
                    order.order_id = int(order_id)
            order.save()

        return result

    def get_shops(self, **kwargs) -> dict:
        """
            Method for getting a list of your shops
            Required args:
                none
            Returns parameters for request:
                response_json (dict):
                    type (string): "success"
                    desc (string): ""
                    data (dict):
                        user_id (int): User id
                        shops (dict):
                            id (int): Shop ID
                            date_added (datetime): "2020-11-03 18:04:07",
                            name (str): "DEMO1",
                            url (str): "https://demo1",
                            status (int): 1,
                            public_key (str): "D0F98E7DD86BB7500914",
                            desc (str): "DEMO1 SHOP"
            Additional information:
                https://tegro.money/docs/api/info/list-shops/
        """
        return self._submit_request(
            path=f'{self.endpoint}shops/',
            data=kwargs,
        )

    def get_balance(self, **kwargs) -> dict:
        """
            Method for getting the balance of all wallets
            Required args:
                none
            Returns parameters for request:
                response_json (dict):
                    type (string): "success"
                    desc (string): ""
                    data (dict):
                        user_id (int): User id
                        balance (dict):
                            <VAL_ISO_1> (str): VAL_ISO_1 balance,
                            ...
                            <VAL_ISO_n> (str): VAL_ISO_n balance,
            Additional information:
                https://tegro.money/docs/api/info/balance/
        """
        return self._submit_request(
            path=f'{self.endpoint}balance/',
            data=kwargs,
        )

    def check_order(self, **kwargs) -> dict:
        """
            Order information retrieval method
            Required args:
                order_id (integer): Order number in tegro.money
                payment_id (string): ... or Order number in your store
            Returns parameters for request:
                response_json (dict):
                    type (string): "success"
                    desc (string): ""
                    data (dict):
                        id (int): 1232,
                        date_created (datetime): "2020-11-14 23:32:37",
                        date_payed (datetime): "2020-11-14 23:33:39",
                        status (int): 1,
                        payment_system_id (int): 10,
                        currency_id (int): 1,
                        amount (float): "64.18000000",
                        fee (float): "4.00000000",
                        email (str): "user@site.ru",
                        test_order (int): 0,
                        payment_id (str): "Order #17854"
            Additional information:
                https://tegro.money/docs/api/check-order/order/
        """
        return self._submit_request(
            path=f'{self.endpoint}order/',
            data=kwargs,
        )

    def get_orders(self, **kwargs) -> dict:
        """
            Method for obtaining information about orders
            Required args:
                page (integer): Number of page
            Returns parameters for request:
                response_json (dict):
                    type (string): "success"
                    desc (string): ""
                    data (list of dict):
                        [
                            {id (int): 1232,
                            date_created (datetime): "2020-11-14 23:32:37",
                            date_payed (datetime): "2020-11-14 23:33:39",
                            status (int): 1,
                            payment_system_id (int): 10,
                            currency_id (int): 1,
                            amount (float): "64.18000000",
                            fee (float): "4.00000000",
                            email (str): "user@site.ru",
                            test_order (int): 0,
                            payment_id (str): "Order #17854"}
                            ...
                        ]
            Additional information:
                https://tegro.money/docs/api/check-order/list-orders/
        """
        return self._submit_request(
            path=f'{self.endpoint}orders/',
            data=kwargs,
        )

