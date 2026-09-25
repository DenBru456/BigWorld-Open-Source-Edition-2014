function Toggle(id) {
    var e = document.getElementById(id);
    if (e.style.display == "block") {
        e.style.display = "none";
    }
    else {
        e.style.display = "block";
    }
}

function GoTo(id) {
    var e = document.getElementById(id);
    e.style.display = "block";
    window.location.href = "#" + id;
}