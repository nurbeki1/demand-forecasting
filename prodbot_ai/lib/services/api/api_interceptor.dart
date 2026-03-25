import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../storage_service.dart';

/// Auth interceptor for adding token to requests
class AuthInterceptor extends Interceptor {
  @override
  void onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    // Get token from secure storage
    final token = await StorageService.getAccessToken();

    if (token != null && token.isNotEmpty) {
      options.headers['Authorization'] = 'Bearer $token';
    }

    handler.next(options);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    // Handle 401 errors - token expired
    if (err.response?.statusCode == 401) {
      // Try to refresh token
      final refreshed = await _refreshToken();

      if (refreshed) {
        // Retry the original request
        try {
          final token = await StorageService.getAccessToken();
          final options = err.requestOptions;
          options.headers['Authorization'] = 'Bearer $token';

          final response = await Dio().fetch(options);
          return handler.resolve(response);
        } catch (e) {
          // Refresh failed, continue with error
        }
      }

      // Clear tokens and force logout
      await StorageService.clearTokens();
    }

    handler.next(err);
  }

  Future<bool> _refreshToken() async {
    try {
      final refreshToken = await StorageService.getRefreshToken();
      if (refreshToken == null) return false;

      // Create a new Dio instance to avoid interceptor loop
      final dio = Dio();
      final response = await dio.post(
        '${_getBaseUrl()}/auth/refresh',
        data: {'refresh_token': refreshToken},
      );

      if (response.statusCode == 200) {
        final newAccessToken = response.data['access_token'];
        final newRefreshToken = response.data['refresh_token'];

        await StorageService.saveTokens(
          accessToken: newAccessToken,
          refreshToken: newRefreshToken,
        );

        return true;
      }
    } catch (e) {
      debugPrint('Token refresh failed: $e');
    }

    return false;
  }

  String _getBaseUrl() {
    if (kIsWeb) return "http://127.0.0.1:8000";
    return defaultTargetPlatform == TargetPlatform.android
        ? "http://10.0.2.2:8000"
        : "http://127.0.0.1:8000";
  }
}

/// Logging interceptor for debugging
class LoggingInterceptor extends Interceptor {
  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    if (kDebugMode) {
      debugPrint('=== REQUEST ===');
      debugPrint('URL: ${options.uri}');
      debugPrint('Method: ${options.method}');
      debugPrint('Headers: ${options.headers}');
      if (options.data != null) {
        debugPrint('Body: ${options.data}');
      }
      debugPrint('===============');
    }
    handler.next(options);
  }

  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    if (kDebugMode) {
      debugPrint('=== RESPONSE ===');
      debugPrint('URL: ${response.requestOptions.uri}');
      debugPrint('Status: ${response.statusCode}');
      debugPrint('Data: ${response.data}');
      debugPrint('================');
    }
    handler.next(response);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    if (kDebugMode) {
      debugPrint('=== ERROR ===');
      debugPrint('URL: ${err.requestOptions.uri}');
      debugPrint('Type: ${err.type}');
      debugPrint('Message: ${err.message}');
      if (err.response != null) {
        debugPrint('Status: ${err.response?.statusCode}');
        debugPrint('Data: ${err.response?.data}');
      }
      debugPrint('=============');
    }
    handler.next(err);
  }
}

/// Retry interceptor for handling network errors
class RetryInterceptor extends Interceptor {
  final int maxRetries;
  final Duration retryDelay;

  RetryInterceptor({
    this.maxRetries = 3,
    this.retryDelay = const Duration(seconds: 1),
  });

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    final retryCount = err.requestOptions.extra['retryCount'] ?? 0;

    // Only retry on connection errors
    if (_shouldRetry(err) && retryCount < maxRetries) {
      await Future.delayed(retryDelay * (retryCount + 1));

      final options = err.requestOptions;
      options.extra['retryCount'] = retryCount + 1;

      try {
        final response = await Dio().fetch(options);
        return handler.resolve(response);
      } catch (e) {
        // Continue with error if retry fails
      }
    }

    handler.next(err);
  }

  bool _shouldRetry(DioException err) {
    return err.type == DioExceptionType.connectionTimeout ||
        err.type == DioExceptionType.sendTimeout ||
        err.type == DioExceptionType.receiveTimeout ||
        err.type == DioExceptionType.connectionError;
  }
}
