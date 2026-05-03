import 'package:flutter/foundation.dart';

import '../data/models/user_settings.dart';
import 'settings_service.dart';

/// State holder around [SettingsService] that mirrors the web
/// `SettingsContext` (`frontend-admin/src/context/SettingsContext.jsx`):
/// - optimistic UI updates, then persists via PATCH
/// - exposes the full [UserSettings] tree for `Consumer` widgets.
class SettingsProvider extends ChangeNotifier {
  SettingsProvider({SettingsService? service})
      : _service = service ?? SettingsService(),
        _settings = UserSettings.defaults();

  final SettingsService _service;

  UserSettings _settings;
  bool _loading = false;
  bool _saving = false;
  String? _error;

  UserSettings get settings => _settings;
  bool get loading => _loading;
  bool get saving => _saving;
  String? get error => _error;

  /// Hydrate from local cache instantly, then refresh from API.
  Future<void> init() async {
    _settings = _service.getCached();
    notifyListeners();
    await refresh();
  }

  Future<void> refresh() async {
    _loading = true;
    _error = null;
    notifyListeners();
    try {
      _settings = await _service.getSettings();
    } catch (e) {
      _error = e.toString();
    } finally {
      _loading = false;
      notifyListeners();
    }
  }

  /// Optimistically applies [updater] to current settings, then persists
  /// via PATCH `/settings/{section}` with the changed [values].
  Future<void> _patchSection({
    required String section,
    required Map<String, dynamic> values,
    required UserSettings Function(UserSettings) updater,
  }) async {
    final previous = _settings;
    _settings = updater(_settings);
    _saving = true;
    _error = null;
    notifyListeners();
    try {
      _settings = await _service.updateSection(section, values);
    } catch (e) {
      _settings = previous;
      _error = e.toString();
    } finally {
      _saving = false;
      notifyListeners();
    }
  }

  Future<void> updateProfile({
    String? fullName,
    String? language,
  }) {
    final values = <String, dynamic>{};
    if (fullName != null) values['fullName'] = fullName;
    if (language != null) values['language'] = language;
    return _patchSection(
      section: 'profile',
      values: values,
      updater: (s) => s.copyWith(
        profile: s.profile.copyWith(
          fullName: fullName ?? s.profile.fullName,
          language: language ?? s.profile.language,
        ),
      ),
    );
  }

  Future<void> updateForecast({
    int? defaultHorizon,
    bool? showConfidence,
    bool? showExplanation,
    String? modelType,
  }) {
    final values = <String, dynamic>{};
    if (defaultHorizon != null) values['defaultHorizon'] = defaultHorizon;
    if (showConfidence != null) values['showConfidence'] = showConfidence;
    if (showExplanation != null) values['showExplanation'] = showExplanation;
    if (modelType != null) values['modelType'] = modelType;
    return _patchSection(
      section: 'forecast',
      values: values,
      updater: (s) => s.copyWith(
        forecast: s.forecast.copyWith(
          defaultHorizon: defaultHorizon ?? s.forecast.defaultHorizon,
          showConfidence: showConfidence ?? s.forecast.showConfidence,
          showExplanation: showExplanation ?? s.forecast.showExplanation,
          modelType: modelType ?? s.forecast.modelType,
        ),
      ),
    );
  }

  Future<void> updateChat({
    String? responseStyle,
    bool? showSuggestions,
    bool? proactiveInsights,
  }) {
    final values = <String, dynamic>{};
    if (responseStyle != null) values['responseStyle'] = responseStyle;
    if (showSuggestions != null) values['showSuggestions'] = showSuggestions;
    if (proactiveInsights != null) {
      values['proactiveInsights'] = proactiveInsights;
    }
    return _patchSection(
      section: 'chat',
      values: values,
      updater: (s) => s.copyWith(
        chat: s.chat.copyWith(
          responseStyle: responseStyle ?? s.chat.responseStyle,
          showSuggestions: showSuggestions ?? s.chat.showSuggestions,
          proactiveInsights: proactiveInsights ?? s.chat.proactiveInsights,
        ),
      ),
    );
  }

  Future<void> updateUi({
    String? theme,
    bool? compactMode,
    bool? animations,
  }) {
    final values = <String, dynamic>{};
    if (theme != null) values['theme'] = theme;
    if (compactMode != null) values['compactMode'] = compactMode;
    if (animations != null) values['animations'] = animations;
    return _patchSection(
      section: 'ui',
      values: values,
      updater: (s) => s.copyWith(
        ui: s.ui.copyWith(
          theme: theme ?? s.ui.theme,
          compactMode: compactMode ?? s.ui.compactMode,
          animations: animations ?? s.ui.animations,
        ),
      ),
    );
  }

  Future<void> updateNotifications({
    bool? demandIncrease,
    bool? demandDecrease,
    bool? forecastChange,
    bool? emailNotifications,
  }) {
    final values = <String, dynamic>{};
    if (demandIncrease != null) values['demandIncrease'] = demandIncrease;
    if (demandDecrease != null) values['demandDecrease'] = demandDecrease;
    if (forecastChange != null) values['forecastChange'] = forecastChange;
    if (emailNotifications != null) {
      values['emailNotifications'] = emailNotifications;
    }
    return _patchSection(
      section: 'notifications',
      values: values,
      updater: (s) {
        final n = s.notifications;
        return s.copyWith(
          notifications: NotificationSettings(
            demandIncrease: demandIncrease ?? n.demandIncrease,
            demandDecrease: demandDecrease ?? n.demandDecrease,
            forecastChange: forecastChange ?? n.forecastChange,
            emailNotifications: emailNotifications ?? n.emailNotifications,
          ),
        );
      },
    );
  }

  Future<void> resetToDefaults() async {
    _saving = true;
    _error = null;
    notifyListeners();
    try {
      _settings = await _service.resetSettings();
    } catch (e) {
      _error = e.toString();
    } finally {
      _saving = false;
      notifyListeners();
    }
  }
}
