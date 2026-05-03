import 'chat_models.dart';

/// A single message in a conversation. Mirrors web `messages[]` shape
/// in `frontend-admin/src/pages/ChatPage.jsx`.
class ChatMessage {
  final String role; // 'user' | 'assistant'
  final String content;
  final String? intent;
  final ChatData? data;
  final List<ProductImage>? images;
  final List<String>? suggestedQuestions;
  final Map<String, dynamic>? kzData;
  final DateTime createdAt;

  ChatMessage({
    required this.role,
    required this.content,
    this.intent,
    this.data,
    this.images,
    this.suggestedQuestions,
    this.kzData,
    DateTime? createdAt,
  }) : createdAt = createdAt ?? DateTime.now();

  bool get isUser => role == 'user';
  bool get isAssistant => role == 'assistant';

  factory ChatMessage.fromJson(Map<String, dynamic> json) => ChatMessage(
        role: json['role'] as String? ?? 'assistant',
        content: json['content'] as String? ?? '',
        intent: json['intent'] as String?,
        data: json['data'] != null
            ? ChatData.fromJson((json['data'] as Map).cast<String, dynamic>())
            : null,
        images: (json['images'] as List?)
            ?.map((e) => ProductImage.fromJson((e as Map).cast<String, dynamic>()))
            .toList(),
        suggestedQuestions: (json['suggested_questions'] as List?)
            ?.map((e) {
              if (e is String) return e;
              if (e is Map) {
                return (e['prompt'] ?? e['text'] ?? '').toString();
              }
              return e.toString();
            })
            .where((s) => s.isNotEmpty)
            .toList(),
        kzData: (json['kz_data'] as Map?)?.cast<String, dynamic>(),
        createdAt: json['created_at'] != null
            ? DateTime.tryParse(json['created_at'] as String) ?? DateTime.now()
            : DateTime.now(),
      );

  Map<String, dynamic> toJson() => {
        'role': role,
        'content': content,
        if (intent != null) 'intent': intent,
        if (data != null) 'data': data!.toJson(),
        if (images != null) 'images': images!.map((e) => e.toJson()).toList(),
        if (suggestedQuestions != null)
          'suggested_questions': suggestedQuestions,
        if (kzData != null) 'kz_data': kzData,
        'created_at': createdAt.toIso8601String(),
      };

  ChatMessage copyWith({
    String? content,
    Map<String, dynamic>? kzData,
  }) =>
      ChatMessage(
        role: role,
        content: content ?? this.content,
        intent: intent,
        data: data,
        images: images,
        suggestedQuestions: suggestedQuestions,
        kzData: kzData ?? this.kzData,
        createdAt: createdAt,
      );
}

/// Locally-persisted conversation. Mirrors the web `conversations`
/// localStorage entries (`chat_conversations` key in `ChatPage.jsx`).
class Conversation {
  final String id;
  final String title;
  final List<ChatMessage> messages;
  final DateTime updatedAt;

  Conversation({
    required this.id,
    required this.title,
    required this.messages,
    required this.updatedAt,
  });

  factory Conversation.fromJson(Map<String, dynamic> json) => Conversation(
        id: json['id'] as String,
        title: json['title'] as String? ?? 'New chat',
        messages: (json['messages'] as List? ?? [])
            .map((e) => ChatMessage.fromJson((e as Map).cast<String, dynamic>()))
            .toList(),
        updatedAt: DateTime.tryParse(json['updatedAt'] as String? ?? '') ??
            DateTime.now(),
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'title': title,
        'messages': messages.map((m) => m.toJson()).toList(),
        'updatedAt': updatedAt.toIso8601String(),
      };

  Conversation copyWith({
    String? title,
    List<ChatMessage>? messages,
    DateTime? updatedAt,
  }) =>
      Conversation(
        id: id,
        title: title ?? this.title,
        messages: messages ?? this.messages,
        updatedAt: updatedAt ?? this.updatedAt,
      );
}
