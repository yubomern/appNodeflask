const express = require("express")
const http = require("http")
const cors = require("cors")
const bodyParser = require("body-parser")
const helmet = require("helmet")
const rateLimit = require("express-rate-limit")
const { Server } = require("socket.io")
const { Worker } = require("worker_threads")

const app = express()

const server = http.createServer(app)

const io = new Server(server,{
    cors:{
        origin:"*",
        methods:["GET","POST"]
    }
})

const worker = new Worker("./worker.js")

// -------------------------
// SECURITY
// -------------------------

app.use(helmet())

app.use(cors({
    origin:"*"
}))

app.use(bodyParser.json())

const limiter = rateLimit({
    windowMs: 1 * 60 * 1000,
    max: 50
})

app.use(limiter)

app.use(express.static("public"))

// -------------------------
// ADMIN LOGIN
// -------------------------

const ADMIN_USER = "admin"
const ADMIN_PASS = "admin123"

function checkAdmin(req,res,next){

    const user = req.headers["x-admin-user"]
    const pass = req.headers["x-admin-pass"]

    if(user === ADMIN_USER && pass === ADMIN_PASS){
        next()
    }else{
        res.status(401).json({error:"Unauthorized"})
    }

}

// -------------------------
// MEMORY STORAGE
// -------------------------

let notifications = []

worker.on("message",(data)=>{

    notifications = data

})

// -------------------------
// SOCKET
// -------------------------

io.on("connection",(socket)=>{

    console.log("Client connected",socket.id)

})

// -------------------------
// CREATE NOTIFICATION
// -------------------------

app.post("/notify",checkAdmin,(req,res)=>{

    const message = req.body.message

    const notif = {
        id:Date.now(),
        message:message,
        time:new Date()
    }

    worker.postMessage(notif)

    io.emit("new_notification",notif)

    res.json({status:"sent"})

})

// -------------------------
// GET NOTIFICATIONS
// -------------------------

app.get("/notifications",(req,res)=>{

    res.json(notifications)

})

// -------------------------
// SERVER
// -------------------------

const PORT = 3002

server.listen(PORT,()=>{

    console.log("Server running on port",PORT)

})