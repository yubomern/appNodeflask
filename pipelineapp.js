const express = require("express")
const path = require("path")

const {
createPipeline,
movePipeline,
getPipeline,
stages
} = require("./pipelineService")

const app = express()

app.set("view engine","ejs")

app.use(express.urlencoded({extended:true}))

app.use(express.static("public"))

app.get("/",(req,res)=>{

const items = getPipeline()

res.render("index",{
items,
stages
})

})

app.post("/create",(req,res)=>{

createPipeline(req.body.name)

res.redirect("/")

})

app.post("/move/:id",(req,res)=>{

movePipeline(req.params.id)

res.redirect("/")

})

const PORT = 3000

app.listen(PORT,()=>{
console.log("Server running http://localhost:3000")
})