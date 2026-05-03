import 'package:flutter/material.dart';

/// Color palette for ProdBot AI — Dark Theme.
///
/// Aligned with web platform `frontend-admin` design tokens
/// (see `frontend-admin/src/styles/dashboard.css` for the global brand
/// `--accent` token and `frontend-admin/src/styles/landing.css` for the
/// gradient hero/CTA palette).
///
/// - Primary accent: Teal-green (`#10A37F`) — matches dashboard `--accent`
///   (ChatGPT/Claude-style minimal CTA color used across `App.jsx`).
/// - Secondary accent: Cyan (`#06B6D4`) — pairs with primary in landing
///   gradients (`linear-gradient(135deg, var(--accent), var(--accent-secondary))`).
/// - Dark surfaces kept from chat.css: `#0F0F12` / `#16161A` / `#1C1C22` / `#22222A`.
class AppColors {
  AppColors._();

  // ============== PRIMARY (TEAL-GREEN) — matches dashboard.css --accent ==============
  static const Color primary = Color(0xFF10A37F);          // dashboard --accent
  static const Color primaryHover = Color(0xFF0D8A6B);     // dashboard --accent-hover
  static const Color primary100 = Color(0xFF052E22);
  static const Color primary60 = Color(0xFF34D399);        // landing --accent-bright
  static const Color primary50 = Color(0xFF10A37F);
  static const Color primary40 = Color(0xFF6EE7B7);
  static const Color primary30 = Color(0xFFA7F3D0);
  static const Color primary20 = Color(0xFF064E3B);
  static const Color primary10 = Color(0x2610A37F);        // rgba(16,163,127,0.15)
  static const Color primaryLight = Color(0x1210A37F);     // rgba(16,163,127,0.07)
  static const Color primarySubtle = Color(0x2610A37F);    // --accent-light tint

  // ============== SECONDARY (CYAN) — landing.css --accent-secondary ==============
  static const Color secondary = Color(0xFF06B6D4);
  static const Color secondaryHover = Color(0xFF22D3EE);

  // ============== DARK BACKGROUND COLORS (matches web chat.css) ==============
  static const Color background = Color(0xFF0F0F12);       // --bg-primary
  static const Color surface = Color(0xFF16161A);          // --bg-secondary
  static const Color surfaceVariant = Color(0xFF1C1C22);   // --bg-tertiary
  static const Color cardBackground = Color(0xFF22222A);   // --bg-elevated
  static const Color hoverBackground = Color(0xFF28282F);  // --bg-hover
  static const Color chatBubble = Color(0xFF1C1C22);
  static const Color inputBackground = Color(0xFF1C1C22);

  // ============== TEXT COLORS (matches web) ==============
  static const Color textPrimary = Color(0xFFF4F4F5);      // --text-primary
  static const Color textSecondary = Color(0xFFA1A1AA);    // --text-secondary
  static const Color textSecondaryVariant = Color(0xFF71717A); // --text-tertiary
  static const Color textTertiary = Color(0xFF71717A);
  static const Color textDisabled = Color(0xFF3F3F46);
  static const Color textHint = Color(0xFF52525B);         // --text-muted
  static const Color textMuted = Color(0xFFA1A1AA);
  static const Color textWhite = Color(0xFFFFFFFF);
  static const Color textLink = Color(0xFF34D399);

  // ============== ICON COLORS ==============
  static const Color iconDefault = Color(0xFFA1A1AA);
  static const Color iconVariant = Color(0xFF71717A);
  static const Color iconRest = Color(0xFF52525B);
  static const Color iconDisabled = Color(0xFF3F3F46);
  static const Color iconOutline = Color(0xFF27272A);

  // ============== BORDER & DIVIDER (matches web rgba) ==============
  static const Color borderSubtle = Color(0x0FFFFFFF);     // rgba(255,255,255,0.06)
  static const Color border = Color(0x1AFFFFFF);           // rgba(255,255,255,0.10)
  static const Color borderStrong = Color(0x26FFFFFF);     // rgba(255,255,255,0.15)
  static const Color borderVariant = Color(0x0FFFFFFF);
  static const Color divider = Color(0x0FFFFFFF);
  static const Color outline = Color(0x1AFFFFFF);
  static const Color outlineVariant = Color(0x0FFFFFFF);

  // ============== ACCENT / STATUS COLORS ==============
  static const Color error = Color(0xFFEF4444);
  static const Color errorSmooth = Color(0xFF2D1515);
  static const Color success = Color(0xFF22C55E);
  static const Color successSmooth = Color(0xFF102810);
  static const Color warning = Color(0xFFF59E0B);
  static const Color warningSmooth = Color(0xFF2D2010);
  static const Color info = Color(0xFF3B82F6);
  static const Color infoSmooth = Color(0xFF101D35);

  // ============== SPECIAL COLORS ==============
  // Purple kept available for legacy charts/profile screens that still
  // import it from chat.css patterns.
  static const Color purpleHaze = Color(0xFF8B5CF6);
  static const Color lilacGlow = Color(0xFF1E1535);
  static const Color tertiary = Color(0xFF06B6D4);          // landing cyan
  static const Color tertiarySmooth = Color(0xFF052B33);
  // Mint kept for chart series + "growth" indicators (matches web success usage).
  static const Color mint = Color(0xFF34D399);

  // ============== SYSTEM COLORS ==============
  static const Color black = Color(0xFF000000);
  static const Color white = Color(0xFFFFFFFF);
  static const Color sidebar = Color(0xFF141420);
  static const Color transparent = Colors.transparent;

  // ============== SHADOW COLORS ==============
  static const Color shadowLight = Color(0x40000000);
  static const Color shadowMedium = Color(0x60000000);

  // ============== GRADIENTS ==============
  /// Brand gradient — matches web `landing.css` hero/CTA background:
  /// `linear-gradient(135deg, var(--accent) 0%, var(--accent-secondary) 100%)`
  /// (teal-green → cyan).
  static const LinearGradient primaryGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [primary, secondary],
  );

  /// Brighter variant matching `landing.css --accent-bright` glow
  /// for hero spotlights/glows.
  static const LinearGradient primaryGradientBright = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [Color(0xFF10B981), Color(0xFF06B6D4)],
  );

  /// Subtle hero gradient for empty states / banners.
  static const LinearGradient heroGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [Color(0xFF1A1A2E), Color(0xFF16213E)],
  );

  static const LinearGradient darkGradient = LinearGradient(
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
    colors: [Color(0xFF0A0A0F), Color(0xFF141420)],
  );

  // ============== COLOR SCHEME ==============
  static ColorScheme get lightColorScheme => const ColorScheme.light(
        primary: primary,
        primaryContainer: Color(0xFFD1FAE5),
        secondary: secondary,
        secondaryContainer: Color(0xFFCFFAFE),
        surface: Color(0xFFFFFFFF),
        error: error,
        errorContainer: Color(0xFFFEE2E2),
        onPrimary: white,
        onSecondary: white,
        onSurface: Color(0xFF1F1C2F),
        onError: white,
        outline: Color(0xFFD1D5DB),
        outlineVariant: Color(0xFFE5E7EB),
      );

  static ColorScheme get darkColorScheme => const ColorScheme.dark(
        primary: primary,
        primaryContainer: primary100,
        secondary: secondary,
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
}
