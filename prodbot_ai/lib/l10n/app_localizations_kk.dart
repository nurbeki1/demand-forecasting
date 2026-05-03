// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Kazakh (`kk`).
class AppLocalizationsKk extends AppLocalizations {
  AppLocalizationsKk([String locale = 'kk']) : super(locale);

  @override
  String get appTitle => 'ProdBot AI';

  @override
  String get welcomePoweredByAi => 'AI-демеу';

  @override
  String get welcomeTitle => 'Қош келдіңіз';

  @override
  String get welcomeBrandHighlight => 'ProdBot AI';

  @override
  String get welcomeSubtitle =>
      'Сұраныс болжам платформасы.\nАқылды талдау бір сұрау қашықтықта.';

  @override
  String get welcomeStart => 'Бастау';

  @override
  String get welcomeLogin => 'Кіру';

  @override
  String get welcomeOr => 'немесе';

  @override
  String get loginTitle => 'Кіру';

  @override
  String get loginSubtitle => 'Аккаунтыңызға кіру үшін деректерді енгізіңіз';

  @override
  String get loginEmailLabel => 'Email';

  @override
  String get loginEmailHint => 'you@company.com';

  @override
  String get loginPasswordLabel => 'Құпия сөз';

  @override
  String get loginPasswordHint => 'Құпия сөзді енгізіңіз';

  @override
  String get loginRememberMe => 'Мені есте сақтау';

  @override
  String get loginForgotPassword => 'Ұмыттыңыз ба?';

  @override
  String get loginButton => 'Кіру';

  @override
  String get loginNoAccount => 'Аккаунт жоқ па?';

  @override
  String get loginRegister => 'Тіркелу';

  @override
  String get validationEmailRequired => 'Email қажет';

  @override
  String get validationEmailInvalid => 'Жарамды email енгізіңіз';

  @override
  String get validationPasswordRequired => 'Құпия сөз қажет';

  @override
  String get validationPasswordShort => 'Кемінде 4 таңба';

  @override
  String get chatNewChat => 'Жаңа чат';

  @override
  String get chatSearchHint => 'Іздеу…';

  @override
  String get chatRecentChats => 'Соңғы чаттар';

  @override
  String get chatNoConversations => 'Чат әлі жоқ';

  @override
  String get chatSettings => 'Параметрлер';

  @override
  String get chatLogout => 'Шығу';

  @override
  String get chatLogoutTooltip => 'Шығу';

  @override
  String get chatDeleteTitle => 'Чатты жою';

  @override
  String get chatDeleteBody => 'Бұл чатты жою керек пе?';

  @override
  String get chatCancel => 'Болдырмау';

  @override
  String get chatDelete => 'Жою';

  @override
  String get chatAiAssistant => 'AI Assistant';

  @override
  String get chatWelcomeType1 => 'Қош келдіңіз!';

  @override
  String get chatWelcomeType2 => 'Кез-келген сұрақ қойыңыз';

  @override
  String get chatWelcomeType3 => 'AI жауаптары тексерілуі тиіс';

  @override
  String get chatAskAnythingHint => 'Кез-келген сұрақ қойыңыз…';

  @override
  String get chatMessageHint => 'Хабарлама…';

  @override
  String get chatDisclaimer =>
      'AI қате жіберуі мүмкін. Маңызды ақпаратты тексеріңіз.';

  @override
  String get suggestionTopProducts => 'Үздік өнімдер';

  @override
  String get suggestionSalesForecast => 'Сату болжамы';

  @override
  String get suggestionTrending => 'Танымал тауарлар';

  @override
  String get suggestionCompare => 'Өнімдерді салыстыру';

  @override
  String get roleYou => 'Сіз';

  @override
  String get roleAiAssistant => 'AI Assistant';

  @override
  String get modelPickerTitle => 'AI моделі';

  @override
  String get modelRfDesc => 'Тұрақты, кез-келген деректе жақсы жұмыс істейді';

  @override
  String get modelLgbmDesc => 'Өте жылдам, үлкен деректер үшін оңтайлы';

  @override
  String get modelXgbDesc => 'Жоғары дәлдік, күрделі үлгілерді анықтайды';

  @override
  String get miniChartTitle => 'Сұраныс болжамы';

  @override
  String get miniChartHistory => 'Тарих';

  @override
  String get miniChartForecast => 'Болжам';

  @override
  String productsCarouselTitle(int count) {
    return 'Өнімдер ($count)';
  }

  @override
  String get productPriceUnknown => 'Бағасы көрсетілмеген';

  @override
  String get chatErrorGeneric =>
      'Қате: серверге қосылу мүмкін болмады. Кейінірек қайталап көріңіз.';

  @override
  String get routerPageNotFound => 'Бет табылмады';

  @override
  String get routerUnknownRoute => 'Белгісіз маршрут';

  @override
  String get routerGoHome => 'Басты бетке';
}
