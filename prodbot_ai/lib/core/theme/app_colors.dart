import 'package:flutter/material.dart';

/// Color palette extracted from Figma design "JUZ40 Admin"
/// Primary color: Mint Green (#17CE92)
class AppColors {
  AppColors._();

  // ============== PRIMARY COLORS ==============
  /// Main primary color - Mint Green
  static const Color primary = Color(0xFF17CE92);
  static const Color primary100 = Color(0xFF0A5C41);
  static const Color primary60 = Color(0xFF14B57F);
  static const Color primary50 = Color(0xFF17CE92);
  static const Color primary40 = Color(0xFF45D8A8);
  static const Color primary30 = Color(0xFF73E2BE);
  static const Color primary20 = Color(0xFFA1ECD4);
  static const Color primary10 = Color(0xFFD0F6EA);
  static const Color primaryLight = Color(0xFFE8FBF5);

  // ============== BACKGROUND COLORS ==============
  static const Color background = Color(0xFFFFFFFF);  // Figma: #FFFFFF
  static const Color surface = Color(0xFFFFFFFF);
  static const Color surfaceVariant = Color(0xFFF5F5F5);
  static const Color cardBackground = Color(0xFFEFEFEF);  // Figma: #EFEFEF
  static const Color chatBubble = Color(0xFFEFEFEF);  // Figma: #EFEFEF (suggestion boxes)

  // ============== TEXT COLORS ==============
  static const Color textPrimary = Color(0xFF1F1C2F);  // Figma: #1F1C2F
  static const Color textSecondary = Color(0xFF847F7F);  // Figma: #847F7F (muted text)
  static const Color textSecondaryVariant = Color(0xFF9CA3AF);
  static const Color textDisabled = Color(0xFFD1D5DB);
  static const Color textHint = Color(0xFF9E9E9E);  // Figma: #9E9E9E
  static const Color textMuted = Color(0xFF847F7F);  // Figma: #847F7F (suggestion card text)
  static const Color textWhite = Color(0xFFFFFFFF);
  static const Color textLink = Color(0xFF17CE92);

  // ============== ICON COLORS ==============
  static const Color iconDefault = Color(0xFF1F1C2F);
  static const Color iconVariant = Color(0xFF6B7280);
  static const Color iconRest = Color(0xFF9CA3AF);
  static const Color iconDisabled = Color(0xFFD1D5DB);
  static const Color iconOutline = Color(0xFFE5E7EB);

  // ============== BORDER & DIVIDER ==============
  static const Color border = Color(0xFFE5E7EB);
  static const Color borderVariant = Color(0xFFF3F4F6);
  static const Color divider = Color(0xFFF7F7F7);
  static const Color outline = Color(0xFFD1D5DB);
  static const Color outlineVariant = Color(0xFFE5E7EB);

  // ============== ACCENT / STATUS COLORS ==============
  static const Color error = Color(0xFFEF4444);
  static const Color errorSmooth = Color(0xFFFEE2E2);
  static const Color success = Color(0xFF22C55E);
  static const Color successSmooth = Color(0xFFDCFCE7);
  static const Color warning = Color(0xFFF59E0B);
  static const Color warningSmooth = Color(0xFFFEF3C7);
  static const Color info = Color(0xFF3B82F6);
  static const Color infoSmooth = Color(0xFFDBEAFE);

  // ============== SPECIAL COLORS ==============
  static const Color purpleHaze = Color(0xFF8B5CF6);
  static const Color lilacGlow = Color(0xFFDDD6FE);
  static const Color tertiary = Color(0xFF6366F1);
  static const Color tertiarySmooth = Color(0xFFE0E7FF);

  // ============== SYSTEM COLORS ==============
  static const Color black = Color(0xFF000000);
  static const Color white = Color(0xFFFFFFFF);
  static const Color sidebar = Color(0xFF1F2937);
  static const Color transparent = Colors.transparent;

  // ============== SHADOW COLORS ==============
  static const Color shadowLight = Color(0x14182B4B);
  static const Color shadowMedium = Color(0x1E182B4B);

  // ============== GRADIENT ==============
  static const LinearGradient primaryGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [primary, primary60],
  );

  // ============== COLOR SCHEME FOR THEME ==============
  static ColorScheme get lightColorScheme => const ColorScheme.light(
        primary: primary,
        primaryContainer: primaryLight,
        secondary: tertiary,
        secondaryContainer: tertiarySmooth,
        surface: surface,
        error: error,
        errorContainer: errorSmooth,
        onPrimary: white,
        onSecondary: white,
        onSurface: textPrimary,
        onError: white,
        outline: outline,
        outlineVariant: outlineVariant,
      );

  static ColorScheme get darkColorScheme => const ColorScheme.dark(
        primary: primary,
        primaryContainer: primary100,
        secondary: tertiary,
        secondaryContainer: primary100,
        surface: Color(0xFF1F1F1F),
        error: error,
        errorContainer: Color(0xFF3D1515),
        onPrimary: white,
        onSecondary: white,
        onSurface: white,
        onError: white,
        outline: Color(0xFF3D3D3D),
        outlineVariant: Color(0xFF2D2D2D),
      );
}
