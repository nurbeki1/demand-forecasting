/// API Exception types
enum ApiExceptionType {
  timeout,
  noInternet,
  badRequest,
  unauthorized,
  forbidden,
  notFound,
  conflict,
  validationError,
  serverError,
  cancelled,
  unknown,
}

/// Custom API Exception with detailed error information
class ApiException implements Exception {
  final String message;
  final int? statusCode;
  final ApiExceptionType type;
  final dynamic data;

  const ApiException({
    required this.message,
    this.statusCode,
    this.type = ApiExceptionType.unknown,
    this.data,
  });

  @override
  String toString() => message;

  /// Check if error is due to authentication
  bool get isAuthError => type == ApiExceptionType.unauthorized;

  /// Check if error is due to network issues
  bool get isNetworkError =>
      type == ApiExceptionType.noInternet || type == ApiExceptionType.timeout;

  /// Check if error is a server error
  bool get isServerError => type == ApiExceptionType.serverError;

  /// Get user-friendly error message
  String get userMessage {
    switch (type) {
      case ApiExceptionType.timeout:
        return 'Connection timed out. Please try again.';
      case ApiExceptionType.noInternet:
        return 'No internet connection. Please check your network.';
      case ApiExceptionType.unauthorized:
        return 'Please login to continue.';
      case ApiExceptionType.forbidden:
        return 'You don\'t have permission to do this.';
      case ApiExceptionType.notFound:
        return 'The requested resource was not found.';
      case ApiExceptionType.serverError:
        return 'Server error. Please try again later.';
      case ApiExceptionType.cancelled:
        return 'Request was cancelled.';
      default:
        return message;
    }
  }
}
