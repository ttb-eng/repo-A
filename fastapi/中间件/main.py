from fastapi import FastAPI
import uvicorn

app= FastAPI()


#自下而上

@app.middleware("http")
async def middleware(request,call_next):
    print("中间件 start")
    response = await call_next(request)
    print("中间件 end")
    return response

@app.middleware("http")
async def middleware2(request,call_next):
    print("中间件2 start")
    response = await call_next(request)
    print("中间件2 end")
    return response




@app.get("/news")
async def root():
    return {"message":"Hello World"}





if __name__=="__main__":
    uvicorn.run("main:app",port=8999,reload=True)