import 'package:flutter/material.dart';

import '../../../../core/theme/theme.dart';
import '../../../../data/models/conversation.dart';
import '../../../../l10n/app_localizations.dart';
import '../../../widgets/common/brand_logo.dart';
import 'kz_analysis_card.dart';
import 'markdown_view.dart';
import 'mini_chart.dart';
import 'product_carousel.dart';

/// Single message row matching the web `.message.user` / `.message.assistant`
/// layout. Aligns avatar + role label + content (text, products, chart, KZ card,
/// follow-up suggestions) similarly to `frontend-admin/src/pages/ChatPage.jsx`.
class MessageBubble extends StatelessWidget {
  final ChatMessage message;
  final String userInitial;
  final ValueChanged<String> onSuggestionTap;
  final Future<void> Function(int markup)? onKZRecalculate;

  const MessageBubble({
    super.key,
    required this.message,
    required this.userInitial,
    required this.onSuggestionTap,
    this.onKZRecalculate,
  });

  @override
  Widget build(BuildContext context) {
    final isUser = message.isUser;
    final l10n = AppLocalizations.of(context)!;

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 10),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _avatar(isUser),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  isUser ? l10n.roleYou : l10n.roleAiAssistant,
                  style: AppTextStyles.labelSmall.copyWith(
                    color: AppColors.textTertiary,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 6),
                _bubble(),
                if (message.images != null && message.images!.isNotEmpty)
                  ProductCarousel(images: message.images!),
                if (message.data != null) MiniChart(data: message.data!),
                if (message.kzData != null)
                  KZAnalysisCard(
                    data: message.kzData!,
                    onMarkupChange: onKZRecalculate,
                  ),
                if (!isUser &&
                    message.suggestedQuestions != null &&
                    message.suggestedQuestions!.isNotEmpty)
                  _suggestedFollowUps(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _avatar(bool isUser) {
    if (!isUser) {
      return const BrandLogo(size: 32, radius: 8);
    }
    return Container(
      width: 32,
      height: 32,
      decoration: BoxDecoration(
        color: AppColors.surfaceVariant,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: AppColors.borderSubtle),
      ),
      alignment: Alignment.center,
      child: Text(
        userInitial,
        style: AppTextStyles.labelMedium.copyWith(
          color: AppColors.textPrimary,
          fontWeight: FontWeight.w700,
        ),
      ),
    );
  }

  Widget _bubble() {
    final isUser = message.isUser;
    if (isUser) {
      return Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        decoration: BoxDecoration(
          gradient: AppColors.primaryGradient,
          borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
          boxShadow: [
            BoxShadow(
              color: AppColors.primary.withValues(alpha: 0.25),
              blurRadius: 14,
              offset: const Offset(0, 6),
            ),
          ],
        ),
        child: Text(
          message.content,
          style: AppTextStyles.bodyMedium.copyWith(
            color: AppColors.white,
            height: 1.45,
          ),
        ),
      );
    }
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      decoration: BoxDecoration(
        color: AppColors.surfaceVariant,
        borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
        border: Border.all(color: AppColors.borderSubtle),
      ),
      child: MarkdownView(text: message.content),
    );
  }

  Widget _suggestedFollowUps() {
    return Padding(
      padding: const EdgeInsets.only(top: 10),
      child: Wrap(
        spacing: 8,
        runSpacing: 8,
        children: message.suggestedQuestions!
            .take(4)
            .map(
              (q) => InkWell(
                onTap: () => onSuggestionTap(q),
                borderRadius: BorderRadius.circular(999),
                child: Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 12, vertical: 8),
                  decoration: BoxDecoration(
                    color: AppColors.surfaceVariant,
                    borderRadius: BorderRadius.circular(999),
                    border: Border.all(color: AppColors.borderSubtle),
                  ),
                  child: Text(
                    q,
                    style: AppTextStyles.labelMedium.copyWith(
                      color: AppColors.textPrimary,
                    ),
                  ),
                ),
              ),
            )
            .toList(),
      ),
    );
  }
}

/// Three-dot typing indicator shown while the assistant is generating.
class TypingBubble extends StatefulWidget {
  const TypingBubble({super.key});

  @override
  State<TypingBubble> createState() => _TypingBubbleState();
}

class _TypingBubbleState extends State<TypingBubble>
    with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    )..repeat();
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 10),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const BrandLogo(size: 32, radius: 8),
          const SizedBox(width: 12),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
            decoration: BoxDecoration(
              color: AppColors.surfaceVariant,
              borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
              border: Border.all(color: AppColors.borderSubtle),
            ),
            child: AnimatedBuilder(
              animation: _ctrl,
              builder: (context, _) => Row(
                mainAxisSize: MainAxisSize.min,
                children: List.generate(3, (i) {
                  final t = (_ctrl.value + i / 3) % 1.0;
                  final opacity = (0.4 + 0.6 * (t < 0.5 ? t * 2 : 2 - t * 2))
                      .clamp(0.3, 1.0);
                  return Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 2),
                    child: Container(
                      width: 6,
                      height: 6,
                      decoration: BoxDecoration(
                        color: AppColors.primary
                            .withValues(alpha: opacity.toDouble()),
                        shape: BoxShape.circle,
                      ),
                    ),
                  );
                }),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
