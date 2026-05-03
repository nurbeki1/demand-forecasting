import 'dart:async';

import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:intl/intl.dart' as intl;

import 'app_localizations_en.dart';
import 'app_localizations_kk.dart';
import 'app_localizations_ru.dart';

// ignore_for_file: type=lint

/// Callers can lookup localized strings with an instance of AppLocalizations
/// returned by `AppLocalizations.of(context)`.
///
/// Applications need to include `AppLocalizations.delegate()` in their app's
/// `localizationDelegates` list, and the locales they support in the app's
/// `supportedLocales` list. For example:
///
/// ```dart
/// import 'l10n/app_localizations.dart';
///
/// return MaterialApp(
///   localizationsDelegates: AppLocalizations.localizationsDelegates,
///   supportedLocales: AppLocalizations.supportedLocales,
///   home: MyApplicationHome(),
/// );
/// ```
///
/// ## Update pubspec.yaml
///
/// Please make sure to update your pubspec.yaml to include the following
/// packages:
///
/// ```yaml
/// dependencies:
///   # Internationalization support.
///   flutter_localizations:
///     sdk: flutter
///   intl: any # Use the pinned version from flutter_localizations
///
///   # Rest of dependencies
/// ```
///
/// ## iOS Applications
///
/// iOS applications define key application metadata, including supported
/// locales, in an Info.plist file that is built into the application bundle.
/// To configure the locales supported by your app, you’ll need to edit this
/// file.
///
/// First, open your project’s ios/Runner.xcworkspace Xcode workspace file.
/// Then, in the Project Navigator, open the Info.plist file under the Runner
/// project’s Runner folder.
///
/// Next, select the Information Property List item, select Add Item from the
/// Editor menu, then select Localizations from the pop-up menu.
///
/// Select and expand the newly-created Localizations item then, for each
/// locale your application supports, add a new item and select the locale
/// you wish to add from the pop-up menu in the Value field. This list should
/// be consistent with the languages listed in the AppLocalizations.supportedLocales
/// property.
abstract class AppLocalizations {
  AppLocalizations(String locale)
      : localeName = intl.Intl.canonicalizedLocale(locale.toString());

  final String localeName;

  static AppLocalizations? of(BuildContext context) {
    return Localizations.of<AppLocalizations>(context, AppLocalizations);
  }

  static const LocalizationsDelegate<AppLocalizations> delegate =
      _AppLocalizationsDelegate();

  /// A list of this localizations delegate along with the default localizations
  /// delegates.
  ///
  /// Returns a list of localizations delegates containing this delegate along with
  /// GlobalMaterialLocalizations.delegate, GlobalCupertinoLocalizations.delegate,
  /// and GlobalWidgetsLocalizations.delegate.
  ///
  /// Additional delegates can be added by appending to this list in
  /// MaterialApp. This list does not have to be used at all if a custom list
  /// of delegates is preferred or required.
  static const List<LocalizationsDelegate<dynamic>> localizationsDelegates =
      <LocalizationsDelegate<dynamic>>[
    delegate,
    GlobalMaterialLocalizations.delegate,
    GlobalCupertinoLocalizations.delegate,
    GlobalWidgetsLocalizations.delegate,
  ];

  /// A list of this localizations delegate's supported locales.
  static const List<Locale> supportedLocales = <Locale>[
    Locale('en'),
    Locale('kk'),
    Locale('ru')
  ];

  /// No description provided for @appTitle.
  ///
  /// In en, this message translates to:
  /// **'ProdBot AI'**
  String get appTitle;

  /// No description provided for @welcomePoweredByAi.
  ///
  /// In en, this message translates to:
  /// **'AI-powered'**
  String get welcomePoweredByAi;

  /// No description provided for @welcomeTitle.
  ///
  /// In en, this message translates to:
  /// **'Welcome'**
  String get welcomeTitle;

  /// No description provided for @welcomeBrandHighlight.
  ///
  /// In en, this message translates to:
  /// **'ProdBot AI'**
  String get welcomeBrandHighlight;

  /// No description provided for @welcomeSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Demand forecasting platform. Smart analysis one question away.'**
  String get welcomeSubtitle;

  /// No description provided for @welcomeStart.
  ///
  /// In en, this message translates to:
  /// **'Get started'**
  String get welcomeStart;

  /// No description provided for @welcomeLogin.
  ///
  /// In en, this message translates to:
  /// **'Log in'**
  String get welcomeLogin;

