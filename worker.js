const { parentPort } = require("worker_threads")

let storage = []

parentPort.on("message", (data)=>{

    storage.unshift(data)

    parentPort.postMessage(storage)

})