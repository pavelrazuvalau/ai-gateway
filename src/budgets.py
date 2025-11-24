"""
Budget profiles for different environments (test/prod)
"""

from typing import Dict, Any

# Budget profiles for different environments
BUDGET_PROFILES = {
    "test": {
        "description": "Test environment - minimal limits",
        "general_budget": 15.0,  # Total budget for all models
    },
    "prod": {
        "description": "Production environment - normal limits",
        "general_budget": 200.0,  # Total budget for all models
    },
    "unlimited": {
        "description": "No limits (be careful!)",
        "general_budget": 1000.0,  # Very high limit
    },
}


def get_budget_profile(profile_name: str = "test") -> Dict[str, Any]:
    """Get budget profile by name"""
    return BUDGET_PROFILES.get(profile_name, BUDGET_PROFILES["test"])


def get_general_budget(profile_name: str = "test") -> float:
    """Get total budget for profile"""
    profile = get_budget_profile(profile_name)
    return profile.get("general_budget", 100.0)

