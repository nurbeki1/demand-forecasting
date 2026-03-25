import 'package:flutter/material.dart';
import '../../../core/theme/theme.dart';

/// Home Screen - Dashboard based on Figma design
class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(AppDimensions.spacing16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              _buildHeader(),

              const SizedBox(height: AppDimensions.spacing24),

              // Welcome card
              _buildWelcomeCard(),

              const SizedBox(height: AppDimensions.spacing24),

              // Quick actions
              Text(
                'Quick Actions',
                style: AppTextStyles.titleSmall,
              ),
              const SizedBox(height: AppDimensions.spacing12),
              _buildQuickActions(),

              const SizedBox(height: AppDimensions.spacing24),

              // Recent activity
              Text(
                'Recent Activity',
                style: AppTextStyles.titleSmall,
              ),
              const SizedBox(height: AppDimensions.spacing12),
              _buildRecentActivity(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Row(
      children: [
        // Logo
        Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: AppColors.primary,
            borderRadius: BorderRadius.circular(10),
          ),
          child: const Icon(
            Icons.smart_toy_rounded,
            size: 24,
            color: AppColors.white,
          ),
        ),

        const SizedBox(width: AppDimensions.spacing12),

        // Title
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'ProdBot AI',
              style: AppTextStyles.titleMedium,
            ),
            Text(
              'Demand Forecasting',
              style: AppTextStyles.caption,
            ),
          ],
        ),

        const Spacer(),

        // Notifications
        IconButton(
          onPressed: () {},
          icon: const Icon(
            Icons.notifications_outlined,
            color: AppColors.iconDefault,
          ),
        ),
      ],
    );
  }

  Widget _buildWelcomeCard() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(AppDimensions.spacing20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [AppColors.primary, Color(0xFF12A876)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Welcome back!',
            style: AppTextStyles.headlineSmall.copyWith(
              color: AppColors.white,
            ),
          ),
          const SizedBox(height: AppDimensions.spacing8),
          Text(
            'Start a conversation with AI to get demand forecasts for your products.',
            style: AppTextStyles.bodyMedium.copyWith(
              color: AppColors.white.withValues(alpha: 0.9),
            ),
          ),
          const SizedBox(height: AppDimensions.spacing16),
          ElevatedButton(
            onPressed: () {},
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.white,
              foregroundColor: AppColors.primary,
              elevation: 0,
              padding: const EdgeInsets.symmetric(
                horizontal: AppDimensions.spacing20,
                vertical: AppDimensions.spacing12,
              ),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
              ),
            ),
            child: Text(
              'Start Chat',
              style: AppTextStyles.labelLarge.copyWith(
                color: AppColors.primary,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActions() {
    return Row(
      children: [
        Expanded(
          child: _QuickActionCard(
            icon: Icons.analytics_outlined,
            title: 'Forecast',
            color: AppColors.primary,
          ),
        ),
        const SizedBox(width: AppDimensions.spacing12),
        Expanded(
          child: _QuickActionCard(
            icon: Icons.inventory_2_outlined,
            title: 'Products',
            color: AppColors.info,
          ),
        ),
        const SizedBox(width: AppDimensions.spacing12),
        Expanded(
          child: _QuickActionCard(
            icon: Icons.bar_chart_outlined,
            title: 'Analytics',
            color: AppColors.purpleHaze,
          ),
        ),
      ],
    );
  }

  Widget _buildRecentActivity() {
    return Column(
      children: [
        _ActivityItem(
          title: 'Forecast generated',
          subtitle: 'P0001 - 7 days forecast',
          time: '2h ago',
          icon: Icons.check_circle_outline,
          iconColor: AppColors.success,
        ),
        const SizedBox(height: AppDimensions.spacing8),
        _ActivityItem(
          title: 'New product added',
          subtitle: 'P0005 - Electronics',
          time: '5h ago',
          icon: Icons.add_circle_outline,
          iconColor: AppColors.info,
        ),
        const SizedBox(height: AppDimensions.spacing8),
        _ActivityItem(
          title: 'Model retrained',
          subtitle: 'Updated with latest data',
          time: '1d ago',
          icon: Icons.refresh,
          iconColor: AppColors.primary,
        ),
      ],
    );
  }
}

class _QuickActionCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final Color color;

  const _QuickActionCard({
    required this.icon,
    required this.title,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(AppDimensions.spacing16),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
      ),
      child: Column(
        children: [
          Icon(icon, size: 28, color: color),
          const SizedBox(height: AppDimensions.spacing8),
          Text(
            title,
            style: AppTextStyles.labelMedium,
          ),
        ],
      ),
    );
  }
}

class _ActivityItem extends StatelessWidget {
  final String title;
  final String subtitle;
  final String time;
  final IconData icon;
  final Color iconColor;

  const _ActivityItem({
    required this.title,
    required this.subtitle,
    required this.time,
    required this.icon,
    required this.iconColor,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(AppDimensions.spacing12),
      decoration: BoxDecoration(
        color: AppColors.cardBackground,
        borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
      ),
      child: Row(
        children: [
          Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(
              color: iconColor.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(AppDimensions.radiusSm),
            ),
            child: Icon(icon, size: 18, color: iconColor),
          ),
          const SizedBox(width: AppDimensions.spacing12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: AppTextStyles.labelMedium),
                Text(
                  subtitle,
                  style: AppTextStyles.caption,
                ),
              ],
            ),
          ),
          Text(time, style: AppTextStyles.caption),
        ],
      ),
    );
  }
}