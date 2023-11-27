const { CloudantV1 } = require('@ibm-cloud/cloudant');
const { IamAuthenticator } = require('ibm-cloud-sdk-core');

function main(params) {

    const authenticator = new IamAuthenticator({ apikey: params.IAM_API_KEY })
    const cloudant = CloudantV1.newInstance({
      authenticator: authenticator
    });
    cloudant.setServiceUrl(params.COUCH_URL);
    let selector = {};
    if (params.state)
        selector.state =  params.state
    if (params.id)
        selector._id = params.id;
    if (Object.keys(selector).length > 0)
        return getRecordsBySelection(cloudant, dbname, selector);
    else
        return getAllRecords(cloudant, dbname);
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