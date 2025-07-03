"""爬虫管理API端点"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
from datetime import datetime
from loguru import logger

from app.crawlers.crawler_manager import crawler_manager
from app.core.scheduler import scheduler

router = APIRouter()


@router.post("/crawl/all")
async def trigger_crawl_all(background_tasks: BackgroundTasks):
    """手动触发所有爬虫任务"""
    try:
        # 在后台执行爬取任务
        background_tasks.add_task(crawler_manager.run_crawl_task)
        
        return {
            "success": True,
            "message": "爬取任务已启动",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"触发爬取任务失败: {e}")
        raise HTTPException(status_code=500, detail=f"触发爬取任务失败: {str(e)}")


@router.post("/crawl/{crawler_name}")
async def trigger_crawl_single(crawler_name: str, background_tasks: BackgroundTasks):
    """手动触发单个爬虫任务"""
    try:
        # 检查爬虫是否存在
        if crawler_name not in crawler_manager.crawlers:
            raise HTTPException(
                status_code=404, 
                detail=f"未找到爬虫: {crawler_name}"
            )
        
        # 在后台执行单个爬虫
        async def run_single_crawler():
            items = await crawler_manager.crawl_single(crawler_name)
            if items:
                await crawler_manager.save_to_database({crawler_name: items})
                await crawler_manager._clear_cache()
        
        background_tasks.add_task(run_single_crawler)
        
        return {
            "success": True,
            "message": f"爬虫 {crawler_name} 已启动",
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"触发爬虫 {crawler_name} 失败: {e}")
        raise HTTPException(status_code=500, detail=f"触发爬虫失败: {str(e)}")


@router.get("/crawlers")
async def list_crawlers():
    """获取所有可用的爬虫列表"""
    try:
        crawlers_info = []
        
        for crawler_name, crawler_class in crawler_manager.crawlers.items():
            # 创建临时实例获取信息
            temp_crawler = crawler_class()
            platform_name, category_name = crawler_manager._parse_crawler_name(crawler_name)
            
            crawlers_info.append({
                "name": crawler_name,
                "platform": platform_name,
                "category": category_name,
                "description": f"{platform_name} - {category_name}"
            })
        
        return {
            "success": True,
            "data": crawlers_info,
            "total": len(crawlers_info)
        }
    except Exception as e:
        logger.error(f"获取爬虫列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取爬虫列表失败: {str(e)}")


@router.get("/jobs")
async def list_scheduled_jobs():
    """获取所有定时任务状态"""
    try:
        jobs = []
        
        if scheduler.is_running:
            for job in scheduler.scheduler.get_jobs():
                jobs.append({
                    "id": job.id,
                    "name": job.name or job.id,
                    "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                    "trigger": str(job.trigger),
                    "func_name": job.func.__name__ if hasattr(job.func, '__name__') else str(job.func)
                })
        
        return {
            "success": True,
            "data": jobs,
            "scheduler_running": scheduler.is_running,
            "total": len(jobs)
        }
    except Exception as e:
        logger.error(f"获取定时任务列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取定时任务列表失败: {str(e)}")


@router.post("/jobs/{job_id}/pause")
async def pause_job(job_id: str):
    """暂停定时任务"""
    try:
        success = scheduler.pause_job(job_id)
        if success:
            return {
                "success": True,
                "message": f"任务 {job_id} 已暂停"
            }
        else:
            raise HTTPException(status_code=404, detail=f"未找到任务: {job_id}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"暂停任务 {job_id} 失败: {e}")
        raise HTTPException(status_code=500, detail=f"暂停任务失败: {str(e)}")


@router.post("/jobs/{job_id}/resume")
async def resume_job(job_id: str):
    """恢复定时任务"""
    try:
        success = scheduler.resume_job(job_id)
        if success:
            return {
                "success": True,
                "message": f"任务 {job_id} 已恢复"
            }
        else:
            raise HTTPException(status_code=404, detail=f"未找到任务: {job_id}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"恢复任务 {job_id} 失败: {e}")
        raise HTTPException(status_code=500, detail=f"恢复任务失败: {str(e)}")


@router.get("/status")
async def get_crawler_status():
    """获取爬虫系统状态"""
    try:
        return {
            "success": True,
            "data": {
                "scheduler_running": scheduler.is_running,
                "total_crawlers": len(crawler_manager.crawlers),
                "available_crawlers": list(crawler_manager.crawlers.keys()),
                "system_time": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"获取爬虫状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取爬虫状态失败: {str(e)}")