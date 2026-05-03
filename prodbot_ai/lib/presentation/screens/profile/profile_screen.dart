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
          'email': authService.currentUserEmail ??
              userData?['email'] ??
              'testuser@prodbot.kz',
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
      body: SafeArea(
        child: SingleChildScrollView(
          child: Column(
            children: [
              _buildAppBar(),
              const Divider(height: 1, color: AppColors.borderSubtle),
              const SizedBox(height: 8),
              _buildProfileHeader(),
              const SizedBox(height: 12),
              _buildStatsSection(),
              const SizedBox(height: 16),
              _buildQuickActions(),
              const SizedBox(height: 8),
              _buildMenuSection('Аккаунт', [
                _MenuItemData(
                    'Жеке ақпарат', Icons.person_outline_rounded, () {}),
                _MenuItemData('Компания', Icons.business_outlined, () {}),
                _MenuItemData('Қауіпсіздік', Icons.lock_outline_rounded, () {}),
                _MenuItemData(
                    'Хабарламалар', Icons.notifications_outlined, () {}),
              ]),
              const SizedBox(height: 16),
              _buildMenuSection('Қалаулар', [
                _MenuItemData(
                  'Тіл',
                  Icons.language_rounded,
                  () {},
                  trailing: 'Қазақша',
                ),
                _MenuItemData(
                  'Тақырып',
                  Icons.palette_outlined,
                  () {},
                  trailing: 'Қараңғы',
                ),
                _MenuItemData(
                  'Деректерді экспорттау',
                  Icons.download_outlined,
                  () {},
                ),
              ]),
              const SizedBox(height: 16),
              _buildMenuSection('Қолдау', [
                _MenuItemData(
                  'Көмек орталығы',
                  Icons.help_outline_rounded,
                  () {},
                ),
                _MenuItemData(
                  'Қолдау қызметі',
                  Icons.support_agent_outlined,
                  () {},
                ),
                _MenuItemData(
                  'Құпиялылық саясаты',
                  Icons.privacy_tip_outlined,
                  () {},
                ),
              ]),
              const SizedBox(height: 24),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: AppButton.outline(
                  text: 'Шығу',
                  prefixIcon: Icons.logout_rounded,
                  onPressed: _logout,
                ),
              ),
              const SizedBox(height: 16),
              Text(
                'ProdBot AI v1.0.0',
                style: AppTextStyles.caption.copyWith(
                  color: AppColors.textHint,
                ),
              ),
              const SizedBox(height: 32),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAppBar() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 12, 12, 12),
      child: Row(
        children: [
          Text('Профиль', style: AppTextStyles.titleLarge),
          const Spacer(),
          _IconBubble(
            icon: Icons.settings_outlined,
            onTap: _navigateToSettings,
          ),
        ],
      ),
    );
  }

  Widget _buildProfileHeader() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
      child: Column(
        children: [
          Stack(
            children: [
              Container(
                width: 96,
                height: 96,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  gradient: AppColors.primaryGradient,
                  boxShadow: [
                    BoxShadow(
                      color: AppColors.primary.withValues(alpha: 0.4),
                      blurRadius: 28,
                      spreadRadius: -4,
                      offset: const Offset(0, 12),
                    ),
                  ],
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
                          _getInitials(_user['name'] as String),
                          style: AppTextStyles.headlineMedium.copyWith(
                            color: AppColors.white,
                            fontWeight: FontWeight.w800,
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
                    width: 30,
                    height: 30,
                    decoration: BoxDecoration(
                      color: AppColors.surface,
                      shape: BoxShape.circle,
                      border: Border.all(
                        color: AppColors.background,
                        width: 3,
                      ),
                    ),
                    child: const Icon(
                      Icons.camera_alt_rounded,
                      size: 14,
                      color: AppColors.primary,
                    ),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Text(_user['name'] as String, style: AppTextStyles.titleLarge),
          const SizedBox(height: 4),
          Text(
            _user['email'] as String,
            style: AppTextStyles.bodySmall.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 5),
            decoration: BoxDecoration(
              color: AppColors.primary10,
              borderRadius: BorderRadius.circular(999),
              border: Border.all(
                color: AppColors.primary.withValues(alpha: 0.3),
              ),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(
                  Icons.workspace_premium_rounded,
                  size: 14,
                  color: AppColors.primary,
                ),
                const SizedBox(width: 6),
                Text(
                  '${_user['plan']} жоспар',
                  style: AppTextStyles.caption.copyWith(
                    color: AppColors.primary,
                    fontWeight: FontWeight.w700,
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
      margin: const EdgeInsets.symmetric(horizontal: 16),
      padding: const EdgeInsets.symmetric(vertical: 16),
      decoration: BoxDecoration(
        color: AppColors.cardBackground,
        borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
        border: Border.all(color: AppColors.border, width: 1),
      ),
      child: Row(
        children: [
          Expanded(child: _buildStatItem('127', 'Болжамдар')),
          Container(width: 1, height: 36, color: AppColors.border),
          Expanded(child: _buildStatItem('45', 'Өнімдер')),
          Container(width: 1, height: 36, color: AppColors.border),
          Expanded(child: _buildStatItem('91%', 'Дәлдік')),
        ],
      ),
    );
  }

  Widget _buildStatItem(String value, String label) {
    return Column(
      children: [
        Text(
          value,
          style: AppTextStyles.titleMedium.copyWith(
            color: AppColors.textPrimary,
            fontWeight: FontWeight.w700,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          label,
          style: AppTextStyles.caption.copyWith(
            color: AppColors.textSecondary,
          ),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  Widget _buildQuickActions() {
    final actions = [
      _QA('Профильді өңдеу', Icons.person_outline_rounded,
          AppColors.primary, _editProfile),
      _QA('Жоспарды жаңарту', Icons.rocket_launch_outlined,
          AppColors.warning, _upgradePlan),
      _QA('Көмек алу', Icons.help_outline_rounded, AppColors.info, _getHelp),
    ];

    return Padding(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          for (int i = 0; i < actions.length; i++) ...[
            Expanded(
              child: _buildActionCard(
                actions[i].label,
                actions[i].icon,
                actions[i].color,
                actions[i].onTap,
              ),
            ),
            if (i != actions.length - 1) const SizedBox(width: 10),
          ],
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
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 8),
          decoration: BoxDecoration(
            color: AppColors.cardBackground,
            borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
            border: Border.all(color: AppColors.border, width: 1),
          ),
          child: Column(
            children: [
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: color.withValues(alpha: 0.14),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(
                    color: color.withValues(alpha: 0.3),
                  ),
                ),
                child: Icon(icon, color: color, size: 20),
              ),
              const SizedBox(height: 8),
              Text(
                label,
                style: AppTextStyles.labelSmall.copyWith(
                  color: AppColors.textPrimary,
                  fontWeight: FontWeight.w600,
                  fontSize: 11,
                ),
                textAlign: TextAlign.center,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildMenuSection(String title, List<_MenuItemData> items) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.only(left: 4, bottom: 8),
            child: Text(
              title.toUpperCase(),
              style: AppTextStyles.overline.copyWith(
                color: AppColors.textSecondaryVariant,
              ),
            ),
          ),
          Container(
            decoration: BoxDecoration(
              color: AppColors.cardBackground,
              borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
              border: Border.all(color: AppColors.border, width: 1),
            ),
            child: Column(
              children: [
                for (int i = 0; i < items.length; i++) ...[
                  _buildMenuItem(items[i]),
                  if (i != items.length - 1)
                    const Divider(
                      height: 1,
                      color: AppColors.divider,
                      indent: 56,
                    ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMenuItem(_MenuItemData m) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: m.onTap,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
          child: Row(
            children: [
              Container(
                width: 30,
                height: 30,
                decoration: BoxDecoration(
                  color: AppColors.surfaceVariant,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: AppColors.border, width: 1),
                ),
                child: Icon(m.icon,
                    color: AppColors.textSecondary, size: 16),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  m.title,
                  style: AppTextStyles.bodyMedium.copyWith(
                    color: AppColors.textPrimary,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
              if (m.trailing != null) ...[
                Text(
                  m.trailing!,
                  style: AppTextStyles.bodySmall.copyWith(
                    color: AppColors.textSecondary,
                  ),
                ),
                const SizedBox(width: 6),
              ],
              const Icon(
                Icons.chevron_right_rounded,
                color: AppColors.textHint,
                size: 18,
              ),
            ],
          ),
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
      backgroundColor: AppColors.surface,
      builder: (context) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const SizedBox(height: 8),
            ListTile(
              leading: const Icon(Icons.camera_alt_outlined),
              title: const Text('Сурет түсіру'),
              onTap: () => Navigator.pop(context),
            ),
            ListTile(
              leading: const Icon(Icons.photo_library_outlined),
              title: const Text('Галереядан таңдау'),
              onTap: () => Navigator.pop(context),
            ),
            if (_user['avatar'] != null)
              ListTile(
                leading: const Icon(
                  Icons.delete_outline_rounded,
                  color: AppColors.error,
                ),
                title: const Text(
                  'Жою',
                  style: TextStyle(color: AppColors.error),
                ),
                onTap: () => Navigator.pop(context),
              ),
            const SizedBox(height: 8),
          ],
        ),
      ),
    );
  }

  void _editProfile() {}

  void _upgradePlan() {}

  void _getHelp() {}

  void _logout() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Шығу'),
        content: const Text('Аккаунттан шыққыңыз келе ме?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Болдырмау'),
          ),
          TextButton(
            onPressed: () async {
              Navigator.pop(context);
              final authService = context.read<AuthService>();
              await authService.logout();
              if (mounted) {
                Navigator.of(context).pushNamedAndRemoveUntil(
                  '/welcome',
                  (route) => false,
                );
              }
            },
            child: const Text(
              'Шығу',
              style: TextStyle(color: AppColors.error),
            ),
          ),
        ],
      ),
    );
  }
}

class _MenuItemData {
  final String title;
  final IconData icon;
  final VoidCallback onTap;
  final String? trailing;
  _MenuItemData(this.title, this.icon, this.onTap, {this.trailing});
}

class _QA {
  final String label;
  final IconData icon;
  final Color color;
  final VoidCallback onTap;
  _QA(this.label, this.icon, this.color, this.onTap);
}

class _IconBubble extends StatelessWidget {
  final IconData icon;
  final VoidCallback onTap;
  const _IconBubble({required this.icon, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(AppDimensions.radiusSm),
        child: Container(
          width: 38,
          height: 38,
          decoration: BoxDecoration(
            color: AppColors.surface,
            borderRadius: BorderRadius.circular(AppDimensions.radiusSm),
            border: Border.all(color: AppColors.border, width: 1),
          ),
          child: Icon(icon, size: 18, color: AppColors.textSecondary),
        ),
      ),
    );
  }
}
