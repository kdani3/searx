from searx import user_settings
from searx.testing import SearxTestCase


class TestUserSettingsBase(SearxTestCase):
    def test_newly_constructed_settings_object_is_empty(self):
        settings = user_settings.UserSettingsBase()
        self.assertTrue(settings.empty())

    def test_getting_unset_setting_raises_exception(self):
        settings = user_settings.UserSettingsBase()
        with self.assertRaises(user_settings.UnknownSetting):
            settings.get("language")

    def test_get_the_same_value_as_set(self):
        settings = user_settings.UserSettingsBase()
        settings.set("language", "en")
        self.assertEqual("en", settings.get("language"))

    def test_two_settings_are_restorable(self):
        settings = user_settings.UserSettingsBase()
        settings.set("language", "en")
        settings.set("name", "John Doe")
        self.assertEqual("en", settings.get("language"))
        self.assertEqual("John Doe", settings.get("name"))

    def test_single_validator(self):
        class MyUserSettings(user_settings.UserSettingsBase):
            def validate_age(self, value):
                return 0 <= value <= 99

        with self.assertRaises(Exception):
            settings = MyUserSettings()
            settings.set("age", -1)

        with self.assertRaises(Exception):
            settings = MyUserSettings()
            settings.set("age", "1")

        with self.assertRaises(Exception):
            settings = MyUserSettings()
            settings.set("age", 9000)

        settings = MyUserSettings()
        settings.set("age", 9)

    def test_multiple_validators(self):
        class MyUserSettings(user_settings.UserSettingsBase):
            def validate_age(self, value):
                return 0 <= value <= 99

            def validate_name(self, value):
                return 1 <= len(value) <= 100

        settings = MyUserSettings()
        settings.set("age", 9)
        settings.set("name", "John Doe")

        with self.assertRaises(Exception):
            settings.set("name", 5)

    def test_proper_invalid_setting_exception_class(self):
        class MyUserSettings(user_settings.UserSettingsBase):
            def validate_name(self, value):
                return 1 <= len(value) <= 100

        settings = MyUserSettings()
        with self.assertRaises(user_settings.InvalidSetting):
            settings.set("name", 5)

        with self.assertRaises(user_settings.TypeErrorInvalidSetting):
            settings.set("name", 5)

    def test_value_error_proper_exception_raised(self):
        class MyUserSettings(user_settings.UserSettingsBase):
            def validate_name(self, value):
                return 1 <= len(value) <= 100

        settings = MyUserSettings()
        with self.assertRaises(user_settings.InvalidSetting):
            settings.set("name", "")

        with self.assertRaises(user_settings.ValueErrorInvalidSetting):
            settings.set("name", "")

    def test_after_value_is_set_should_not_be_empty(self):
        settings = user_settings.UserSettingsBase()
        settings.set("foo", "bar")
        self.assertFalse(settings.empty())

    def test_restore_empty_cookies_should_be_empty(self):
        settings = user_settings.UserSettingsBase()
        settings.restore_from_cookies({})
        self.assertTrue(settings.empty())

    def test_restore_non_empty_cookies_should_not_be_empty(self):
        settings = user_settings.UserSettingsBase()
        settings.restore_from_cookies({"foo": "bar"})
        self.assertFalse(settings.empty())

    def test_export_settings_then_restore_the_same_string(self):
        to_export_from = user_settings.UserSettingsBase()
        to_export_from.set("name", "John Doe")
        cookies = {}
        to_export_from.save_to_cookies(cookies)
        to_import_to = user_settings.UserSettingsBase()
        to_import_to.restore_from_cookies(cookies)
        self.assertEqual(to_import_to.get("name"), "John Doe")

    def test_export_various_values_and_restore_them(self):
        class MyUserSettings(user_settings.UserSettingsBase):
            def deserialize_age(self, value):
                return int(value)

            def serialize_owns(self, value):
                return ','.join(value)

            def deserialize_owns(self, value):
                return set(value.split(','))

        to_export_from = MyUserSettings()
        to_export_from.set("name", "John Doe")
        to_export_from.set("age", 32)
        to_export_from.set("owns", {"foo", "bar", })
        cookies = {}
        to_export_from.save_to_cookies(cookies)
        to_import_to = MyUserSettings()
        to_import_to.restore_from_cookies(cookies)
        self.assertEqual(to_import_to.get("name"), "John Doe")
        self.assertEqual(to_import_to.get("age"), 32)
        self.assertEqual(to_import_to.get("owns"), {"foo", "bar", })

    def test_save_to_cookies_should_only_use_strings(self):
        to_export_from = user_settings.UserSettingsBase()
        to_export_from.set("name", "John Doe")
        to_export_from.set("age", 32)
        to_export_from.set("owns", {"foo", "bar", })
        cookies = {}
        to_export_from.save_to_cookies(cookies)
        for value in cookies.values():
            self.assertIsInstance(value, str)


class TestUserSettings(SearxTestCase):
    def setUp(self):
        self._settings = user_settings.UserSettings()

    def test_method(self):
        self._settings.set("method", "POST")
        self._settings.set("method", "GET")

        with self.assertRaises(user_settings.InvalidSetting):
            self._settings.set("method", "SET")
        with self.assertRaises(user_settings.InvalidSetting):
            self._settings.set("method", 3.14)

    def test_locale(self):
        self._settings.set("locale", "en")
        with self.assertRaises(user_settings.InvalidSetting):
            self._settings.set("locale", "English")
        with self.assertRaises(user_settings.InvalidSetting):
            self._settings.set("locale", 55)
        with self.assertRaises(user_settings.InvalidSetting):
            self._settings.set("locale", None)

    def test_language(self):
        self._settings.set("language", "en_US")
        with self.assertRaises(user_settings.InvalidSetting):
            self._settings.set("language", "English")
        with self.assertRaises(user_settings.InvalidSetting):
            self._settings.set("language", 55)
        with self.assertRaises(user_settings.InvalidSetting):
            self._settings.set("language", None)

    def test_blocked_engines(self):
        self._settings.set("blocked_engines", set())
        self._settings.set("blocked_engines", {"google__general", })
        self._settings.set("blocked_engines", {"google__general", "bing_general", })
        with self.assertRaises(user_settings.InvalidSetting):
            self._settings.set("blocked_engines", "google__general")
