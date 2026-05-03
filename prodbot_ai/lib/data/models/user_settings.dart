/// User settings model — mirrors the web `SettingsContext` defaults
/// (`frontend-admin/src/context/SettingsContext.jsx`) and the backend
/// `/settings` schema (`back/app/settings_routes.py`).
class UserSettings {
  final ProfileSettings profile;
  final ForecastSettings forecast;
  final ChatSettings chat;
  final TrustSettings trust;
  final UiSettings ui;
  final NotificationSettings notifications;

  const UserSettings({
    required this.profile,
    required this.forecast,
    required this.chat,
    required this.trust,
    required this.ui,
    required this.notifications,
  });

  factory UserSettings.defaults() => const UserSettings(
        profile: ProfileSettings(),
        forecast: ForecastSettings(),
        chat: ChatSettings(),
        trust: TrustSettings(),
        ui: UiSettings(),
        notifications: NotificationSettings(),
      );

  factory UserSettings.fromJson(Map<String, dynamic> json) {
    final defaults = UserSettings.defaults();
    return UserSettings(
      profile: ProfileSettings.fromJson(
        (json['profile'] as Map?)?.cast<String, dynamic>(),
      ) ??
          defaults.profile,
      forecast: ForecastSettings.fromJson(
        (json['forecast'] as Map?)?.cast<String, dynamic>(),
      ) ??
          defaults.forecast,
      chat: ChatSettings.fromJson(
        (json['chat'] as Map?)?.cast<String, dynamic>(),
      ) ??
          defaults.chat,
      trust: TrustSettings.fromJson(
        (json['trust'] as Map?)?.cast<String, dynamic>(),
      ) ??
          defaults.trust,
      ui: UiSettings.fromJson(
        (json['ui'] as Map?)?.cast<String, dynamic>(),
      ) ??
          defaults.ui,
      notifications: NotificationSettings.fromJson(
        (json['notifications'] as Map?)?.cast<String, dynamic>(),
      ) ??
          defaults.notifications,
    );
  }

  Map<String, dynamic> toJson() => {
        'profile': profile.toJson(),
        'forecast': forecast.toJson(),
        'chat': chat.toJson(),
        'trust': trust.toJson(),
        'ui': ui.toJson(),
        'notifications': notifications.toJson(),
      };

  UserSettings copyWith({
    ProfileSettings? profile,
    ForecastSettings? forecast,
    ChatSettings? chat,
    TrustSettings? trust,
    UiSettings? ui,
    NotificationSettings? notifications,
  }) =>
      UserSettings(
        profile: profile ?? this.profile,
        forecast: forecast ?? this.forecast,
        chat: chat ?? this.chat,
        trust: trust ?? this.trust,
        ui: ui ?? this.ui,
        notifications: notifications ?? this.notifications,
      );
}

class ProfileSettings {
  final String fullName;
  final String email;
  final String language; // kk | ru | en

  const ProfileSettings({
    this.fullName = '',
    this.email = '',
    this.language = 'kk',
  });

  static ProfileSettings? fromJson(Map<String, dynamic>? json) {
    if (json == null) return null;
    return ProfileSettings(
      fullName: json['fullName'] as String? ?? '',
      email: json['email'] as String? ?? '',
      language: json['language'] as String? ?? 'kk',
    );
  }

  Map<String, dynamic> toJson() => {
        'fullName': fullName,
        'email': email,
        'language': language,
      };

  ProfileSettings copyWith({String? fullName, String? email, String? language}) =>
      ProfileSettings(
        fullName: fullName ?? this.fullName,
        email: email ?? this.email,
        language: language ?? this.language,
      );
}

class ForecastSettings {
  final int defaultHorizon; // 7 | 14 | 30
  final bool showConfidence;
  final bool showExplanation;
  final String? dataFreshness;
  final String modelType; // linear | randomforest | auto

  const ForecastSettings({
    this.defaultHorizon = 7,
    this.showConfidence = true,
    this.showExplanation = true,
    this.dataFreshness,
    this.modelType = 'auto',
  });

  static ForecastSettings? fromJson(Map<String, dynamic>? json) {
    if (json == null) return null;
    return ForecastSettings(
      defaultHorizon: (json['defaultHorizon'] as num?)?.toInt() ?? 7,
      showConfidence: json['showConfidence'] as bool? ?? true,
      showExplanation: json['showExplanation'] as bool? ?? true,
      dataFreshness: json['dataFreshness'] as String?,
      modelType: json['modelType'] as String? ?? 'auto',
    );
  }

