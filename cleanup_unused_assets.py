#!/usr/bin/env python3
"""
Cleanup script to remove unnecessary files downloaded during localization.
Removes external HTML mirrors (LinkedIn, WhatsApp, Twitter, etc.) that aren't
referenced by the main website HTML files.
"""

import os
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DEPLOY_DIR = PROJECT_ROOT / "deploy"
LOCAL_DIR = DEPLOY_DIR / "local"

# Domains that contain only HTML mirrors, not actual assets used by the site
UNNECESSARY_HTML_DOMAINS = [
    # LinkedIn domains (all country codes)
    "linkedin.com",
    "www.linkedin.com",
    "ae.linkedin.com", "ar.linkedin.com", "at.linkedin.com", "au.linkedin.com",
    "bo.linkedin.com", "br.linkedin.com", "ca.linkedin.com", "ch.linkedin.com",
    "cl.linkedin.com", "cn.linkedin.com", "co.linkedin.com", "cr.linkedin.com",
    "cz.linkedin.com", "de.linkedin.com", "dk.linkedin.com", "do.linkedin.com",
    "ec.linkedin.com", "es.linkedin.com", "fr.linkedin.com", "gh.linkedin.com",
    "gt.linkedin.com", "hk.linkedin.com", "id.linkedin.com", "ie.linkedin.com",
    "il.linkedin.com", "in.linkedin.com", "it.linkedin.com", "jm.linkedin.com",
    "jp.linkedin.com", "ke.linkedin.com", "kr.linkedin.com", "lu.linkedin.com",
    "mx.linkedin.com", "my.linkedin.com", "ng.linkedin.com", "nl.linkedin.com",
    "no.linkedin.com", "nz.linkedin.com", "pa.linkedin.com", "pe.linkedin.com",
    "ph.linkedin.com", "pk.linkedin.com", "pl.linkedin.com", "pr.linkedin.com",
    "pt.linkedin.com", "ro.linkedin.com", "ru.linkedin.com", "se.linkedin.com",
    "sg.linkedin.com", "sv.linkedin.com", "th.linkedin.com", "tr.linkedin.com",
    "tt.linkedin.com", "tw.linkedin.com", "uk.linkedin.com", "uy.linkedin.com",
    "ve.linkedin.com", "za.linkedin.com", "zw.linkedin.com",
    
    # Other social/external HTML mirrors
    "twitter.com",
    "wa.me",
    "bolt.new",
    "www.googletagmanager.com",  # GTM JS is not needed (tracking)
]

# Files/extensions to keep (actual assets needed by the site)
ASSET_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.ico',  # Images
    '.woff', '.woff2', '.ttf', '.otf', '.eot',  # Fonts
    '.css', '.js', '.json',  # Styles and scripts
    '.php',  # Some PHP files might be CSS/JS
}

def should_keep_file(file_path: Path) -> bool:
    """Determine if a file should be kept based on its extension."""
    return file_path.suffix.lower() in ASSET_EXTENSIONS

def should_remove_domain(domain: str) -> bool:
    """Check if entire domain folder should be removed."""
    return any(domain == d or domain.startswith(d + '/') for d in UNNECESSARY_HTML_DOMAINS)

def cleanup():
    """Remove unnecessary HTML files and empty domain folders."""
    removed_dirs = []
    removed_files = []
    kept_files = []
    
    # Process each domain folder
    if not LOCAL_DIR.exists():
        print(f"Local directory does not exist: {LOCAL_DIR}")
        return
    
    for domain_dir in LOCAL_DIR.iterdir():
        if not domain_dir.is_dir():
            continue
            
        domain_name = domain_dir.name
        
        # Check if entire domain should be removed
        if should_remove_domain(domain_name):
            print(f"Removing entire domain: {domain_name}")
            shutil.rmtree(domain_dir)
            removed_dirs.append(domain_name)
            continue
        
        # Otherwise, remove only HTML files but keep assets
        html_files = []
        assets = []
        
        for file_path in domain_dir.rglob('*'):
            if file_path.is_file():
                if file_path.suffix.lower() == '.html':
                    html_files.append(file_path)
                elif should_keep_file(file_path):
                    assets.append(file_path)
                    kept_files.append(str(file_path.relative_to(LOCAL_DIR)))
        
        # Remove HTML files
        for html_file in html_files:
            html_file.unlink()
            removed_files.append(str(html_file.relative_to(LOCAL_DIR)))
        
        # Remove empty directories (recursively)
        try:
            for empty_dir in sorted(domain_dir.rglob('*'), key=lambda p: len(p.parts), reverse=True):
                if empty_dir.is_dir() and not any(empty_dir.iterdir()):
                    empty_dir.rmdir()
        except:
            pass  # Directory not empty, that's fine
    
    # Summary
    print("\n" + "="*60)
    print("CLEANUP SUMMARY")
    print("="*60)
    print(f"Removed domains: {len(removed_dirs)}")
    if removed_dirs:
        print(f"  - {', '.join(removed_dirs[:5])}{' ...' if len(removed_dirs) > 5 else ''}")
    print(f"Removed HTML files: {len(removed_files)}")
    print(f"Kept asset files: {len(kept_files)}")
    print(f"\nTotal assets remaining: {sum(1 for _ in LOCAL_DIR.rglob('*') if _.is_file())}")
    print("="*60)

if __name__ == "__main__":
    cleanup()

