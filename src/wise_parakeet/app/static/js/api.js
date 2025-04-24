const CLASSIFICATION_API_URL = '/api/classify';

function classifyEmail(callback) {
    var apiReq = new XMLHttpRequest();
    apiReq.responseType = 'json';
    apiReq.onreadystatechange = callback;
    apiReq.open('POST', CLASSIFICATION_API_URL);
    apiReq.send();
}

export { classifyEmail };