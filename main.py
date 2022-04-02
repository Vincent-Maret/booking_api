from typing import List, Set, Dict, Tuple, Optional
from flask import Flask
from flask import request
from flask import Response

restaurants = {
    'Coin moldu',
    'Falafel Fix',
    'Station Ramen',
    'Amritsari Masala',
    'Pupsicle',
    '50 nuances de café',
    'Au-delà des tacos',
    'La barre de smoothie',
    'Loki’s Lounge',
    'Veggie Wonderland',
    'Kebab Capital'
}

app = Flask(__name__)


@app.route('/restaurants', methods=['GET'])
def get_restaurant_list() -> Dict[str, tuple]:
    '''Return a list of restaurants'''
    return {
        "restaurants": tuple(restaurants)
    }


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
