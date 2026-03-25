import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../../../core/theme/theme.dart';

enum ForecastStatus { active, completed, draft }

class ForecastData {
  final String id;
  final String productId;
  final String productName;
  final DateTime createdAt;
  final int horizon;
  final double? accuracy;
  final ForecastStatus status;

  ForecastData({
    required this.id,
    required this.productId,
    required this.productName,
    required this.createdAt,
    required this.horizon,
    this.accuracy,
    required this.status,
  });

  String get statusText {
    switch (status) {
      case ForecastStatus.active:
        return 'Active';
      case ForecastStatus.completed:
        return 'Completed';
      case ForecastStatus.draft:
        return 'Draft';
    }
  }

  Color get statusColor {
    switch (status) {
      case ForecastStatus.active:
        return AppColors.info;
      case ForecastStatus.completed:
        return AppColors.success;
      case ForecastStatus.draft:
        return AppColors.warning;
    }
  }
}

class ForecastCard extends StatelessWidget {
  final ForecastData forecast;
  final VoidCallback? onTap;

  const ForecastCard({
    super.key,
    required this.forecast,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(AppDimensions.spacing16),
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
          border: Border.all(color: AppColors.border),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header row
            Row(
              children: [
                // Product icon
                Container(
                  width: 44,
                  height: 44,
                  decoration: BoxDecoration(
                    color: AppColors.primary10,
                    borderRadius: BorderRadius.circular(AppDimensions.radiusSm),
                  ),
                  child: const Icon(
                    Icons.inventory_2_outlined,
                    color: AppColors.primary,
                    size: 22,
                  ),
                ),

                const SizedBox(width: AppDimensions.spacing12),

                // Product info
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        forecast.productName,
                        style: AppTextStyles.labelLarge,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 2),
                      Text(
                        forecast.productId,
                        style: AppTextStyles.caption,
                      ),
                    ],
                  ),
                ),

                // Status badge
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: AppDimensions.spacing10,
                    vertical: AppDimensions.spacing4,
                  ),
                  decoration: BoxDecoration(
                    color: forecast.statusColor.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(AppDimensions.radiusFull),
                  ),
                  child: Text(
                    forecast.statusText,
                    style: AppTextStyles.labelSmall.copyWith(
                      color: forecast.statusColor,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),

            const SizedBox(height: AppDimensions.spacing16),

            // Metrics row
            Row(
              children: [
                // Horizon
                _MetricItem(
                  icon: Icons.calendar_today_outlined,
                  label: 'Horizon',
                  value: '${forecast.horizon} days',
                ),

                const SizedBox(width: AppDimensions.spacing24),

                // Accuracy
                if (forecast.accuracy != null)
                  _MetricItem(
                    icon: Icons.show_chart,
                    label: 'Accuracy',
                    value: '${forecast.accuracy!.toStringAsFixed(1)}%',
                    valueColor: _getAccuracyColor(forecast.accuracy!),
                  ),

                const Spacer(),

                // Date
                Text(
                  _formatDate(forecast.createdAt),
                  style: AppTextStyles.caption,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final diff = now.difference(date);

    if (diff.inHours < 24) {
      if (diff.inHours < 1) {
        return '${diff.inMinutes}m ago';
      }
      return '${diff.inHours}h ago';
    } else if (diff.inDays < 7) {
      return '${diff.inDays}d ago';
    }
    return DateFormat('MMM d').format(date);
  }

  Color _getAccuracyColor(double accuracy) {
    if (accuracy >= 90) return AppColors.success;
    if (accuracy >= 80) return AppColors.warning;
    return AppColors.error;
  }
}

class _MetricItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color? valueColor;

  const _MetricItem({
    required this.icon,
    required this.label,
    required this.value,
    this.valueColor,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(
          icon,
          size: 16,
          color: AppColors.iconVariant,
        ),
        const SizedBox(width: AppDimensions.spacing6),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              label,
              style: AppTextStyles.caption.copyWith(
                fontSize: 10,
              ),
            ),
            Text(
              value,
              style: AppTextStyles.labelMedium.copyWith(
                color: valueColor ?? AppColors.textPrimary,
              ),
            ),
          ],
        ),
      ],
    );
  }
}

/// Accuracy indicator widget
class AccuracyIndicator extends StatelessWidget {
  final double accuracy;
  final double size;

  const AccuracyIndicator({
    super.key,
    required this.accuracy,
    this.size = 60,
  });

  Color get _color {
    if (accuracy >= 90) return AppColors.success;
    if (accuracy >= 80) return AppColors.warning;
    return AppColors.error;
  }

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: size,
      height: size,
      child: Stack(
        children: [
          // Background circle
          CircularProgressIndicator(
            value: 1,
            strokeWidth: 6,
            backgroundColor: _color.withValues(alpha: 0.2),
            valueColor: AlwaysStoppedAnimation(_color.withValues(alpha: 0.2)),
          ),
          // Progress circle
          CircularProgressIndicator(
            value: accuracy / 100,
            strokeWidth: 6,
            backgroundColor: Colors.transparent,
            valueColor: AlwaysStoppedAnimation(_color),
          ),
          // Center text
          Center(
            child: Text(
              '${accuracy.toInt()}%',
              style: AppTextStyles.labelLarge.copyWith(
                color: _color,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
