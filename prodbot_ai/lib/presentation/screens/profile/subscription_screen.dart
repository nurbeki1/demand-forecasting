import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/theme/theme.dart';
import '../../../l10n/app_localizations.dart';
import '../../../services/auth_service.dart';

/// Placeholder subscription / upgrade screen. Opens while the user is already
/// logged in (`pushNamed`) — no redirect to the login page.
class SubscriptionScreen extends StatelessWidget {
  const SubscriptionScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final auth = context.watch<AuthService>();
    final email = auth.currentUserEmail;
    final premium = auth.canUsePremiumMlModels;
    final planLabel =
        premium ? l10n.subscriptionPlanPremium : l10n.subscriptionPlanFree;

    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(8, 8, 12, 8),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  IconButton(
                    icon: const Icon(Icons.arrow_back_rounded, size: 22),
                    color: AppColors.textSecondary,
                    onPressed: () => Navigator.of(context).maybePop(),
                  ),
                  const SizedBox(width: 4),
                  Expanded(
                    child: Text(
                      l10n.subscriptionScreenTitle,
                      style: AppTextStyles.titleLarge.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ],
              ),
            ),
            if (email != null && email.isNotEmpty)
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 0, 16, 10),
                child: Align(
                  alignment: Alignment.centerRight,
                  child: _AccountMetaChip(
                    email: email,
                    planLabel: planLabel,
                    premium: premium,
                  ),
                ),
              ),
            const Divider(height: 1, color: AppColors.borderSubtle),
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.fromLTRB(20, 24, 20, 32),
                child: Text(
                  l10n.subscriptionPlaceholderBody,
                  style: AppTextStyles.bodyMedium.copyWith(
                    color: AppColors.textSecondary,
                    height: 1.45,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Secondary context — same idea as web `.subscription-account-meta`.
class _AccountMetaChip extends StatelessWidget {
  final String email;
  final String planLabel;
  final bool premium;

  const _AccountMetaChip({
    required this.email,
    required this.planLabel,
    required this.premium,
  });

  @override
  Widget build(BuildContext context) {
    return Tooltip(
      message: '$email — $planLabel',
      child: Container(
        constraints: const BoxConstraints(maxWidth: 340),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: Colors.black.withValues(alpha: 0.35),
          borderRadius: BorderRadius.circular(999),
          border: Border.all(color: Colors.white.withValues(alpha: 0.08)),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Flexible(
              child: Text(
                email,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: AppTextStyles.labelSmall.copyWith(
                  color: AppColors.textSecondary,
                  fontSize: 12,
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 6),
              child: Text(
                '·',
                style: TextStyle(
                  color: AppColors.textTertiary.withValues(alpha: 0.45),
                  fontSize: 12,
                ),
              ),
            ),
            Text(
              planLabel.toUpperCase(),
              style: AppTextStyles.labelSmall.copyWith(
                fontSize: 10,
                fontWeight: FontWeight.w700,
                letterSpacing: 0.4,
                color: premium
                    ? const Color(0xFF34D399)
                    : AppColors.textTertiary,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
