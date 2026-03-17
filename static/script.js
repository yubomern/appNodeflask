const socket = io()

// ----------------
// LOAD PRODUCTS
// ----------------

function loadProducts(){

fetch("/api/products")

.then(res=>res.json())

.then(data=>{

let html=""

data.forEach(p=>{

html+=`

<tr>

<td>${p.id}</td>
<td>${p.name}</td>
<td>${p.quantity}</td>
<td>${p.price}</td>

<td>

<button onclick="deleteProduct(${p.id})">
Delete
</button>

</td>

</tr>

`

})

document.getElementById("productTable").innerHTML=html

})

}

// ----------------
// ADD PRODUCT
// ----------------

function addProduct(){

let name=document.getElementById("name").value
let quantity=document.getElementById("qty").value
let price=document.getElementById("price").value

fetch("/api/products",{

method:"POST",

headers:{
"Content-Type":"application/json"
},

body:JSON.stringify({

name:name,
quantity:quantity,
price:price

})

})
.then(()=>loadProducts())

}

// ----------------
// DELETE
// ----------------

function deleteProduct(id){

fetch("/api/products/"+id,{

method:"DELETE"

})
.then(()=>loadProducts())

}

// ----------------
// CHAT
// ----------------

function sendMessage(){

let input=document.getElementById("chatInput")

socket.send(input.value)

input.value=""

}

socket.on("message",function(msg){

let li=document.createElement("li")

li.innerText=msg

document.getElementById("messages").appendChild(li)

})

// ----------------
// NOTIFICATION
// ----------------

socket.on("notification",function(data){

alert(data.msg)

})

// ----------------

loadProducts()