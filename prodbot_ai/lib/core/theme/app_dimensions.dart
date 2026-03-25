import 'package:flutter/material.dart';

/// Spacing and dimensions extracted from Figma design "JUZ40 Admin"
class AppDimensions {
  AppDimensions._();

  // ============== SPACING SYSTEM (4px base) ==============
  static const double spacing2 = 2;
  static const double spacing4 = 4;
  static const double spacing6 = 6;
  static const double spacing8 = 8;
  static const double spacing10 = 10;
  static const double spacing12 = 12;
  static const double spacing14 = 14;
  static const double spacing16 = 16;
  static const double spacing20 = 20;
  static const double spacing24 = 24;
  static const double spacing28 = 28;
  static const double spacing32 = 32;
  static const double spacing40 = 40;
  static const double spacing48 = 48;
  static const double spacing56 = 56;
  static const double spacing64 = 64;
  static const double spacing72 = 72;
  static const double spacing80 = 80;
  static const double spacing96 = 96;

  // ============== SEMANTIC SPACING ==============
  static const double xs = 4;
  static const double sm = 8;
  static const double md = 16;
  static const double lg = 24;
  static const double xl = 32;
  static const double xxl = 48;

  // ============== SCREEN PADDING ==============
  static const double screenPaddingHorizontal = 24;
  static const double screenPaddingVertical = 16;
  static const EdgeInsets screenPadding = EdgeInsets.symmetric(
    horizontal: screenPaddingHorizontal,
    vertical: screenPaddingVertical,
  );

  // ============== BORDER RADIUS ==============
  static const double radiusXs = 4;
  static const double radiusSm = 8;
  static const double radiusMd = 12;
  static const double radiusLg = 16;
  static const double radiusXl = 20;
  static const double radiusXxl = 24;
  static const double radiusRound = 50;
  static const double radiusFull = 999;

  // ============== BORDER RADIUS (BorderRadius) ==============
  static BorderRadius get borderRadiusXs => BorderRadius.circular(radiusXs);
  static BorderRadius get borderRadiusSm => BorderRadius.circular(radiusSm);
  static BorderRadius get borderRadiusMd => BorderRadius.circular(radiusMd);
  static BorderRadius get borderRadiusLg => BorderRadius.circular(radiusLg);
  static BorderRadius get borderRadiusXl => BorderRadius.circular(radiusXl);
  static BorderRadius get borderRadiusXxl => BorderRadius.circular(radiusXxl);
  static BorderRadius get borderRadiusRound => BorderRadius.circular(radiusRound);

  // ============== BUTTON DIMENSIONS ==============
  static const double buttonHeightSm = 36;
  static const double buttonHeightMd = 44;
  static const double buttonHeightLg = 54;
  static const double buttonHeightXl = 60;

  static const double buttonMinWidth = 120;

  // ============== INPUT DIMENSIONS ==============
  static const double inputHeight = 52;
  static const double inputHeightSm = 44;
  static const double inputHeightLg = 56;

  // ============== ICON SIZES ==============
  static const double iconXs = 12;
  static const double iconSm = 16;
  static const double iconMd = 20;
  static const double iconLg = 24;
  static const double iconXl = 28;
  static const double iconXxl = 32;
  static const double iconHuge = 48;

  // ============== AVATAR SIZES ==============
  static const double avatarXs = 24;
  static const double avatarSm = 32;
  static const double avatarMd = 40;
  static const double avatarLg = 48;
  static const double avatarXl = 64;
  static const double avatarXxl = 80;
  static const double avatarHuge = 120;

  // ============== CARD DIMENSIONS ==============
  static const double cardPadding = 16;
  static const double cardPaddingSm = 12;
  static const double cardPaddingLg = 20;
  static const double cardElevation = 0;

  // ============== APP BAR ==============
  static const double appBarHeight = 56;
  static const double appBarElevation = 0;

  // ============== BOTTOM NAV BAR ==============
  static const double bottomNavHeight = 80;

  // ============== DIVIDER ==============
  static const double dividerThickness = 1;

  // ============== BORDER WIDTH ==============
  static const double borderWidthThin = 1;
  static const double borderWidthMedium = 1.5;
  static const double borderWidthThick = 2;

  // ============== SHADOW ==============
  static List<BoxShadow> get shadowSm => [
        BoxShadow(
          color: const Color(0xFF182B4B).withValues(alpha: 0.08),
          blurRadius: 8,
          offset: const Offset(0, 2),
        ),
      ];

  static List<BoxShadow> get shadowMd => [
        BoxShadow(
          color: const Color(0xFF182B4B).withValues(alpha: 0.08),
          blurRadius: 16,
          offset: const Offset(0, 4),
        ),
      ];

  static List<BoxShadow> get shadowLg => [
        BoxShadow(
          color: const Color(0xFF182B4B).withValues(alpha: 0.12),
          blurRadius: 22,
          spreadRadius: -6,
          offset: const Offset(0, 8),
        ),
        BoxShadow(
          color: const Color(0xFF182B4B).withValues(alpha: 0.12),
          blurRadius: 64,
          spreadRadius: -4,
          offset: const Offset(0, 14),
        ),
      ];

  static List<BoxShadow> get shadowCard => [
        BoxShadow(
          color: const Color(0xFF182B4B).withValues(alpha: 0.06),
          blurRadius: 12,
          offset: const Offset(0, 4),
        ),
      ];

  // ============== ANIMATION DURATIONS ==============
  static const Duration animationFast = Duration(milliseconds: 150);
  static const Duration animationNormal = Duration(milliseconds: 300);
  static const Duration animationSlow = Duration(milliseconds: 500);

  // ============== ANIMATION CURVES ==============
  static const Curve animationCurve = Curves.easeInOut;
  static const Curve animationCurveFast = Curves.easeOut;
}

/// Extension for easy access to spacing
extension SpacingExtension on num {
  SizedBox get verticalSpace => SizedBox(height: toDouble());
  SizedBox get horizontalSpace => SizedBox(width: toDouble());
}
