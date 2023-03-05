import os
import json
import time

from quart import Blueprint, Response
from .serviceorders import delete_data_from_service, post_data_from_service

deleterentalb = Blueprint('delete_rental', __name__, )


@deleterentalb.route('/api/v1/rental/<string:rentalUid>', methods=['DELETE'])
async def delete_rental(rentalUid: str) -> Response:
    response = delete_data_from_service(
        'http://' + os.environ['RENTAL_SERVICE_HOST'] + ':' + os.environ['RENTAL_SERVICE_PORT']
        + '/api/v1/rental/'+rentalUid, timeout=10)

    while response is None:
        time.sleep(10)
        response = delete_data_from_service(
            'http://' + os.environ['RENTAL_SERVICE_HOST'] + ':' + os.environ['RENTAL_SERVICE_PORT']
            + '/api/v1/rental/' + rentalUid, timeout=10)

    if response.status_code != 200:
        return Response(
            status=response.status_code,
            content_type='application/json',
            response=response.text
        )

    rental = response.json()

    response = delete_data_from_service(
        'http://' + os.environ['CARS_SERVICE_HOST'] + ':' + os.environ['CARS_SERVICE_PORT']
        + '/api/v1/cars/' + rental['carUid'] + '/order', timeout=10)

    while response is None:
        time.sleep(10)
        response = delete_data_from_service(
            'http://' + os.environ['CARS_SERVICE_HOST'] + ':' + os.environ['CARS_SERVICE_PORT']
            + '/api/v1/cars/' + rental['carUid'] + '/order', timeout=10)

    response = delete_data_from_service(
        'http://' + os.environ['PAYMENT_SERVICE_HOST'] + ':' + os.environ['PAYMENT_SERVICE_PORT']
        + '/api/v1/payment/' + rental['paymentUid'], timeout=10)

    if response is None:
        response = post_data_from_service(
            'http://' + os.environ['QUEUE_SERVICE_HOST'] + ':' + os.environ['QUEUE_SERVICE_PORT']
            + '/api/v1/command_delete', timeout=10,
            data={
                'url': (
                        'http://' + os.environ['PAYMENT_SERVICE_HOST'] + ':' + os.environ['PAYMENT_SERVICE_PORT']
                        + '/api/v1/payment/' + rental['paymentUid']
                ),
                'headers': {}
            })

    return Response(
        status=204
    )
