'''An api to manage booking for fake restaurants'''
from typing import List, Set, Dict, Tuple, Literal, TypedDict, get_args
import re
from werkzeug.exceptions import HTTPException
from flask import Flask, abort, jsonify, request, Request

#######################################
# Custom types
#######################################
RestaurantId = Literal['coin_moldu',
                       'falafel_fix',
                       'station_ramen',
                       'amritsari_masala',
                       'pupsicle',
                       '50_nuances_de_café',
                       'au-delà_des_tacos',
                       'la_barre_de_smoothie',
                       'loki’s_lounge',
                       'veggie_wonderland',
                       'kebab_capital']


class Booking(TypedDict):
    '''Booking type'''
    slot: str
    name: str
    phone: str


class RestaurantData(TypedDict):
    '''Restaurant data type'''
    name: str
    slots: Set[str]
    bookings: List[Booking]


class Hateoas(TypedDict):
    '''HATEOAS item type'''
    href: str
    rel: str
    method: Literal['GET', 'POST', 'PUT', 'DELETE']


class RestaurantListRes(TypedDict):
    '''Return type of get_restaurant_list'''
    restaurants: List[str]
    links: List[Hateoas]


class RestaurantSlotsRes(TypedDict):
    '''Return type of get_restaurant_slots'''
    slots: List[str]
    links: List[Hateoas]


class BookingRes(TypedDict):
    '''Return type of get_restaurant_slots'''
    message: str
    links: List[Hateoas]


#######################################
# Constants
#######################################
SLOTS: Set[str] = {'19h', '19h30', '20h', '20h30', '21h', '21h30'}
RESTAURANT_IDS = get_args(RestaurantId)
PHONE_REGEX = re.compile(r"^\d{10}$")
BASE_URL = 'http://localhost:8080'

#######################################
# Data
#######################################
restaurants: Dict[RestaurantId, RestaurantData] = {}

for rid in RESTAURANT_IDS:
    restaurants[rid] = {
        'name': rid.replace('_', ' ').capitalize(),
        'slots': SLOTS.copy(),
        'bookings': []
    }


#######################################
# Helpers
#######################################
def check_dto(request: Request) -> Tuple[str, str]:
    '''Raise an error if given dto is malformed.'''
    if not isinstance(request.json, dict):
        abort(400, 'Request format must be json')
    elif not 'name' in request.json:
        abort(400, 'A name must be given')
    elif not 'phone' in request.json:
        abort(400, 'A phone must be given')

    name = request.json['name']
    phone = request.json['phone']

    if not isinstance(name, str) or len(name) == 0:
        abort(400, 'Malformated name')
    elif not isinstance(phone, str) or not PHONE_REGEX.match(phone):
        abort(400, 'Malformated phone')

    return (name, phone)


#######################################
# API
#######################################
app = Flask(__name__)


@app.errorhandler(Exception)
def handle_error(error):
    '''Serialize all exceptions to JSON'''
    code = 500
    if isinstance(error, HTTPException):
        code = error.code
    return jsonify(error=str(error)), code


@app.route('/restaurants', methods=['GET'])
def get_restaurant_list() -> RestaurantListRes:
    '''Return a list of restaurants name'''
    return {
        "restaurants": [r['name'] for r in restaurants.values()],
        "links": [{
            'rel': 'Retrieve slots for {}'.format(r_id),
            'method': 'GET',
            'href': '{}/restaurant/{}/availableSlots'.format(BASE_URL, r_id)
        } for r_id in RESTAURANT_IDS]
    }


@app.route('/restaurant/<r_id>/availableSlots', methods=['GET'])
def get_restaurant_slots(r_id: RestaurantId) -> RestaurantSlotsRes:
    '''Return available slots for given restaurant'''
    if not r_id in RESTAURANT_IDS:
        abort(404, 'Restaurant id {} do not exist'.format(r_id))

    return {
        'slots': list(restaurants[r_id]["slots"]),
        'links': [{
            'rel': 'Book slot {}'.format(slot),
            'method': 'POST',
            'href': '{}/restaurant/{}/book/{}'.format(BASE_URL, r_id, slot)
        } for slot in restaurants[r_id]["slots"]]
    }


@app.route('/restaurant/<r_id>/book/<slot>', methods=['POST'])
def book(r_id: RestaurantId, slot: str) -> BookingRes:
    '''Book given slot for given restaurant'''
    if not r_id in RESTAURANT_IDS:
        abort(404, 'Restaurant id {} do not exist'.format(r_id))
    elif not slot in restaurants[r_id]['slots']:
        abort(400, 'Slot {} is not available'.format(slot))

    name, phone = check_dto(request)

    restaurants[r_id]['bookings'].append(
        {'slot': slot, 'name': name, 'phone': phone})
    restaurants[r_id]['slots'].remove(slot)

    return {
        'message': 'Slot {} booked'.format(slot),
        'links': [
            {
                'rel': 'Update booking for {} at {}'.format(slot, r_id),
                'method': 'PUT',
                'href': '{}/restaurant/{}/book/{}'.format(BASE_URL, r_id, slot)
            },
            {
                'rel': 'Delete booking for {} at {}'.format(slot, r_id),
                'method': 'DELETE',
                'href': '{}/restaurant/{}/book/{}'.format(BASE_URL, r_id, slot)
            }
        ]
    }


@app.route('/restaurant/<r_id>/book/<slot>', methods=['PUT'])
def update_booking(r_id: RestaurantId, slot: str) -> BookingRes:
    '''Book given slot for given restaurant'''
    if not r_id in RESTAURANT_IDS:
        abort(404, 'Restaurant id {} do not exist'.format(r_id))

    name, phone = check_dto(request)
    booking_index = next(
        (i for i, booking in enumerate(restaurants[r_id]['bookings'])
         if booking['slot'] == slot), None)

    if booking_index is None:
        abort(404, 'Can not update a booking that not exist. Please create it instead')

    del restaurants[r_id]['bookings'][booking_index]
    restaurants[r_id]['bookings'].append(
        {'slot': slot, 'name': name, 'phone': phone})

    return {
        'message': 'Booking on Slot {} updated'.format(slot),
        'links': [
            {
                'rel': 'Update booking for {} at {}'.format(slot, r_id),
                'method': 'PUT',
                'href': '{}/restaurant/{}/book/{}'.format(BASE_URL, r_id, slot)
            },
            {
                'rel': 'Delete booking for {} at {}'.format(slot, r_id),
                'method': 'DELETE',
                'href': '{}/restaurant/{}/book/{}'.format(BASE_URL, r_id, slot)
            }
        ]
    }


@app.route('/restaurant/<r_id>/book/<slot>', methods=['DELETE'])
def delete_booking(r_id: RestaurantId, slot: str) -> BookingRes:
    '''Delete booking on given slot for given restaurant and make it available again.'''
    if not r_id in RESTAURANT_IDS:
        abort(404, 'Restaurant id {} do not exist'.format(r_id))

    booking_index = next(
        (i for i, booking in enumerate(restaurants[r_id]['bookings'])
         if booking['slot'] == slot), None)

    if booking_index is None:
        abort(404, 'Can not delete booking. Slot {} is not booked'.format(slot))

    del restaurants[r_id]['bookings'][booking_index]
    restaurants[r_id]['slots'].add(slot)

    return {
        'message': 'Booking on Slot {} deleted'.format(slot),
        'links': [
            {
                'rel': 'Get restaurant list',
                'method': 'GET',
                'href': '{}/restaurants'.format(BASE_URL)
            },
        ]
    }


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
