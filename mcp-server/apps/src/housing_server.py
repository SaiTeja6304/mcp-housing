from typing import Optional
from mcp.server.fastmcp import FastMCP 
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import html
from utils import *
import httpx
import sys


mcp = FastMCP("Jump Off Campus MCP Server")

DEFAULT_LIMIT = 10

@mcp.tool()
async def get_house_locations() -> list:
    """Get all available university-wise housing locations and their slugs/subdomains from Jump Off Campus.

    Returns:
        list: A list of dictionaries representing housing locations with keys: 'university', 'city', 'location', and 'slug'.
    """
    url = "https://www.jumpoffcampus.com/"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=20)
            page_html = response.text
            soup = BeautifulSoup(page_html, "html.parser")

            box = soup.find("div", attrs={"data-react-cache-id": "PortalSelect/rails_binding-0"})
            if not box:
                return [{"error": "Could not find the portal data on the page."}]
            
            data = json.loads(html.unescape(box["data-react-props"]))

            housing_locations = []
            for item in data.get("schools", []):
                housing_locations.append({
                    "university": item.get("name", ""),
                    "city": item.get("city", "").strip() if item.get("city") else "",
                    "location": item.get("address", "").strip() if item.get("address") else "",
                    "slug": item.get("subdomain")
                })
        
        return housing_locations
    except Exception as e:
        return [{"error": str(e)}]


@mcp.tool()
async def get_housing_listings(slug: str, limit: Optional[int] = DEFAULT_LIMIT) -> dict:
    """Get all available housing listings for a specific location using its slug.

    Results are limited by default to avoid overwhelming the context window.
    Check the returned `metadata` to see the total number of available records
    and whether the result was truncated. Re-call with a higher `limit` or use
    `filter_house_information` with specific filters to narrow results instead.

    Args:
        slug: The university/location slug.
        limit: Maximum number of listings to return (default: 10). Pass None for all.

    Returns:
        Use the full pipeline tool filter_house_information to get the listing_path required for get_house_link tool
        dict: An envelope with keys:
            - metadata: total_records, returned_records, truncated, warning
            - records: list of listing dicts with keys 'name', 'cost', 'place', 'move_in', 'posted'
    """
    url = f"https://{slug}.jumpoffcampus.com/api/listings"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers={"Accept": "application/json"}, timeout=20)
            response.raise_for_status()
            listings_data = response.json()
    except Exception as e:
        return [{"error": str(e)}]

    if not isinstance(listings_data, list):
        return [{"error": f"Expected list of listings, but got {type(listings_data)}"}]

    listings = []

    for item in listings_data:
        listing = {
            "name": item.get("title", ""),
            "cost": f"${item.get('price')} / {item.get('beds')} beds",
            "place": item.get("layout", ""),
            "move_in": format_move_in(item.get("start_date")),
            "posted": format_posted(item.get("posted_at")),
        }

        listings.append(listing)

    total = len(listings)
    sliced = listings if limit is None else listings[:limit]
    return build_response(sliced, total, limit)


