/**
 * JavaScript responsible for handling events in index.html
 */

window.onload = init

function init() {
    var classifyBtn = document.getElementById('classify_btn');
    classifyBtn.onclick = classifyEmail;
}

function classifyEmail() {
    console.log('hi');
}