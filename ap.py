from flask import Flask, jsonify, request
import requests
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

previous_state_numbers = []

def fetch_data_with_timeout(api_url, timeout_ms=500):
    try:
        access_token = os.getenv('ACCESS_TOKEN')
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(api_url, headers=headers, timeout=timeout_ms / 1000)
        response.raise_for_status()
        return response.json()
    except requests.Timeout:
        print('Request took too long and was ignored.')
        return None
    except requests.RequestException as e:
        print(f'Request failed: {e}')
        return None

def calculate_average(numbers):
    return sum(numbers) / len(numbers) if numbers else 0

@app.route('/numbers/<string:category_id>', methods=['POST'])
def get_numbers(category_id):
    global previous_state_numbers

    category_id = category_id.lower()
    api_url = None

    if category_id == 'e':
        api_url = 'http://20.244.56.144/test/even'
    elif category_id == 'f':
        api_url = 'http://20.244.56.144/test/fib'
    elif category_id == 'p':
        api_url = 'http://20.244.56.144/test/primes'
    elif category_id == 'r':
        api_url = 'http://20.244.56.144/test/rand'
    else:
        return jsonify({"message": "Error: invalid number type"}), 400

    response_data = fetch_data_with_timeout(api_url, 500)

    if response_data:
        number_list = response_data.get('numbers', [])
        current_state_numbers = list(set(number_list))[-10:]
        average_value = calculate_average(current_state_numbers)
        response = {
            "numbers": number_list,
            "previousState": previous_state_numbers,
            "currentState": current_state_numbers,
            "average": average_value
        }
        previous_state_numbers = current_state_numbers
        return jsonify(response)
    else:
        return jsonify({'message': 'Request timed out and was ignored'}), 504

@app.errorhandler(500)
def internal_error(error):
    return "Something broke!", 500

if __name__ == '__main__':
    app.run(port=int(os.getenv('PORT', 5000)))
