const API = "http://localhost:5000"

function loadStocks(){

fetch(API + "/stocks")

.then(res => res.json())

.then(data => {

let html = ""

data.forEach(s => {

html += `
<tr>

<td>${s.id}</td>

<td>${s.name}</td>

<td>${s.quantity}</td>

<td>${s.pipeline}</td>

<td>

<a href="${API}/uploads/${s.file}" target="_blank">
file
</a>

</td>

<td>

<button onclick="removeStock(${s.id})">
Delete
</button>

</td>

</tr>
`

})

document.getElementById("table").innerHTML = html

})

}

function createStock(){

let formData = new FormData()

formData.append("name", document.getElementById("name").value)

formData.append("quantity", document.getElementById("quantity").value)

formData.append("pipeline", document.getElementById("pipeline").value)

formData.append("file", document.getElementById("file").files[0])

fetch(API + "/stocks", {

method:"POST",

body:formData

})
.then(()=>loadStocks())

}

function removeStock(id){

fetch(API + "/stocks/" + id, {

method:"DELETE"

})
.then(()=>loadStocks())

}

loadStocks()

const socket = io();

const API_TOKEN = "mysecrettoken";

function loadStocks(){

$.get("/stocks", function(data){

$("#stockList").html("")

data.forEach(s => {

$("#stockList").append(
`
<li>
${s.name} - ${s.quantity}

<button onclick="deleteStock(${s.id})">Delete</button>

</li>
`
)

})

})

}

$("#stockForm").submit(function(e){

e.preventDefault()

let formData = new FormData(this)

$.ajax({

url: "/stocks",
method: "POST",
headers:{
Authorization: API_TOKEN
},
data: formData,
processData:false,
contentType:false,

success:function(){

loadStocks()

}

})

})

function deleteStock(id){

$.ajax({

url:`/stocks/${id}`,
method:"DELETE",
headers:{
Authorization: API_TOKEN
},

success:function(){

loadStocks()

}

})

}

socket.on("notification", function(data){

$("#notif").text(data.message)

setTimeout(()=>{

$("#notif").text("")

},3000)

})

loadStocks()