@mcp.tool()
async def filter_house_information(
    slug: str,
    housing_type: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    min_beds: Optional[int] = None,
    max_beds: Optional[int] = None,
    min_move_in_date: Optional[str] = None,
    max_move_in_date: Optional[str] = None,
    wheelchair_access: Optional[bool] = None,
    pets_allowed: Optional[bool] = None,
    laundry: Optional[bool] = None,
    utilities: Optional[bool] = None,
    furnished: Optional[bool] = None,
    parking: Optional[bool] = None,
    air_conditioning: Optional[bool] = None,
    limit: Optional[int] = DEFAULT_LIMIT) -> dict:
    """Filter and retrieve detailed housing information for a location using various search criteria.

    Results are limited by default to avoid overwhelming the context window.
    Check the returned `metadata` to see the total number of matching records
    and whether the result was truncated. Re-call with a higher `limit`, or
    add more filters to narrow results further before increasing the limit.

    Args:
        slug: The university/location slug.
        housing_type: Type of housing ("Shared room", "Private room", or "Entire place").
        min_price: Minimum monthly rent price.
        max_price: Maximum monthly rent price.
        min_beds: Minimum number of bedrooms required.
        max_beds: Maximum number of bedrooms allowed.
        min_move_in_date: Earliest allowed move-in date (YYYY-MM-DD).
        max_move_in_date: Latest allowed move-in date (YYYY-MM-DD).
        wheelchair_access: True to filter by wheelchair/handicap accessible units.
        pets_allowed: True if pets are allowed.
        laundry: True if washer/dryer is included/available.
        utilities: True if some utilities are included in rent.
        furnished: True if the unit is furnished.
        parking: True if designated parking is included.
        air_conditioning: True if air conditioning is available.
        limit: Maximum number of listings to return (default: 10). Pass None for all.

    Returns:
        This tool returns listing_path required for get_house_link tool
        dict: An envelope with keys:
            - metadata: total_records, returned_records, truncated, warning
            - records: list of detailed house dicts including listing_path for get_house_link
    """
    
    url = f"https://{slug}.jumpoffcampus.com/api/listings"

    params = {
        "controller": "housing",
        "action": "index",
        "layout": housing_type,
        "min_price": min_price,
        "max_price": max_price,
        "min_bedrooms": min_beds,
        "max_bedrooms": max_beds,
        "min_start_date": min_move_in_date,
        "max_start_date": max_move_in_date,
        "wheelchair_access": wheelchair_access,
        "pets": pets_allowed,
        "laundry": laundry,
        "utilities": utilities,
        "furnished": furnished,
        "parking": parking,
        "air_conditioning": air_conditioning,
    }

    params = {
        key: ("true" if value is True else "false" if value is False else value)
        for key, value in params.items()
        if value is not None
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url,
                headers={"Accept": "application/json"},
                params=params,
                timeout=20)
        
            response.raise_for_status()
            house_data = response.json()
    except Exception as e:
        return [{"error": str(e)}]

    if not isinstance(house_data, list):
        return [{"error": f"Expected list of houses, but got {type(house_data)}"}] 

    filtered_house_info = []

    for item in house_data:
        listing = {
            "house_name": item.get("title", ""),
            "house_address": f'{item.get("address_1", "")}, {item.get("city", "")}, {item.get("state", "")}, {item.get("zip", "")}',
            "house_price": item.get("price", ""),
            "house_description": item.get("description", ""),
            "lease_length": item.get("lease_length", ""),
            "house_sqft": item.get("sq_ft", ""),
            "house_pets_allowed": "Pets Allowed" if item.get("pets_allowed") else "No Pets Allowed",
            "laundry": "Laundry Available" if item.get("laundry") else "No Laundry Available",
            "wheelchair_accessible": "Wheelchair Accessible" if item.get("wheelchair_access") else "Not Wheelchair Accessible",
            "furnished": "Furnished" if item.get("furnished") else "Not Furnished",
            "gas": "Gas Included" if item.get("gas") else "Gas Not Included",
            "electric": "Electricity Included" if item.get("electric") else "Electricity Not Included",
            "water": "Water Included" if item.get("water") else "Water Not Included",
            "heat": "Heat Included" if item.get("heat") else "Heat Not Included",
            "cooling": "Cooling Included" if item.get("cooling") else "Cooling Not Included",
            "internet": "Internet Included" if item.get("internet") else "Internet Not Included",
            "air_conditioning": "Air Conditioning Included" if item.get("air_conditioning") else "Air Conditioning Not Included",
            "parking": item.get("parking", ""),
            "layout": item.get("layout", ""),
            "house_beds": item.get("beds", ""),
            "house_bathrooms": item.get("bathrooms", ""),
            "contact": item.get("phone", ""),
            "relationship_to_house": item.get("relationship", ""),
            "move_in": format_move_in(item.get("start_date")),
            "posted": format_posted(item.get("posted_at")),
            "listing_path": item.get("listing_path", ""),
        }

        filtered_house_info.append(listing)

    total = len(filtered_house_info)
    sliced = filtered_house_info if limit is None else filtered_house_info[:limit]
    return build_response(sliced, total, limit)


