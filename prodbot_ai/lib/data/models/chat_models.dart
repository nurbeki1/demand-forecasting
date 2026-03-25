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
  final Map<String, dynamic>? entities;
  final List<String> suggestions;
  final ChatData? data;
  final List<ProductImage>? images;

  ChatResponse({
    required this.reply,
    required this.intent,
    this.entities,
    required this.suggestions,
    this.data,
    this.images,
  });

  factory ChatResponse.fromJson(Map<String, dynamic> json) {
    return ChatResponse(
      reply: json['reply'] as String,
      intent: json['intent'] as String,
      entities: json['entities'] as Map<String, dynamic>?,
      suggestions: (json['suggestions'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          [],
      data: json['data'] != null
          ? ChatData.fromJson(json['data'] as Map<String, dynamic>)
          : null,
      images: (json['images'] as List<dynamic>?)
              ?.map((e) => ProductImage.fromJson(e as Map<String, dynamic>))
              .toList(),
    );
  }

  Map<String, dynamic> toJson() => {
        'reply': reply,
        'intent': intent,
        'entities': entities,
        'suggestions': suggestions,
        'data': data?.toJson(),
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
