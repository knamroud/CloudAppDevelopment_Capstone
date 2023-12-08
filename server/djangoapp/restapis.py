import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
import os
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions

def get_request(url, api_key=None, **kwargs):
    
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        if api_key:
            print("With api key {} ".format(api_key))
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs, json=kwargs, auth=HTTPBasicAuth('apikey', api_key))
        else:
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs, json=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

def post_request(url, json_payload, api_key=None, **kwargs):
    print(kwargs)
    print("POST to {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        if api_key:
            print("With api key {} ".format(api_key))
            response = requests.post(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs, json=json_payload, auth=HTTPBasicAuth('apikey', api_key))
        else:
            response = requests.post(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs, json=json_payload)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data


def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)["result"]
    if json_result:
        print(json_result)
        # For each dealer object
        for dealer in json_result:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results

def get_dealer_by_id(url, dealerId):
    # Call get_request with a URL parameter
    json_result = get_request(url, id=int(dealerId))["result"]
    if json_result:
        dealer_doc = json_result[0]
        # Create a CarDealer object with values in `doc` object
        dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                short_name=dealer_doc["short_name"],
                                st=dealer_doc["st"], zip=dealer_doc["zip"])
        return dealer_obj

def get_dealers_by_state(url, state):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, state=state)["result"]
    if json_result:
        # For each dealer object
        for dealer in json_result:
            # Get its content in `doc` object
            dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results

def get_dealer_reviews_from_cf(url, dealerId):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, dealerId=dealerId)["data"]["docs"]
    print(json_result)
    if json_result:
        # For each dealer object
        for review_doc in json_result:
            # Create a CarDealer object with values in `doc` object
            review_obj = DealerReview(
                dealership=review_doc.get("dealership", ""), name=review_doc.get("name", ""), purchase=review_doc.get("purchase", ""),
                review=review_doc.get("review", ""), purchase_date=review_doc.get("purchase_date", ""), car_make=review_doc.get("car_make", ""),
                car_model=review_doc.get("car_model", ""), car_year=review_doc.get("car_year", ""),
                sentiment=analyze_review_sentiments(review_doc.get("review", "")), id=review_doc.get("id", "")
            )
            results.append(review_obj)

    return results

def analyze_review_sentiments(review_text):
    url = os.environ['NLU_URL']
    api_key = os.environ["NLU_API_KEY"]
    version = '2023-03-25'
    authenticator = IAMAuthenticator(api_key)
    nlu = NaturalLanguageUnderstandingV1(
        version=version, authenticator=authenticator)
    nlu.set_service_url(url)
    try:
        response = nlu.analyze(text=review_text, features=Features(
            sentiment=SentimentOptions())).get_result()
        print(json.dumps(response))
        sentiment_label = response["sentiment"]["document"]["label"]
    except:
        sentiment_label = "neutral"
    print(sentiment_label)

    return sentiment_label