  /// No description provided for @welcomeOr.
  ///
  /// In en, this message translates to:
  /// **'or'**
  String get welcomeOr;

  /// No description provided for @loginTitle.
  ///
  /// In en, this message translates to:
  /// **'Sign in'**
  String get loginTitle;

  /// No description provided for @loginSubtitle.
  ///
  /// In en, this message translates to:
  /// **'Enter your details to sign in to your account'**
  String get loginSubtitle;

  /// No description provided for @loginEmailLabel.
  ///
  /// In en, this message translates to:
  /// **'Email'**
  String get loginEmailLabel;

  /// No description provided for @loginEmailHint.
  ///
  /// In en, this message translates to:
  /// **'you@company.com'**
  String get loginEmailHint;

  /// No description provided for @loginPasswordLabel.
  ///
  /// In en, this message translates to:
  /// **'Password'**
  String get loginPasswordLabel;

  /// No description provided for @loginPasswordHint.
  ///
  /// In en, this message translates to:
  /// **'Enter password'**
  String get loginPasswordHint;

  /// No description provided for @loginRememberMe.
  ///
  /// In en, this message translates to:
  /// **'Remember me'**
  String get loginRememberMe;

  /// No description provided for @loginForgotPassword.
  ///
  /// In en, this message translates to:
  /// **'Forgot password?'**
  String get loginForgotPassword;

  /// No description provided for @loginButton.
  ///
  /// In en, this message translates to:
  /// **'Sign in'**
  String get loginButton;

  /// No description provided for @loginNoAccount.
  ///
  /// In en, this message translates to:
  /// **'No account?'**
  String get loginNoAccount;

  /// No description provided for @loginRegister.
  ///
  /// In en, this message translates to:
  /// **'Register'**
  String get loginRegister;

  /// No description provided for @validationEmailRequired.
  ///
  /// In en, this message translates to:
  /// **'Email is required'**
  String get validationEmailRequired;

  /// No description provided for @validationEmailInvalid.
  ///
  /// In en, this message translates to:
  /// **'Enter a valid email'**
  String get validationEmailInvalid;

  /// No description provided for @validationPasswordRequired.
  ///
  /// In en, this message translates to:
  /// **'Password is required'**
  String get validationPasswordRequired;

  /// No description provided for @validationPasswordShort.
  ///
  /// In en, this message translates to:
  /// **'At least 4 characters'**
  String get validationPasswordShort;

  /// No description provided for @chatNewChat.
  ///
  /// In en, this message translates to:
  /// **'New chat'**
  String get chatNewChat;

  /// No description provided for @chatSearchHint.
  ///
  /// In en, this message translates to:
  /// **'Search…'**
  String get chatSearchHint;

  /// No description provided for @chatRecentChats.
  ///
  /// In en, this message translates to:
  /// **'Recent chats'**
  String get chatRecentChats;

  /// No description provided for @chatNoConversations.
  ///
  /// In en, this message translates to:
  /// **'No chats yet'**
  String get chatNoConversations;

  /// No description provided for @chatSettings.
  ///
  /// In en, this message translates to:
  /// **'Settings'**
  String get chatSettings;

  /// No description provided for @chatLogout.
  ///
  /// In en, this message translates to:
  /// **'Log out'**
  String get chatLogout;

  /// No description provided for @chatLogoutTooltip.
  ///
  /// In en, this message translates to:
  /// **'Log out'**
  String get chatLogoutTooltip;

  /// No description provided for @chatDeleteTitle.
  ///
  /// In en, this message translates to:
  /// **'Delete chat'**
  String get chatDeleteTitle;

  /// No description provided for @chatDeleteBody.
  ///
  /// In en, this message translates to:
  /// **'Delete this chat?'**
  String get chatDeleteBody;

  /// No description provided for @chatCancel.
  ///
  /// In en, this message translates to:
  /// **'Cancel'**
  String get chatCancel;

  /// No description provided for @chatDelete.
  ///
  /// In en, this message translates to:
  /// **'Delete'**
  String get chatDelete;

  /// No description provided for @chatAiAssistant.
  ///
  /// In en, this message translates to:
  /// **'AI Assistant'**
  String get chatAiAssistant;

  /// No description provided for @chatWelcomeType1.
  ///
  /// In en, this message translates to:
  /// **'Welcome!'**
  String get chatWelcomeType1;

  /// No description provided for @chatWelcomeType2.
  ///
  /// In en, this message translates to:
  /// **'Ask anything'**
  String get chatWelcomeType2;

