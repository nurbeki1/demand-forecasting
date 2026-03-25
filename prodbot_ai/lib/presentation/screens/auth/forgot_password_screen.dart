import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/theme/theme.dart';
import '../../../services/auth_service.dart';
import '../../widgets/common/app_button.dart';
import '../../widgets/common/app_text_field.dart';

class ForgotPasswordScreen extends StatefulWidget {
  const ForgotPasswordScreen({super.key});

  @override
  State<ForgotPasswordScreen> createState() => _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends State<ForgotPasswordScreen> {
  final _emailController = TextEditingController();
  String? _emailError;
  bool _emailSent = false;

  @override
  void dispose() {
    _emailController.dispose();
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

  Future<void> _handleResetPassword() async {
    setState(() => _emailError = null);

    final error = _validateEmail(_emailController.text);
    if (error != null) {
      setState(() => _emailError = error);
      return;
    }

    final authService = context.read<AuthService>();
    final success = await authService.requestPasswordReset(
      _emailController.text.trim(),
    );

    if (success && mounted) {
      setState(() => _emailSent = true);
    }
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
          child: _emailSent ? _buildSuccessContent() : _buildFormContent(),
        ),
      ),
    );
  }

  Widget _buildFormContent() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SizedBox(height: AppDimensions.spacing16),

        // Title
        Text(
          'Forgot Password?',
          style: AppTextStyles.headlineLarge,
        ),
        const SizedBox(height: AppDimensions.spacing8),

        // Subtitle
        Text(
          'No worries! Enter your email address and we\'ll send you a link to reset your password.',
          style: AppTextStyles.bodyMedium.copyWith(
            color: AppColors.textSecondary,
          ),
        ),

        const SizedBox(height: AppDimensions.spacing32),

        // Email field
        AppTextField.email(
          controller: _emailController,
          errorText: _emailError,
          onChanged: (_) {
            if (_emailError != null) {
              setState(() => _emailError = null);
            }
          },
          onFieldSubmitted: (_) => _handleResetPassword(),
        ),

        // Error message
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

        // Submit button
        Consumer<AuthService>(
          builder: (context, authService, _) {
            return AppButton.primary(
              text: 'Send Reset Link',
              isLoading: authService.isLoading,
              onPressed: authService.isLoading ? null : _handleResetPassword,
            );
          },
        ),

        const SizedBox(height: AppDimensions.spacing24),

        // Back to login link
        Center(
          child: GestureDetector(
            onTap: () => Navigator.of(context).pop(),
            child: Text.rich(
              TextSpan(
                text: 'Remember your password? ',
                style: AppTextStyles.bodySmall,
                children: [
                  TextSpan(
                    text: 'Log in',
                    style: AppTextStyles.link.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildSuccessContent() {
    return Column(
      children: [
        const SizedBox(height: AppDimensions.spacing48),

        // Success icon
        Container(
          width: 100,
          height: 100,
          decoration: BoxDecoration(
            color: AppColors.successSmooth,
            shape: BoxShape.circle,
          ),
          child: const Icon(
            Icons.mark_email_read_outlined,
            size: 48,
            color: AppColors.success,
          ),
        ),

        const SizedBox(height: AppDimensions.spacing32),

        // Title
        Text(
          'Check Your Email',
          style: AppTextStyles.headlineMedium,
          textAlign: TextAlign.center,
        ),

        const SizedBox(height: AppDimensions.spacing12),

        // Subtitle
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: AppDimensions.spacing16),
          child: Text(
            'We\'ve sent a password reset link to\n${_emailController.text}',
            style: AppTextStyles.bodyMedium.copyWith(
              color: AppColors.textSecondary,
            ),
            textAlign: TextAlign.center,
          ),
        ),

        const SizedBox(height: AppDimensions.spacing32),

        // Back to login button
        AppButton.primary(
          text: 'Back to Login',
          onPressed: () {
            Navigator.of(context).popUntil((route) => route.isFirst);
          },
        ),

        const SizedBox(height: AppDimensions.spacing16),

        // Resend link
        TextButton(
          onPressed: () {
            setState(() => _emailSent = false);
          },
          child: Text(
            'Didn\'t receive the email? Resend',
            style: AppTextStyles.link,
          ),
        ),
      ],
    );
  }
}
