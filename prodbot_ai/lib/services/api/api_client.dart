import 'package:dio/dio.dart';
import 'api_exception.dart';
import 'api_interceptor.dart';
import '../../core/config/app_config.dart';

/// API Client using Dio with proper error handling
/// Supports automatic token refresh and request interceptors
class ApiClient {
  static ApiClient? _instance;
  late final Dio _dio;

  // Base URL from configuration
  static String get baseUrl => AppConfig.apiBaseUrl;

  ApiClient._internal() {
    _dio = Dio(
      BaseOptions(
        baseUrl: baseUrl,
        connectTimeout: Duration(seconds: AppConfig.apiTimeoutSeconds),
        receiveTimeout: Duration(seconds: AppConfig.apiTimeoutSeconds),
        sendTimeout: Duration(seconds: AppConfig.apiTimeoutSeconds),
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
      ),
    );

    // Add interceptors
    _dio.interceptors.addAll([
      AuthInterceptor(),
      LoggingInterceptor(),
    ]);
  }

  factory ApiClient() {
    _instance ??= ApiClient._internal();
    return _instance!;
  }

  Dio get dio => _dio;

  // Set auth token
  void setAuthToken(String token) {
    _dio.options.headers['Authorization'] = 'Bearer $token';
  }

  // Clear auth token
  void clearAuthToken() {
    _dio.options.headers.remove('Authorization');
  }

  // GET request
  Future<T> get<T>(
    String path, {
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    try {
      final response = await _dio.get<T>(
        path,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
      );
      return response.data as T;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // POST request
  Future<T> post<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    try {
      final response = await _dio.post<T>(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
      );
      return response.data as T;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // PUT request
  Future<T> put<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    try {
      final response = await _dio.put<T>(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
      );
      return response.data as T;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // PATCH request
  Future<T> patch<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    try {
      final response = await _dio.patch<T>(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
      );
      return response.data as T;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // DELETE request
  Future<T> delete<T>(
    String path, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    try {
      final response = await _dio.delete<T>(
        path,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
      );
      return response.data as T;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // Upload file
  Future<T> uploadFile<T>(
    String path, {
    required String filePath,
    required String fieldName,
    Map<String, dynamic>? additionalData,
    ProgressCallback? onSendProgress,
    CancelToken? cancelToken,
  }) async {
    try {
      final formData = FormData.fromMap({
        fieldName: await MultipartFile.fromFile(filePath),
        ...?additionalData,
      });

      final response = await _dio.post<T>(
        path,
        data: formData,
        onSendProgress: onSendProgress,
        cancelToken: cancelToken,
      );
      return response.data as T;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // Error handler
  ApiException _handleError(DioException e) {
    switch (e.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return ApiException(
          message: 'Connection timeout. Please check your internet connection.',
          statusCode: null,
          type: ApiExceptionType.timeout,
        );

      case DioExceptionType.connectionError:
        return ApiException(
          message: 'No internet connection. Please try again.',
          statusCode: null,
          type: ApiExceptionType.noInternet,
        );

      case DioExceptionType.badResponse:
        return _handleResponseError(e.response);

      case DioExceptionType.cancel:
        return ApiException(
          message: 'Request was cancelled.',
          statusCode: null,
          type: ApiExceptionType.cancelled,
        );

      default:
        return ApiException(
          message: e.message ?? 'An unexpected error occurred.',
          statusCode: null,
          type: ApiExceptionType.unknown,
        );
    }
  }

  ApiException _handleResponseError(Response? response) {
    final statusCode = response?.statusCode;
    final data = response?.data;

    String message = 'An error occurred';

    if (data is Map<String, dynamic>) {
      message = data['detail'] ?? data['message'] ?? message;
    }

    switch (statusCode) {
      case 400:
        return ApiException(
          message: message,
          statusCode: 400,
          type: ApiExceptionType.badRequest,
        );
      case 401:
        return ApiException(
          message: 'Authentication failed. Please login again.',
          statusCode: 401,
          type: ApiExceptionType.unauthorized,
        );
      case 403:
        return ApiException(
          message: 'You do not have permission to perform this action.',
          statusCode: 403,
          type: ApiExceptionType.forbidden,
        );
      case 404:
        return ApiException(
          message: 'Resource not found.',
          statusCode: 404,
          type: ApiExceptionType.notFound,
        );
      case 409:
        return ApiException(
          message: message,
          statusCode: 409,
          type: ApiExceptionType.conflict,
        );
      case 422:
        return ApiException(
          message: message,
          statusCode: 422,
          type: ApiExceptionType.validationError,
        );
      case 500:
      case 501:
      case 502:
      case 503:
        return ApiException(
          message: 'Server error. Please try again later.',
          statusCode: statusCode,
          type: ApiExceptionType.serverError,
        );
      default:
        return ApiException(
          message: message,
          statusCode: statusCode,
          type: ApiExceptionType.unknown,
        );
    }
  }
}
