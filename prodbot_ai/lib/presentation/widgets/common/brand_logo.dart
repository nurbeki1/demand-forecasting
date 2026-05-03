import 'package:flutter/material.dart';
import '../../../core/theme/theme.dart';

/// Indigo→purple gradient logo used across the app.
/// Mirrors the web `.logo-icon` / `.empty-logo` styling
/// (see `frontend-admin/src/styles/chat.css`).
class BrandLogo extends StatelessWidget {
  final double size;
  final double radius;
  final IconData icon;
  final bool withGlow;

  const BrandLogo({
    super.key,
    this.size = 36,
    this.radius = AppDimensions.radiusSm,
    this.icon = Icons.auto_awesome_rounded,
    this.withGlow = false,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        gradient: AppColors.primaryGradient,
        borderRadius: BorderRadius.circular(radius),
        boxShadow: withGlow
            ? [
                BoxShadow(
                  color: AppColors.primary.withValues(alpha: 0.35),
                  blurRadius: 28,
                  spreadRadius: -2,
                  offset: const Offset(0, 12),
                ),
              ]
            : null,
      ),
      child: Icon(
        icon,
        size: size * 0.55,
        color: AppColors.white,
      ),
    );
  }
}
