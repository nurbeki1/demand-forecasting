import 'package:flutter/material.dart';
import '../../../core/theme/theme.dart';

/// History Screen - Chat history based on Figma design
class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  final List<ChatHistoryItem> _historyItems = [
    ChatHistoryItem(
      title: 'Product demand forecast',
      subtitle: 'P0001 forecast for 7 days',
      date: DateTime.now().subtract(const Duration(hours: 2)),
    ),
    ChatHistoryItem(
      title: 'Sales analysis',
      subtitle: 'Analyze sales trends',
      date: DateTime.now().subtract(const Duration(days: 1)),
    ),
    ChatHistoryItem(
      title: 'Inventory prediction',
      subtitle: 'P0003 stock levels',
      date: DateTime.now().subtract(const Duration(days: 2)),
    ),
    ChatHistoryItem(
      title: 'Seasonal trends',
      subtitle: 'Q4 demand patterns',
      date: DateTime.now().subtract(const Duration(days: 3)),
    ),
    ChatHistoryItem(
      title: 'Product comparison',
      subtitle: 'P0001 vs P0002 forecast',
      date: DateTime.now().subtract(const Duration(days: 5)),
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: Column(
          children: [
            // Header
            _buildHeader(),

            const Divider(height: 1, color: AppColors.divider),

            // Search bar
            _buildSearchBar(),

            // History list
            Expanded(
              child: _historyItems.isEmpty
                  ? _buildEmptyState()
                  : ListView.separated(
                      padding: const EdgeInsets.all(AppDimensions.spacing16),
                      itemCount: _historyItems.length,
                      separatorBuilder: (_, __) => const SizedBox(
                        height: AppDimensions.spacing12,
                      ),
                      itemBuilder: (context, index) {
                        return _HistoryCard(item: _historyItems[index]);
                      },
                    ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AppDimensions.spacing16,
        vertical: AppDimensions.spacing12,
      ),
      child: Row(
        children: [
          // Icon
          Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              color: AppColors.primary10,
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Icon(
              Icons.history_rounded,
              size: 18,
              color: AppColors.primary,
            ),
          ),

          const SizedBox(width: AppDimensions.spacing12),

          // Title
          Text(
            'History',
            style: AppTextStyles.titleMedium,
          ),

          const Spacer(),

          // Clear all button
          TextButton(
            onPressed: () {
              // TODO: Clear history
            },
            child: Text(
              'Clear all',
              style: AppTextStyles.labelMedium.copyWith(
                color: AppColors.textSecondary,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSearchBar() {
    return Padding(
      padding: const EdgeInsets.all(AppDimensions.spacing16),
      child: Container(
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
          border: Border.all(color: AppColors.border),
        ),
        child: TextField(
          decoration: InputDecoration(
            hintText: 'Search history...',
            hintStyle: AppTextStyles.bodyMedium.copyWith(
              color: AppColors.textHint,
            ),
            prefixIcon: const Icon(
              Icons.search,
              color: AppColors.iconVariant,
            ),
            border: InputBorder.none,
            contentPadding: const EdgeInsets.symmetric(
              horizontal: AppDimensions.spacing16,
              vertical: AppDimensions.spacing14,
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              color: AppColors.primary10,
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.history_rounded,
              size: 40,
              color: AppColors.primary,
            ),
          ),
          const SizedBox(height: AppDimensions.spacing24),
          Text(
            'No history yet',
            style: AppTextStyles.titleMedium,
          ),
          const SizedBox(height: AppDimensions.spacing8),
          Text(
            'Your chat history will appear here',
            style: AppTextStyles.bodyMedium.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
        ],
      ),
    );
  }
}

class ChatHistoryItem {
  final String title;
  final String subtitle;
  final DateTime date;

  ChatHistoryItem({
    required this.title,
    required this.subtitle,
    required this.date,
  });

  String get formattedDate {
    final now = DateTime.now();
    final diff = now.difference(date);

    if (diff.inHours < 24) {
      return '${diff.inHours}h ago';
    } else if (diff.inDays < 7) {
      return '${diff.inDays}d ago';
    } else {
      return '${date.day}/${date.month}/${date.year}';
    }
  }
}

class _HistoryCard extends StatelessWidget {
  final ChatHistoryItem item;

  const _HistoryCard({required this.item});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(AppDimensions.spacing16),
      decoration: BoxDecoration(
        color: AppColors.cardBackground,
        borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
      ),
      child: Row(
        children: [
          // Chat icon
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: AppColors.primary10,
              borderRadius: BorderRadius.circular(AppDimensions.radiusSm),
            ),
            child: const Icon(
              Icons.chat_bubble_outline_rounded,
              size: 20,
              color: AppColors.primary,
            ),
          ),

          const SizedBox(width: AppDimensions.spacing12),

          // Content
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  item.title,
                  style: AppTextStyles.labelLarge,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: AppDimensions.spacing4),
                Text(
                  item.subtitle,
                  style: AppTextStyles.bodySmall.copyWith(
                    color: AppColors.textMuted,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),

          const SizedBox(width: AppDimensions.spacing8),

          // Date
          Text(
            item.formattedDate,
            style: AppTextStyles.caption,
          ),

          const SizedBox(width: AppDimensions.spacing8),

          // Arrow
          const Icon(
            Icons.chevron_right,
            color: AppColors.iconVariant,
            size: 20,
          ),
        ],
      ),
    );
  }
}