"""
Configuration management and resource profiles
DEPRECATED: Use core.config for new code, but kept for backward compatibility
"""

from typing import Dict, Any, Optional
from enum import Enum

# Re-export from core.config for backward compatibility
try:
    from .core.config import ResourceProfile, BudgetProfile, PortConfig, AppConfig
except ImportError:
    # Fallback if core module not available
    class ResourceProfile(str, Enum):
        """Resource profile types"""
        DESKTOP = "desktop"
        SMALL_VPS = "small"
        MEDIUM_VPS = "medium"
        LARGE_VPS = "large"


RESOURCE_PROFILES = {
    ResourceProfile.DESKTOP: {
        "name": "Desktop/Local",
        "description": "Local development, unlimited resources",
        "cpu_cores": "4-8",
        "ram": "8GB+",
        "workers": "4",
        "recommended_for": "home computer, local server",
    },
    ResourceProfile.SMALL_VPS: {
        "name": "Small VPS",
        "description": "Budget VPS for light use",
        "cpu_cores": "2",
        "ram": "2GB",
        "workers": "1",
        "recommended_for": "1-2 users, occasional use",
        "note": "1 worker - WARNING: Actual usage ~2.3-2.5GB (exceeds 2GB). See docs/system-requirements.md#small-vps-2gb-ram-2-cpu-cores",
    },
    ResourceProfile.MEDIUM_VPS: {
        "name": "Medium VPS",
        "description": "Recommended for most users",
        "cpu_cores": "4",
        "ram": "4GB",
        "workers": "2",
        "recommended_for": "3-5 users",
        "note": "2 workers - safe on 4GB RAM (uses ~3.3GB, leaves ~700MB buffer). Monitor with: docker stats",
    },
    ResourceProfile.LARGE_VPS: {
        "name": "Large VPS",
        "description": "For high load and teams",
        "cpu_cores": "8",
        "ram": "8GB+",
        "workers": "6",
        "recommended_for": "10+ users, active use",
        "note": "6 workers - safe for 8GB+ RAM (uses ~5.1GB, leaves ~3GB buffer). Monitor with: docker stats",
    },
}


def get_profile_info(profile: ResourceProfile) -> Dict[str, Any]:
    """Get information about a resource profile"""
    return RESOURCE_PROFILES.get(profile, {})


def select_resource_profile() -> Optional[ResourceProfile]:
    """Interactive selection of resource profile"""
    from .utils import print_header, print_info, Colors
    
    print_header("💻 Performance Profile Selection")
    print()
    print_info("What are workers?")
    print_info("Workers are separate processes that handle API requests in parallel.")
    print_info("More workers = better performance under load, but more RAM usage.")
    print_info("IMPORTANT: Real measurements show each worker uses ~460MB RAM (not 100-200MB).")
    print_info("This is due to LiteLLM's model loading, caching, and Python 3.13 overhead.")
    print_info("LiteLLM uses Gunicorn to manage workers.")
    print_info("")
    print_info("Why multiple workers?")
    print_info("• Handle multiple requests simultaneously")
    print_info("• Better CPU utilization (especially for I/O-bound operations)")
    print_info("• If one worker is busy, others can handle new requests")
    print_info("")
    print_info("Formula: (CPU cores * 2) + 1, adjusted for available RAM")
    print_info("Note: Profiles are optimized based on REAL memory measurements.")
    print()
    
    profiles = [
        (ResourceProfile.DESKTOP, "1"),
        (ResourceProfile.SMALL_VPS, "2"),
        (ResourceProfile.MEDIUM_VPS, "3"),
        (ResourceProfile.LARGE_VPS, "4"),
    ]
    
    for profile, num in profiles:
        info = RESOURCE_PROFILES[profile]
        print(f"{Colors.BLUE}[{num}] {info['name']}{Colors.RESET} - {info['description']}")
        print(f"    CPU: {info['cpu_cores']}, RAM: {info['ram']}, Workers: {info['workers']}")
        if 'note' in info:
            print(f"    {Colors.YELLOW}Note: {info['note']}{Colors.RESET}")
        print(f"    For: {info['recommended_for']}")
        print()
    
    print(f"{Colors.BLUE}[5] Don't configure workers{Colors.RESET} - Use LiteLLM defaults")
    print(f"    {Colors.YELLOW}You'll need to configure workers manually in docker-compose.override.yml{Colors.RESET}")
    print()
    
    while True:
        choice = input("Select profile [1-5]: ").strip()
        
        if choice == "5":
            print(f"{Colors.GREEN}✅ Selected: Don't configure workers (using defaults){Colors.RESET}")
            return None  # Special value to indicate no workers configuration
        
        for profile, num in profiles:
            if choice == num:
                info = RESOURCE_PROFILES[profile]
                print(f"{Colors.GREEN}✅ Selected profile: {info['name']}{Colors.RESET}")
                return profile
        
        print(f"{Colors.RED}❌ Invalid choice. Enter 1, 2, 3, 4, or 5{Colors.RESET}")

