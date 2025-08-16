
from app.integrations.config.config_integration import ConfigIntegration
from app.integrations.config.config_schema import ConfigRequest


config: ConfigRequest = ConfigIntegration().load()