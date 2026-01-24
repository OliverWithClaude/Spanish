"""
Image search module for vocabulary learning
Uses Unsplash API for free, high-quality images
"""

import os
import requests
from typing import Optional, Tuple

# Categories where images make sense (concrete, visual concepts)
# Note: These are normalized (lowercase, "and" instead of "&") and will be matched fuzzily
IMAGEABLE_CATEGORIES = {
    "food and drinks",
    "food & drinks",  # Keep both for backwards compatibility
    "family and people",
    "family & people",
    "office vocabulary",
    "shopping basics",
    "colors and adjectives",
    "colors & adjectives",
    "weather and seasons",
    "weather & seasons",
    "at the restaurant",
    "slang",  # Some slang terms may be imageable
}

# Categories that are too abstract for meaningful images
ABSTRACT_CATEGORIES = {
    "greetings and introductions",
    "greetings & introductions",
    "numbers 1-100",
    "basic questions",
    "time and days",
    "time & days",
    "meetings and schedules",
    "meetings & schedules",
    "communication and email",
    "communication & email",
    "asking for help",
    "common verbs",
}

def get_unsplash_api_key() -> Optional[str]:
    """Get Unsplash API key from environment variable"""
    return os.environ.get("UNSPLASH_API_KEY")


def is_imageable(category: str) -> bool:
    """
    Determine if a vocabulary category is suitable for image display.

    Args:
        category: The vocabulary category (e.g., "Food & Drinks")

    Returns:
        True if the category contains concrete, imageable words
    """
    if not category:
        return False

    # Normalize: lowercase, strip, and replace ampersand with "and"
    category_normalized = category.lower().strip().replace(" & ", " and ").replace("&", "and")

    # Also normalize the imageable and abstract sets for comparison
    imageable_normalized = {cat.replace(" & ", " and ").replace("&", "and") for cat in IMAGEABLE_CATEGORIES}
    abstract_normalized = {cat.replace(" & ", " and ").replace("&", "and") for cat in ABSTRACT_CATEGORIES}

    # Check if it's in our imageable list
    if category_normalized in imageable_normalized:
        return True

    # Check if it's explicitly abstract
    if category_normalized in abstract_normalized:
        return False

    # Default to False for unknown categories
    return False


def search_image(query: str, fallback_query: str = None) -> Tuple[Optional[str], Optional[str]]:
    """
    Search for an image on Unsplash.

    Args:
        query: The search term (usually the English translation)
        fallback_query: Alternative search term if first fails

    Returns:
        Tuple of (image_url, photographer_credit) or (None, None) if not found
    """
    api_key = get_unsplash_api_key()

    if not api_key:
        print("Warning: UNSPLASH_API_KEY not set. Image search disabled.")
        return None, None

    headers = {
        "Authorization": f"Client-ID {api_key}"
    }

    # Try primary query
    url = f"https://api.unsplash.com/search/photos?query={query}&per_page=1&orientation=squarish"

    try:
        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code == 200:
            data = response.json()

            if data.get("results") and len(data["results"]) > 0:
                photo = data["results"][0]
                image_url = photo["urls"]["small"]  # 400px wide
                photographer = photo["user"]["name"]
                return image_url, f"Photo by {photographer} on Unsplash"

        # Try fallback query if primary failed
        if fallback_query and fallback_query != query:
            url = f"https://api.unsplash.com/search/photos?query={fallback_query}&per_page=1&orientation=squarish"
            response = requests.get(url, headers=headers, timeout=5)

            if response.status_code == 200:
                data = response.json()

                if data.get("results") and len(data["results"]) > 0:
                    photo = data["results"][0]
                    image_url = photo["urls"]["small"]
                    photographer = photo["user"]["name"]
                    return image_url, f"Photo by {photographer} on Unsplash"

        # Rate limit or other error
        if response.status_code == 403:
            print("Unsplash API rate limit reached (50/hour on free tier)")
            return None, "Rate limit reached - try again later"

    except requests.exceptions.Timeout:
        print("Unsplash API timeout")
        return None, None
    except requests.exceptions.RequestException as e:
        print(f"Unsplash API error: {e}")
        return None, None

    return None, None


def get_memory_image(spanish: str, english: str, category: str) -> Tuple[Optional[str], Optional[str], bool]:
    """
    Get an image to help remember a vocabulary word.

    Args:
        spanish: The Spanish word
        english: The English translation
        category: The vocabulary category

    Returns:
        Tuple of (image_url, credit_text, is_imageable)
        - image_url: URL to display, or None
        - credit_text: Attribution text for the image
        - is_imageable: Whether this category supports images
    """
    # Check if this category is imageable
    if not is_imageable(category):
        return None, None, False

    # Search using English translation (better results on Unsplash)
    # Use Spanish as fallback for culture-specific terms
    image_url, credit = search_image(english, spanish)

    return image_url, credit, True
