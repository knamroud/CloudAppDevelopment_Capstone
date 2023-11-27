from ibmcloudant.cloudant_v1 import CloudantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator


def main(param_dict):
    try:
        authenticator = IAMAuthenticator(param_dict["IAM_API_KEY"])
        client = CloudantV1(authenticator=authenticator)
        client.set_service_url(param_dict["COUCH_URL"])
        response = client.post_find(
            db='reviews',
            selector={'dealership': {'$eq': int(param_dict['dealerId'])}},
        ).get_result()
        result= {
            'headers': {'Content-Type':'application/json'}, 
            'body': {'data':response} 
            }        
        return result
    except:  
        return { 
            'statusCode': 404, 
            'message': 'Something went wrong'
            }