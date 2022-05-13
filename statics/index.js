var client_id = Date.now()
const socket = io("ws://localhost:8000/", {path:"/ws/socket.io/"})
document.querySelector("#ws-id").textContent = client_id;

socket.on("connect",()=>{
    console.log("message bien");
})

socket.on("request_position",(e)=>{
    console.log(e)
    console.log("commande recu")
    socket.emit("position_driver",{lat:5.31864, lng:-4.09584, id:"d612b880-e582-4b42-a5d4-4f799efbe22a","commande":e})
})

function sendMessage(event) {
    var input = document.getElementById("messageText")
    if(socket.connected){
        socket.emit("connection")
        input.value = ''
                }else{
                    input.value = 'false'
                }
    event.preventDefault()
}

 function changer(){
    var button = document.getElementById("switch")
     socket.emit('driver_online',{"longitude":1, "latitude":2, "driver_id":"d612b880-e582-4b42-a5d4-4f799efbe22a"})
}
var commande
socket.on("new_commande_send",(e)=>{
    console.log("reception d'une nouvelle commande")
    console.log(e)
    commande.data = e
    nc = document.getElementById("nc")
    nc.innerHtml = e.id
})

function accept(){
    console.log("j'acepte la commande ")
    console.log(commande.data )
    socket.emit("accept_commande",{"commande":commande.data})
}