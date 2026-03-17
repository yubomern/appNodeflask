const fs = require("fs")
const { v4: uuid } = require("uuid")

const FILE = "./data.json"

const stages = [
"DEV",
"INT",
"UAT",
"QUALIF",
"PREPROD",
"PROD"
]

function readData(){
return JSON.parse(fs.readFileSync(FILE))
}

function saveData(data){
fs.writeFileSync(FILE,JSON.stringify(data,null,2))
}

function createPipeline(name){

const data = readData()

const item = {
id: uuid(),
name,
stage:"DEV",
createdAt:new Date().toISOString()
}

data.unshift(item)

saveData(data)

return item
}

function movePipeline(id){

const data = readData()

const updated = data.map(p=>{

if(p.id !== id) return p

const index = stages.indexOf(p.stage)

const next = stages[index+1]

if(!next) return p

return {...p,stage:next}

})

saveData(updated)

return updated
}

function getPipeline(){
return readData()
}

module.exports={
createPipeline,
movePipeline,
getPipeline,
stages
}