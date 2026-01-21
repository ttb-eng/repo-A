from fastapi import FastAPI,Query,Depends   #Depends
import uvicorn
app = FastAPI()



@app.get("/aaa")
async def root():
    return {"message": "Hello World"}

#分页逻辑公用
#依赖项
async def common_parameters(
        skip:int = Query(0,ge=0),
        limit:int = Query(0,le=60)
):
    return {"skip":skip,"limit":limit}


#声明依赖项
@app.get("/news1/news_list")
async def news_list(commons=Depends(common_parameters)):
    return commons

@app.get("/user1/user_list")
async def user_list(commons=Depends(common_parameters)):
    return commons






if __name__ == "__main__":
    uvicorn.run("main:app", port=8000,reload=True)