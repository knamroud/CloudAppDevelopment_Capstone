const { CloudantV1 } = require('@ibm-cloud/cloudant');
const { IamAuthenticator } = require('ibm-cloud-sdk-core');

async function main(params) {

    const authenticator = new IamAuthenticator({ apikey: params.IAM_API_KEY })
    const cloudant = CloudantV1.newInstance({
      authenticator: authenticator
    });
    const dbname = "dealerships";
    cloudant.setServiceUrl(params.COUCH_URL);
    let selector = {};
    if (params.state)
        selector.state =  params.state
    if (params.id)
        selector._id = params.id;
    if (Object.keys(selector).length > 0)
        result = await getRecordsBySelection(cloudant, dbname, selector);
    else
        result = await getAllRecords(cloudant, dbname);

    return {
        statusCode: 200,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(result)
    };
}

 function getAllRecords(cloudant,dbname) {
     return new Promise((resolve, reject) => {
         cloudant.postAllDocs({ db: dbname, includeDocs: true, limit: 10 })
             .then((result)=>{
               resolve({result:result.result.rows});
             })
             .catch(err => {
                console.log(err);
                reject({ err: err });
             });
         })
 }

 function getRecordsBySelection(cloudant, dbname, selector) {
    return new Promise((resolve, reject) => {
        cloudant.postFind({ db: dbname, selector: selector })            
            .then((result)=>{
              resolve({result:result.result.docs});
            })
            .catch(err => {
               console.log(err);
               reject({ err: err });
            });
    })
}