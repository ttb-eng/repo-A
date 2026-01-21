from datetime import datetime
from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import DateTime, func, String, Float, select
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker,AsyncSession
import uvicorn
from sqlalchemy.orm import DeclarativeBase, Mapped,mapped_column


app=FastAPI()


#创建异步引擎
ASYNC_DATABASE_URL="mysql+aiomysql://root:FaDaCai2026..@localhost:3306/fastapi_first?charset=utf8mb4"
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,#可选，输出sql日志
    pool_size=10,#设置连接池活跃的连接数
    max_overflow=20,#允许额为的连接数
)



#2.定义模型类,基类+表对应的模型类
#基类：创建的时间，更新时间；书籍表：id,书名，作者，价格，出版社
class Base(DeclarativeBase):
    create_time:Mapped[datetime]=mapped_column(DateTime,insert_default=func.now(),default=func.now,comment="创建时间")
    update_time:Mapped[datetime]=mapped_column(DateTime,insert_default=func.now(),default=func.now,onupdate=func.now,comment="修改时间")




class Book(Base):
    __tablename__="book"

    id:Mapped[int] = mapped_column(primary_key=True,comment="书籍id")
    bookname:Mapped[str] = mapped_column(String(255),comment="书名")#String限制最大255
    author:Mapped[str]= mapped_column(String(255),comment="作者")
    price:Mapped[float] = mapped_column(Float,comment="书籍价格")
    publisher:Mapped[str] = mapped_column(String(255),comment="出版社")


#3.建表:定义函数建表 -> FastAPI 启动时侯调用建表的函数
async def create_tables():
    #获取数据库的异步引擎，创建事务 -> 建表
    async with async_engine.connect() as conn:
        await conn.run_sync(Base.metadata.create_all) # Base 模型类的元数据创建



@app.on_event("startup")
async def startup_event():
    await create_tables()
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     async with async_engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)
#     yield
#     await async_engine.dispose()
#
# app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message":"Hello World"}



#需求：查询功能，查询图书->依赖注入：创建依赖项，获取数据库的会话 +Depends 注入路由处理函数
AsyncSessionLocal=async_sessionmaker(
    bind=async_engine,#绑定数据库引擎
    class_=AsyncSession, #指定绘画类
    expire_on_commit=False #提交后会话不过期，不会重新查询数据库
)
#依赖项
async def get_database():
    async with AsyncSessionLocal() as session:
        try:
            yield session #返回数据库会话给路由处理函数
            await session.commit()#提交事务

        except Exception:
            await session.rollback() #有异常，回滚
            raise
        finally:
            await session.close()#关闭会话


@app.get("/book/books")
async def get_book_list(db:AsyncSession=Depends(get_database)):
    #查询所有
    #result = await db.execute(select(Book))#查询->返回一个ORM对象
    #book = result.scalars().all()
    #book=result.scalars().first() #获取单条

    #2
    book=await db.get(Book,2)#获取单挑，通过主键
    return book




#需求：路径参数，书籍id
@app.get("/book/get_book/{book_id}")
async def get_book_list_where(book_id:int,db:AsyncSession=Depends(get_database)):
    result = await db.execute(select(Book).where(Book.id == book_id))
    book=result.scalar_one_or_none()
    return book

#需求按照价格大于等于prices的
@app.get("/book/price_book/{price}")
async def get_price_book(price:float,db:AsyncSession=Depends(get_database)):
    result = await db.execute(select(Book).where(Book.price >= price))
    book=result.scalars().all()
    return book


#模糊查询
@app.get("/book/search_book")
async def get_search_book(db:AsyncSession=Depends(get_database)):
    #result=await db.execute(select(Book).where(Book.author.like("曹%")))  #%任意个，_表示一个,
    #result = await db.execute(select(Book).where(Book.author.like("曹%")&(Book.price>=100)))  #&:and   |:or  ~:与非
    id_list=[1,3,5,7]
    result = await db.execute(select(Book).where(Book.id.in_(id_list)))#书籍id列表，数据库里面的id 如果在书籍id里面，返回  用in_
    book = result.scalars().all()
    return book




#聚合查询select(func.方法名（模型名.属性）)
@app.get("/book/count_book")
async def get_count_book(db:AsyncSession=Depends(get_database)):
    #result=await db.execute(select(func.count(Book.id)))
    #result = await db.execute(select(func.max(Book.price)))
    #result = await db.execute(select(func.sum(Book.price)))
    result = await db.execute(select(func.avg(Book.price)))
    num = result.scalar()#scalar用来提取一个数值，标量
    return num




#分页查询
@app.get("/book/get_book_list")
async def get_book_list(
        page:int=1,
        page_size:int=2,
        db:AsyncSession=Depends(get_database)
):
    skip = (page - 1) * page_size      #（页码-1）*每一页数量
    stmt = select(Book).offset(skip).limit(page_size) #offset跳过的纪录数，limit每页记录数
    result = await db.execute(stmt)
    books = result.scalars().all()
    return books



#增加:用户输入图书信息，增加到数据库
class BookBase(BaseModel):
    id:int
    bookname:str
    author:str
    price:float
    publisher:str
@app.post("/book/book_add")
async def add_book(book:BookBase,db:AsyncSession=Depends(get_database)):
    book_obj=Book(**book.__dict__)
    db.add(book_obj)
    await db.commit()
    return book

#更新,先查，再改
class BookPUT(BaseModel):
    bookname:str
    author:str
    price:float
    publisher:str
@app.put("/book/book_update/{book_id}")
async def update_book(book_id:int,data:BookPUT,db:AsyncSession=Depends(get_database)):
    #查找
    db_book=await db.get(Book,book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="这个不存在")
    #修改
    db_book.bookname = data.bookname
    db_book.author = data.author
    db_book.price = data.price
    db_book.publisher = data.publisher
    db_book.update_time = datetime.now()
    await db.commit()
    return db_book


#删除
@app.delete("/book/book_delete/{book_id}")
async def delete_book(book_id:int,db:AsyncSession=Depends(get_database)):
    db_book = await db.get(Book,book_id)
    if db_book is None:
        raise HTTPException(status_code=404, detail="没有这本书")
    await db.delete(db_book)
    await db.commit()
    return {"message":"Book deleted"}





if __name__=="__main__":
    uvicorn.run("fastapi_first:app",port=8020,reload=True)