@mcp.tool()
async def get_house_link(slug: str, listing_path: str) -> str:
    """Generate the full direct URL to a housing listing on the Jump Off Campus website.

    Args:
        slug: The university/location slug.
        listing_path: The specific listing path (e.g., "/listings/26-highland") retrieved from search results.

    Returns:
        str: The full URL to the housing listing page.
    """

    house_url = f"https://{slug}.jumpoffcampus.com{listing_path}"
    return house_url


@mcp.tool()
async def get_slug_posts(slug: str, limit: Optional[int] = DEFAULT_LIMIT) -> dict:
    """Retrieve community posts, announcements, and articles associated with a specific university/location slug.

    Results are limited by default to avoid overwhelming the context window.
    Check the returned `metadata` to see the total number of available posts
    and whether the result was truncated. Re-call with a higher `limit` if needed.

    Args:
        slug: The university/location slug.
        limit: Maximum number of posts to return (default: 10). Pass None for all.

    Returns:
        dict: An envelope with keys:
            - metadata: total_records, returned_records, truncated, warning
            - records: list of post dicts with keys 'post_id', 'post_title', 'post_author',
                       'published_at', 'post_description', 'post_url'
    """
    url = f"https://{slug}.jumpoffcampus.com/posts"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=20)
        
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            posts = []

            for heading in soup.find_all("h4"):
                link = heading.find("a", href=True)
                if not link or "/posts/" not in link["href"]:
                    continue

                post_title = clean_text(link.get_text(" ", strip=True))
                post_url = urljoin(url, link["href"])
                post_id = link["href"].rstrip("/").split("/")[-1]

                text_parts = []
                for sibling in heading.find_next_siblings():
                    if sibling.name == "h4":
                        break

                    text = clean_text(sibling.get_text(" ", strip=True))
                    if text:
                        text_parts.append(text)

                meta = text_parts[0] if text_parts else ""
                post_description = text_parts[1] if len(text_parts) > 1 else ""

                author = ""
                published_at = ""

                match = re.search(r"By\s+(.*?)\s+•\s+Published\s+(.+)", meta)
                if match:
                    author = match.group(1)
                    published_at = match.group(2)

                posts.append({
                    "post_id": post_id,
                    "post_title": post_title,
                    "post_author": author,
                    "published_at": published_at,
                    "post_description": post_description,
                    "post_url": post_url,
                })

        total = len(posts)
        sliced = posts if limit is None else posts[:limit]
        return build_response(sliced, total, limit)
            
    except Exception as e:
        return [{"error": str(e)}]


@mcp.tool()
async def get_slug_post(slug: str, post_id: str) -> dict | None:
    """Retrieve full details and content of a specific community post using the university slug and the post ID.

    Args:
        slug: The university/location slug.
        post_id: The unique ID of the post.

    Returns:
        dict | None: A dictionary containing the post details or None if not found, with keys: 'post_id', 'post_title', 'post_author', 'published_at', 'post_description', and 'post_url'.
    """
    post_id = post_id.strip()
    post_url = f"https://{slug}.jumpoffcampus.com/posts/{post_id}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(post_url, timeout=20)
        
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")

            title_node = soup.select_one(".page-header h1")
            meta_node = soup.select_one(".page-header .text-muted")
            content_node = soup.select_one(".post-content .trix-content")

            if not title_node:
                return None

            post_title = clean_text(title_node.get_text(" ", strip=True))
            meta = clean_text(meta_node.get_text(" ", strip=True)) if meta_node else ""
            post_description = clean_text(content_node.get_text(" ", strip=True)) if content_node else ""

            post_author = ""
            published_at = ""

            match = re.search(r"By\s+(.*?)\s+•\s+Published\s+(.+)", meta)
            if match:
                post_author = match.group(1)
                published_at = match.group(2)

        return {
            "post_id": post_id,
            "post_title": post_title,
            "post_author": post_author,
            "published_at": published_at,
            "post_description": post_description,
            "post_url": post_url,
        }
    except Exception as e:
        print(f"Error retrieving post: {e}", file=sys.stderr)
        return None


if __name__ == "__main__": 
    print("Started Jump Off Campus MCP Server", file=sys.stderr)
    try:
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        print("\nJump Off Campus MCP Server terminated", file=sys.stderr)
