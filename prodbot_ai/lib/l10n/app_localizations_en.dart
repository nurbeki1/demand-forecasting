// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for English (`en`).
class AppLocalizationsEn extends AppLocalizations {
  AppLocalizationsEn([String locale = 'en']) : super(locale);

  @override
  String get appTitle => 'Forecast AI';

  @override
  String get welcomePoweredByAi => 'AI-powered';

  @override
  String get welcomeTitle => 'Welcome';

  @override
  String get welcomeBrandHighlight => 'Forecast AI';

  @override
  String get welcomeSubtitle =>
      'Demand forecasting platform. Smart analysis one question away.';

  @override
  String get welcomeStart => 'Get started';

  @override
  String get welcomeLogin => 'Log in';

  @override
  String get welcomeOr => 'or';

  @override
  String get loginTitle => 'Sign in';

  @override
  String get loginSubtitle => 'Enter your details to sign in to your account';

  @override
  String get loginEmailLabel => 'Email';

  @override
  String get loginEmailHint => 'you@company.com';

  @override
  String get loginPasswordLabel => 'Password';

  @override
  String get loginPasswordHint => 'Enter password';

  @override
  String get loginRememberMe => 'Remember me';

  @override
  String get loginForgotPassword => 'Forgot password?';

  @override
  String get loginButton => 'Sign in';

  @override
  String get loginNoAccount => 'No account?';

  @override
  String get loginRegister => 'Register';

  @override
  String get validationEmailRequired => 'Email is required';

  @override
  String get validationEmailInvalid => 'Enter a valid email';

  @override
  String get validationPasswordRequired => 'Password is required';

  @override
  String get validationPasswordShort => 'At least 4 characters';

  @override
  String get chatNewChat => 'New chat';

  @override
  String get chatSearchHint => 'Search…';

  @override
  String get chatRecentChats => 'Recent chats';

  @override
  String get chatNoConversations => 'No chats yet';

  @override
  String get chatSettings => 'Settings';

  @override
  String get chatLogout => 'Log out';

  @override
  String get chatLogoutTooltip => 'Log out';

  @override
  String get chatDeleteTitle => 'Delete chat';

  @override
  String get chatDeleteBody => 'Delete this chat?';

  @override
  String get chatCancel => 'Cancel';

  @override
  String get chatDelete => 'Delete';

  @override
  String get chatAiAssistant => 'AI Assistant';

  @override
  String get chatWelcomeType1 => 'Welcome!';

  @override
  String get chatWelcomeType2 => 'Ask anything';

  @override
  String get chatWelcomeType3 => 'AI answers should be verified';

  @override
  String get chatAskAnythingHint => 'Ask anything…';

  @override
  String get chatMessageHint => 'Message…';

  @override
  String get chatDisclaimer =>
      'AI may make mistakes. Verify important information.';

  @override
  String get suggestionTopProducts => 'Top products';

  @override
  String get suggestionSalesForecast => 'Sales forecast';

  @override
  String get suggestionTrending => 'Trending items';

  @override
  String get suggestionCompare => 'Compare products';

  @override
  String get roleYou => 'You';

  @override
  String get roleAiAssistant => 'AI Assistant';

  @override
  String get modelPickerTitle => 'AI model';

  @override
  String get modelRfDesc => 'Stable, works well on most data';

  @override
  String get modelLgbmDesc => 'Very fast, ideal for large datasets';

  @override
  String get modelXgbDesc => 'High accuracy, finds complex patterns';

  @override
  String get modelRequiresSubscription => 'Available with a subscription';

  @override
  String get miniChartTitle => 'Demand forecast';

  @override
  String get miniChartHistory => 'History';

  @override
  String get miniChartForecast => 'Forecast';

  @override
  String productsCarouselTitle(int count) {
    return 'Products ($count)';
  }

  @override
  String get productPriceUnknown => 'No price';

  @override
  String get chatErrorGeneric =>
      'Error: could not reach the server. Try again later.';

  @override
  String get settingsSubscriptionButton => 'Subscription';

  @override
  String get subscriptionScreenTitle => 'Subscription';

  @override
  String get subscriptionSignedInAs => 'Signed in as';

  @override
  String get subscriptionCurrentPlan => 'Current plan';

  @override
  String get subscriptionPlanFree => 'Free';

  @override
  String get subscriptionPlanPremium => 'Premium';

  @override
  String get subscriptionPlaceholderBody =>
      'Here you will be able to buy or renew your subscription. This screen is available while you stay logged in — no need to sign in again.';

  @override
  String get routerPageNotFound => 'Page not found';

  @override
  String get routerUnknownRoute => 'Unknown route';

  @override
  String get routerGoHome => 'Go home';
}
