import 'package:flutter/material.dart';
import '../../../core/theme/theme.dart';

enum AppButtonVariant { primary, secondary, outline, text, danger, gradient }

enum AppButtonSize { small, medium, large }

/// Custom button widget aligned with the web platform design tokens
/// (`frontend-admin/src/styles/chat.css`).
///
/// New `gradient` variant renders the indigo→purple brand gradient that
/// the web uses for primary CTAs (e.g. `.cta-button`, `.empty-send-btn`).
class AppButton extends StatelessWidget {
  final String text;
  final VoidCallback? onPressed;
  final AppButtonVariant variant;
  final AppButtonSize size;
  final bool isLoading;
  final bool isFullWidth;
  final IconData? prefixIcon;
  final IconData? suffixIcon;
  final Widget? child;

  const AppButton({
    super.key,
    required this.text,
    this.onPressed,
    this.variant = AppButtonVariant.primary,
    this.size = AppButtonSize.large,
    this.isLoading = false,
    bool? fullWidth,
    IconData? icon,
    IconData? prefixIcon,
    this.suffixIcon,
    this.child,
  })  : isFullWidth = fullWidth ?? true,
        prefixIcon = icon ?? prefixIcon;

  // Primary filled button (solid indigo)
  const AppButton.primary({
    super.key,
    required this.text,
    this.onPressed,
    this.size = AppButtonSize.large,
    this.isLoading = false,
    this.isFullWidth = true,
    this.prefixIcon,
    this.suffixIcon,
    this.child,
  }) : variant = AppButtonVariant.primary;

  /// Brand gradient button (indigo → purple) for the most important CTAs.
  /// Mirrors the web `.cta-button` and `.auth-submit` styling.
  const AppButton.gradient({
    super.key,
    required this.text,
    this.onPressed,
    this.size = AppButtonSize.large,
    this.isLoading = false,
    this.isFullWidth = true,
    this.prefixIcon,
    this.suffixIcon,
    this.child,
  }) : variant = AppButtonVariant.gradient;

  // Outlined button
  const AppButton.outline({
    super.key,
    required this.text,
    this.onPressed,
    this.size = AppButtonSize.large,
    this.isLoading = false,
    this.isFullWidth = true,
    this.prefixIcon,
    this.suffixIcon,
    this.child,
  }) : variant = AppButtonVariant.outline;

  // Text button
  const AppButton.text({
    super.key,
    required this.text,
    this.onPressed,
    this.size = AppButtonSize.medium,
    this.isLoading = false,
    this.isFullWidth = false,
    this.prefixIcon,
    this.suffixIcon,
    this.child,
  }) : variant = AppButtonVariant.text;

  // Danger button
  const AppButton.danger({
    super.key,
    required this.text,
    this.onPressed,
    this.size = AppButtonSize.large,
    this.isLoading = false,
    this.isFullWidth = true,
    this.prefixIcon,
    this.suffixIcon,
    this.child,
  }) : variant = AppButtonVariant.danger;

  double get _height {
    switch (size) {
      case AppButtonSize.small:
        return AppDimensions.buttonHeightSm;
      case AppButtonSize.medium:
        return AppDimensions.buttonHeightMd;
      case AppButtonSize.large:
        return AppDimensions.buttonHeightLg;
    }
  }

  EdgeInsets get _padding {
    switch (size) {
      case AppButtonSize.small:
        return const EdgeInsets.symmetric(
          horizontal: AppDimensions.spacing12,
          vertical: AppDimensions.spacing8,
        );
      case AppButtonSize.medium:
        return const EdgeInsets.symmetric(
          horizontal: AppDimensions.spacing16,
          vertical: AppDimensions.spacing12,
        );
      case AppButtonSize.large:
        return const EdgeInsets.symmetric(
          horizontal: AppDimensions.spacing24,
          vertical: AppDimensions.spacing14,
        );
    }
  }

  TextStyle get _textStyle {
    switch (size) {
      case AppButtonSize.small:
        return AppTextStyles.buttonSmall;
      case AppButtonSize.medium:
      case AppButtonSize.large:
        return AppTextStyles.button;
    }
  }

  double get _iconSize {
    switch (size) {
      case AppButtonSize.small:
        return AppDimensions.iconSm;
      case AppButtonSize.medium:
        return AppDimensions.iconMd;
      case AppButtonSize.large:
        return AppDimensions.iconLg;
    }
  }

  @override
  Widget build(BuildContext context) {
    final bool isDisabled = onPressed == null || isLoading;

    return SizedBox(
      width: isFullWidth ? double.infinity : null,
      height: _height,
      child: _buildButton(context, isDisabled),
    );
  }

