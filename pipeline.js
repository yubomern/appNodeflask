const express = require("express")
const http = require("http")
const cors = require("cors")
const { Server } = require("socket.io")

const app = express()

app.use(cors())
app.use(express.json())

const server = http.createServer(app)

const io = new Server(server,{
    cors:{origin:"*"}
})

let pipeline=[]

io.on("connection",(socket)=>{

    console.log("client connected")

    socket.emit("pipeline_update",pipeline)

    socket.on("pipeline_update",(data)=>{

        pipeline=data

        io.emit("pipeline_update",pipeline)

    })

})

server.listen(3005,()=>{
    console.log("pipeline server running")
})