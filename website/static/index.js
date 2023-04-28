function deletePrinter(printerID){
    fetch('/delete-printer', {
        method: "POST",
        body: JSON.stringify({ printerID: printerID }),
    }).then((_res) => {
        window.location.href = "/printers";
      });
}


function deleteKey(keyid){
    fetch('/delete-key', {
        method: "POST",
        body: JSON.stringify({ keyID: keyid }),
    }).then((_res) => {
        window.location.href = "/APIKEYS";
      });
}


function ADD(){
    fetch('/login', {
        method: "PUT"}).then((_res) => {
            setTimeout('', 5000);
            window.location.href = "/login";
          });
}