  Widget _buildButton(BuildContext context, bool isDisabled) {
    switch (variant) {
      case AppButtonVariant.primary:
        return _buildPrimaryButton(isDisabled);
      case AppButtonVariant.secondary:
        return _buildSecondaryButton(isDisabled);
      case AppButtonVariant.outline:
        return _buildOutlineButton(isDisabled);
      case AppButtonVariant.text:
        return _buildTextButton(isDisabled);
      case AppButtonVariant.danger:
        return _buildDangerButton(isDisabled);
      case AppButtonVariant.gradient:
        return _buildGradientButton(isDisabled);
    }
  }

  Widget _buildPrimaryButton(bool isDisabled) {
    return ElevatedButton(
      onPressed: isDisabled ? null : onPressed,
      style: ElevatedButton.styleFrom(
        backgroundColor:
            isDisabled ? AppColors.surfaceVariant : AppColors.primary,
        foregroundColor:
            isDisabled ? AppColors.textHint : AppColors.white,
        elevation: 0,
        padding: _padding,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
        ),
      ),
      child: _buildButtonContent(
        isDisabled ? AppColors.textHint : AppColors.white,
      ),
    );
  }

  Widget _buildGradientButton(bool isDisabled) {
    return DecoratedBox(
      decoration: BoxDecoration(
        gradient: isDisabled ? null : AppColors.primaryGradient,
        color: isDisabled ? AppColors.surfaceVariant : null,
        borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
        boxShadow: isDisabled
            ? null
            : [
                BoxShadow(
                  color: AppColors.primary.withValues(alpha: 0.32),
                  blurRadius: 24,
                  spreadRadius: -4,
                  offset: const Offset(0, 10),
                ),
              ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: isDisabled ? null : onPressed,
          borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
          child: Padding(
            padding: _padding,
            child: Center(
              child: _buildButtonContent(
                isDisabled ? AppColors.textHint : AppColors.white,
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildSecondaryButton(bool isDisabled) {
    return ElevatedButton(
      onPressed: isDisabled ? null : onPressed,
      style: ElevatedButton.styleFrom(
        backgroundColor:
            isDisabled ? AppColors.surfaceVariant : AppColors.primary10,
        foregroundColor: AppColors.primary,
        elevation: 0,
        padding: _padding,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
          side: BorderSide(
            color: AppColors.primary.withValues(alpha: 0.3),
            width: 1,
          ),
        ),
      ),
      child: _buildButtonContent(
        isDisabled ? AppColors.textDisabled : AppColors.primary,
      ),
    );
  }

  Widget _buildOutlineButton(bool isDisabled) {
    return OutlinedButton(
      onPressed: isDisabled ? null : onPressed,
      style: OutlinedButton.styleFrom(
        foregroundColor:
            isDisabled ? AppColors.textHint : AppColors.textPrimary,
        side: BorderSide(
          color: isDisabled ? AppColors.borderSubtle : AppColors.border,
          width: AppDimensions.borderWidthThin,
        ),
        padding: _padding,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
        ),
      ),
      child: _buildButtonContent(
        isDisabled ? AppColors.textHint : AppColors.textPrimary,
      ),
    );
  }

  Widget _buildTextButton(bool isDisabled) {
    return TextButton(
      onPressed: isDisabled ? null : onPressed,
      style: TextButton.styleFrom(
        foregroundColor: isDisabled ? AppColors.textDisabled : AppColors.primary,
        padding: _padding,
      ),
      child: _buildButtonContent(
        isDisabled ? AppColors.textDisabled : AppColors.primary,
      ),
    );
  }

  Widget _buildDangerButton(bool isDisabled) {
    return ElevatedButton(
      onPressed: isDisabled ? null : onPressed,
      style: ElevatedButton.styleFrom(
        backgroundColor:
            isDisabled ? AppColors.surfaceVariant : AppColors.error,
        foregroundColor: AppColors.white,
        elevation: 0,
        padding: _padding,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
        ),
      ),
      child: _buildButtonContent(AppColors.white),
    );
  }

  Widget _buildButtonContent(Color color) {
    if (isLoading) {
      return SizedBox(
        width: _iconSize,
        height: _iconSize,
        child: CircularProgressIndicator(
          strokeWidth: 2,
          valueColor: AlwaysStoppedAnimation<Color>(color),
        ),
      );
    }

    if (child != null) {
      return child!;
    }

    final List<Widget> children = [];

    if (prefixIcon != null) {
      children.add(Icon(prefixIcon, size: _iconSize, color: color));
      children.add(const SizedBox(width: AppDimensions.spacing8));
    }

    children.add(
      Text(
        text,
        style: _textStyle.copyWith(color: color),
      ),
    );

    if (suffixIcon != null) {
      children.add(const SizedBox(width: AppDimensions.spacing8));
      children.add(Icon(suffixIcon, size: _iconSize, color: color));
    }

    return Row(
      mainAxisSize: MainAxisSize.min,
      mainAxisAlignment: MainAxisAlignment.center,
      children: children,
    );
  }
}
