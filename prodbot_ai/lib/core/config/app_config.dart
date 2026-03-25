import 'package:flutter/foundation.dart';

/// Application configuration
/// Centralizes all environment-specific settings
class AppConfig {
  AppConfig._();

  // ============== ENVIRONMENT ==============
  static const bool isProduction = bool.fromEnvironment(
    'dart.vm.product',
    defaultValue: false,
  );

  static const bool isDevelopment = !isProduction;

  // ============== API CONFIGURATION ==============
  /// Base URL for API requests
  static String get apiBaseUrl {
    // Check for custom URL from environment
    const customUrl = String.fromEnvironment('API_URL');
    if (customUrl.isNotEmpty) return customUrl;

    // Default URLs based on platform
    if (kIsWeb) return "http://127.0.0.1:8000";

    // Android emulator uses 10.0.2.2 to reach host's localhost
    // iOS simulator uses 127.0.0.1
    return defaultTargetPlatform == TargetPlatform.android
        ? "http://10.0.2.2:8000"
        : "http://127.0.0.1:8000";
  }

  /// API timeout in seconds
  static const int apiTimeoutSeconds = 30;

  // ============== TEST ACCOUNT (Development Only) ==============
  /// Test account is only available in development mode
  static bool get hasTestAccount => isDevelopment;

  static const String testEmail = String.fromEnvironment(
    'TEST_EMAIL',
    defaultValue: 'testuser@prodbot.kz',
  );

  static const String testPassword = String.fromEnvironment(
    'TEST_PASSWORD',
    defaultValue: 'nuraima',
  );

  static const String testToken = 'test_token_prodbot_ai_2024';
  static const String testUserId = 'test_user_001';

  // ============== FEATURE FLAGS ==============
  static const bool enableAnalytics = bool.fromEnvironment(
    'ENABLE_ANALYTICS',
    defaultValue: false,
  );

  static const bool enableCrashReporting = bool.fromEnvironment(
    'ENABLE_CRASH_REPORTING',
    defaultValue: false,
  );

  // ============== APP INFO ==============
  static const String appName = 'ProdBot AI';
  static const String appVersion = '1.0.0';

  /// Print current configuration (for debugging)
  static void printConfig() {
    if (isDevelopment) {
      debugPrint('=== App Configuration ===');
      debugPrint('Environment: ${isProduction ? "Production" : "Development"}');
      debugPrint('API URL: $apiBaseUrl');
      debugPrint('Test Account: ${hasTestAccount ? "Enabled" : "Disabled"}');
      debugPrint('========================');
    }
  }
}