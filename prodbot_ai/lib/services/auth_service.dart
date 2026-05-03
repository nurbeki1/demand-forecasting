import 'package:flutter/foundation.dart';
import 'api/api_client.dart';
import 'api/api_exception.dart';
import 'storage_service.dart';
import '../core/config/app_config.dart';
import '../data/models/current_user.dart';

/// Authentication result model
class AuthResult {
  final bool success;
  final String? accessToken;
  final String? refreshToken;
  final String? userId;
  final String? email;
  final String? error;

  const AuthResult({
    required this.success,
    this.accessToken,
    this.refreshToken,
    this.userId,
    this.email,
    this.error,
  });

  factory AuthResult.success({
    required String accessToken,
    String? refreshToken,
    String? userId,
    String? email,
  }) {
    return AuthResult(
      success: true,
      accessToken: accessToken,
      refreshToken: refreshToken,
      userId: userId,
      email: email,
    );
  }

  factory AuthResult.failure(String error) {
    return AuthResult(success: false, error: error);
  }
}

/// Auth Service with proper error handling and token management
class AuthService extends ChangeNotifier {
  final ApiClient _apiClient = ApiClient();

  bool _isLoading = false;
  bool _isAuthenticated = false;
  CurrentUser? _profile;
  String? _currentUserEmail;
  String? _currentUserId;
  String? _error;

  bool get isLoading => _isLoading;
  bool get isAuthenticated => _isAuthenticated;
  CurrentUser? get profile => _profile;
  String? get currentUserEmail => _currentUserEmail;
  String? get currentUserId => _currentUserId;
  String? get error => _error;

  /// Mirrors ML model access rules on the backend (`subscription_plan` only).
  bool get canUsePremiumMlModels => _profile?.canUsePremiumMlModels ?? false;

  Future<void> refreshProfile() async {
    try {
      final json = await _apiClient.get<Map<String, dynamic>>('/auth/me');
      final u = CurrentUser.fromJson(json);
      _profile = u;
      _currentUserEmail = u.email;
      _currentUserId = u.id.toString();
      await StorageService.saveUserData(u.toStorageMap());
      notifyListeners();
    } catch (e) {
      debugPrint('refreshProfile: $e');
    }
  }

  /// Initialize auth state from storage
  Future<void> init() async {
    _isLoading = true;
    notifyListeners();

    try {
      final token = await StorageService.getAccessToken();
      if (token != null && token.isNotEmpty) {
        _isAuthenticated = true;
        _apiClient.setAuthToken(token);

        final userData = StorageService.getUserData();
        if (userData != null && userData['email'] != null) {
          final u = CurrentUser.fromStored(userData);
          _profile = u;
          _currentUserEmail = u.email.isNotEmpty ? u.email : userData['email'] as String?;
          _currentUserId =
              u.id > 0 ? u.id.toString() : userData['id']?.toString();
        }
        await refreshProfile();
      }
    } catch (e) {
      debugPrint('Auth init error: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Login with email and password
  Future<AuthResult> login(String email, String password) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _apiClient.post<Map<String, dynamic>>(
        '/auth/login',
        data: {
          'email': email,
          'password': password,
        },
      );

      final accessToken = response['access_token'] as String;
      final refreshToken = response['refresh_token'] as String?;
      final userId = response['user_id']?.toString();

      await StorageService.saveTokens(
        accessToken: accessToken,
        refreshToken: refreshToken,
      );

      _isAuthenticated = true;
      _apiClient.setAuthToken(accessToken);
      await refreshProfile();

      if (_profile != null) {
        _currentUserEmail = _profile!.email;
        _currentUserId = _profile!.id.toString();
      } else {
        _currentUserEmail = email;
        _currentUserId = userId;
      }

      _isLoading = false;
      notifyListeners();

      return AuthResult.success(
        accessToken: accessToken,
        refreshToken: refreshToken,
        userId: _currentUserId,
        email: _currentUserEmail ?? email,
      );
    } on ApiException catch (e) {
      _error = e.userMessage;
      _isLoading = false;
      notifyListeners();
      return AuthResult.failure(e.userMessage);
    } catch (e) {
      _error = AppConfig.hasTestAccount
          ? 'Server unavailable. Use test account: ${AppConfig.testEmail}'
          : 'Server unavailable. Please try again later.';
      _isLoading = false;
      notifyListeners();
      return AuthResult.failure(_error!);
    }
  }

  /// Register new user
  Future<AuthResult> register(String email, String password, {String? name}) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      await _apiClient.post<Map<String, dynamic>>(
        '/auth/register',
        data: {
          'email': email,
          'password': password,
          if (name != null) 'name': name,
        },
      );

      return await login(email, password);
    } on ApiException catch (e) {
      _error = e.userMessage;
      _isLoading = false;
      notifyListeners();
      return AuthResult.failure(e.userMessage);
    } catch (e) {
      _error = 'Registration failed. Please try again.';
      _isLoading = false;
      notifyListeners();
      return AuthResult.failure(_error!);
    }
  }

  /// Logout user
  Future<void> logout() async {
    _isLoading = true;
    notifyListeners();

    try {
      try {
        await _apiClient.post('/auth/logout');
      } catch (_) {}

      await StorageService.clearTokens();
      await StorageService.clearUserData();
      _apiClient.clearAuthToken();

      _isAuthenticated = false;
      _profile = null;
      _currentUserEmail = null;
      _currentUserId = null;
      _error = null;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Request password reset
  Future<bool> requestPasswordReset(String email) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      await _apiClient.post(
        '/auth/forgot-password',
        data: {'email': email},
      );

      _isLoading = false;
      notifyListeners();
      return true;
    } on ApiException catch (e) {
      _error = e.userMessage;
      _isLoading = false;
      notifyListeners();
      return false;
    } catch (e) {
      _error = 'Failed to send reset email. Please try again.';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// Reset password with token
  Future<bool> resetPassword(String token, String newPassword) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      await _apiClient.post(
        '/auth/reset-password',
        data: {
          'token': token,
          'password': newPassword,
        },
      );

      _isLoading = false;
      notifyListeners();
      return true;
    } on ApiException catch (e) {
      _error = e.userMessage;
      _isLoading = false;
      notifyListeners();
      return false;
    } catch (e) {
      _error = 'Failed to reset password. Please try again.';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// Change password
  Future<bool> changePassword(String currentPassword, String newPassword) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      await _apiClient.post(
        '/auth/change-password',
        data: {
          'current_password': currentPassword,
          'new_password': newPassword,
        },
      );

      _isLoading = false;
      notifyListeners();
      return true;
    } on ApiException catch (e) {
      _error = e.userMessage;
      _isLoading = false;
      notifyListeners();
      return false;
    } catch (e) {
      _error = 'Failed to change password. Please try again.';
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  /// Clear error
  void clearError() {
    _error = null;
    notifyListeners();
  }
}
