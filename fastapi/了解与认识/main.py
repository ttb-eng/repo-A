from fastapi import FastAPI,Path,Query,HTTPException
import uvicorn
from mpmath import limit
from pydantic import BaseModel,Field
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse




app=FastAPI()
@app.get("/")
async def root():
    return {"message": "Hello World666"}
#路径参数
@app.get("/items/{item_id}")
async def read_item(item_id:int):
    return {"id":item_id,"item_id": f"Hello {item_id}"}
#path限制
@app.get("/book/{id}")
async def read_item(id:int=Path(...,gt=0,lt=100,description="书籍取值范围1-99")):#gt大于，lt小于,description描述
    return {"id":id,"item_id": f"这是第 {id}本书"}

@app.get("/name/{name_id}")
async def read_name(name_id:str=Path(...,min_length=1,max_length=10)):#1-10
    return {"id":name_id,"name_id": f"作者名字{name_id}"}

#查询参数 分页:skip，跳过的记录：limit，返回记录数：10
@app.get("/news/new_list")
async def get_news_list(
        skip:int=Query(0,description="跳过的记录",lt=100),
        limits:int=Query(10,description="返回的记录"),
):
    return {"skip":skip,"limit":limits}
#请求体参数
class User(BaseModel):
    user_name:str=Field(default="张三",description="用户名，长度在2~5",min_length=2,max_length=5)
    password:str=Field(min_length=8,max_length=20,description="密码8~20")

@app.post("/register")
async def register(user:User):
    return user


#指定响应类
@app.get("/html",response_class=HTMLResponse)
async def get_html():
    return "<h1>Hello World</h1>"


#响应格式（图片，音频，PDF）
@app.get("/file")
async def get_file():
    file_path = "./files/1.jpeg"#传输在files文件里面的1.jpeg
    return FileResponse(file_path)

#自定义相应格式，这里设置News格式，响应的必须是News格式，少行多行报错
class News(BaseModel):
    id:int
    title:str
    content:str

@app.get("/News/{id}",response_model=News)
async def get_news(id:int):
    return{
        "id":id,
        "title":f"这是第{id}本书",
        "content":"这是本好书",
    }

#异常处理
@app.get("/news/{id}")
async def get_news(id:int):
    id_list = [1,2,3,4,5,6,7]
    if id not in  id_list:
        raise HTTPException(status_code=404,detail="当前id不存在")
    return {"id":id}













if __name__=="__main__":
    uvicorn.run("main:app",port=8099,reload=True)


