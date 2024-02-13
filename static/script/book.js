function rate(x, username, isbn) {
    console.log(x);
    console.log(username);
    console.log(isbn);

    let rating=x;

     let userRating = {
            'isbn_no' : isbn,
            'username' : username,
            'rating' : rating
    }
    const request = new XMLHttpRequest();
    request.open('POST', `/processRating/${JSON.stringify(userRating)}`);

    request.onload = () =>{

    $("#exampleModal").modal("hide");
    const flaskMessage = request.responseText
    console.log(flaskMessage)

    }

    request.send()


}

function toggle(x) {
    for (let i = 0; i <= x; i++)
        document.getElementById(i).src = "../static/css/golden_star.png";
}
function reset() {
    for (let i = 0; i <= 9; i++)
        document.getElementById(i).src = "../static/css/star.png";
}