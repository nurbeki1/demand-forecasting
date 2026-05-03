import 'package:flutter/material.dart';

import '../../../../core/theme/theme.dart';
import '../../../../l10n/app_localizations.dart';

/// Mirrors web ModelSelector definition (`frontend-admin/src/pages/ChatPage.jsx`).
class ModelOption {
  final String value;
  final String label;
  final String name;
  final String description;
  final Color color;
  const ModelOption({
    required this.value,
    required this.label,
    required this.name,
    required this.description,
    required this.color,
  });
}

List<ModelOption> modelOptions(AppLocalizations l10n) => [
      ModelOption(
        value: 'random_forest',
        label: 'RF',
        name: 'Random Forest',
        description: l10n.modelRfDesc,
        color: const Color(0xFF60A5FA),
      ),
      ModelOption(
        value: 'lightgbm',
        label: 'LGBM',
        name: 'LightGBM',
        description: l10n.modelLgbmDesc,
        color: const Color(0xFF34D399),
      ),
      ModelOption(
        value: 'xgboost',
        label: 'XGB',
        name: 'XGBoost',
        description: l10n.modelXgbDesc,
        color: const Color(0xFFF59E0B),
      ),
    ];

/// Compact pill that shows the active model and opens a bottom-sheet picker.
class ModelSelector extends StatelessWidget {
  final String value;
  final ValueChanged<String> onChanged;
  /// When false, only `random_forest` is selectable (free tier).
  final bool premiumUnlocked;

  const ModelSelector({
    super.key,
    required this.value,
    required this.onChanged,
    this.premiumUnlocked = false,
  });

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final options = modelOptions(l10n);
    final effectiveValue =
        premiumUnlocked ? value : 'random_forest';
    final selected = options.firstWhere(
      (m) => m.value == effectiveValue,
      orElse: () => options.first,
    );
    return InkWell(
      onTap: () => _open(context),
      borderRadius: BorderRadius.circular(999),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
        decoration: BoxDecoration(
          color: AppColors.surfaceVariant,
          borderRadius: BorderRadius.circular(999),
          border: Border.all(color: AppColors.borderSubtle),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              selected.label,
              style: AppTextStyles.labelSmall.copyWith(
                color: selected.color,
                fontWeight: FontWeight.w700,
              ),
            ),
            const SizedBox(width: 4),
            Icon(
              Icons.keyboard_arrow_down_rounded,
              size: 16,
              color: AppColors.textSecondary,
            ),
          ],
        ),
      ),
    );
  }

  void _open(BuildContext context) {
    showModalBottomSheet<void>(
      context: context,
      backgroundColor: AppColors.cardBackground,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) {
        final sheetL10n = AppLocalizations.of(ctx)!;
        final opts = modelOptions(sheetL10n);
        final sheetValue = premiumUnlocked ? value : 'random_forest';
        return SafeArea(
          child: Padding(
            padding: const EdgeInsets.fromLTRB(16, 12, 16, 16),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Center(
                  child: Container(
                    width: 36,
                    height: 4,
                    decoration: BoxDecoration(
                      color: AppColors.border,
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                ),
                const SizedBox(height: 14),
                Text(
                  sheetL10n.modelPickerTitle,
                  style: AppTextStyles.titleMedium.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 12),
                ...opts.map((m) {
                  final locked =
                      !premiumUnlocked && m.value != 'random_forest';
                  final selected = m.value == sheetValue;
                  return InkWell(
                    onTap: locked
                        ? null
                        : () {
                            onChanged(m.value);
                            Navigator.of(ctx).pop();
                          },
                    borderRadius: BorderRadius.circular(12),
                    child: Opacity(
                      opacity: locked ? 0.5 : 1,
                      child: Container(
                        margin: const EdgeInsets.only(bottom: 8),
                        padding: const EdgeInsets.all(14),
                        decoration: BoxDecoration(
                          color: selected
                              ? m.color.withValues(alpha: 0.10)
                              : AppColors.surfaceVariant,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                            color: selected
                                ? m.color.withValues(alpha: 0.45)
                                : AppColors.borderSubtle,
                          ),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Text(
                                  m.name,
                                  style: AppTextStyles.titleSmall.copyWith(
                                    color: locked
                                        ? AppColors.textSecondary
                                        : m.color,
                                    fontWeight: FontWeight.w700,
                                  ),
                                ),
                                const Spacer(),
                                if (selected && !locked)
                                  Icon(Icons.check_rounded,
                                      size: 18, color: m.color),
                              ],
                            ),
                            const SizedBox(height: 4),
                            Text(
                              locked
                                  ? sheetL10n.modelRequiresSubscription
                                  : m.description,
                              style: AppTextStyles.bodySmall.copyWith(
                                color: AppColors.textSecondary,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  );
                }),
              ],
            ),
          ),
        );
      },
    );
  }
}
