import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/theme/theme.dart';
import '../../../services/auth_service.dart';
import '../../../services/storage_service.dart';
import '../../widgets/common/widgets.dart';
import 'settings_screen.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  // User data loaded from storage
  Map<String, dynamic> _user = {
    'name': 'Madina Samet',
    'email': 'testuser@prodbot.kz',
    'company': 'ProdBot AI',
    'role': 'User',
    'avatar': null,
    'plan': 'Pro',
    'joinDate': 'February 2024',
  };

  @override
  void initState() {
    super.initState();
    _loadUserData();
  }

  Future<void> _loadUserData() async {
    final authService = context.read<AuthService>();
    final userData = StorageService.getUserData();

    if (mounted) {
      setState(() {
        _user = {
          'name': userData?['name'] ?? 'Madina Samet',
          'email': authService.currentUserEmail ?? userData?['email'] ?? 'testuser@prodbot.kz',
          'company': userData?['company'] ?? 'ProdBot AI',
          'role': userData?['role'] ?? 'User',
          'avatar': userData?['avatar'],
          'plan': 'Pro',
          'joinDate': 'February 2024',
        };
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Profile'),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings_outlined),
            onPressed: () => _navigateToSettings(),
          ),
        ],
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            // Profile header
            _buildProfileHeader(),

            // Stats
            _buildStatsSection(),

            // Quick actions
            _buildQuickActions(),

            // Menu items
            _buildMenuSection(),

            const SizedBox(height: AppDimensions.spacing24),

            // Logout button
            Padding(
              padding: const EdgeInsets.symmetric(
                horizontal: AppDimensions.spacing16,
              ),
              child: AppButton(
                text: 'Log Out',
                variant: AppButtonVariant.outline,
                icon: Icons.logout,
                onPressed: _logout,
                fullWidth: true,
              ),
            ),

            const SizedBox(height: AppDimensions.spacing16),

            // Version info
            Text(
              'ProdBot AI v1.0.0',
              style: AppTextStyles.caption,
            ),

            const SizedBox(height: AppDimensions.spacing32),
          ],
        ),
      ),
    );
  }

  Widget _buildProfileHeader() {
    return Container(
      padding: const EdgeInsets.all(AppDimensions.spacing24),
      child: Column(
        children: [
          // Avatar
          Stack(
            children: [
              Container(
                width: 100,
                height: 100,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: AppColors.primary10,
                  border: Border.all(
                    color: AppColors.primary,
                    width: 3,
                  ),
                ),
                child: _user['avatar'] != null
                    ? ClipOval(
                        child: Image.network(
                          _user['avatar'],
                          fit: BoxFit.cover,
                        ),
                      )
                    : Center(
                        child: Text(
                          _getInitials(_user['name']),
                          style: AppTextStyles.headlineMedium.copyWith(
                            color: AppColors.primary,
                          ),
                        ),
                      ),
              ),
              Positioned(
                bottom: 0,
                right: 0,
                child: GestureDetector(
                  onTap: _changeAvatar,
                  child: Container(
                    width: 32,
                    height: 32,
                    decoration: BoxDecoration(
                      color: AppColors.primary,
                      shape: BoxShape.circle,
                      border: Border.all(
                        color: AppColors.white,
                        width: 2,
                      ),
                    ),
                    child: const Icon(
                      Icons.camera_alt,
                      size: 16,
                      color: AppColors.white,
                    ),
                  ),
                ),
              ),
            ],
          ),

          const SizedBox(height: AppDimensions.spacing16),

          // Name
          Text(_user['name'], style: AppTextStyles.headlineSmall),

          const SizedBox(height: AppDimensions.spacing4),

          // Email
          Text(
            _user['email'],
            style: AppTextStyles.bodyMedium.copyWith(
              color: AppColors.textSecondary,
            ),
          ),

          const SizedBox(height: AppDimensions.spacing8),

          // Plan badge
          Container(
            padding: const EdgeInsets.symmetric(
              horizontal: AppDimensions.spacing12,
              vertical: AppDimensions.spacing4,
            ),
            decoration: BoxDecoration(
              color: AppColors.primary10,
              borderRadius: BorderRadius.circular(AppDimensions.radiusFull),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(
                  Icons.workspace_premium,
                  size: 16,
                  color: AppColors.primary,
                ),
                const SizedBox(width: AppDimensions.spacing4),
                Text(
                  '${_user['plan']} Plan',
                  style: AppTextStyles.labelSmall.copyWith(
                    color: AppColors.primary,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatsSection() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: AppDimensions.spacing16),
      padding: const EdgeInsets.all(AppDimensions.spacing16),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
        border: Border.all(color: AppColors.border),
      ),
      child: Row(
        children: [
          Expanded(child: _buildStatItem('127', 'Forecasts')),
          Container(width: 1, height: 40, color: AppColors.border),
          Expanded(child: _buildStatItem('45', 'Products')),
          Container(width: 1, height: 40, color: AppColors.border),
          Expanded(child: _buildStatItem('91%', 'Avg Accuracy')),
        ],
      ),
    );
  }

  Widget _buildStatItem(String value, String label) {
    return Column(
      children: [
        Text(value, style: AppTextStyles.titleMedium),
        const SizedBox(height: AppDimensions.spacing4),
        Text(
          label,
          style: AppTextStyles.caption,
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  Widget _buildQuickActions() {
    return Padding(
      padding: const EdgeInsets.all(AppDimensions.spacing16),
      child: Row(
        children: [
          Expanded(
            child: _buildActionCard(
              'Edit Profile',
              Icons.person_outline,
              AppColors.primary,
              _editProfile,
            ),
          ),
          const SizedBox(width: AppDimensions.spacing12),
          Expanded(
            child: _buildActionCard(
              'Upgrade Plan',
              Icons.rocket_launch_outlined,
              AppColors.warning,
              _upgradePlan,
            ),
          ),
          const SizedBox(width: AppDimensions.spacing12),
          Expanded(
            child: _buildActionCard(
              'Get Help',
              Icons.help_outline,
              AppColors.info,
              _getHelp,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActionCard(
    String label,
    IconData icon,
    Color color,
    VoidCallback onTap,
  ) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(AppDimensions.spacing12),
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
          border: Border.all(color: AppColors.border),
        ),
        child: Column(
          children: [
            Container(
              width: 44,
              height: 44,
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(AppDimensions.radiusSm),
              ),
              child: Icon(icon, color: color, size: 22),
            ),
            const SizedBox(height: AppDimensions.spacing8),
            Text(
              label,
              style: AppTextStyles.labelSmall,
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMenuSection() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: AppDimensions.spacing16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Account', style: AppTextStyles.labelLarge),
          const SizedBox(height: AppDimensions.spacing12),

          _buildMenuItem(
            'Personal Information',
            Icons.person_outline,
            () {},
          ),
          _buildMenuItem(
            'Company Settings',
            Icons.business_outlined,
            () {},
          ),
          _buildMenuItem(
            'Security',
            Icons.lock_outline,
            () {},
          ),
          _buildMenuItem(
            'Notifications',
            Icons.notifications_outlined,
            () {},
          ),

          const SizedBox(height: AppDimensions.spacing24),

          Text('Preferences', style: AppTextStyles.labelLarge),
          const SizedBox(height: AppDimensions.spacing12),

          _buildMenuItem(
            'Language',
            Icons.language,
            () {},
            trailing: 'English',
          ),
          _buildMenuItem(
            'Theme',
            Icons.palette_outlined,
            () {},
            trailing: 'Light',
          ),
          _buildMenuItem(
            'Data Export',
            Icons.download_outlined,
            () {},
          ),

          const SizedBox(height: AppDimensions.spacing24),

          Text('Support', style: AppTextStyles.labelLarge),
          const SizedBox(height: AppDimensions.spacing12),

          _buildMenuItem(
            'Help Center',
            Icons.help_outline,
            () {},
          ),
          _buildMenuItem(
            'Contact Support',
            Icons.support_agent_outlined,
            () {},
          ),
          _buildMenuItem(
            'Privacy Policy',
            Icons.privacy_tip_outlined,
            () {},
          ),
          _buildMenuItem(
            'Terms of Service',
            Icons.description_outlined,
            () {},
          ),
        ],
      ),
    );
  }

  Widget _buildMenuItem(
    String title,
    IconData icon,
    VoidCallback onTap, {
    String? trailing,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.only(bottom: AppDimensions.spacing8),
        padding: const EdgeInsets.all(AppDimensions.spacing12),
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
          border: Border.all(color: AppColors.border),
        ),
        child: Row(
          children: [
            Icon(icon, color: AppColors.iconVariant, size: 22),
            const SizedBox(width: AppDimensions.spacing12),
            Expanded(
              child: Text(title, style: AppTextStyles.labelMedium),
            ),
            if (trailing != null)
              Text(
                trailing,
                style: AppTextStyles.bodySmall.copyWith(
                  color: AppColors.textSecondary,
                ),
              ),
            const SizedBox(width: AppDimensions.spacing8),
            const Icon(
              Icons.chevron_right,
              color: AppColors.iconVariant,
              size: 20,
            ),
          ],
        ),
      ),
    );
  }

  String _getInitials(String name) {
    final parts = name.split(' ');
    if (parts.length >= 2) {
      return '${parts[0][0]}${parts[1][0]}'.toUpperCase();
    }
    return name.isNotEmpty ? name[0].toUpperCase() : '?';
  }

  void _navigateToSettings() {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => const SettingsScreen()),
    );
  }

  void _changeAvatar() {
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.symmetric(vertical: AppDimensions.spacing16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.camera_alt_outlined),
              title: const Text('Take Photo'),
              onTap: () => Navigator.pop(context),
            ),
            ListTile(
              leading: const Icon(Icons.photo_library_outlined),
              title: const Text('Choose from Gallery'),
              onTap: () => Navigator.pop(context),
            ),
            if (_user['avatar'] != null)
              ListTile(
                leading: const Icon(Icons.delete_outline, color: AppColors.error),
                title: Text('Remove Photo', style: TextStyle(color: AppColors.error)),
                onTap: () => Navigator.pop(context),
              ),
          ],
        ),
      ),
    );
  }

  void _editProfile() {
    // Navigate to edit profile screen
  }

  void _upgradePlan() {
    // Show upgrade plan dialog or navigate
  }

  void _getHelp() {
    // Navigate to help center
  }

  void _logout() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
        ),
        title: const Text('Log Out'),
        content: const Text('Are you sure you want to log out?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () async {
              Navigator.pop(context);
              // Perform logout
              final authService = context.read<AuthService>();
              await authService.logout();
              // Navigate to welcome
              if (mounted) {
                Navigator.of(context).pushNamedAndRemoveUntil(
                  '/welcome',
                  (route) => false,
                );
              }
            },
            child: Text(
              'Log Out',
              style: TextStyle(color: AppColors.error),
            ),
          ),
        ],
      ),
    );
  }
}
