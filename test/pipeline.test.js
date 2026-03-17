const fs = require("fs")
const service = require("../pipelineService")

test("create pipeline",()=>{

const item = service.createPipeline("Test App")

expect(item.name).toBe("Test App")

})

test("move pipeline",()=>{

const items = service.getPipeline()

if(items.length === 0) return

const id = items[0].id

const updated = service.movePipeline(id)

expect(updated).toBeDefined()

})