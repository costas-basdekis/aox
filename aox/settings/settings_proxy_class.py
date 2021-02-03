from typing import Optional

from aox.settings.settings_class import Settings


__all__ = ['UninitialisedSettingsError', 'SettingsProxy', 'settings_proxy']


class UninitialisedSettingsError(Exception):
    """
    Error signifying that the settings were trying to be accessed before they
    were initialised.
    """

    DEFAULT_MESSAGE = "The settings have not been initialised yet"

    def __init__(self, message=DEFAULT_MESSAGE, *args):
        super().__init__(message, *args)


class SettingsProxy:
    """A proxy to safely access the current active settings instance"""
    settings: Optional['Settings'] = None
    """The actual settings instance"""

    def __call__(self, raise_if_missing: bool = True) -> Optional['Settings']:
        """Shortcut for `SettingsProxy.get`"""
        return self.get(raise_if_missing)

    def get(self, raise_if_missing: bool = True) -> Optional['Settings']:
        """Get the current (initialised or not) settings"""
        if raise_if_missing and self.settings is None:
            raise UninitialisedSettingsError()
        return self.settings

    def ensure_default(self) -> Optional['Settings']:
        """Set the default settings, if not initialised yet"""
        if self.has():
            return
        return self.set_default()

    def set_default(self) -> Optional['Settings']:
        """Update the settings instance to the one gotten by default"""
        return self.set(Settings.from_default())

    def set(self, new_settings: Optional['Settings']) -> Optional['Settings']:
        """Update the settings instance to custom one"""
        self.settings = new_settings

        return self.settings

    def has(self) -> bool:
        """Check whether settings have been initialised"""
        return self.settings is not None


settings_proxy = SettingsProxy()
