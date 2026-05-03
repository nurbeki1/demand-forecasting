import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/locale/app_locale.dart';
import '../../../core/theme/theme.dart';
import '../../../l10n/app_localizations.dart';
import '../../../routes/app_router.dart';
import '../../../services/auth_service.dart';
import '../../../services/chat_provider.dart';
import '../../widgets/common/brand_logo.dart';
import 'widgets/chat_drawer.dart';
import 'widgets/message_bubble.dart';
import 'widgets/pill_input.dart';
import 'widgets/typewriter_text.dart';

/// Chat-first home screen. Mirrors the structure of `ChatPage.jsx`:
/// - Sidebar (here as a Drawer)
/// - Empty state with logo + typewriter + pill input + suggestions
/// - Messages list with input docked at the bottom
/// - Settings opens via push
class ChatHomeScreen extends StatefulWidget {
  const ChatHomeScreen({super.key});

  @override
  State<ChatHomeScreen> createState() => _ChatHomeScreenState();
}

class _ChatHomeScreenState extends State<ChatHomeScreen> {
  final TextEditingController _inputController = TextEditingController();
  final FocusNode _inputFocus = FocusNode();
  final ScrollController _scrollController = ScrollController();
  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<ChatProvider>().init();
    });
  }

  @override
  void dispose() {
    _inputController.dispose();
    _inputFocus.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!_scrollController.hasClients) return;
      _scrollController.animateTo(
        _scrollController.position.maxScrollExtent + 120,
        duration: const Duration(milliseconds: 280),
        curve: Curves.easeOut,
      );
    });
  }

  Future<void> _send([String? overrideText]) async {
    final provider = context.read<ChatProvider>();
    final text = (overrideText ?? _inputController.text).trim();
    if (text.isEmpty || provider.loading) return;
    _inputController.clear();
    await provider.sendMessage(
      text,
      language: apiLanguageFromLocale(Localizations.localeOf(context)),
    );
    _scrollToBottom();
  }

  Future<void> _logout() async {
    final auth = context.read<AuthService>();
    await auth.logout();
    if (!mounted) return;
    Navigator.of(context).pushNamedAndRemoveUntil(
      AppRoutes.welcome,
      (_) => false,
    );
  }

  void _openSettings() {
    Navigator.of(context).pushNamed(AppRoutes.settings);
  }

  @override
  Widget build(BuildContext context) {
    final chat = context.watch<ChatProvider>();
    final auth = context.watch<AuthService>();
    final isEmpty = chat.isEmpty;

    final email = auth.currentUserEmail;
    final initial =
        (email == null || email.isEmpty) ? 'U' : email.substring(0, 1).toUpperCase();

    return Scaffold(
      key: _scaffoldKey,
      backgroundColor: AppColors.background,
      drawer: ChatDrawer(
        conversations: chat.conversations,
        currentId: chat.currentConversationId,
        userEmail: email,
        onNewChat: () => chat.startNewChat(),
        onSelect: (id) => chat.selectConversation(id),
        onDelete: (id) => chat.deleteConversation(id),
        onSettings: _openSettings,
        onLogout: _logout,
      ),
      body: SafeArea(
        child: Column(
          children: [
            _Header(
              isEmpty: isEmpty,
              onMenu: () => _scaffoldKey.currentState?.openDrawer(),
              onNewChat: () => chat.startNewChat(),
            ),
            Expanded(
              child: isEmpty
                  ? _emptyState(chat)
                  : _messagesList(chat, initial),
            ),
            if (!isEmpty) _bottomInput(chat),
          ],
        ),
      ),
    );
  }

  Widget _emptyState(ChatProvider chat) {
    final l10n = AppLocalizations.of(context)!;
    final suggestions = [
      l10n.suggestionTopProducts,
      l10n.suggestionSalesForecast,
      l10n.suggestionTrending,
      l10n.suggestionCompare,
    ];

    return Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 24),
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 640),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const BrandLogo(size: 64, radius: 18, withGlow: true),
              const SizedBox(height: 22),
              SizedBox(
                height: 48,
                child: TypewriterText(
                  phrases: [
                    l10n.chatWelcomeType1,
                    l10n.chatWelcomeType2,
                    l10n.chatWelcomeType3,
                  ],
                ),
              ),
              const SizedBox(height: 18),
              PillInput(
                controller: _inputController,
                focusNode: _inputFocus,
                hintText: l10n.chatAskAnythingHint,
                isLarge: true,
                loading: chat.loading,
                selectedModel: chat.selectedModel,
                onModelChanged: chat.setModel,
                onSend: _send,
              ),
              const SizedBox(height: 8),
              Text(
                l10n.chatDisclaimer,
                style: AppTextStyles.labelSmall.copyWith(
                  color: AppColors.textTertiary,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 18),
              Wrap(
                alignment: WrapAlignment.center,
                spacing: 10,
                runSpacing: 10,
                children: suggestions
                    .map(
                      (s) => InkWell(
                        onTap: () {
                          _inputController.text = s;
                          _inputController.selection =
                              TextSelection.collapsed(offset: s.length);
                          _inputFocus.requestFocus();
                        },
                        borderRadius: BorderRadius.circular(999),
                        child: Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 14, vertical: 10),
                          decoration: BoxDecoration(
                            color: AppColors.surfaceVariant,
                            borderRadius: BorderRadius.circular(999),
                            border: Border.all(color: AppColors.borderSubtle),
                          ),
                          child: Text(
                            s,
                            style: AppTextStyles.bodySmall.copyWith(
                              color: AppColors.textPrimary,
                            ),
                          ),
                        ),
                      ),
                    )
                    .toList(),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _messagesList(ChatProvider chat, String initial) {
    return ListView.builder(
      controller: _scrollController,
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 16),
      itemCount: chat.messages.length + (chat.loading ? 1 : 0),
      itemBuilder: (context, index) {
        if (index == chat.messages.length) {
          return const TypingBubble();
        }
        final m = chat.messages[index];
        return MessageBubble(
          message: m,
          userInitial: initial,
          onSuggestionTap: (q) => _send(q),
          onKZRecalculate:
              m.kzData != null ? (markup) => chat.recalculateKZ(message: m, markup: markup) : null,
        );
      },
    );
  }

  Widget _bottomInput(ChatProvider chat) {
    final l10n = AppLocalizations.of(context)!;
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 14),
      decoration: BoxDecoration(
        color: AppColors.background,
        border: Border(
          top: BorderSide(color: AppColors.borderSubtle, width: 1),
        ),
      ),
      child: PillInput(
        controller: _inputController,
        focusNode: _inputFocus,
        hintText: l10n.chatMessageHint,
        isLarge: false,
        loading: chat.loading,
        selectedModel: chat.selectedModel,
        onModelChanged: chat.setModel,
        onSend: _send,
      ),
    );
  }
}

class _Header extends StatelessWidget {
  final bool isEmpty;
  final VoidCallback onMenu;
  final VoidCallback onNewChat;

  const _Header({
    required this.isEmpty,
    required this.onMenu,
    required this.onNewChat,
  });

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return Container(
      height: 56,
      padding: const EdgeInsets.symmetric(horizontal: 8),
      decoration: BoxDecoration(
        color: AppColors.background,
        border: Border(
          bottom: BorderSide(color: AppColors.borderSubtle),
        ),
      ),
      child: Row(
        children: [
          IconButton(
            onPressed: onMenu,
            icon: const Icon(Icons.menu_rounded,
                size: 22, color: AppColors.textPrimary),
          ),
          if (!isEmpty)
            Expanded(
              child: Text(
                l10n.chatAiAssistant,
                style: AppTextStyles.titleMedium.copyWith(
                  fontWeight: FontWeight.w600,
                ),
              ),
            )
          else
            const Expanded(child: SizedBox.shrink()),
          IconButton(
            onPressed: onNewChat,
            tooltip: l10n.chatNewChat,
            icon: const Icon(Icons.add_rounded,
                size: 22, color: AppColors.textPrimary),
          ),
        ],
      ),
    );
  }
}
