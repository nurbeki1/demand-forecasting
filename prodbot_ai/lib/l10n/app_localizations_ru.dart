// ignore: unused_import
import 'package:intl/intl.dart' as intl;
import 'app_localizations.dart';

// ignore_for_file: type=lint

/// The translations for Russian (`ru`).
class AppLocalizationsRu extends AppLocalizations {
  AppLocalizationsRu([String locale = 'ru']) : super(locale);

  @override
  String get appTitle => 'ProdBot AI';

  @override
  String get welcomePoweredByAi => 'На базе ИИ';

  @override
  String get welcomeTitle => 'Добро пожаловать';

  @override
  String get welcomeBrandHighlight => 'ProdBot AI';

  @override
  String get welcomeSubtitle =>
      'Платформа прогноза спроса. Умный анализ на расстоянии одного вопроса.';

  @override
  String get welcomeStart => 'Начать';

  @override
  String get welcomeLogin => 'Войти';

  @override
  String get welcomeOr => 'или';

  @override
  String get loginTitle => 'Вход';

  @override
  String get loginSubtitle => 'Введите данные для входа в аккаунт';

  @override
  String get loginEmailLabel => 'Email';

  @override
  String get loginEmailHint => 'you@company.com';

  @override
  String get loginPasswordLabel => 'Пароль';

  @override
  String get loginPasswordHint => 'Введите пароль';

  @override
  String get loginRememberMe => 'Запомнить меня';

  @override
  String get loginForgotPassword => 'Забыли пароль?';

  @override
  String get loginButton => 'Войти';

  @override
  String get loginNoAccount => 'Нет аккаунта?';

  @override
  String get loginRegister => 'Регистрация';

  @override
  String get validationEmailRequired => 'Укажите email';

  @override
  String get validationEmailInvalid => 'Введите корректный email';

  @override
  String get validationPasswordRequired => 'Укажите пароль';

  @override
  String get validationPasswordShort => 'Не менее 4 символов';

  @override
  String get chatNewChat => 'Новый чат';

  @override
  String get chatSearchHint => 'Поиск…';

  @override
  String get chatRecentChats => 'Недавние чаты';

  @override
  String get chatNoConversations => 'Чатов пока нет';

  @override
  String get chatSettings => 'Настройки';

  @override
  String get chatLogout => 'Выйти';

  @override
  String get chatLogoutTooltip => 'Выйти';

  @override
  String get chatDeleteTitle => 'Удалить чат';

  @override
  String get chatDeleteBody => 'Удалить этот чат?';

  @override
  String get chatCancel => 'Отмена';

  @override
  String get chatDelete => 'Удалить';

  @override
  String get chatAiAssistant => 'AI Assistant';

  @override
  String get chatWelcomeType1 => 'Добро пожаловать!';

  @override
  String get chatWelcomeType2 => 'Задайте любой вопрос';

  @override
  String get chatWelcomeType3 => 'Ответы ИИ нужно проверять';

  @override
  String get chatAskAnythingHint => 'Задайте любой вопрос…';

  @override
  String get chatMessageHint => 'Сообщение…';

  @override
  String get chatDisclaimer =>
      'ИИ может ошибаться. Проверяйте важную информацию.';

  @override
  String get suggestionTopProducts => 'Топ товаров';

  @override
  String get suggestionSalesForecast => 'Прогноз продаж';

  @override
  String get suggestionTrending => 'Популярные товары';

  @override
  String get suggestionCompare => 'Сравнить товары';

  @override
  String get roleYou => 'Вы';

  @override
  String get roleAiAssistant => 'AI Assistant';

  @override
  String get modelPickerTitle => 'Модель ИИ';

  @override
  String get modelRfDesc => 'Стабильная, хорошо работает на любых данных';

  @override
  String get modelLgbmDesc => 'Очень быстрая, для больших данных';

  @override
  String get modelXgbDesc => 'Высокая точность, сложные закономерности';

  @override
  String get miniChartTitle => 'Прогноз спроса';

  @override
  String get miniChartHistory => 'История';

  @override
  String get miniChartForecast => 'Прогноз';

  @override
  String productsCarouselTitle(int count) {
    return 'Товары ($count)';
  }

  @override
  String get productPriceUnknown => 'Цена не указана';

  @override
  String get chatErrorGeneric =>
      'Ошибка: не удалось связаться с сервером. Попробуйте позже.';

  @override
  String get routerPageNotFound => 'Страница не найдена';

  @override
  String get routerUnknownRoute => 'Неизвестный маршрут';

  @override
  String get routerGoHome => 'На главную';
}
