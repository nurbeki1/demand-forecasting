import 'package:flutter/material.dart';
import '../../../../core/theme/theme.dart';
import 'suggestion_card.dart';

class ChatMessageData {
  final String text;
  final bool isUser;
  final bool showSuggestions;
  final DateTime? timestamp;

  ChatMessageData({
    required this.text,
    required this.isUser,
    this.showSuggestions = false,
    this.timestamp,
  });
}

class ChatMessage extends StatelessWidget {
  final ChatMessageData data;
  final Function(String)? onSuggestionTap;

  const ChatMessage({
    super.key,
    required this.data,
    this.onSuggestionTap,
  });

  static const List<String> _suggestions = [
    'Ask the system about future demand.',
    'Analyze sales, trends, and seasonality',
  ];

  @override
  Widget build(BuildContext context) {
    if (data.isUser) {
      return _buildUserMessage();
    }
    return _buildBotMessage();
  }

  Widget _buildUserMessage() {
    return Padding(
      padding: const EdgeInsets.only(bottom: AppDimensions.spacing12),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.end,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(width: AppDimensions.spacing48),
          Flexible(
            child: Container(
              padding: const EdgeInsets.symmetric(
                horizontal: AppDimensions.spacing16,
                vertical: AppDimensions.spacing12,
              ),
              decoration: BoxDecoration(
                color: AppColors.primary,
                borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
              ),
              child: Text(
                data.text,
                style: AppTextStyles.bodyMedium.copyWith(
                  color: AppColors.white,
                ),
              ),
            ),
          ),
          const SizedBox(width: AppDimensions.spacing8),
          // User avatar
          Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              color: AppColors.primary20,
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Icon(
              Icons.person,
              size: 18,
              color: AppColors.primary,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBotMessage() {
    return Padding(
      padding: const EdgeInsets.only(bottom: AppDimensions.spacing12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Bot avatar
              Container(
                width: 32,
                height: 32,
                decoration: BoxDecoration(
                  color: AppColors.primary10,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(
                  Icons.smart_toy_rounded,
                  size: 18,
                  color: AppColors.primary,
                ),
              ),
              const SizedBox(width: AppDimensions.spacing8),
              Flexible(
                child: Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: AppDimensions.spacing16,
                    vertical: AppDimensions.spacing12,
                  ),
                  decoration: BoxDecoration(
                    color: AppColors.chatBubble,
                    borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
                  ),
                  child: Text(
                    data.text,
                    style: AppTextStyles.bodyMedium.copyWith(
                      color: AppColors.textMuted,  // Figma: #847F7F
                    ),
                  ),
                ),
              ),
              const SizedBox(width: AppDimensions.spacing48),
            ],
          ),

          // Show suggestions
          if (data.showSuggestions) ...[
            const SizedBox(height: AppDimensions.spacing12),
            ..._suggestions.map((suggestion) => Padding(
                  padding: const EdgeInsets.only(
                    left: 40,
                    bottom: AppDimensions.spacing8,
                  ),
                  child: SuggestionCard(
                    text: suggestion,
                    onTap: () => onSuggestionTap?.call(suggestion),
                  ),
                )),
          ],
        ],
      ),
    );
  }
}
