const CLASSIFICATION_API_URL = '/api/classify';

function classifyEmail(callback, emailData) {
    var apiReq = new XMLHttpRequest();
    apiReq.onreadystatechange = callback;
    // see https://stackoverflow.com/questions/6396101/pure-javascript-send-post-data-without-a-form
    apiReq.responseType = 'json';
    apiReq.open('POST', CLASSIFICATION_API_URL);
    apiReq.setRequestHeader('Content-Type', 'application/json');
    apiReq.send(JSON.stringify(emailData));
}

export { classifyEmail };