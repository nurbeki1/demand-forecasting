import 'package:flutter/material.dart';

import '../../../../core/theme/theme.dart';
import '../../../../data/models/conversation.dart';
import '../../../../l10n/app_localizations.dart';
import '../../../widgets/common/brand_logo.dart';

/// Mobile equivalent of the web `ChatSidebar` (`frontend-admin/src/pages/ChatPage.jsx`).
/// Hosts: New chat, Search, recent chats list, settings, user/email + logout.
class ChatDrawer extends StatefulWidget {
  final List<Conversation> conversations;
  final String? currentId;
  final String? userEmail;
  final VoidCallback onNewChat;
  final ValueChanged<String> onSelect;
  final ValueChanged<String> onDelete;
  final VoidCallback onSettings;
  final VoidCallback onSubscription;
  final VoidCallback onLogout;

  const ChatDrawer({
    super.key,
    required this.conversations,
    required this.currentId,
    required this.userEmail,
    required this.onNewChat,
    required this.onSelect,
    required this.onDelete,
    required this.onSettings,
    required this.onSubscription,
    required this.onLogout,
  });

  @override
  State<ChatDrawer> createState() => _ChatDrawerState();
}

class _ChatDrawerState extends State<ChatDrawer> {
  String _query = '';

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final filtered = _query.trim().isEmpty
        ? widget.conversations
        : widget.conversations
            .where((c) =>
                c.title.toLowerCase().contains(_query.trim().toLowerCase()))
            .toList();

