from typing import List, Set, Dict, Tuple, Optional, Union, Literal, TypedDict, get_args
import re
from werkzeug.exceptions import HTTPException
from flask import Flask, abort, jsonify, request, Request

PHONE_REGEX = re.compile(r"^\d{10}$")

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


SLOTS: Set[str] = {'19h', '19h30', '20h', '20h30', '21h', '21h30'}
RESTAURANT_IDS = get_args(RestaurantId)

restaurants: Dict[RestaurantId, RestaurantData] = {}

for rid in RESTAURANT_IDS:
    restaurants[rid] = {
        'name': rid.replace('_', ' ').capitalize(),
        'slots': SLOTS.copy(),
        'bookings': []
    }

app = Flask(__name__)


def check_dto(r_id: RestaurantId, slot: str, request: Request) -> Tuple[str, str]:
    '''Raise an error if given dto is malformed'''
    if not r_id in RESTAURANT_IDS:
        abort(404, 'Restaurant id {} do not exist'.format(r_id))
    elif not slot in restaurants[r_id]['slots']:
        abort(400, 'Slot {} is not available'.format(slot))
    elif not isinstance(request.json, dict):
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


@app.errorhandler(Exception)
def handle_error(error):
    '''Serialize all exceptions to JSON'''
    code = 500
    if isinstance(error, HTTPException):
        code = error.code
    return jsonify(error=str(error)), code


@app.route('/restaurants', methods=['GET'])
def get_restaurant_list() -> Dict[str, List[str]]:
    '''Return a list of restaurants name'''
    return {
        "restaurants": [r['name'] for r in restaurants.values()]
    }


@app.route('/restaurant/<r_id>/availableSlots', methods=['GET'])
def get_restaurant_slots(r_id: RestaurantId) -> Dict[str, List[str]]:
    '''Return available slots for given restaurant'''
    if not r_id in RESTAURANT_IDS:
        abort(404, 'Restaurant id {} do not exist'.format(r_id))

    return {'slots': list(restaurants[r_id]["slots"])}


@app.route('/restaurant/<r_id>/book/<slot>', methods=['POST'])
def book_slot(r_id: RestaurantId, slot: str) -> str:
    '''Book given slot for given restaurant'''
    name, phone = check_dto(r_id, slot, request)

    restaurants[r_id]['bookings'].append(
        {'slot': slot, 'name': name, 'phone': phone})
    restaurants[r_id]['slots'].remove(slot)

    return 'Slot {} booked'.format(slot)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
