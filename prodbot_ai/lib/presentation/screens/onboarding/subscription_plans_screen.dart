import 'package:flutter/material.dart';

import '../../../core/theme/theme.dart';
import '../../../l10n/app_localizations.dart';
import '../auth/register_screen.dart';

/// Pricing / subscription tiers — opened from welcome «Қазір бастау».
/// Visual tone: dark canvas, teal→cyan accents (matches landing reference).
class SubscriptionPlansScreen extends StatelessWidget {
  const SubscriptionPlansScreen({super.key});

  void _openRegister(BuildContext context) {
    Navigator.of(context).push(
      MaterialPageRoute<void>(builder: (_) => const RegisterScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;

    return Scaffold(
      backgroundColor: AppColors.background,
      body: Stack(
        children: [
          Positioned.fill(
            child: DecoratedBox(
              decoration: BoxDecoration(
                gradient: RadialGradient(
                  center: const Alignment(0, -0.55),
                  radius: 1.15,
                  colors: [
                    AppColors.primary.withValues(alpha: 0.22),
                    AppColors.secondary.withValues(alpha: 0.08),
                    Colors.transparent,
                  ],
                  stops: const [0.0, 0.42, 1.0],
                ),
              ),
            ),
          ),
          CustomScrollView(
            slivers: [
              SliverAppBar(
                pinned: true,
                backgroundColor: AppColors.background.withValues(alpha: 0.85),
                elevation: 0,
                leading: IconButton(
                  icon: Icon(Icons.arrow_back_rounded,
                      color: AppColors.textSecondary),
                  onPressed: () => Navigator.of(context).maybePop(),
                ),
              ),
              SliverPadding(
                padding: const EdgeInsets.fromLTRB(20, 0, 20, 36),
                sliver: SliverList(
                  delegate: SliverChildListDelegate([
                    Text(
                      l10n.subscriptionHeroHeadline,
                      style: AppTextStyles.headlineMedium.copyWith(
                        color: AppColors.textPrimary,
                        height: 1.2,
                        fontWeight: FontWeight.w800,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 12),
                    Text(
                      l10n.subscriptionPlansTitle,
                      style: AppTextStyles.titleLarge.copyWith(
                        color: AppColors.textSecondary,
                        fontWeight: FontWeight.w600,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      l10n.subscriptionPlansSubtitle,
                      style: AppTextStyles.bodyMedium.copyWith(
                        color: AppColors.textTertiary,
                        height: 1.45,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 28),
                    _PlanCard(
                      name: l10n.subscriptionPlanStarter,
                      priceLine: l10n.subscriptionPriceFree,
                      features: [
                        l10n.subscriptionFeatFree1,
                        l10n.subscriptionFeatFree2,
                        l10n.subscriptionFeatFree3,
                      ],
                      highlighted: false,
                      ctaLabel: l10n.subscriptionCtaFree,
                      onCta: () => _openRegister(context),
                      useGradientCta: false,
                    ),
                    const SizedBox(height: 14),
                    _PlanCard(
                      name: l10n.subscriptionPlanPro,
                      priceLine: l10n.subscriptionPriceProMonthly,
                      features: [
                        l10n.subscriptionFeatPro1,
                        l10n.subscriptionFeatPro2,
                        l10n.subscriptionFeatPro3,
                      ],
                      highlighted: true,
                      badgeText: l10n.subscriptionRecommended,
                      ctaLabel: l10n.subscriptionCtaPro,
                      onCta: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text(l10n.subscriptionBillingSoon),
                            behavior: SnackBarBehavior.floating,
                          ),
                        );
                        _openRegister(context);
                      },
                      useGradientCta: true,
                    ),
                    const SizedBox(height: 14),
                    _PlanCard(
                      name: l10n.subscriptionPlanEnterprise,
                      priceLine: l10n.subscriptionPriceEnterprise,
                      features: [
                        l10n.subscriptionFeatEnt1,
                        l10n.subscriptionFeatEnt2,
                        l10n.subscriptionFeatEnt3,
                      ],
                      highlighted: false,
                      ctaLabel: l10n.subscriptionCtaEnterprise,
                      onCta: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text(l10n.subscriptionBillingSoon),
                            behavior: SnackBarBehavior.floating,
                          ),
                        );
                        _openRegister(context);
                      },
                      useGradientCta: false,
                    ),
                  ]),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _PlanCard extends StatelessWidget {
  final String name;
  final String priceLine;
  final List<String> features;
  final bool highlighted;
  final String? badgeText;
  final String ctaLabel;
  final VoidCallback onCta;
  final bool useGradientCta;

  const _PlanCard({
    required this.name,
    required this.priceLine,
    required this.features,
    required this.highlighted,
    this.badgeText,
    required this.ctaLabel,
    required this.onCta,
    required this.useGradientCta,
  });

  static const _ctaTextOnGradient = Color(0xFF0A0A0F);

  @override
  Widget build(BuildContext context) {
    final inner = Container(
      padding: const EdgeInsets.fromLTRB(18, 18, 18, 16),
      decoration: BoxDecoration(
        color: AppColors.cardBackground,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: highlighted
              ? AppColors.transparent
              : AppColors.border,
        ),
        boxShadow: highlighted
            ? [
                BoxShadow(
                  color: AppColors.primary.withValues(alpha: 0.12),
                  blurRadius: 28,
                  spreadRadius: -6,
                  offset: const Offset(0, 14),
                ),
              ]
            : null,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      name,
                      style: AppTextStyles.titleMedium.copyWith(
                        fontWeight: FontWeight.w800,
                        color: AppColors.textPrimary,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      priceLine,
                      style: AppTextStyles.headlineSmall.copyWith(
                        color: highlighted
                            ? AppColors.primary60
                            : AppColors.textSecondary,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ],
                ),
              ),
              if (badgeText != null)
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 10,
                    vertical: 5,
                  ),
                  decoration: BoxDecoration(
                    gradient: AppColors.primaryGradient,
                    borderRadius: BorderRadius.circular(999),
                  ),
                  child: Text(
                    badgeText!,
                    style: AppTextStyles.labelSmall.copyWith(
                      color: _ctaTextOnGradient,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                ),
            ],
          ),
          const SizedBox(height: 16),
          ...features.map(
            (f) => Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(
                    Icons.check_circle_rounded,
                    size: 20,
                    color: AppColors.primary,
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      f,
                      style: AppTextStyles.bodySmall.copyWith(
                        color: AppColors.textSecondary,
                        height: 1.35,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 8),
          if (useGradientCta)
            _GradientPillButton(
              label: ctaLabel,
              onTap: onCta,
            )
          else
            OutlinedButton(
              onPressed: onCta,
              style: OutlinedButton.styleFrom(
                foregroundColor: AppColors.textPrimary,
                side: const BorderSide(color: AppColors.borderStrong),
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(999),
                ),
              ),
              child: Text(
                ctaLabel,
                style: AppTextStyles.labelLarge.copyWith(
                  fontWeight: FontWeight.w700,
                ),
              ),
            ),
        ],
      ),
    );

    if (!highlighted) return inner;

    return Container(
      decoration: BoxDecoration(
        gradient: AppColors.primaryGradient,
        borderRadius: BorderRadius.circular(22),
        boxShadow: [
          BoxShadow(
            color: AppColors.primary.withValues(alpha: 0.25),
            blurRadius: 24,
            offset: const Offset(0, 12),
          ),
        ],
      ),
      padding: const EdgeInsets.all(2),
      child: inner,
    );
  }
}

class _GradientPillButton extends StatelessWidget {
  final String label;
  final VoidCallback onTap;

  const _GradientPillButton({
    required this.label,
    required this.onTap,
  });

  static const _fg = Color(0xFF0A0A0F);

  @override
  Widget build(BuildContext context) {
    return DecoratedBox(
      decoration: BoxDecoration(
        gradient: AppColors.primaryGradientBright,
        borderRadius: BorderRadius.circular(999),
        boxShadow: [
          BoxShadow(
            color: AppColors.primary.withValues(alpha: 0.35),
            blurRadius: 18,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(999),
          child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 20),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  label,
                  style: AppTextStyles.labelLarge.copyWith(
                    color: _fg,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const SizedBox(width: 6),
                Icon(Icons.arrow_forward_rounded, color: _fg, size: 20),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
