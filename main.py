from typing import List, Set, Dict, Tuple, Optional, Union, Literal, TypedDict, get_args
from flask import Flask, abort


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


class RestaurantData(TypedDict):
    '''Restaurant data type'''
    name: str
    slots: Set[str]


SLOTS: Set[str] = {'19h', '19h30', '20h', '20h30', '21h', '21h30'}
RESTAURANT_IDS = get_args(RestaurantId)

restaurants: Dict[RestaurantId, RestaurantData] = {}

for rid in RESTAURANT_IDS:
    restaurants[rid] = {
        'name': rid,
        'slots': SLOTS.copy()
    }

app = Flask(__name__)


@app.route('/restaurants', methods=['GET'])
def get_restaurant_list() -> Dict[str, List[str]]:
    '''Return a list of restaurants name'''
    return {
        "restaurants": [r['name'] for r in restaurants.values()]
    }


@app.route('/<r_id>/availableSlots', methods=['GET'])
def get_restaurant_slots(r_id: RestaurantId) -> Dict[str, List[str]]:
    '''Return available slots for given restaurant'''
    if not r_id in RESTAURANT_IDS:
        abort(404, 'Restaurant id {} do not exist'.format(r_id))

    return {'slots': list(restaurants[r_id]["slots"])}


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
