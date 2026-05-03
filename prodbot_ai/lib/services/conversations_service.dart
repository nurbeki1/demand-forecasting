import 'dart:convert';
import 'dart:math';

import '../data/models/conversation.dart';
import 'storage_service.dart';

/// Local persistence for chat conversations. Mirrors the web
/// localStorage keys `chat_conversations` and `current_conversation_id`
/// from `frontend-admin/src/pages/ChatPage.jsx`.
class ConversationsService {
  static const _conversationsKey = 'chat_conversations_v1';
  static const _currentIdKey = 'current_conversation_id_v1';

  List<Conversation> getAll() {
    final raw = StorageService.getString(_conversationsKey);
    if (raw == null || raw.isEmpty) return [];
    try {
      final list = jsonDecode(raw) as List<dynamic>;
      return list
          .map((e) => Conversation.fromJson((e as Map).cast<String, dynamic>()))
          .toList();
    } catch (_) {
      return [];
    }
  }

  Future<void> saveAll(List<Conversation> conversations) async {
    final encoded = jsonEncode(conversations.map((c) => c.toJson()).toList());
    await StorageService.setString(_conversationsKey, encoded);
  }

  String? getCurrentId() => StorageService.getString(_currentIdKey);

  Future<void> setCurrentId(String? id) async {
    if (id == null) {
      await StorageService.remove(_currentIdKey);
    } else {
      await StorageService.setString(_currentIdKey, id);
    }
  }

  /// Generate a unique-ish id (web parity: `Date.now() + random`).
  String generateId() {
    final ts = DateTime.now().millisecondsSinceEpoch.toRadixString(36);
    final rand = Random().nextInt(1 << 32).toRadixString(36);
    return '$ts$rand';
  }
}
