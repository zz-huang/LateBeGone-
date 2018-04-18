import lyft from 'node-lyft';
let defaultClient = lyft.ApiClient.instance;

// Configure OAuth2 access token for authorization: Client Authentication
let clientAuth = defaultClient.authentications['Client Authentication'];
clientAuth.accessToken = 'qSSLT3qEdTxEe+ORMu5uE3XNx1u/91b0PBdoEIVPcvgBAsg67gn890XT65jQusItWISKN538HYzlmE3tXZVeeC8ML6qMv/5xxYqgeGEeDCvrmlqdZbYvO0o=';

let apiInstance = new lyft.PublicApi();

let opts = {
    'endLat': 37.7972, // Latitude of the ending location
    'endLng': -122.4533 // Longitude of the ending location
};

apiInstance.getCost(37.7763, -122.3918, opts).then((data) => {
    console.log('API called successfully. Returned data: ' + data);
}, (error) => {
    console.error(error);
});