import secrets
from pathlib import Path
from typing import Any, Dict, Optional, Union

from hydra import compose, initialize_config_dir
from omegaconf import DictConfig
from pydantic import BaseModel, BaseSettings, EmailStr, validator
from pydantic.env_settings import SettingsSourceCallable

_config_file_path = Path(__file__)
proj_dir = _config_file_path.parent.parent.parent


def hydra_config_settings_source(settings: BaseSettings) -> Dict[str, Any]:  # noqa
    # https://docs.pydantic.dev/usage/settings/#adding-sources
    config_dir, config_name = str(proj_dir), "config.yaml"
    try:
        initialize_config_dir(version_base=None, config_dir=config_dir)
        _cfg = compose(config_name)
        return dictconfig_to_pydict(_cfg)
    except Exception as exc:
        raise ValueError(
            f"initialize config fail. {config_dir = }; {config_name = }"
        ) from exc


def dictconfig_to_pydict(cfg) -> dict:
    """convert omegaconf.DictConfig to python build-in dict

    If initialized Settings with hydra and
    BaseSetting#changing-priority(env_settings > init_settings ...),
    there is bug when partial override config by environ variable.
    Convert dictconfig to python build-in dict to fix it.
    """
    if not isinstance(cfg, DictConfig):
        return cfg
    return {k: dictconfig_to_pydict(v) for k, v in cfg.items()}


class DBConf(BaseModel):
    driver: str
    host: str
    port: int
    database: str
    username: Optional[str] = None
    password: Optional[str] = None

    @property
    def uri(self) -> str:
        auth = f"{self.username}:{self.password}@" if self.username else ""
        return f"{self.driver}://{auth}{self.host}:{self.port}/{self.database}"


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, list[str]]) -> Union[list[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    PROJECT_NAME: str
    # SERVER_NAME: str
    # SERVER_HOST: AnyHttpUrl
    db: DBConf

    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None

    @validator("EMAILS_FROM_NAME")
    def get_project_name(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if not v:
            return values["PROJECT_NAME"]
        return v

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_TEMPLATES_DIR: str = "/app/app/email-templates/build"
    EMAILS_ENABLED: bool = False

    @validator("EMAILS_ENABLED", pre=True)
    def get_emails_enabled(cls, v: bool, values: Dict[str, Any]) -> bool:
        return bool(
            values.get("SMTP_HOST")
            and values.get("SMTP_PORT")
            and values.get("EMAILS_FROM_EMAIL")
        )

    EMAIL_TEST_USER: EmailStr = "test@example.com"  # type: ignore
    FIRST_SUPERUSER: EmailStr
    FIRST_SUPERUSER_PASSWORD: str
    USERS_OPEN_REGISTRATION: bool = False

    class Config:
        case_sensitive = True
        frozen = True
        env_nested_delimiter = "__"

        env_file = ".env"
        env_file_encoding = "utf-8"

        # https://pydantic-docs.helpmanual.io/usage/settings/#changing-priority
        # env settings > init settings > ...
        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> tuple[SettingsSourceCallable, ...]:
            return (
                env_settings,
                init_settings,
                hydra_config_settings_source,
                file_secret_settings,
            )


settings = Settings()


if __name__ == "__main__":
    from icecream import ic

    ic(proj_dir)
    ic(settings)
