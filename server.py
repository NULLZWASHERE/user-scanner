import asyncio
import sys
import os
from concurrent.futures import ThreadPoolExecutor

import uvicorn
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from api._scanner import get_scan_results, get_modules

executor = ThreadPoolExecutor(max_workers=4)

app = FastAPI(
    title="user-scanner API",
    description=(
        "OSINT API for scanning usernames and emails across 290+ platforms.\n\n"
        "**Endpoints:**\n"
        "- `GET /api/scan` — scan a username or email\n"
        "- `GET /api/modules` — list all available scan modules\n\n"
        "> **Vercel note:** Full scans (no `category`/`module` filter) check 100–185+ sites "
        "and may exceed Vercel's 10 s default timeout. Use `category` or `module` for "
        "targeted, fast scans in production."
    ),
    version="1.4.1.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
async def root():
    return {
        "name": "user-scanner API",
        "version": "1.4.1.1",
        "docs": "/docs",
        "endpoints": {
            "GET /api/scan": "Scan a username or email across platforms",
            "GET /api/modules": "List all available modules by category",
        },
    }


@app.get("/api/scan", summary="Scan a username or email")
async def scan(
    type: str = Query(..., description="'username' or 'email'"),
    target: str = Query(..., description="The username or email to scan"),
    category: str = Query(None, description="Limit to a specific category (e.g. social, dev, gaming)"),
    module: str = Query(None, description="Limit to a single module (e.g. github, twitter)"),
    only_found: bool = Query(False, description="Return only found/registered results"),
    no_nsfw: bool = Query(False, description="Exclude NSFW platforms"),
):
    if type not in ("username", "email"):
        raise HTTPException(400, detail="'type' must be 'username' or 'email'")

    loop = asyncio.get_event_loop()
    try:
        results = await loop.run_in_executor(
            executor,
            lambda: get_scan_results(
                target=target,
                is_email=(type == "email"),
                category=category,
                module=module,
                only_found=only_found,
                no_nsfw=no_nsfw,
            ),
        )
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    except Exception as e:
        raise HTTPException(500, detail=f"Internal error: {str(e)}")

    return {
        "target": target,
        "type": type,
        "count": len(results),
        "results": results,
    }


@app.get("/api/modules", summary="List all available scan modules")
async def modules(
    type: str = Query(..., description="'username' or 'email'"),
    no_nsfw: bool = Query(False, description="Exclude NSFW platforms"),
):
    if type not in ("username", "email"):
        raise HTTPException(400, detail="'type' must be 'username' or 'email'")

    data = get_modules(is_email=(type == "email"), no_nsfw=no_nsfw)
    total = sum(len(v) for v in data.values())
    return {
        "type": type,
        "total_modules": total,
        "categories": data,
    }


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=5000, reload=True)
