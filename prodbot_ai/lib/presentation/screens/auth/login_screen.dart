import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/theme/theme.dart';
import '../../../services/auth_service.dart';
import '../../widgets/common/app_button.dart';
import '../../widgets/common/app_text_field.dart';
import 'register_screen.dart';
import 'forgot_password_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _emailFocusNode = FocusNode();
  final _passwordFocusNode = FocusNode();

  bool _rememberMe = false;
  String? _emailError;
  String? _passwordError;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    _emailFocusNode.dispose();
    _passwordFocusNode.dispose();
    super.dispose();
  }

  String? _validateEmail(String? value) {
    if (value == null || value.isEmpty) {
      return 'Please enter your email';
    }
    final emailRegex = RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$');
    if (!emailRegex.hasMatch(value)) {
      return 'Please enter a valid email';
    }
    return null;
  }

  String? _validatePassword(String? value) {
    if (value == null || value.isEmpty) {
      return 'Please enter your password';
    }
    if (value.length < 4) {
      return 'Password must be at least 4 characters';
    }
    return null;
  }

  Future<void> _handleLogin() async {
    // Clear previous errors
    setState(() {
      _emailError = null;
      _passwordError = null;
    });

    // Validate
    final emailError = _validateEmail(_emailController.text);
    final passwordError = _validatePassword(_passwordController.text);

    if (emailError != null || passwordError != null) {
      setState(() {
        _emailError = emailError;
        _passwordError = passwordError;
      });
      return;
    }

    final authService = context.read<AuthService>();
    final result = await authService.login(
      _emailController.text.trim(),
      _passwordController.text,
    );

    if (result.success && mounted) {
      // Navigate to main
      Navigator.of(context).pushNamedAndRemoveUntil('/main', (route) => false);
    }
  }

  void _navigateToRegister() {
    Navigator.of(context).push(
      MaterialPageRoute(builder: (_) => const RegisterScreen()),
    );
  }

  void _navigateToForgotPassword() {
    Navigator.of(context).push(
      MaterialPageRoute(builder: (_) => const ForgotPasswordScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios, size: 20),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: AppDimensions.screenPadding,
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: AppDimensions.spacing16),

                // Title
                Text(
                  'Welcome back!',
                  style: AppTextStyles.headlineLarge,
                ),
                const SizedBox(height: AppDimensions.spacing8),

                // Subtitle
                Text(
                  'Please enter your email and password to log in',
                  style: AppTextStyles.bodyMedium.copyWith(
                    color: AppColors.textSecondary,
                  ),
                ),

                const SizedBox(height: AppDimensions.spacing32),

                // Email field
                AppTextField.email(
                  controller: _emailController,
                  focusNode: _emailFocusNode,
                  errorText: _emailError,
                  onChanged: (_) {
                    if (_emailError != null) {
                      setState(() => _emailError = null);
                    }
                  },
                  onFieldSubmitted: (_) {
                    _passwordFocusNode.requestFocus();
                  },
                ),

                const SizedBox(height: AppDimensions.spacing20),

                // Password field
                AppTextField.password(
                  controller: _passwordController,
                  focusNode: _passwordFocusNode,
                  errorText: _passwordError,
                  onChanged: (_) {
                    if (_passwordError != null) {
                      setState(() => _passwordError = null);
                    }
                  },
                  onFieldSubmitted: (_) => _handleLogin(),
                ),

                const SizedBox(height: AppDimensions.spacing16),

                // Remember me & Forgot password row
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    // Remember me
                    GestureDetector(
                      onTap: () {
                        setState(() => _rememberMe = !_rememberMe);
                      },
                      child: Row(
                        children: [
                          SizedBox(
                            width: 20,
                            height: 20,
                            child: Checkbox(
                              value: _rememberMe,
                              onChanged: (value) {
                                setState(() => _rememberMe = value ?? false);
                              },
                              activeColor: AppColors.primary,
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(4),
                              ),
                            ),
                          ),
                          const SizedBox(width: AppDimensions.spacing8),
                          Text(
                            'Remember me',
                            style: AppTextStyles.bodySmall,
                          ),
                        ],
                      ),
                    ),

                    // Forgot password
                    TextButton(
                      onPressed: _navigateToForgotPassword,
                      style: TextButton.styleFrom(
                        padding: EdgeInsets.zero,
                        minimumSize: Size.zero,
                        tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                      ),
                      child: Text(
                        'Forgot Password?',
                        style: AppTextStyles.link,
                      ),
                    ),
                  ],
                ),

                // Error message from auth service
                Consumer<AuthService>(
                  builder: (context, authService, _) {
                    if (authService.error != null) {
                      return Padding(
                        padding: const EdgeInsets.only(top: AppDimensions.spacing16),
                        child: Container(
                          padding: const EdgeInsets.all(AppDimensions.spacing12),
                          decoration: BoxDecoration(
                            color: AppColors.errorSmooth,
                            borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
                            border: Border.all(
                              color: AppColors.error.withValues(alpha: 0.3),
                            ),
                          ),
                          child: Row(
                            children: [
                              const Icon(
                                Icons.error_outline,
                                color: AppColors.error,
                                size: 20,
                              ),
                              const SizedBox(width: AppDimensions.spacing8),
                              Expanded(
                                child: Text(
                                  authService.error!,
                                  style: AppTextStyles.bodySmall.copyWith(
                                    color: AppColors.error,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                      );
                    }
                    return const SizedBox.shrink();
                  },
                ),

                const SizedBox(height: AppDimensions.spacing32),

                // Login button
                Consumer<AuthService>(
                  builder: (context, authService, _) {
                    return AppButton.primary(
                      text: 'Continue',
                      isLoading: authService.isLoading,
                      onPressed: authService.isLoading ? null : _handleLogin,
                    );
                  },
                ),

                const SizedBox(height: AppDimensions.spacing24),

                // Sign up link
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      "Don't have an account? ",
                      style: AppTextStyles.bodySmall,
                    ),
                    GestureDetector(
                      onTap: _navigateToRegister,
                      child: Text(
                        'Sign up',
                        style: AppTextStyles.link.copyWith(
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: AppDimensions.spacing32),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
