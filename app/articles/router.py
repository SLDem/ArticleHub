from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from app.articles.models import Article
from app.articles.schemas import ArticleCreateSchema, ArticleUpdateSchema
from app.dependencies import get_current_user
from app.tasks.tasks import analyze_article_task

router = APIRouter(prefix="/api/articles")


@router.post("/", status_code=201)
async def create_article(data: ArticleCreateSchema, user=Depends(get_current_user)):
    article = Article(**data.dict(), author_id=str(user.id))
    await article.insert()
    return article


@router.get("/", response_model=List[Article])
async def list_articles(search: Optional[str] = None, tag: Optional[str] = None):
    query = {}
    if search:
        query = {"$or": [{"title": {"$regex": search, "$options": "i"}}, {"content": {"$regex": search, "$options": "i"}}]}
    if tag:
        query["tags"] = tag
    articles = await Article.find(query).to_list()
    return articles


@router.get("/{article_id}/")
async def get_article(article_id: str):
    article = await Article.get(article_id)
    if not article:
        raise HTTPException(404, "Article not found")
    return article


@router.put("/{article_id}/")
async def update_article(article_id: str, data: ArticleUpdateSchema, user=Depends(get_current_user)):
    article = await Article.get(article_id)
    if not article or article.author_id != str(user.id):
        raise HTTPException(403, "Not allowed")
    update_data = {k: v for k, v in data.dict().items() if v is not None}
    await article.set(update_data)
    return article


@router.delete("/{article_id}/", status_code=204)
async def delete_article(article_id: str, user=Depends(get_current_user)):
    article = await Article.get(article_id)
    if not article or article.author_id != str(user.id):
        raise HTTPException(403, "Not allowed")
    await article.delete()
    return


@router.post("/{article_id}/analyze/")
async def analyze_article(article_id: str):
    article = await Article.get(article_id)
    if not article:
        raise HTTPException(404, "Article not found")
    result = analyze_article_task.delay(article_id)
    print('result')
    print(result.status)
    return {"message": "Analysis started"}
