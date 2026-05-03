import 'package:flutter/material.dart';

/// Maps `/settings` profile.language (`kk` | `ru` | `en`) to a Flutter [Locale].
Locale localeFromProfileLanguage(String code) {
  switch (code.toLowerCase().trim()) {
    case 'ru':
      return const Locale('ru');
    case 'en':
      return const Locale('en');
    case 'kk':
    default:
      return const Locale('kk');
  }
}

/// Backend `/chat` accepts `kk`, `ru`, `en`.
String apiLanguageFromLocale(Locale locale) {
  final c = locale.languageCode.toLowerCase();
  if (c == 'ru' || c == 'en') return c;
  return 'kk';
}
