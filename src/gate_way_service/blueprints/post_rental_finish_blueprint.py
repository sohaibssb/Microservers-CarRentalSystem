import os
import json

from quart import Blueprint, Response, request
from .service_requests import delete_data_from_service, post_data_from_service

post_rental_finish_blueprint = Blueprint('post_rental_finish', __name__, )


@post_rental_finish_blueprint.route('/api/v1/rental/<string:rentalUid>/finish', methods=['POST'])
async def post_rental_finish(rentalUid: str) -> Response:
    response = post_data_from_service(
        'http://' + os.environ['RENTAL_SERVICE_HOST'] + ':' + os.environ['RENTAL_SERVICE_PORT']
        + '/api/v1/rental/'+rentalUid+'/finish', timeout=5)

    if response is None:
        return Response(
            status=500,
            content_type='application/json',
            response=json.dumps({
                'errors': ['Rental service is unavailable.']
            })
        )
    elif response.status_code != 200:
        return Response(
            status=response.status_code,
            content_type='application/json',
            response=response.text
        )

    rental = response.json()

    response = delete_data_from_service(
        'http://' + os.environ['CARS_SERVICE_HOST'] + ':' + os.environ['CARS_SERVICE_PORT']
        + '/api/v1/cars/' + rental['carUid'] + '/order', timeout=5)

    if response is None:
        return Response(
            status=500,
            content_type='application/json',
            response=json.dumps({
                'errors': ['Cars service is unavailable.']
            })
        )

    return Response(
        status=204
    )