    return Drawer(
      backgroundColor: AppColors.sidebar,
      shape: const RoundedRectangleBorder(),
      width: MediaQuery.of(context).size.width * 0.84,
      child: SafeArea(
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(14, 14, 14, 8),
              child: Row(
                children: [
                  const BrandLogo(size: 32, radius: 8),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      l10n.appTitle,
                      style: AppTextStyles.titleMedium.copyWith(
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ),
                  IconButton(
                    onPressed: () => Navigator.of(context).maybePop(),
                    icon: const Icon(Icons.close_rounded,
                        size: 20, color: AppColors.textSecondary),
                  ),
                ],
              ),
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(14, 6, 14, 10),
              child: _PrimaryActionTile(
                icon: Icons.add_rounded,
                label: l10n.chatNewChat,
                onTap: () {
                  Navigator.of(context).maybePop();
                  widget.onNewChat();
                },
              ),
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(14, 0, 14, 8),
              child: Container(
                height: 44,
                padding: const EdgeInsets.symmetric(horizontal: 12),
                decoration: BoxDecoration(
                  color: AppColors.surfaceVariant,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: AppColors.borderSubtle),
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    Icon(Icons.search_rounded,
                        size: 18, color: AppColors.textTertiary),
                    const SizedBox(width: 8),
                    Expanded(
                      child: TextField(
                        onChanged: (v) => setState(() => _query = v),
                        textAlignVertical: TextAlignVertical.center,
                        style: AppTextStyles.bodyMedium.copyWith(
                          color: AppColors.textPrimary,
                          fontSize: 14,
                        ),
                        decoration: InputDecoration(
                          isCollapsed: true,
                          contentPadding: EdgeInsets.zero,
                          border: InputBorder.none,
                          hintText: l10n.chatSearchHint,
                          hintStyle: AppTextStyles.bodyMedium.copyWith(
                            color: AppColors.textTertiary,
                            fontSize: 14,
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 4),
              child: Align(
                alignment: Alignment.centerLeft,
                child: Text(
                  l10n.chatRecentChats,
                  style: AppTextStyles.labelSmall.copyWith(
                    color: AppColors.textTertiary,
                    letterSpacing: 0.6,
                  ),
                ),
              ),
            ),
            Expanded(
              child: filtered.isEmpty
                  ? _empty(context)
                  : ListView.builder(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 8, vertical: 4),
                      itemCount: filtered.length.clamp(0, 50),
                      itemBuilder: (_, i) {
                        final c = filtered[i];
                        return _ChatTile(
                          conversation: c,
                          active: c.id == widget.currentId,
                          onTap: () {
                            Navigator.of(context).maybePop();
                            widget.onSelect(c.id);
                          },
                          onDelete: () => widget.onDelete(c.id),
                        );
                      },
                    ),
            ),
            const Divider(
                height: 1, thickness: 1, color: AppColors.borderSubtle),
            Padding(
              padding: const EdgeInsets.fromLTRB(14, 8, 14, 8),
              child: Column(
                children: [
                  _PrimaryActionTile(
                    icon: Icons.settings_rounded,
                    label: l10n.chatSettings,
                    subtle: true,
                    onTap: () {
                      Navigator.of(context).maybePop();
                      widget.onSettings();
                    },
                  ),
                  const SizedBox(height: 6),
                  _PrimaryActionTile(
                    icon: Icons.credit_card_outlined,
                    label: l10n.settingsSubscriptionButton,
                    subtle: true,
                    onTap: () {
                      Navigator.of(context).maybePop();
                      widget.onSubscription();
                    },
                  ),
                  const SizedBox(height: 6),
                  Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 10, vertical: 8),
                    decoration: BoxDecoration(
                      color: AppColors.surfaceVariant,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: AppColors.borderSubtle),
                    ),
                    child: Row(
                      children: [
                        Container(
                          width: 32,
                          height: 32,
                          decoration: BoxDecoration(
                            gradient: AppColors.primaryGradient,
                            borderRadius: BorderRadius.circular(8),
                          ),
                          alignment: Alignment.center,
                          child: Text(
                            (widget.userEmail ?? 'U')
                                .substring(0, 1)
                                .toUpperCase(),
                            style: AppTextStyles.labelMedium.copyWith(
                              color: AppColors.white,
                              fontWeight: FontWeight.w700,
                            ),
                          ),
                        ),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Text(
                            widget.userEmail ?? 'User',
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: AppTextStyles.bodySmall.copyWith(
                              color: AppColors.textPrimary,
                            ),
                          ),
                        ),
                        IconButton(
                          tooltip: l10n.chatLogoutTooltip,
                          onPressed: () {
                            Navigator.of(context).maybePop();
                            widget.onLogout();
                          },
                          icon: Icon(Icons.logout_rounded,
                              size: 18, color: AppColors.textSecondary),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _empty(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Text(
          l10n.chatNoConversations,
          style: AppTextStyles.bodySmall.copyWith(
            color: AppColors.textTertiary,
          ),
        ),
      ),
    );
  }
}

class _PrimaryActionTile extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;
  final bool subtle;
  const _PrimaryActionTile({
    required this.icon,
    required this.label,
    required this.onTap,
    this.subtle = false,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
        decoration: BoxDecoration(
          color: subtle ? AppColors.surfaceVariant : null,
          gradient: subtle ? null : AppColors.primaryGradient,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: subtle
                ? AppColors.borderSubtle
                : AppColors.transparent,
          ),
        ),
        child: Row(
          children: [
            Icon(
              icon,
              size: 18,
              color: subtle ? AppColors.textPrimary : AppColors.white,
            ),
            const SizedBox(width: 10),
            Text(
              label,
              style: AppTextStyles.bodyMedium.copyWith(
                color: subtle ? AppColors.textPrimary : AppColors.white,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ChatTile extends StatelessWidget {
  final Conversation conversation;
  final bool active;
  final VoidCallback onTap;
  final VoidCallback onDelete;

  const _ChatTile({
    required this.conversation,
    required this.active,
    required this.onTap,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Material(
        color: AppColors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(10),
          child: Container(
            padding:
                const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
            decoration: BoxDecoration(
              color: active
                  ? AppColors.primary.withValues(alpha: 0.10)
                  : null,
              borderRadius: BorderRadius.circular(10),
              border: active
                  ? Border.all(
                      color: AppColors.primary.withValues(alpha: 0.30))
                  : null,
            ),
            child: Row(
              children: [
                Icon(Icons.chat_bubble_outline_rounded,
                    size: 16, color: AppColors.textSecondary),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    conversation.title.isEmpty
                        ? l10n.chatNewChat
                        : conversation.title,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: AppTextStyles.bodySmall.copyWith(
                      color: AppColors.textPrimary,
                    ),
                  ),
                ),
                IconButton(
                  iconSize: 16,
                  splashRadius: 18,
                  padding: EdgeInsets.zero,
                  constraints:
                      const BoxConstraints(minWidth: 28, minHeight: 28),
                  onPressed: () {
                    showDialog<void>(
                      context: context,
                      builder: (ctx) => AlertDialog(
                        backgroundColor: AppColors.cardBackground,
                        title: Text(
                          l10n.chatDeleteTitle,
                          style: AppTextStyles.titleMedium,
                        ),
                        content: Text(
                          l10n.chatDeleteBody,
                          style: AppTextStyles.bodyMedium.copyWith(
                            color: AppColors.textSecondary,
                          ),
                        ),
                        actions: [
                          TextButton(
                            onPressed: () => Navigator.of(ctx).pop(),
                            child: Text(
                              l10n.chatCancel,
                              style: AppTextStyles.labelMedium.copyWith(
                                color: AppColors.textSecondary,
                              ),
                            ),
                          ),
                          TextButton(
                            onPressed: () {
                              Navigator.of(ctx).pop();
                              onDelete();
                            },
                            child: Text(
                              l10n.chatDelete,
                              style: AppTextStyles.labelMedium.copyWith(
                                color: AppColors.error,
                                fontWeight: FontWeight.w700,
                              ),
                            ),
                          ),
                        ],
                      ),
                    );
                  },
                  icon: Icon(
                    Icons.delete_outline_rounded,
                    color: AppColors.textTertiary,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
