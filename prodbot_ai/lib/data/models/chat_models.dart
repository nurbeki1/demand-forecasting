/// Chat models for AI Chat functionality

/// Product image data for display in chat
class ProductImage {
  final String productId;
  final String name;
  final String imageUrl;
  final double price;
  final double rating;

  ProductImage({
    required this.productId,
    required this.name,
    required this.imageUrl,
    required this.price,
    required this.rating,
  });

  factory ProductImage.fromJson(Map<String, dynamic> json) {
    return ProductImage(
      productId: json['product_id'] as String? ?? '',
      name: json['name'] as String? ?? '',
      imageUrl: json['image_url'] as String? ?? '',
      price: (json['price'] as num?)?.toDouble() ?? 0.0,
      rating: (json['rating'] as num?)?.toDouble() ?? 0.0,
    );
  }

  Map<String, dynamic> toJson() => {
        'product_id': productId,
        'name': name,
        'image_url': imageUrl,
        'price': price,
        'rating': rating,
      };
}

/// Response from chat API
class ChatResponse {
  final String reply;
  final String intent;
  final String? responseType;
  final Map<String, dynamic>? entities;
  final List<String> suggestions;
  final List<String> suggestedQuestions;
  final List<String>? availableDetails;
  final ChatData? data;
  final List<ProductImage>? images;
  final Map<String, dynamic>? kzData;

  ChatResponse({
    required this.reply,
    required this.intent,
    this.responseType,
    this.entities,
    required this.suggestions,
    this.suggestedQuestions = const [],
    this.availableDetails,
    this.data,
    this.images,
    this.kzData,
  });

  factory ChatResponse.fromJson(Map<String, dynamic> json) {
    Map<String, dynamic>? rawData;
    if (json['data'] is Map) {
      rawData = (json['data'] as Map).cast<String, dynamic>();
    }
    final hasForecastShape = rawData != null &&
        (rawData.containsKey('history') || rawData.containsKey('forecast'));
    return ChatResponse(
      reply: json['reply'] as String? ?? '',
      intent: json['intent'] as String? ?? 'general',
      responseType: json['response_type'] as String?,
      entities: (json['entities'] as Map?)?.cast<String, dynamic>(),
      suggestions: (json['suggestions'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          [],
      suggestedQuestions: (json['suggested_questions'] as List<dynamic>?)
              ?.map((e) {
                if (e is String) return e;
                if (e is Map) {
                  return (e['prompt'] ?? e['text'] ?? '').toString();
                }
                return e.toString();
              })
              .where((s) => s.isNotEmpty)
              .toList() ??
          [],
      availableDetails: (json['available_details'] as List<dynamic>?)
          ?.map((e) => e as String)
          .toList(),
      data: hasForecastShape ? ChatData.fromJson(rawData) : null,
      images: (json['images'] as List<dynamic>?)
              ?.map((e) => ProductImage.fromJson(e as Map<String, dynamic>))
              .toList(),
      // KZ analysis lives under `data` when intent == 'kz_market_analysis'
      kzData: rawData != null && !hasForecastShape ? rawData : null,
    );
  }

  Map<String, dynamic> toJson() => {
        'reply': reply,
        'intent': intent,
        'response_type': responseType,
        'entities': entities,
        'suggestions': suggestions,
        'suggested_questions': suggestedQuestions,
        'available_details': availableDetails,
        'data': data?.toJson() ?? kzData,
        'images': images?.map((e) => e.toJson()).toList(),
      };
}

/// Chart data from chat response
class ChatData {
  final String productId;
  final List<HistoryPoint> history;
  final List<ForecastPoint> forecast;

  ChatData({
    required this.productId,
    required this.history,
    required this.forecast,
  });

  factory ChatData.fromJson(Map<String, dynamic> json) {
    return ChatData(
      productId: json['product_id'] as String,
      history: (json['history'] as List<dynamic>)
          .map((e) => HistoryPoint.fromJson(e as Map<String, dynamic>))
          .toList(),
      forecast: (json['forecast'] as List<dynamic>)
          .map((e) => ForecastPoint.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }

  Map<String, dynamic> toJson() => {
        'product_id': productId,
        'history': history.map((e) => e.toJson()).toList(),
        'forecast': forecast.map((e) => e.toJson()).toList(),
      };
}

/// Historical data point
class HistoryPoint {
  final String date;
  final double demand;

  HistoryPoint({
    required this.date,
    required this.demand,
  });

  factory HistoryPoint.fromJson(Map<String, dynamic> json) {
    return HistoryPoint(
      date: json['date'] as String,
      demand: (json['demand'] as num).toDouble(),
    );
  }

  Map<String, dynamic> toJson() => {
        'date': date,
        'demand': demand,
      };
}

/// Forecast data point
class ForecastPoint {
  final String date;
  final double predictedDemand;

  ForecastPoint({
    required this.date,
    required this.predictedDemand,
  });

  factory ForecastPoint.fromJson(Map<String, dynamic> json) {
    return ForecastPoint(
      date: json['date'] as String,
      predictedDemand: (json['predicted_demand'] as num).toDouble(),
    );
  }

  Map<String, dynamic> toJson() => {
        'date': date,
        'predicted_demand': predictedDemand,
      };
}

/// Chat message from history
class ChatHistoryMessage {
  final String role;
  final String content;
  final String timestamp;
  final String? intent;
  final ChatData? data;
  final List<ProductImage>? images;

  ChatHistoryMessage({
    required this.role,
    required this.content,
    required this.timestamp,
    this.intent,
    this.data,
    this.images,
  });

  factory ChatHistoryMessage.fromJson(Map<String, dynamic> json) {
    return ChatHistoryMessage(
      role: json['role'] as String,
      content: json['content'] as String,
      timestamp: json['timestamp'] as String,
      intent: json['intent'] as String?,
      data: json['data'] != null
          ? ChatData.fromJson(json['data'] as Map<String, dynamic>)
          : null,
      images: (json['images'] as List<dynamic>?)
              ?.map((e) => ProductImage.fromJson(e as Map<String, dynamic>))
              .toList(),
    );
  }

  Map<String, dynamic> toJson() => {
        'role': role,
        'content': content,
        'timestamp': timestamp,
        'intent': intent,
        'data': data?.toJson(),
        'images': images?.map((e) => e.toJson()).toList(),
      };

  bool get isUser => role == 'user';
  bool get isAssistant => role == 'assistant';
}

/// Chat history response
class ChatHistoryResponse {
  final List<ChatHistoryMessage> messages;

  ChatHistoryResponse({required this.messages});

  factory ChatHistoryResponse.fromJson(List<dynamic> json) {
    return ChatHistoryResponse(
      messages: json
          .map((e) => ChatHistoryMessage.fromJson(e as Map<String, dynamic>))
          .toList(),
    );
  }
}

/// Clear history response
class ClearHistoryResponse {
  final String message;
  final int clearedMessages;

  ClearHistoryResponse({
    required this.message,
    required this.clearedMessages,
  });

  factory ClearHistoryResponse.fromJson(Map<String, dynamic> json) {
    return ClearHistoryResponse(
      message: json['message'] as String,
      clearedMessages: json['cleared_messages'] as int,
    );
  }
}
