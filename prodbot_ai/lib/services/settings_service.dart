import 'dart:convert';

import '../data/models/user_settings.dart';
import 'api/api_client.dart';
import 'storage_service.dart';

/// Service that talks to the backend `/settings` endpoints.
///
/// Mirrors the web `frontend-admin/src/api/settingsApi.js` and the
/// FastAPI router in `back/app/settings_routes.py`.
///
/// Local cache via [StorageService] gives offline-first reads —
/// the UI shows cached values immediately and reconciles on response.
class SettingsService {
  final ApiClient _apiClient;

  SettingsService({ApiClient? apiClient})
      : _apiClient = apiClient ?? ApiClient();

  static const _cacheKey = 'user_settings_cache_v1';

  Future<UserSettings> getSettings() async {
    final response = await _apiClient.get<Map<String, dynamic>>('/settings');
    final settings = UserSettings.fromJson(response);
    await _cache(settings);
    return settings;
  }

  /// Reads cached settings (no network). Returns defaults if none.
  UserSettings getCached() {
    final raw = StorageService.getString(_cacheKey);
    if (raw == null || raw.isEmpty) return UserSettings.defaults();
    try {
      final json = jsonDecode(raw) as Map<String, dynamic>;
      return UserSettings.fromJson(json);
    } catch (_) {
      return UserSettings.defaults();
    }
  }

  /// PATCH `/settings/{section}` — partial update of a single section.
  Future<UserSettings> updateSection(
    String section,
    Map<String, dynamic> values,
  ) async {
    final response = await _apiClient.patch<Map<String, dynamic>>(
      '/settings/$section',
      data: {'values': values},
    );
    final settings = UserSettings.fromJson(response);
    await _cache(settings);
    return settings;
  }

  Future<UserSettings> resetSettings() async {
    await _apiClient.delete<Map<String, dynamic>>('/settings');
    final defaults = UserSettings.defaults();
    await _cache(defaults);
    return defaults;
  }

  Future<void> _cache(UserSettings s) =>
      StorageService.setString(_cacheKey, jsonEncode(s.toJson()));
}
