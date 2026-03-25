import 'package:flutter/material.dart';
import '../../../core/theme/theme.dart';
import '../auth/login_screen.dart';
import '../auth/register_screen.dart';

/// Welcome screen based on Figma design "JUZ40 Admin"
/// Node: 33737-76120
class WelcomeScreen extends StatelessWidget {
  const WelcomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.white,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(
            horizontal: AppDimensions.screenPaddingHorizontal,
          ),
          child: Column(
            children: [
              const Spacer(flex: 2),

              // Logo - 137x137 from Figma
              Image.asset(
                'assets/images/logo.png',
                width: 137,
                height: 137,
              ),

              const SizedBox(height: AppDimensions.spacing40),

              // "Welcome to" text - Plus Jakarta Sans Bold 36px
              Text(
                'Welcome to',
                style: AppTextStyles.displaySmall.copyWith(
                  color: AppColors.textPrimary,
                  fontWeight: FontWeight.w700,
                ),
              ),

              const SizedBox(height: AppDimensions.spacing8),

              // "ProdBot AI" text - Plus Jakarta Sans Bold 36px, green
              Text(
                'ProdBot AI',
                style: AppTextStyles.displaySmall.copyWith(
                  color: AppColors.primary,
                  fontWeight: FontWeight.w700,
                ),
              ),

              const Spacer(flex: 2),

              // Log in button - 379x56, green background, radius 50
              SizedBox(
                width: double.infinity,
                height: 56,
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.of(context).push(
                      MaterialPageRoute(builder: (_) => const LoginScreen()),
                    );
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.primary,
                    foregroundColor: AppColors.white,
                    elevation: 0,
                    shadowColor: Colors.black.withValues(alpha: 0.1),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(50),
                    ),
                  ),
                  child: Text(
                    'Log in',
                    style: AppTextStyles.button,
                  ),
                ),
              ),

              const SizedBox(height: AppDimensions.spacing24),

              // Sign up button - 379x56, light green background, radius 50
              SizedBox(
                width: double.infinity,
                height: 56,
                child: ElevatedButton(
                  onPressed: () {
                    Navigator.of(context).push(
                      MaterialPageRoute(builder: (_) => const RegisterScreen()),
                    );
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFFE8FAF4), // Light green from Figma
                    foregroundColor: AppColors.primary,
                    elevation: 0,
                    shadowColor: Colors.black.withValues(alpha: 0.2),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(50),
                    ),
                  ),
                  child: Text(
                    'Sign up',
                    style: AppTextStyles.button.copyWith(
                      color: AppColors.primary,
                    ),
                  ),
                ),
              ),

              const SizedBox(height: AppDimensions.spacing48),

              // "or continue with" divider
              Row(
                children: [
                  Expanded(
                    child: Container(
                      height: 1,
                      color: const Color(0xFFDEDEDE),
                    ),
                  ),
                  Padding(
                    padding: const EdgeInsets.symmetric(
                      horizontal: AppDimensions.spacing16,
                    ),
                    child: Text(
                      'or continue with',
                      style: AppTextStyles.bodyLarge.copyWith(
                        color: AppColors.textPrimary,
                      ),
                    ),
                  ),
                  Expanded(
                    child: Container(
                      height: 1,
                      color: const Color(0xFFDEDEDE),
                    ),
                  ),
                ],
              ),

              const SizedBox(height: AppDimensions.spacing32),

              // Social login buttons - 3 buttons, responsive width
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  // Google
                  Expanded(
                    child: _SocialButton(
                      icon: 'assets/icons/google.png',
                      fallbackIcon: Icons.g_mobiledata_rounded,
                      onTap: () {
                        // TODO: Google login
                      },
                    ),
                  ),
                  const SizedBox(width: AppDimensions.spacing12),
                  // Apple
                  Expanded(
                    child: _SocialButton(
                      icon: 'assets/icons/apple.png',
                      fallbackIcon: Icons.apple,
                      onTap: () {
                        // TODO: Apple login
                      },
                    ),
                  ),
                  const SizedBox(width: AppDimensions.spacing12),
                  // X (Twitter)
                  Expanded(
                    child: _SocialButton(
                      icon: 'assets/icons/x.png',
                      fallbackIcon: Icons.close,
                      onTap: () {
                        // TODO: X login
                      },
                    ),
                  ),
                ],
              ),

              const SizedBox(height: AppDimensions.spacing48),
            ],
          ),
        ),
      ),
    );
  }
}

/// Social login button - responsive width, 56 height, gray background (#F7F7F7), radius 50
class _SocialButton extends StatelessWidget {
  final String icon;
  final IconData fallbackIcon;
  final VoidCallback onTap;

  const _SocialButton({
    required this.icon,
    required this.fallbackIcon,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(50),
      child: Container(
        height: 56,
        decoration: BoxDecoration(
          color: const Color(0xFFF7F7F7), // Gray background from Figma
          borderRadius: BorderRadius.circular(50),
          border: Border.all(
            color: const Color(0xFFEDEDED), // Border from Figma
            width: 1,
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.1),
              blurRadius: 4,
              offset: const Offset(0, 1),
            ),
          ],
        ),
        child: Center(
          child: _buildIcon(),
        ),
      ),
    );
  }

  Widget _buildIcon() {
    // Try to load image, fallback to icon
    return Image.asset(
      icon,
      width: 24,
      height: 24,
      errorBuilder: (context, error, stackTrace) {
        return Icon(
          fallbackIcon,
          size: 24,
          color: AppColors.textPrimary,
        );
      },
    );
  }
}