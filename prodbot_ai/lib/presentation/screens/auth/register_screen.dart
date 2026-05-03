import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/theme/theme.dart';
import '../../../services/auth_service.dart';
import '../../widgets/auth/auth_motion.dart';
import '../../widgets/common/widgets.dart';

/// Register screen styled after the web `AuthModal` register flow.
class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen>
    with TickerProviderStateMixin {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();

  late AnimationController _entrance;
  late AnimationController _pulse;

  String? _nameError;
  String? _emailError;
  String? _passwordError;
  String? _confirmPasswordError;
  bool _acceptTerms = false;
  int _formErrorTick = 0;

  @override
  void initState() {
    super.initState();
    _entrance = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 980),
    );
    _pulse = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 2800),
    );
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      if (authReduceMotion(context)) {
        _entrance.value = 1.0;
      } else {
        _entrance.forward();
        _pulse.repeat(reverse: true);
      }
    });
  }

  @override
  void dispose() {
    _entrance.dispose();
    _pulse.dispose();
    _nameController.dispose();
    _emailController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  String? _validateName(String? value) {
    if (value == null || value.isEmpty) return 'Атыңызды енгізіңіз';
    if (value.length < 2) return 'Кемінде 2 таңба';
    return null;
  }

  String? _validateEmail(String? value) {
    if (value == null || value.isEmpty) return 'Email қажет';
    final emailRegex = RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$');
    if (!emailRegex.hasMatch(value)) return 'Жарамды email енгізіңіз';
    return null;
  }

  String? _validatePassword(String? value) {
    if (value == null || value.isEmpty) return 'Құпия сөз қажет';
    if (value.length < 6) return 'Кемінде 6 таңба';
    return null;
  }

  String? _validateConfirmPassword(String? value) {
    if (value == null || value.isEmpty) return 'Құпия сөзді растаңыз';
    if (value != _passwordController.text) return 'Құпия сөздер сәйкес емес';
    return null;
  }

  double _calculatePasswordStrength(String password) {
    if (password.isEmpty) return 0;
    double s = 0;
    if (password.length >= 6) s += 0.2;
    if (password.length >= 8) s += 0.1;
    if (password.length >= 12) s += 0.1;
    if (password.contains(RegExp(r'[a-z]'))) s += 0.15;
    if (password.contains(RegExp(r'[A-Z]'))) s += 0.15;
    if (password.contains(RegExp(r'[0-9]'))) s += 0.15;
    if (password.contains(RegExp(r'[!@#$%^&*(),.?":{}|<>]'))) s += 0.15;
    return s.clamp(0.0, 1.0);
  }

  Color _getStrengthColor(double s) {
    if (s < 0.3) return AppColors.error;
    if (s < 0.6) return AppColors.warning;
    return AppColors.success;
  }

  String _getStrengthText(double s) {
    if (s < 0.3) return 'Әлсіз';
    if (s < 0.6) return 'Орташа';
    return 'Күшті';
  }

  Future<void> _handleRegister() async {
    setState(() {
      _nameError = null;
      _emailError = null;
      _passwordError = null;
      _confirmPasswordError = null;
    });

    final nameError = _validateName(_nameController.text);
    final emailError = _validateEmail(_emailController.text);
    final passwordError = _validatePassword(_passwordController.text);
    final confirmPasswordError =
        _validateConfirmPassword(_confirmPasswordController.text);

    if (nameError != null ||
        emailError != null ||
        passwordError != null ||
        confirmPasswordError != null) {
      setState(() {
        _nameError = nameError;
        _emailError = emailError;
        _passwordError = passwordError;
        _confirmPasswordError = confirmPasswordError;
        _formErrorTick++;
      });
      return;
    }

    if (!_acceptTerms) {
      setState(() => _formErrorTick++);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Шартты қабылдауыңыз керек'),
          behavior: SnackBarBehavior.floating,
        ),
      );
      return;
    }

    final authService = context.read<AuthService>();
    final result = await authService.register(
      _emailController.text.trim(),
      _passwordController.text,
      name: _nameController.text.trim(),
    );

    if (result.success && mounted) {
      Navigator.of(context).pushNamedAndRemoveUntil('/main', (route) => false);
    }
  }

  void _navigateToLogin() => Navigator.of(context).pop();

  @override
  Widget build(BuildContext context) {
    final passwordStrength =
        _calculatePasswordStrength(_passwordController.text);

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
          const Positioned.fill(child: AuthAmbientBackdrop()),
          SafeArea(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(
                horizontal: 24,
                vertical: 16,
              ),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    authStaggeredChild(
                      parent: _entrance,
                      step: 0,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          Center(
                            child: AuthLogoPulse(
                              animation: _pulse,
                              child: const BrandLogo(
                                size: 64,
                                radius: 18,
                                icon: Icons.person_add_rounded,
                                withGlow: true,
                              ),
                            ),
                          ),
                          const SizedBox(height: 24),
                          Text(
                            'Тіркелу',
                            style: AppTextStyles.displaySmall,
                            textAlign: TextAlign.center,
                          ),
                          const SizedBox(height: 6),
                          Text(
                            'Жаңа аккаунт жасау үшін деректерді енгізіңіз',
                            style: AppTextStyles.bodyMedium.copyWith(
                              color: AppColors.textSecondary,
                            ),
                            textAlign: TextAlign.center,
                          ),
                        ],
                      ),
                    ),

                    authStaggeredChild(
                      parent: _entrance,
                      step: 1,
                      child: const SizedBox(height: 32),
                    ),

                    authStaggeredChild(
                      parent: _entrance,
                      step: 2,
                      child: AuthShakeWrapper(
                        trigger: _formErrorTick,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            AppTextField(
                              label: 'Толық аты',
                              hintText: 'Атыңызды енгізіңіз',
                              controller: _nameController,
                              errorText: _nameError,
                              keyboardType: TextInputType.name,
                              textCapitalization: TextCapitalization.words,
                              prefixIcon:
                                  const Icon(Icons.person_outline_rounded),
                              onChanged: (_) {
                                if (_nameError != null) {
                                  setState(() => _nameError = null);
                                }
                              },
                            ),
                            const SizedBox(height: 14),
                            AppTextField.email(
                              label: 'Email',
                              hintText: 'email@example.com',
                              controller: _emailController,
                              errorText: _emailError,
                              onChanged: (_) {
                                if (_emailError != null) {
                                  setState(() => _emailError = null);
                                }
                              },
                            ),
                            const SizedBox(height: 14),
                            AppTextField.password(
                              label: 'Құпия сөз',
                              hintText: '••••••••',
                              controller: _passwordController,
                              errorText: _passwordError,
                              textInputAction: TextInputAction.next,
                              onChanged: (_) {
                                setState(() {
                                  if (_passwordError != null) {
                                    _passwordError = null;
                                  }
                                });
                              },
                            ),
                            if (_passwordController.text.isNotEmpty) ...[
                              const SizedBox(height: 10),
                              Row(
                                children: [
                                  Expanded(
                                    child: ClipRRect(
                                      borderRadius: BorderRadius.circular(4),
                                      child: LinearProgressIndicator(
                                        value: passwordStrength,
                                        backgroundColor: AppColors.border,
                                        valueColor:
                                            AlwaysStoppedAnimation<Color>(
                                          _getStrengthColor(passwordStrength),
                                        ),
                                        minHeight: 4,
                                      ),
                                    ),
                                  ),
                                  const SizedBox(width: 12),
                                  Text(
                                    _getStrengthText(passwordStrength),
                                    style: AppTextStyles.caption.copyWith(
                                      color: _getStrengthColor(
                                          passwordStrength),
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                ],
                              ),
                            ],
                            const SizedBox(height: 14),
                            AppTextField.password(
                              label: 'Құпия сөзді растау',
                              hintText: '••••••••',
                              controller: _confirmPasswordController,
                              errorText: _confirmPasswordError,
                              onChanged: (_) {
                                if (_confirmPasswordError != null) {
                                  setState(() => _confirmPasswordError = null);
                                }
                              },
                            ),
                            const SizedBox(height: 16),
                            InkWell(
                              onTap: () => setState(
                                  () => _acceptTerms = !_acceptTerms),
                              borderRadius: BorderRadius.circular(8),
                              child: Padding(
                                padding:
                                    const EdgeInsets.symmetric(vertical: 4),
                                child: Row(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    SizedBox(
                                      width: 18,
                                      height: 18,
                                      child: Checkbox(
                                        value: _acceptTerms,
                                        onChanged: (v) => setState(() =>
                                            _acceptTerms = v ?? false),
                                        materialTapTargetSize:
                                            MaterialTapTargetSize.shrinkWrap,
                                      ),
                                    ),
                                    const SizedBox(width: 10),
                                    Expanded(
                                      child: Text.rich(
                                        TextSpan(
                                          text: 'Мен ',
                                          style: AppTextStyles.bodySmall
                                              .copyWith(
                                            color: AppColors.textSecondary,
                                          ),
                                          children: [
                                            TextSpan(
                                              text: 'қызмет шарттарын',
                                              style: AppTextStyles.link.copyWith(
                                                color: AppColors.primary,
                                                fontWeight: FontWeight.w600,
                                              ),
                                            ),
                                            const TextSpan(text: ' және '),
                                            TextSpan(
                                              text: 'құпиялылық саясатын',
                                              style: AppTextStyles.link.copyWith(
                                                color: AppColors.primary,
                                                fontWeight: FontWeight.w600,
                                              ),
                                            ),
                                            const TextSpan(
                                                text: ' қабылдаймын'),
                                          ],
                                        ),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),

                    authStaggeredChild(
                      parent: _entrance,
                      step: 3,
                      child: Consumer<AuthService>(
                        builder: (context, authService, _) {
                          if (authService.error != null) {
                            return Padding(
                              padding: const EdgeInsets.only(top: 12),
                              child: AuthShakeWrapper(
                                trigger: authService.error,
                                child: _ErrorBanner(
                                    message: authService.error!),
                              ),
                            );
                          }
                          return const SizedBox.shrink();
                        },
                      ),
                    ),

                    authStaggeredChild(
                      parent: _entrance,
                      step: 4,
                      child: const SizedBox(height: 24),
                    ),

                    authStaggeredChild(
                      parent: _entrance,
                      step: 4,
                      child: Consumer<AuthService>(
                        builder: (context, authService, _) {
                          return AppButton.gradient(
                            text: 'Аккаунт жасау',
                            isLoading: authService.isLoading,
                            onPressed: authService.isLoading
                                ? null
                                : _handleRegister,
                          );
                        },
                      ),
                    ),

                    authStaggeredChild(
                      parent: _entrance,
                      step: 5,
                      child: const SizedBox(height: 20),
                    ),

                    authStaggeredChild(
                      parent: _entrance,
                      step: 5,
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            'Аккаунт бар ма? ',
                            style: AppTextStyles.bodySmall.copyWith(
                              color: AppColors.textSecondary,
                            ),
                          ),
                          GestureDetector(
                            onTap: _navigateToLogin,
                            child: Text(
                              'Кіру',
                              style: AppTextStyles.link.copyWith(
                                color: AppColors.primary,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),

                    authStaggeredChild(
                      parent: _entrance,
                      step: 6,
                      child: const SizedBox(height: 32),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
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
