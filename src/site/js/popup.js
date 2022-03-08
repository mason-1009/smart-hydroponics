function setModalBlur(blurred) {
    if(blurred)
        document.getElementById("content-area").style.filter="blur(10px)";
    else
        document.getElementById("content-area").style.filter="none";
}

function closeModal() {
    document.getElementById("modal-popup").style.display="none";
    setModalBlur(false);
}

function displayModal(text) {
    // enable modal box display
    setModalBlur(true);
    document.getElementById("modal-popup").style.display="block";
    document.getElementById("modal-warning-text").innerHTML=text;
}
