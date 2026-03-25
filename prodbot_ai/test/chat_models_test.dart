import 'package:flutter_test/flutter_test.dart';
import 'package:prodbot_ai/data/models/chat_models.dart';

void main() {
  group('ChatResponse', () {
    test('fromJson creates valid ChatResponse', () {
      final json = {
        'reply': 'Test response',
        'intent': 'forecast',
        'entities': {'product_ids': ['P0001']},
        'suggestions': ['Suggestion 1', 'Suggestion 2'],
      };

      final response = ChatResponse.fromJson(json);

      expect(response.reply, 'Test response');
      expect(response.intent, 'forecast');
      expect(response.suggestions.length, 2);
    });

    test('fromJson handles null entities', () {
      final json = {
        'reply': 'Test',
        'intent': 'general',
        'suggestions': [],
      };

      final response = ChatResponse.fromJson(json);

      expect(response.entities, isNull);
    });

    test('fromJson parses data with chart info', () {
      final json = {
        'reply': 'Forecast generated',
        'intent': 'forecast',
        'suggestions': [],
        'data': {
          'product_id': 'P0001',
          'history': [
            {'date': '2024-01-01', 'demand': 100.0}
          ],
          'forecast': [
            {'date': '2024-01-02', 'predicted_demand': 110.0}
          ],
        },
      };

      final response = ChatResponse.fromJson(json);

      expect(response.data, isNotNull);
      expect(response.data!.productId, 'P0001');
      expect(response.data!.history.length, 1);
      expect(response.data!.forecast.length, 1);
    });

    test('toJson serializes correctly', () {
      final response = ChatResponse(
        reply: 'Test',
        intent: 'general',
        suggestions: ['S1'],
      );

      final json = response.toJson();

      expect(json['reply'], 'Test');
      expect(json['intent'], 'general');
      expect(json['suggestions'], ['S1']);
    });
  });

  group('ChatData', () {
    test('fromJson parses history and forecast', () {
      final json = {
        'product_id': 'P0002',
        'history': [
          {'date': '2024-01-01', 'demand': 50.0},
          {'date': '2024-01-02', 'demand': 55.0},
        ],
        'forecast': [
          {'date': '2024-01-03', 'predicted_demand': 60.0},
        ],
      };

      final data = ChatData.fromJson(json);

      expect(data.productId, 'P0002');
      expect(data.history.length, 2);
      expect(data.forecast.length, 1);
      expect(data.history[0].demand, 50.0);
      expect(data.forecast[0].predictedDemand, 60.0);
    });

    test('handles empty arrays', () {
      final json = {
        'product_id': 'P0003',
        'history': [],
        'forecast': [],
      };

      final data = ChatData.fromJson(json);

      expect(data.history.isEmpty, true);
      expect(data.forecast.isEmpty, true);
    });
  });

  group('HistoryPoint', () {
    test('fromJson parses correctly', () {
      final json = {'date': '2024-03-15', 'demand': 123.5};

      final point = HistoryPoint.fromJson(json);

      expect(point.date, '2024-03-15');
      expect(point.demand, 123.5);
    });

    test('handles integer demand', () {
      final json = {'date': '2024-03-15', 'demand': 100};

      final point = HistoryPoint.fromJson(json);

      expect(point.demand, 100.0);
    });
  });

  group('ForecastPoint', () {
    test('fromJson parses correctly', () {
      final json = {'date': '2024-03-16', 'predicted_demand': 150.75};

      final point = ForecastPoint.fromJson(json);

      expect(point.date, '2024-03-16');
      expect(point.predictedDemand, 150.75);
    });
  });

  group('ChatHistoryMessage', () {
    test('fromJson parses user message', () {
      final json = {
        'role': 'user',
        'content': 'Hello AI',
        'timestamp': '2024-03-15T10:30:00',
      };

      final message = ChatHistoryMessage.fromJson(json);

      expect(message.role, 'user');
      expect(message.content, 'Hello AI');
      expect(message.isUser, true);
      expect(message.isAssistant, false);
    });

    test('fromJson parses assistant message', () {
      final json = {
        'role': 'assistant',
        'content': 'Hello! How can I help?',
        'timestamp': '2024-03-15T10:30:01',
        'intent': 'general',
      };

      final message = ChatHistoryMessage.fromJson(json);

      expect(message.role, 'assistant');
      expect(message.isUser, false);
      expect(message.isAssistant, true);
      expect(message.intent, 'general');
    });

    test('fromJson parses message with data', () {
      final json = {
        'role': 'assistant',
        'content': 'Forecast ready',
        'timestamp': '2024-03-15T10:30:02',
        'data': {
          'product_id': 'P0001',
          'history': [],
          'forecast': [],
        },
      };

      final message = ChatHistoryMessage.fromJson(json);

      expect(message.data, isNotNull);
      expect(message.data!.productId, 'P0001');
    });
  });

  group('ChatHistoryResponse', () {
    test('fromJson parses list of messages', () {
      final json = [
        {
          'role': 'user',
          'content': 'Question',
          'timestamp': '2024-03-15T10:00:00',
        },
        {
          'role': 'assistant',
          'content': 'Answer',
          'timestamp': '2024-03-15T10:00:01',
        },
      ];

      final response = ChatHistoryResponse.fromJson(json);

      expect(response.messages.length, 2);
      expect(response.messages[0].isUser, true);
      expect(response.messages[1].isAssistant, true);
    });

    test('handles empty list', () {
      final response = ChatHistoryResponse.fromJson([]);

      expect(response.messages.isEmpty, true);
    });
  });

  group('ClearHistoryResponse', () {
    test('fromJson parses correctly', () {
      final json = {
        'message': 'History cleared',
        'cleared_messages': 5,
      };

      final response = ClearHistoryResponse.fromJson(json);

      expect(response.message, 'History cleared');
      expect(response.clearedMessages, 5);
    });
  });
}