  Map<String, dynamic> toJson() => {
        'defaultHorizon': defaultHorizon,
        'showConfidence': showConfidence,
        'showExplanation': showExplanation,
        'dataFreshness': dataFreshness,
        'modelType': modelType,
      };

  ForecastSettings copyWith({
    int? defaultHorizon,
    bool? showConfidence,
    bool? showExplanation,
    String? dataFreshness,
    String? modelType,
  }) =>
      ForecastSettings(
        defaultHorizon: defaultHorizon ?? this.defaultHorizon,
        showConfidence: showConfidence ?? this.showConfidence,
        showExplanation: showExplanation ?? this.showExplanation,
        dataFreshness: dataFreshness ?? this.dataFreshness,
        modelType: modelType ?? this.modelType,
      );
}

class ChatSettings {
  final String responseStyle; // short | detailed | analytical
  final bool showSuggestions;
  final bool proactiveInsights;

  const ChatSettings({
    this.responseStyle = 'analytical',
    this.showSuggestions = true,
    this.proactiveInsights = true,
  });

  static ChatSettings? fromJson(Map<String, dynamic>? json) {
    if (json == null) return null;
    return ChatSettings(
      responseStyle: json['responseStyle'] as String? ?? 'analytical',
      showSuggestions: json['showSuggestions'] as bool? ?? true,
      proactiveInsights: json['proactiveInsights'] as bool? ?? true,
    );
  }

  Map<String, dynamic> toJson() => {
        'responseStyle': responseStyle,
        'showSuggestions': showSuggestions,
        'proactiveInsights': proactiveInsights,
      };

  ChatSettings copyWith({
    String? responseStyle,
    bool? showSuggestions,
    bool? proactiveInsights,
  }) =>
      ChatSettings(
        responseStyle: responseStyle ?? this.responseStyle,
        showSuggestions: showSuggestions ?? this.showSuggestions,
        proactiveInsights: proactiveInsights ?? this.proactiveInsights,
      );
}

class TrustSettings {
  final bool showConfidenceLevel;
  final bool showExplanations;
  final bool showDataSources;

  const TrustSettings({
    this.showConfidenceLevel = true,
    this.showExplanations = true,
    this.showDataSources = true,
  });

  static TrustSettings? fromJson(Map<String, dynamic>? json) {
    if (json == null) return null;
    return TrustSettings(
      showConfidenceLevel: json['showConfidenceLevel'] as bool? ?? true,
      showExplanations: json['showExplanations'] as bool? ?? true,
      showDataSources: json['showDataSources'] as bool? ?? true,
    );
  }

  Map<String, dynamic> toJson() => {
        'showConfidenceLevel': showConfidenceLevel,
        'showExplanations': showExplanations,
        'showDataSources': showDataSources,
      };
}

class UiSettings {
  final String theme; // dark | light | auto
  final bool compactMode;
  final bool animations;

  const UiSettings({
    this.theme = 'dark',
    this.compactMode = false,
    this.animations = true,
  });

  static UiSettings? fromJson(Map<String, dynamic>? json) {
    if (json == null) return null;
    return UiSettings(
      theme: json['theme'] as String? ?? 'dark',
      compactMode: json['compactMode'] as bool? ?? false,
      animations: json['animations'] as bool? ?? true,
    );
  }

  Map<String, dynamic> toJson() => {
        'theme': theme,
        'compactMode': compactMode,
        'animations': animations,
      };

  UiSettings copyWith({String? theme, bool? compactMode, bool? animations}) =>
      UiSettings(
        theme: theme ?? this.theme,
        compactMode: compactMode ?? this.compactMode,
        animations: animations ?? this.animations,
      );
}

class NotificationSettings {
  final bool demandIncrease;
  final bool demandDecrease;
  final bool forecastChange;
  final bool emailNotifications;

  const NotificationSettings({
    this.demandIncrease = true,
    this.demandDecrease = true,
    this.forecastChange = true,
    this.emailNotifications = false,
  });

  static NotificationSettings? fromJson(Map<String, dynamic>? json) {
    if (json == null) return null;
    return NotificationSettings(
      demandIncrease: json['demandIncrease'] as bool? ?? true,
      demandDecrease: json['demandDecrease'] as bool? ?? true,
      forecastChange: json['forecastChange'] as bool? ?? true,
      emailNotifications: json['emailNotifications'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() => {
        'demandIncrease': demandIncrease,
        'demandDecrease': demandDecrease,
        'forecastChange': forecastChange,
        'emailNotifications': emailNotifications,
      };
}
