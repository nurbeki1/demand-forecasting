import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';
import 'package:prodbot_ai/services/api/api_client.dart';
import 'package:prodbot_ai/services/chat_service.dart';
import 'package:prodbot_ai/data/models/chat_models.dart';

// Generate mocks
@GenerateMocks([ApiClient])
import 'chat_service_test.mocks.dart';

void main() {
  late MockApiClient mockApiClient;
  late ChatService chatService;

  setUp(() {
    mockApiClient = MockApiClient();
    chatService = ChatService(apiClient: mockApiClient);
  });

  group('ChatService.sendMessage', () {
    test('sends message and returns ChatResponse', () async {
      // Arrange
      when(mockApiClient.post<Map<String, dynamic>>(
        '/chat',
        data: {'message': 'Hello'},
      )).thenAnswer((_) async => {
            'reply': 'Hi there!',
            'intent': 'general',
            'suggestions': ['Option 1'],
          });

      // Act
      final result = await chatService.sendMessage('Hello');

      // Assert
      expect(result.reply, 'Hi there!');
      expect(result.intent, 'general');
      expect(result.suggestions.length, 1);
      verify(mockApiClient.post<Map<String, dynamic>>(
        '/chat',
        data: {'message': 'Hello'},
      )).called(1);
    });

    test('returns ChatResponse with data for forecast', () async {
      when(mockApiClient.post<Map<String, dynamic>>(
        '/chat',
        data: anyNamed('data'),
      )).thenAnswer((_) async => {
            'reply': 'Forecast ready',
            'intent': 'forecast',
            'suggestions': [],
            'data': {
              'product_id': 'P0001',
              'history': [
                {'date': '2024-01-01', 'demand': 100}
              ],
              'forecast': [
                {'date': '2024-01-02', 'predicted_demand': 110}
              ],
            },
          });

      final result = await chatService.sendMessage('Forecast for P0001');

      expect(result.data, isNotNull);
      expect(result.data!.productId, 'P0001');
    });
  });

  group('ChatService.getHistory', () {
    test('returns list of ChatMessages', () async {
      when(mockApiClient.get<List<dynamic>>(
        '/chat/history',
        queryParameters: null,
      )).thenAnswer((_) async => [
            {
              'role': 'user',
              'content': 'Hello',
              'timestamp': '2024-01-01T10:00:00',
            },
            {
              'role': 'assistant',
              'content': 'Hi',
              'timestamp': '2024-01-01T10:00:01',
            },
          ]);

      final result = await chatService.getHistory();

      expect(result.length, 2);
      expect(result[0].isUser, true);
      expect(result[1].isAssistant, true);
    });

    test('passes limit parameter', () async {
      when(mockApiClient.get<List<dynamic>>(
        '/chat/history',
        queryParameters: {'limit': 10},
      )).thenAnswer((_) async => []);

      await chatService.getHistory(limit: 10);

      verify(mockApiClient.get<List<dynamic>>(
        '/chat/history',
        queryParameters: {'limit': 10},
      )).called(1);
    });
  });

  group('ChatService.clearHistory', () {
    test('clears history and returns response', () async {
      when(mockApiClient.delete<Map<String, dynamic>>(
        '/chat/history',
      )).thenAnswer((_) async => {
            'message': 'History cleared',
            'cleared_messages': 5,
          });

      final result = await chatService.clearHistory();

      expect(result.message, 'History cleared');
      expect(result.clearedMessages, 5);
    });
  });

  group('ChatService.getAnalyticsSummary', () {
    test('returns analytics data', () async {
      when(mockApiClient.get<Map<String, dynamic>>(
        '/analytics/summary',
      )).thenAnswer((_) async => {
            'overview': {'total_records': 1000},
            'top_by_demand': [],
            'top_by_growth': [],
            'declining': [],
          });

      final result = await chatService.getAnalyticsSummary();

      expect(result['overview'], isNotNull);
      expect(result['overview']['total_records'], 1000);
    });
  });

  group('ChatService.getAnalyticsTrends', () {
    test('returns trends data', () async {
      when(mockApiClient.get<Map<String, dynamic>>(
        '/analytics/trends',
      )).thenAnswer((_) async => {
            'growing': [],
            'declining': [],
            'stable': [],
          });

      final result = await chatService.getAnalyticsTrends();

      expect(result.containsKey('growing'), true);
      expect(result.containsKey('declining'), true);
      expect(result.containsKey('stable'), true);
    });
  });
}
