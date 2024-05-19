document.getElementById('dataForm').addEventListener('submit', function(event) {
    event.preventDefault();

    let inp = document.getElementById('userInput').value;
    console.log(inp);
})