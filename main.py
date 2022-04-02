from typing import List, Set, Dict, Tuple, Optional, Union
from flask import Flask
from flask import request
from flask import Response

SLOTS = {'19h', '19h30', '20h', '20h30', '21h', '21h30'}

restaurants = {
    'Coin moldu': SLOTS.copy(),
    'Falafel Fix': SLOTS.copy(),
    'Station Ramen': SLOTS.copy(),
    'Amritsari Masala': SLOTS.copy(),
    'Pupsicle': SLOTS.copy(),
    '50 nuances de café': SLOTS.copy(),
    'Au-delà des tacos': SLOTS.copy(),
    'La barre de smoothie': SLOTS.copy(),
    'Loki’s Lounge': SLOTS.copy(),
    'Veggie Wonderland': SLOTS.copy(),
    'Kebab Capital': SLOTS.copy()
}


app = Flask(__name__)


@app.route('/restaurants', methods=['GET'])
def get_restaurant_list() -> Dict[str, List[str]]:
    '''Return a list of restaurants'''
    return {
        "restaurants": list(restaurants.keys())
    }


@app.route('/<restaurantId>/availableSlots', methods=['GET'])
def get_restaurant_slots(restaurantId: str) -> Dict[str, List[str]]:
    '''Return available slots for given restaurant'''
    return {'slots': list(restaurants[restaurantId])}


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
