import sys
import os
import asyncio
from dataclasses import replace as dc_replace
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from user_scanner.core.helpers import ScanConfig, load_categories, load_modules, get_site_name, find_module
from user_scanner.core.orchestrator import run_user_full, run_user_category, run_user_module
from user_scanner.core.email_orchestrator import (
    run_email_full_batch, run_email_category_batch, run_email_module_batch
)

# Limit concurrent requests to avoid overwhelming sites / getting blocked
MAX_WORKERS = 20   # Adjust between 10-30

def get_scan_results(
    target: str,
    is_email: bool,
    category: str = None,
    module: str = None,
    only_found: bool = False,
    no_nsfw: bool = False,
) -> list[dict]:
    
    config = ScanConfig(allow_loud=False, only_found=False, no_nsfw=no_nsfw, verbose=False)

    try:
        if module:
            modules = find_module(module.replace(".", "_"), is_email, no_nsfw)
            if not modules:
                raise ValueError(f"Module '{module}' not found")
            
            results = []
            for m in modules:
                module_config = dc_replace(config, allow_loud=True)
                if is_email:
                    results.extend(run_email_module_batch(m, target, module_config))
                else:
                    results.extend(run_user_module(m, target, module_config))

        elif category:
            categories = load_categories(is_email, no_nsfw)
            cat_path = categories.get(category)
            if not cat_path:
                raise ValueError(f"Category '{category}' not found.")
            
            if is_email:
                results = run_email_category_batch(cat_path, target, config)
            else:
                results = run_user_category(cat_path, target, config)

        else:
            # Full scan - this is the slow one
            if is_email:
                results = run_email_full_batch(target, config)
            else:
                results = run_user_full(target, config)

        if only_found:
            results = [r for r in results if r.is_found()]

        return [r.to_dict() for r in results]

    except Exception as e:
        raise Exception(f"Scan failed: {str(e)}")
