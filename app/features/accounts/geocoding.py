from dataclasses import dataclass

import httpx

from app.core.config import get_settings
from app.features.accounts.options import SAN_PEDRO_ADDRESS_SUFFIX


SAN_PEDRO_BOUNDS = {
    "min_lat": 14.235,
    "max_lat": 14.418,
    "min_lng": 120.945,
    "max_lng": 121.131,
}
SAN_PEDRO_CENTER = {"lat": 14.3413, "lng": 121.0446}


class GeocodingError(Exception):
    pass


class GeocodingUnavailable(GeocodingError):
    pass


class GeocodingNoResult(GeocodingError):
    pass


@dataclass(frozen=True)
class GeocodeCandidate:
    latitude: float
    longitude: float
    display_address: str
    provider: str
    source: str
    confidence: float | None = None


def is_inside_san_pedro(latitude: float, longitude: float) -> bool:
    return (
        SAN_PEDRO_BOUNDS["min_lat"] <= latitude <= SAN_PEDRO_BOUNDS["max_lat"]
        and SAN_PEDRO_BOUNDS["min_lng"] <= longitude <= SAN_PEDRO_BOUNDS["max_lng"]
    )


async def geocode_enterprise_address(address: str, barangay: str, enterprise_name: str | None = None) -> GeocodeCandidate:
    settings = get_settings()
    provider = settings.geocoder_provider.strip().lower()
    query = build_geocode_query(address, barangay, enterprise_name)

    if provider == "nominatim":
        return await geocode_with_nominatim(query, barangay)
    if provider == "geoapify":
        return await geocode_with_geoapify(query, barangay)

    raise GeocodingUnavailable(f"Unsupported geocoder provider: {settings.geocoder_provider}")


def build_geocode_query(address: str, barangay: str, enterprise_name: str | None = None) -> str:
    cleaned_address = address.strip().rstrip(",")
    prefix = f"{enterprise_name.strip()}, " if enterprise_name and enterprise_name.strip() else ""
    barangay_segment = f"Barangay {barangay.strip()}"

    if cleaned_address.lower().endswith(SAN_PEDRO_ADDRESS_SUFFIX.lower()):
        return f"{prefix}{cleaned_address}, {barangay_segment}, Philippines"

    return f"{prefix}{cleaned_address}, {barangay_segment}, {SAN_PEDRO_ADDRESS_SUFFIX}, Philippines"


async def geocode_with_nominatim(query: str, barangay: str) -> GeocodeCandidate:
    settings = get_settings()
    base_url = settings.geocoder_base_url or "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "jsonv2",
        "addressdetails": "1",
        "limit": "5",
        "countrycodes": "ph",
        "viewbox": "120.945,14.418,121.131,14.235",
        "bounded": "1",
    }
    headers = {"User-Agent": settings.geocoder_user_agent}

    try:
        async with httpx.AsyncClient(timeout=8) as client:
            response = await client.get(base_url, params=params, headers=headers)
            response.raise_for_status()
            payload = response.json()
    except httpx.HTTPError as exc:
        raise GeocodingUnavailable("Nominatim geocoding request failed.") from exc

    candidates: list[GeocodeCandidate] = []
    for item in payload if isinstance(payload, list) else []:
        try:
            latitude = float(item["lat"])
            longitude = float(item["lon"])
        except (KeyError, TypeError, ValueError):
            continue

        if not is_inside_san_pedro(latitude, longitude):
            continue

        confidence = normalize_confidence(item.get("importance"))
        candidates.append(
            GeocodeCandidate(
                latitude=latitude,
                longitude=longitude,
                display_address=str(item.get("display_name") or query),
                provider="nominatim",
                source="geocoded",
                confidence=confidence,
            ),
        )

    return select_best_candidate(candidates, barangay)


async def geocode_with_geoapify(query: str, barangay: str) -> GeocodeCandidate:
    settings = get_settings()
    if not settings.geocoder_api_key:
        raise GeocodingUnavailable("Geoapify geocoding requires GEOCODER_API_KEY.")

    base_url = settings.geocoder_base_url or "https://api.geoapify.com/v1/geocode/search"
    params = {
        "text": query,
        "filter": "rect:120.945,14.418,121.131,14.235",
        "bias": f"proximity:{SAN_PEDRO_CENTER['lng']},{SAN_PEDRO_CENTER['lat']}",
        "limit": "5",
        "apiKey": settings.geocoder_api_key,
    }

    try:
        async with httpx.AsyncClient(timeout=8) as client:
            response = await client.get(base_url, params=params)
            response.raise_for_status()
            payload = response.json()
    except httpx.HTTPError as exc:
        raise GeocodingUnavailable("Geoapify geocoding request failed.") from exc

    candidates: list[GeocodeCandidate] = []
    for feature in payload.get("features", []) if isinstance(payload, dict) else []:
        properties = feature.get("properties", {})
        try:
            latitude = float(properties["lat"])
            longitude = float(properties["lon"])
        except (KeyError, TypeError, ValueError):
            continue

        if not is_inside_san_pedro(latitude, longitude):
            continue

        rank = properties.get("rank") if isinstance(properties, dict) else {}
        confidence = normalize_confidence(rank.get("confidence")) if isinstance(rank, dict) else None
        candidates.append(
            GeocodeCandidate(
                latitude=latitude,
                longitude=longitude,
                display_address=str(properties.get("formatted") or query),
                provider="geoapify",
                source="geocoded",
                confidence=confidence,
            ),
        )

    return select_best_candidate(candidates, barangay)


def select_best_candidate(candidates: list[GeocodeCandidate], barangay: str) -> GeocodeCandidate:
    if not candidates:
        raise GeocodingNoResult("No geocoding result was found inside San Pedro.")

    barangay_key = normalize_location_text(barangay)
    return max(
        candidates,
        key=lambda candidate: (
            barangay_key in normalize_location_text(candidate.display_address),
            candidate.confidence or 0,
        ),
    )


def normalize_confidence(value: object) -> float | None:
    if not isinstance(value, str | int | float):
        return None

    try:
        number = float(value)
    except ValueError:
        return None

    return max(0.0, min(number, 1.0))


def normalize_location_text(value: str) -> str:
    return "".join(character for character in value.lower() if character.isalnum())
