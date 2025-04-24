import { classifyEmail } from './api.js'

window.onload = init

function init() {
    var classifyBtn = document.getElementById('classify_btn');
    classifyBtn.onclick = displayClassificationResult;
}

function classifyEmailCallback() {
    var resultDisplay = document.getElementById('result_display');
    if(this.readyState == 4 && this.status == 200) {
        var res = this.response;
        resultDisplay.innerText = 'Spam: ' + Boolean(res.spam);
        resultDisplay.hidden = false;        
    }
    else if(this.readyState == 4 && this.status != 200){
        alert('Error processing request - please wait a moment and then try again.');
        resultDisplay.hidden = true;
    }    
}

function displayClassificationResult() {
    classifyEmail(classifyEmailCallback);

}