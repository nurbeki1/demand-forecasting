import '../data/models/chat_models.dart';
import 'api/api_client.dart';

/// Service for AI Chat functionality
class ChatService {
  final ApiClient _apiClient;

  ChatService({ApiClient? apiClient}) : _apiClient = apiClient ?? ApiClient();

  /// Send a message to the AI chat
  /// Returns ChatResponse with reply, intent, suggestions, and optional chart data
  Future<ChatResponse> sendMessage(String message) async {
    final response = await _apiClient.post<Map<String, dynamic>>(
      '/chat',
      data: {'message': message},
    );
    return ChatResponse.fromJson(response);
  }

  /// Get chat history for the current user
  /// [limit] - Optional limit on number of messages to retrieve
  Future<List<ChatHistoryMessage>> getHistory({int? limit}) async {
    final queryParams = <String, dynamic>{};
    if (limit != null) {
      queryParams['limit'] = limit;
    }

    final response = await _apiClient.get<List<dynamic>>(
      '/chat/history',
      queryParameters: queryParams.isNotEmpty ? queryParams : null,
    );

    return response
        .map((e) => ChatHistoryMessage.fromJson(e as Map<String, dynamic>))
        .toList();
  }

  /// Clear chat history for the current user
  Future<ClearHistoryResponse> clearHistory() async {
    final response = await _apiClient.delete<Map<String, dynamic>>(
      '/chat/history',
    );
    return ClearHistoryResponse.fromJson(response);
  }

  /// Get analytics summary
  Future<Map<String, dynamic>> getAnalyticsSummary() async {
    return await _apiClient.get<Map<String, dynamic>>('/analytics/summary');
  }

  /// Get analytics trends
  Future<Map<String, dynamic>> getAnalyticsTrends() async {
    return await _apiClient.get<Map<String, dynamic>>('/analytics/trends');
  }
}
