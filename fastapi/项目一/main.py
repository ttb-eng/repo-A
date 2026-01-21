from fastapi import FastAPI
import uvicorn
from routers import news
from fastapi.middleware.cors import CORSMiddleware





app=FastAPI()
#同源三条件：协议，域名，端口
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],#允许的源，这里默认所有
    allow_credentials=True,#允许携带cookie
    allow_methods=["*"],#允许的请求方法
    allow_headers=["*"],#允许的请求头
)



#注册路由
app.include_router(news.router)




if __name__=="__main__":
    uvicorn.run("main:app",port=8000,reload =True)