  /// No description provided for @chatWelcomeType3.
  ///
  /// In en, this message translates to:
  /// **'AI answers should be verified'**
  String get chatWelcomeType3;

  /// No description provided for @chatAskAnythingHint.
  ///
  /// In en, this message translates to:
  /// **'Ask anything…'**
  String get chatAskAnythingHint;

  /// No description provided for @chatMessageHint.
  ///
  /// In en, this message translates to:
  /// **'Message…'**
  String get chatMessageHint;

  /// No description provided for @chatDisclaimer.
  ///
  /// In en, this message translates to:
  /// **'AI may make mistakes. Verify important information.'**
  String get chatDisclaimer;

  /// No description provided for @suggestionTopProducts.
  ///
  /// In en, this message translates to:
  /// **'Top products'**
  String get suggestionTopProducts;

  /// No description provided for @suggestionSalesForecast.
  ///
  /// In en, this message translates to:
  /// **'Sales forecast'**
  String get suggestionSalesForecast;

  /// No description provided for @suggestionTrending.
  ///
  /// In en, this message translates to:
  /// **'Trending items'**
  String get suggestionTrending;

  /// No description provided for @suggestionCompare.
  ///
  /// In en, this message translates to:
  /// **'Compare products'**
  String get suggestionCompare;

  /// No description provided for @roleYou.
  ///
  /// In en, this message translates to:
  /// **'You'**
  String get roleYou;

  /// No description provided for @roleAiAssistant.
  ///
  /// In en, this message translates to:
  /// **'AI Assistant'**
  String get roleAiAssistant;

  /// No description provided for @modelPickerTitle.
  ///
  /// In en, this message translates to:
  /// **'AI model'**
  String get modelPickerTitle;

  /// No description provided for @modelRfDesc.
  ///
  /// In en, this message translates to:
  /// **'Stable, works well on most data'**
  String get modelRfDesc;

  /// No description provided for @modelLgbmDesc.
  ///
  /// In en, this message translates to:
  /// **'Very fast, ideal for large datasets'**
  String get modelLgbmDesc;

  /// No description provided for @modelXgbDesc.
  ///
  /// In en, this message translates to:
  /// **'High accuracy, finds complex patterns'**
  String get modelXgbDesc;

  /// No description provided for @miniChartTitle.
  ///
  /// In en, this message translates to:
  /// **'Demand forecast'**
  String get miniChartTitle;

  /// No description provided for @miniChartHistory.
  ///
  /// In en, this message translates to:
  /// **'History'**
  String get miniChartHistory;

  /// No description provided for @miniChartForecast.
  ///
  /// In en, this message translates to:
  /// **'Forecast'**
  String get miniChartForecast;

  /// No description provided for @productsCarouselTitle.
  ///
  /// In en, this message translates to:
  /// **'Products ({count})'**
  String productsCarouselTitle(int count);

  /// No description provided for @productPriceUnknown.
  ///
  /// In en, this message translates to:
  /// **'No price'**
  String get productPriceUnknown;

  /// No description provided for @chatErrorGeneric.
  ///
  /// In en, this message translates to:
  /// **'Error: could not reach the server. Try again later.'**
  String get chatErrorGeneric;

  /// No description provided for @routerPageNotFound.
  ///
  /// In en, this message translates to:
  /// **'Page not found'**
  String get routerPageNotFound;

  /// No description provided for @routerUnknownRoute.
  ///
  /// In en, this message translates to:
  /// **'Unknown route'**
  String get routerUnknownRoute;

  /// No description provided for @routerGoHome.
  ///
  /// In en, this message translates to:
  /// **'Go home'**
  String get routerGoHome;
}

class _AppLocalizationsDelegate
    extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  @override
  Future<AppLocalizations> load(Locale locale) {
    return SynchronousFuture<AppLocalizations>(lookupAppLocalizations(locale));
  }

  @override
  bool isSupported(Locale locale) =>
      <String>['en', 'kk', 'ru'].contains(locale.languageCode);

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}

AppLocalizations lookupAppLocalizations(Locale locale) {
  // Lookup logic when only language code is specified.
  switch (locale.languageCode) {
    case 'en':
      return AppLocalizationsEn();
    case 'kk':
      return AppLocalizationsKk();
    case 'ru':
      return AppLocalizationsRu();
  }

  throw FlutterError(
      'AppLocalizations.delegate failed to load unsupported locale "$locale". This is likely '
      'an issue with the localizations generation tool. Please file an issue '
      'on GitHub with a reproducible sample app and the gen-l10n configuration '
      'that was used.');
}
