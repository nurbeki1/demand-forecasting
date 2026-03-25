import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Storage service for managing app data
/// Uses flutter_secure_storage for sensitive data (tokens)
/// Uses shared_preferences for regular data
class StorageService {
  static const _accessTokenKey = 'access_token';
  static const _refreshTokenKey = 'refresh_token';
  static const _userKey = 'user_data';
  static const _onboardingKey = 'has_seen_onboarding';
  static const _rememberMeKey = 'remember_me';
  static const _themeKey = 'theme_mode';
  static const _languageKey = 'language';

  static FlutterSecureStorage? _secureStorage;
  static SharedPreferences? _prefs;

  /// Initialize storage services
  static Future<void> init() async {
    _prefs = await SharedPreferences.getInstance();

    // Secure storage is not available on web and macOS (requires signing)
    // Only use on iOS and Android
    if (!kIsWeb &&
        defaultTargetPlatform != TargetPlatform.macOS &&
        defaultTargetPlatform != TargetPlatform.linux &&
        defaultTargetPlatform != TargetPlatform.windows) {
      _secureStorage = const FlutterSecureStorage(
        aOptions: AndroidOptions(
          encryptedSharedPreferences: true,
        ),
        iOptions: IOSOptions(
          accessibility: KeychainAccessibility.first_unlock,
        ),
      );
    }
  }

  /// Check if secure storage is available
  static bool get _useSecureStorage => _secureStorage != null;

  // ============== SECURE STORAGE (TOKENS) ==============

  /// Save access and refresh tokens
  static Future<void> saveTokens({
    required String accessToken,
    String? refreshToken,
  }) async {
    if (_useSecureStorage) {
      await _secureStorage?.write(key: _accessTokenKey, value: accessToken);
      if (refreshToken != null) {
        await _secureStorage?.write(key: _refreshTokenKey, value: refreshToken);
      }
    } else {
      // Fallback to shared preferences (less secure but works on all platforms)
      await _prefs?.setString(_accessTokenKey, accessToken);
      if (refreshToken != null) {
        await _prefs?.setString(_refreshTokenKey, refreshToken);
      }
    }
  }

  /// Get access token
  static Future<String?> getAccessToken() async {
    if (_useSecureStorage) {
      return await _secureStorage?.read(key: _accessTokenKey);
    }
    return _prefs?.getString(_accessTokenKey);
  }

  /// Get refresh token
  static Future<String?> getRefreshToken() async {
    if (_useSecureStorage) {
      return await _secureStorage?.read(key: _refreshTokenKey);
    }
    return _prefs?.getString(_refreshTokenKey);
  }

  /// Clear all tokens
  static Future<void> clearTokens() async {
    if (_useSecureStorage) {
      await _secureStorage?.delete(key: _accessTokenKey);
      await _secureStorage?.delete(key: _refreshTokenKey);
    } else {
      await _prefs?.remove(_accessTokenKey);
      await _prefs?.remove(_refreshTokenKey);
    }
  }

  /// Check if user is logged in
  static Future<bool> isLoggedIn() async {
    final token = await getAccessToken();
    return token != null && token.isNotEmpty;
  }

  // ============== USER DATA ==============

  /// Save user data
  static Future<void> saveUserData(Map<String, dynamic> userData) async {
    await _prefs?.setString(_userKey, jsonEncode(userData));
  }

  /// Get user data
  static Map<String, dynamic>? getUserData() {
    final data = _prefs?.getString(_userKey);
    if (data != null) {
      return jsonDecode(data) as Map<String, dynamic>;
    }
    return null;
  }

  /// Clear user data
  static Future<void> clearUserData() async {
    await _prefs?.remove(_userKey);
  }

  // ============== APP SETTINGS ==============

  /// Save onboarding status
  static Future<void> setHasSeenOnboarding(bool hasSeen) async {
    await _prefs?.setBool(_onboardingKey, hasSeen);
  }

  /// Check if user has seen onboarding
  static bool hasSeenOnboarding() {
    return _prefs?.getBool(_onboardingKey) ?? false;
  }

  /// Save remember me preference
  static Future<void> setRememberMe(bool remember) async {
    await _prefs?.setBool(_rememberMeKey, remember);
  }

  /// Get remember me preference
  static bool getRememberMe() {
    return _prefs?.getBool(_rememberMeKey) ?? false;
  }

  /// Save theme mode (0 = system, 1 = light, 2 = dark)
  static Future<void> setThemeMode(int mode) async {
    await _prefs?.setInt(_themeKey, mode);
  }

  /// Get theme mode
  static int getThemeMode() {
    return _prefs?.getInt(_themeKey) ?? 0;
  }

  /// Save language code
  static Future<void> setLanguage(String languageCode) async {
    await _prefs?.setString(_languageKey, languageCode);
  }

  /// Get language code
  static String getLanguage() {
    return _prefs?.getString(_languageKey) ?? 'en';
  }

  // ============== GENERIC METHODS ==============

  /// Save string value
  static Future<void> setString(String key, String value) async {
    await _prefs?.setString(key, value);
  }

  /// Get string value
  static String? getString(String key) {
    return _prefs?.getString(key);
  }

  /// Save int value
  static Future<void> setInt(String key, int value) async {
    await _prefs?.setInt(key, value);
  }

  /// Get int value
  static int? getInt(String key) {
    return _prefs?.getInt(key);
  }

  /// Save bool value
  static Future<void> setBool(String key, bool value) async {
    await _prefs?.setBool(key, value);
  }

  /// Get bool value
  static bool? getBool(String key) {
    return _prefs?.getBool(key);
  }

  /// Remove a key
  static Future<void> remove(String key) async {
    await _prefs?.remove(key);
  }

  /// Clear all data (logout)
  static Future<void> clearAll() async {
    await clearTokens();
    await clearUserData();

    // Keep some settings
    final themeMode = getThemeMode();
    final language = getLanguage();
    final hasSeenOnboarding = StorageService.hasSeenOnboarding();

    await _prefs?.clear();

    // Restore settings
    await setThemeMode(themeMode);
    await setLanguage(language);
    await setHasSeenOnboarding(hasSeenOnboarding);
  }
}
