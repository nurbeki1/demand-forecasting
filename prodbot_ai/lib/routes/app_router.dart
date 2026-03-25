import 'package:flutter/material.dart';
import '../presentation/screens/splash/splash_screen.dart';
import '../presentation/screens/onboarding/welcome_screen.dart';
import '../presentation/screens/auth/login_screen.dart';
import '../presentation/screens/auth/register_screen.dart';
import '../presentation/screens/auth/forgot_password_screen.dart';
import '../presentation/screens/main/main_screen.dart';
import '../presentation/screens/home/home_screen.dart';
import '../presentation/screens/forecast/forecast_list_screen.dart';
import '../presentation/screens/forecast/forecast_detail_screen.dart';
import '../presentation/screens/forecast/create_forecast_screen.dart';
import '../presentation/screens/forecast/widgets/forecast_card.dart';
import '../presentation/screens/products/products_screen.dart';
import '../presentation/screens/products/product_detail_screen.dart';
import '../presentation/screens/products/add_product_screen.dart';
import '../presentation/screens/products/widgets/product_card.dart';
import '../presentation/screens/analytics/analytics_screen.dart';
import '../presentation/screens/profile/profile_screen.dart';
import '../presentation/screens/profile/settings_screen.dart';

/// Route names
class AppRoutes {
  AppRoutes._();

  static const String splash = '/';
  static const String welcome = '/welcome';
  static const String onboarding = '/onboarding';
  static const String login = '/login';
  static const String register = '/register';
  static const String forgotPassword = '/forgot-password';
  static const String main = '/main';
  static const String home = '/home';
  static const String forecast = '/forecast';
  static const String forecastDetail = '/forecast/detail';
  static const String createForecast = '/forecast/create';
  static const String products = '/products';
  static const String productDetail = '/products/detail';
  static const String addProduct = '/products/add';
  static const String analytics = '/analytics';
  static const String profile = '/profile';
  static const String settings = '/settings';
}

/// App Router - handles all navigation
class AppRouter {
  AppRouter._();

  static Route<dynamic> generateRoute(RouteSettings settings) {
    switch (settings.name) {
      case AppRoutes.splash:
        return _fadeRoute(const SplashScreen(), settings);

      case AppRoutes.welcome:
        return _slideRoute(const WelcomeScreen(), settings);

      case AppRoutes.onboarding:
        return _slideRoute(const WelcomeScreen(), settings);

      case AppRoutes.login:
        return _slideRoute(const LoginScreen(), settings);

      case AppRoutes.register:
        return _slideRoute(const RegisterScreen(), settings);

      case AppRoutes.forgotPassword:
        return _slideRoute(const ForgotPasswordScreen(), settings);

      case AppRoutes.main:
        return _fadeRoute(const MainScreen(), settings);

      case AppRoutes.home:
        return _fadeRoute(const HomeScreen(), settings);

      case AppRoutes.forecast:
        return _slideRoute(const ForecastListScreen(), settings);

      case AppRoutes.forecastDetail:
        final args = settings.arguments;
        if (args is ForecastData) {
          return _slideRoute(
            ForecastDetailScreen(forecast: args),
            settings,
          );
        }
        return _fadeRoute(
          _ErrorScreen(routeName: settings.name),
          settings,
        );

      case AppRoutes.createForecast:
        return _slideUpRoute(const CreateForecastScreen(), settings);

      case AppRoutes.products:
        return _slideRoute(const ProductsScreen(), settings);

      case AppRoutes.productDetail:
        final args = settings.arguments;
        if (args is ProductData) {
          return _slideRoute(
            ProductDetailScreen(product: args),
            settings,
          );
        }
        return _fadeRoute(
          _ErrorScreen(routeName: settings.name),
          settings,
        );

      case AppRoutes.addProduct:
        return _slideUpRoute(const AddProductScreen(), settings);

      case AppRoutes.analytics:
        return _slideRoute(const AnalyticsScreen(), settings);

      case AppRoutes.profile:
        return _slideRoute(const ProfileScreen(), settings);

      case AppRoutes.settings:
        return _slideRoute(const SettingsScreen(), settings);

      default:
        return _fadeRoute(
          _ErrorScreen(routeName: settings.name),
          settings,
        );
    }
  }

  /// Fade transition
  static Route<T> _fadeRoute<T>(Widget page, RouteSettings settings) {
    return PageRouteBuilder<T>(
      settings: settings,
      pageBuilder: (context, animation, secondaryAnimation) => page,
      transitionsBuilder: (context, animation, secondaryAnimation, child) {
        return FadeTransition(
          opacity: animation,
          child: child,
        );
      },
      transitionDuration: const Duration(milliseconds: 300),
    );
  }

  /// Slide transition from right
  static Route<T> _slideRoute<T>(Widget page, RouteSettings settings) {
    return PageRouteBuilder<T>(
      settings: settings,
      pageBuilder: (context, animation, secondaryAnimation) => page,
      transitionsBuilder: (context, animation, secondaryAnimation, child) {
        const begin = Offset(1.0, 0.0);
        const end = Offset.zero;
        const curve = Curves.easeInOut;

        var tween = Tween(begin: begin, end: end).chain(
          CurveTween(curve: curve),
        );

        return SlideTransition(
          position: animation.drive(tween),
          child: child,
        );
      },
      transitionDuration: const Duration(milliseconds: 300),
    );
  }

  /// Slide transition from bottom
  static Route<T> _slideUpRoute<T>(Widget page, RouteSettings settings) {
    return PageRouteBuilder<T>(
      settings: settings,
      pageBuilder: (context, animation, secondaryAnimation) => page,
      transitionsBuilder: (context, animation, secondaryAnimation, child) {
        const begin = Offset(0.0, 1.0);
        const end = Offset.zero;
        const curve = Curves.easeInOut;

        var tween = Tween(begin: begin, end: end).chain(
          CurveTween(curve: curve),
        );

        return SlideTransition(
          position: animation.drive(tween),
          child: child,
        );
      },
      transitionDuration: const Duration(milliseconds: 300),
    );
  }
}

/// Error screen for unknown routes
class _ErrorScreen extends StatelessWidget {
  final String? routeName;

  const _ErrorScreen({this.routeName});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.error_outline,
              size: 64,
              color: Colors.grey,
            ),
            const SizedBox(height: 16),
            Text(
              'Page not found',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 8),
            Text(
              routeName ?? 'Unknown route',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Colors.grey,
                  ),
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: () {
                Navigator.of(context).pushNamedAndRemoveUntil(
                  AppRoutes.main,
                  (route) => false,
                );
              },
              child: const Text('Go Home'),
            ),
          ],
        ),
      ),
    );
  }
}
