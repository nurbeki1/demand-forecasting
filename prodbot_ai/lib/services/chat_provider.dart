import 'package:flutter/material.dart';

import '../l10n/app_localizations.dart';
import '../data/models/conversation.dart';
import 'chat_service.dart';
import 'conversations_service.dart';

/// Holds the active chat conversation tree and persists it locally.
/// Mirrors the state of `frontend-admin/src/pages/ChatPage.jsx`.
class ChatProvider extends ChangeNotifier {
  ChatProvider({
    ChatService? chatService,
    ConversationsService? conversationsService,
  })  : _chatService = chatService ?? ChatService(),
        _conversationsService = conversationsService ?? ConversationsService();

  final ChatService _chatService;
  final ConversationsService _conversationsService;

  List<Conversation> _conversations = [];
  String? _currentConversationId;
  List<ChatMessage> _messages = [];
  String _selectedModel = 'random_forest';
  bool _loading = false;
  String? _error;

  List<Conversation> get conversations => _conversations;
  String? get currentConversationId => _currentConversationId;
  List<ChatMessage> get messages => _messages;
  String get selectedModel => _selectedModel;
  bool get loading => _loading;
  String? get error => _error;
  bool get isEmpty => _messages.isEmpty;

  void init() {
    _conversations = _conversationsService.getAll();
    final id = _conversationsService.getCurrentId();
    if (id != null) {
      final existing = _conversations.firstWhere(
        (c) => c.id == id,
        orElse: () => Conversation(
          id: '',
          title: '',
          messages: const [],
          updatedAt: DateTime.now(),
        ),
      );
      if (existing.id.isNotEmpty) {
        _currentConversationId = id;
        _messages = List.of(existing.messages);
      }
    }
    notifyListeners();
  }

  void clampModelForSubscription(bool premiumUnlocked) {
    if (!premiumUnlocked && _selectedModel != 'random_forest') {
      _selectedModel = 'random_forest';
      notifyListeners();
    }
  }

  void setModel(String model) {
    if (_selectedModel == model) return;
    _selectedModel = model;
    notifyListeners();
  }

  Future<void> selectConversation(String id) async {
    final conv = _conversations.firstWhere(
      (c) => c.id == id,
      orElse: () => Conversation(
        id: '',
        title: '',
        messages: const [],
        updatedAt: DateTime.now(),
      ),
    );
    if (conv.id.isEmpty) return;
    _currentConversationId = id;
    _messages = List.of(conv.messages);
    await _conversationsService.setCurrentId(id);
    notifyListeners();
  }

  Future<void> startNewChat({bool callBackend = true}) async {
    _messages = [];
    _currentConversationId = null;
    _error = null;
    await _conversationsService.setCurrentId(null);
    notifyListeners();
    if (callBackend) {
      try {
        await _chatService.clearHistory();
      } catch (_) {
        // ignore backend failure — local state still cleared
      }
    }
  }

  Future<void> deleteConversation(String id) async {
    _conversations = _conversations.where((c) => c.id != id).toList();
    await _conversationsService.saveAll(_conversations);
    if (_currentConversationId == id) {
      await startNewChat(callBackend: false);
    } else {
      notifyListeners();
    }
  }

  Future<void> sendMessage(String text, {String language = 'kk'}) async {
    final trimmed = text.trim();
    if (trimmed.isEmpty || _loading) return;

    final userMessage = ChatMessage(role: 'user', content: trimmed);
    _messages = [..._messages, userMessage];
    _loading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _chatService.sendMessage(
        trimmed,
        language: language,
        modelType: _selectedModel,
      );

      final assistantMessage = ChatMessage(
        role: 'assistant',
        content: response.reply,
        intent: response.intent,
        data: response.data,
        images: response.images,
        suggestedQuestions: response.suggestedQuestions.isNotEmpty
            ? response.suggestedQuestions
            : response.suggestions,
        kzData: response.kzData,
      );
      _messages = [..._messages, assistantMessage];
      await _persistCurrent();
    } catch (e) {
      final l10n = lookupAppLocalizations(Locale(language));
      _messages = [
        ..._messages,
        ChatMessage(
          role: 'assistant',
          content: l10n.chatErrorGeneric,
        ),
      ];
      _error = e.toString();
    } finally {
      _loading = false;
      notifyListeners();
    }
  }

  Future<void> recalculateKZ({
    required ChatMessage message,
    required int markup,
  }) async {
    final productName = message.kzData?['product_name'] as String?;
    if (productName == null) return;
    try {
      final response = await _chatService.recalculateKZAnalysis(
        productName: productName,
        markupPercent: markup,
      );
      final newKz = {...response, 'markup_percent': markup};
      _messages = _messages
          .map((m) => identical(m, message) ? m.copyWith(kzData: newKz) : m)
          .toList();
      await _persistCurrent();
      notifyListeners();
    } catch (e) {
      _error = e.toString();
      notifyListeners();
    }
  }

  Future<void> _persistCurrent() async {
    if (_messages.isEmpty) return;
    final firstUser = _messages.firstWhere(
      (m) => m.isUser,
      orElse: () => _messages.first,
    );
    final title = firstUser.content.length > 40
        ? '${firstUser.content.substring(0, 40)}…'
        : firstUser.content;

    final id = _currentConversationId ?? _conversationsService.generateId();
    final conv = Conversation(
      id: id,
      title: title,
      messages: List.of(_messages),
      updatedAt: DateTime.now(),
    );

    final idx = _conversations.indexWhere((c) => c.id == id);
    if (idx >= 0) {
      _conversations[idx] = conv;
    } else {
      _conversations = [conv, ..._conversations];
    }
    _currentConversationId = id;
    await _conversationsService.saveAll(_conversations);
    await _conversationsService.setCurrentId(id);
  }
}
