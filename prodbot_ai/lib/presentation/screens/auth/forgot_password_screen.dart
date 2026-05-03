import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/theme/theme.dart';
import '../../../services/auth_service.dart';
import '../../widgets/common/widgets.dart';

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
    if (value == null || value.isEmpty) return 'Email қажет';
    final emailRegex = RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$');
    if (!emailRegex.hasMatch(value)) return 'Жарамды email енгізіңіз';
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
          icon: const Icon(Icons.arrow_back_rounded, size: 22),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: Stack(
        children: [
          Positioned.fill(
            child: DecoratedBox(
              decoration: BoxDecoration(
                gradient: RadialGradient(
                  center: const Alignment(0, -0.7),
                  radius: 1.0,
                  colors: [
                    AppColors.primary.withValues(alpha: 0.10),
                    Colors.transparent,
                  ],
                ),
              ),
            ),
          ),
          SafeArea(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(
                horizontal: 24,
                vertical: 16,
              ),
              child: _emailSent ? _buildSuccess(context) : _buildForm(context),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildForm(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Center(
          child: BrandLogo(
            size: 64,
            radius: 18,
            icon: Icons.lock_reset_rounded,
            withGlow: true,
          ),
        ),
        const SizedBox(height: 24),
        Text(
          'Құпия сөзді ұмыттыңыз ба?',
          style: AppTextStyles.displaySmall,
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 8),
        Text(
          'Email енгізіңіз — қалпына келтіру сілтемесін жібереміз.',
          style: AppTextStyles.bodyMedium.copyWith(
            color: AppColors.textSecondary,
          ),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 32),

        AppTextField.email(
          label: 'Email',
          hintText: 'email@example.com',
          controller: _emailController,
          errorText: _emailError,
          onChanged: (_) {
            if (_emailError != null) setState(() => _emailError = null);
          },
          onFieldSubmitted: (_) => _handleResetPassword(),
        ),

        Consumer<AuthService>(
          builder: (context, authService, _) {
            if (authService.error != null) {
              return Padding(
                padding: const EdgeInsets.only(top: 12),
                child: _ErrorBanner(message: authService.error!),
              );
            }
            return const SizedBox.shrink();
          },
        ),

        const SizedBox(height: 24),

        Consumer<AuthService>(
          builder: (context, authService, _) {
            return AppButton.gradient(
              text: 'Сілтемені жіберу',
              isLoading: authService.isLoading,
              onPressed:
                  authService.isLoading ? null : _handleResetPassword,
            );
          },
        ),

        const SizedBox(height: 20),

        Center(
          child: GestureDetector(
            onTap: () => Navigator.of(context).pop(),
            child: Text.rich(
              TextSpan(
                text: 'Құпия сөзді есте сақтайсыз ба? ',
                style: AppTextStyles.bodySmall.copyWith(
                  color: AppColors.textSecondary,
                ),
                children: [
                  TextSpan(
                    text: 'Кіру',
                    style: AppTextStyles.link.copyWith(
                      color: AppColors.primary,
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

  Widget _buildSuccess(BuildContext context) {
    return Column(
      children: [
        const SizedBox(height: 40),
        Container(
          width: 96,
          height: 96,
          decoration: BoxDecoration(
            color: AppColors.success.withValues(alpha: 0.12),
            shape: BoxShape.circle,
            border: Border.all(
              color: AppColors.success.withValues(alpha: 0.35),
              width: 1,
            ),
          ),
          child: const Icon(
            Icons.mark_email_read_rounded,
            size: 44,
            color: AppColors.success,
          ),
        ),
        const SizedBox(height: 28),
        Text(
          'Email тексеріңіз',
          style: AppTextStyles.headlineMedium,
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 12),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Text(
            'Қалпына келтіру сілтемесі жіберілді:\n${_emailController.text}',
            style: AppTextStyles.bodyMedium.copyWith(
              color: AppColors.textSecondary,
            ),
            textAlign: TextAlign.center,
          ),
        ),
        const SizedBox(height: 32),
        AppButton.gradient(
          text: 'Кіруге оралу',
          onPressed: () {
            Navigator.of(context).popUntil((route) => route.isFirst);
          },
        ),
        const SizedBox(height: 12),
        TextButton(
          onPressed: () => setState(() => _emailSent = false),
          child: Text(
            'Email алмадыңыз ба? Қайта жіберу',
            style: AppTextStyles.link.copyWith(color: AppColors.primary),
          ),
        ),
      ],
    );
  }
}

class _ErrorBanner extends StatelessWidget {
  final String message;
  const _ErrorBanner({required this.message});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: AppColors.error.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
        border: Border.all(color: AppColors.error.withValues(alpha: 0.35)),
      ),
      child: Row(
        children: [
          const Icon(Icons.error_outline, color: AppColors.error, size: 18),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              message,
              style: AppTextStyles.caption.copyWith(color: AppColors.error),
            ),
          ),
        ],
      ),
    );
  }
}
