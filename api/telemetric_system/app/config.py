"""Application configuration management.

This module loads environment variables (optionally from a local .env file),
assembles structured configuration for the application, validates required
settings, and exposes a single, immutable settings object.

Handled areas:
- Environment variables loading
- Database connection strings
- Redis configuration
- MQTT broker settings
- JWT secret keys
- Alert thresholds
- API rate limits

Validation ensures critical settings are present and well-formed. Where
reasonable, secure or practical defaults are provided.
"""

from __future__ import annotations

import os
import pathlib
import re
from dataclasses import dataclass
from typing import Dict, Optional


class ConfigError(RuntimeError):
    """Raised when required configuration is missing or invalid."""


def _load_dotenv(env_path: pathlib.Path) -> Dict[str, str]:
    """Load KEY=VALUE pairs from a .env file if present.

    - Lines starting with '#' are comments and ignored.
    - Empty lines are ignored.
    - Quotes around values are stripped.
    - Does not override existing os.environ entries; it only returns a dict.
    """

    if not env_path.exists() or not env_path.is_file():
        return {}

    values: Dict[str, str] = {}
    with env_path.open("r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip().strip("'\"")
            if key:
                values[key] = val
    return values


def _env_get(
    key: str,
    default: Optional[str] = None,
    source: Optional[Dict[str, str]] = None,
) -> Optional[str]:
    """Get env var with fallback to .env sourced values, then default."""

    if key in os.environ:
        return os.environ[key]
    if source and key in source:
        return source[key]
    return default


def _to_bool(value: Optional[str], default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _to_int(value: Optional[str], default: int) -> int:
    try:
        return int(value) if value is not None else default
    except ValueError as exc:
        raise ConfigError(f"Invalid integer for configuration: {value}") from exc


def _to_float(value: Optional[str], default: float) -> float:
    try:
        return float(value) if value is not None else default
    except ValueError as exc:
        raise ConfigError(f"Invalid float for configuration: {value}") from exc


def _validate_url_scheme(url: str, allowed: tuple[str, ...]) -> None:
    match = re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url or "")
    if not match:
        raise ConfigError(f"Invalid URL (missing scheme): {url}")
    scheme = url.split(":", 1)[0]
    if scheme not in allowed:
        raise ConfigError(f"Unsupported URL scheme '{scheme}' for: {url}")


def _build_postgres_url(src: Dict[str, str]) -> Optional[str]:
    """Build a PostgreSQL URL from discrete parts if DATABASE_URL is not set."""

    host = _env_get("POSTGRES_HOST", source=src)
    if not host:
        return None
    user = _env_get("POSTGRES_USER", source=src) or "postgres"
    password = _env_get("POSTGRES_PASSWORD", source=src) or ""
    port = _env_get("POSTGRES_PORT", source=src) or "5432"
    database = _env_get("POSTGRES_DB", source=src) or "postgres"
    auth = f"{user}:{password}@" if password else f"{user}@"
    return f"postgresql://{auth}{host}:{port}/{database}"


@dataclass(frozen=True)
class DatabaseSettings:
    primary_url: str
    mongo_url: Optional[str]


@dataclass(frozen=True)
class RedisSettings:
    url: Optional[str]
    host: str
    port: int
    db: int


@dataclass(frozen=True)
class MqttSettings:
    host: str
    port: int
    username: Optional[str]
    password: Optional[str]
    use_tls: bool


@dataclass(frozen=True)
class JwtSettings:
    secret: str
    algorithm: str
    access_token_minutes: int
    refresh_token_minutes: int


@dataclass(frozen=True)
class AlertThresholds:
    speed_limit_kph: float
    engine_temp_high_c: float
    fuel_theft_liters_delta: float
    harsh_accel_g: float
    hard_brake_g: float


@dataclass(frozen=True)
class ApiRateLimits:
    requests_per_minute: int
    burst: int


@dataclass(frozen=True)
class Settings:
    env: str
    debug: bool
    database: DatabaseSettings
    redis: RedisSettings
    mqtt: MqttSettings
    jwt: JwtSettings
    alerts: AlertThresholds
    rate_limits: ApiRateLimits


def load_settings() -> Settings:
    """Load and validate settings from environment and optional .env file."""

    project_root = pathlib.Path(__file__).resolve().parents[2]
    print(project_root)
    dotenv_values = _load_dotenv(project_root / ".env")

    env = _env_get("ENV", "development", dotenv_values) or "development"
    debug = _to_bool(_env_get("DEBUG", None, dotenv_values), default=(env != "production"))

    # Database
    db_url = _env_get("DATABASE_URL", None, dotenv_values)
    if not db_url:
        db_url = _build_postgres_url(dotenv_values)  # build if parts provided
    if not db_url:
        raise ConfigError(
            "DATABASE_URL is required (or POSTGRES_HOST and related parts to build it)."
        )
    # Support both PostgreSQL and SQLite
    if db_url.startswith("sqlite"):
        pass  # SQLite doesn't need scheme validation
    else:
        _validate_url_scheme(db_url, ("postgresql", "postgres", "postgresql+psycopg2"))

    mongo_url = _env_get("MONGO_URL", None, dotenv_values)
    if mongo_url:
        _validate_url_scheme(mongo_url, ("mongodb", "mongodb+srv"))

    database = DatabaseSettings(primary_url=db_url, mongo_url=mongo_url)

    # Redis
    redis_url = _env_get("REDIS_URL", None, dotenv_values)
    if redis_url:
        _validate_url_scheme(redis_url, ("redis", "rediss"))
    redis_host = _env_get("REDIS_HOST", "localhost", dotenv_values) or "localhost"
    redis_port = _to_int(_env_get("REDIS_PORT", None, dotenv_values), 6379)
    redis_db = _to_int(_env_get("REDIS_DB", None, dotenv_values), 0)
    redis_settings = RedisSettings(url=redis_url, host=redis_host, port=redis_port, db=redis_db)

    # MQTT
    mqtt_host = _env_get("MQTT_HOST", "localhost", dotenv_values) or "localhost"
    mqtt_port = _to_int(_env_get("MQTT_PORT", None, dotenv_values), 1883)
    mqtt_user = _env_get("MQTT_USERNAME", None, dotenv_values)
    mqtt_pass = _env_get("MQTT_PASSWORD", None, dotenv_values)
    mqtt_tls = _to_bool(_env_get("MQTT_TLS", None, dotenv_values), default=False)
    mqtt_settings = MqttSettings(
        host=mqtt_host,
        port=mqtt_port,
        username=mqtt_user,
        password=mqtt_pass,
        use_tls=mqtt_tls,
    )

    # JWT
    jwt_secret = _env_get("JWT_SECRET", None, dotenv_values)
    if not jwt_secret:
        raise ConfigError("JWT_SECRET is required for token signing")
    jwt_algorithm = _env_get("JWT_ALGORITHM", "HS256", dotenv_values) or "HS256"
    access_minutes = _to_int(_env_get("JWT_ACCESS_MINUTES", None, dotenv_values), 15)
    refresh_minutes = _to_int(_env_get("JWT_REFRESH_MINUTES", None, dotenv_values), 24 * 60)
    jwt_settings = JwtSettings(
        secret=jwt_secret,
        algorithm=jwt_algorithm,
        access_token_minutes=access_minutes,
        refresh_token_minutes=refresh_minutes,
    )

    # Alert thresholds
    speed_limit = _to_float(_env_get("ALERT_SPEED_LIMIT_KPH", None, dotenv_values), 120.0)
    engine_temp_high = _to_float(_env_get("ALERT_ENGINE_TEMP_HIGH_C", None, dotenv_values), 110.0)
    fuel_theft_delta = _to_float(_env_get("ALERT_FUEL_THEFT_LITERS_DELTA", None, dotenv_values), 5.0)
    harsh_accel = _to_float(_env_get("ALERT_HARSH_ACCEL_G", None, dotenv_values), 0.35)
    hard_brake = _to_float(_env_get("ALERT_HARD_BRAKE_G", None, dotenv_values), 0.4)
    alerts = AlertThresholds(
        speed_limit_kph=speed_limit,
        engine_temp_high_c=engine_temp_high,
        fuel_theft_liters_delta=fuel_theft_delta,
        harsh_accel_g=harsh_accel,
        hard_brake_g=hard_brake,
    )

    # API rate limits
    rpm = _to_int(_env_get("API_RPM", None, dotenv_values), 120)
    burst = _to_int(_env_get("API_BURST", None, dotenv_values), 240)
    rate_limits = ApiRateLimits(requests_per_minute=rpm, burst=burst)

    return Settings(
        env=env,
        debug=debug,
        database=database,
        redis=redis_settings,
        mqtt=mqtt_settings,
        jwt=jwt_settings,
        alerts=alerts,
        rate_limits=rate_limits,
    )


# Eagerly load settings at import time to fail fast if configuration is invalid.
try:
    SETTINGS: Settings = load_settings()
except ConfigError as _config_error:
    # Re-raise with clear message while preserving original stack for debugging
    raise
