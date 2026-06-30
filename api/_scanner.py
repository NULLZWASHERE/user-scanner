import sys
import os
from dataclasses import replace as dc_replace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from user_scanner.core.helpers import ScanConfig, load_categories, load_modules, get_site_name, find_module
from user_scanner.core.orchestrator import run_user_full, run_user_category, run_user_module
from user_scanner.core.email_orchestrator import (
    run_email_full_batch,
    run_email_category_batch,
    run_email_module_batch,
)


def get_scan_results(
    target: str,
    is_email: bool,
    category: str = None,
    module: str = None,
    only_found: bool = False,
    no_nsfw: bool = False,
) -> list[dict]:
    config = ScanConfig(allow_loud=False, only_found=False, no_nsfw=no_nsfw, verbose=False)

    if module:
        modules = find_module(module.replace(".", "_"), is_email, no_nsfw)
        if not modules:
            raise ValueError(f"Module '{module}' not found")
        module_config = dc_replace(config, allow_loud=True)
        results = []
        for m in modules:
            if is_email:
                results.extend(run_email_module_batch(m, target, module_config))
            else:
                results.extend(run_user_module(m, target, module_config))
    elif category:
        categories = load_categories(is_email, no_nsfw)
        cat_path = categories.get(category)
        if not cat_path:
            available = list(categories.keys())
            raise ValueError(f"Category '{category}' not found. Available: {available}")
        if is_email:
            results = run_email_category_batch(cat_path, target, config)
        else:
            results = run_user_category(cat_path, target, config)
    else:
        if is_email:
            results = run_email_full_batch(target, config)
        else:
            results = run_user_full(target, config)

    if only_found:
        results = [r for r in results if r.is_found()]

    return [r.to_dict() for r in results]


def get_modules(is_email: bool, no_nsfw: bool = False) -> dict:
    categories = load_categories(is_email, no_nsfw)
    return {
        cat_name: [get_site_name(m) for m in load_modules(cat_path)]
        for cat_name, cat_path in categories.items()
    }
