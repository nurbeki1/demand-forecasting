import 'package:flutter/material.dart';
import '../../../core/theme/theme.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  // Settings state
  bool _darkMode = false;
  bool _notifications = true;
  bool _emailAlerts = true;
  bool _pushNotifications = true;
  bool _lowStockAlerts = true;
  bool _forecastAlerts = true;
  bool _biometricAuth = false;
  String _language = 'English';
  String _currency = 'USD';
  String _dateFormat = 'MM/DD/YYYY';

  final List<String> _languages = ['English', 'Spanish', 'French', 'German', 'Chinese'];
  final List<String> _currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CNY'];
  final List<String> _dateFormats = ['MM/DD/YYYY', 'DD/MM/YYYY', 'YYYY-MM-DD'];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Settings'),
      ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Appearance section
            _buildSectionHeader('Appearance'),
            _buildSwitchTile(
              'Dark Mode',
              'Use dark theme for the app',
              Icons.dark_mode_outlined,
              _darkMode,
              (value) => setState(() => _darkMode = value),
            ),
            _buildDropdownTile(
              'Language',
              _language,
              Icons.language,
              _languages,
              (value) => setState(() => _language = value!),
            ),
            _buildDropdownTile(
              'Currency',
              _currency,
              Icons.attach_money,
              _currencies,
              (value) => setState(() => _currency = value!),
            ),
            _buildDropdownTile(
              'Date Format',
              _dateFormat,
              Icons.calendar_today_outlined,
              _dateFormats,
              (value) => setState(() => _dateFormat = value!),
            ),

            const SizedBox(height: AppDimensions.spacing16),

            // Notifications section
            _buildSectionHeader('Notifications'),
            _buildSwitchTile(
              'Enable Notifications',
              'Receive app notifications',
              Icons.notifications_outlined,
              _notifications,
              (value) => setState(() => _notifications = value),
            ),
            if (_notifications) ...[
              _buildSwitchTile(
                'Email Alerts',
                'Receive notifications via email',
                Icons.email_outlined,
                _emailAlerts,
                (value) => setState(() => _emailAlerts = value),
              ),
              _buildSwitchTile(
                'Push Notifications',
                'Receive push notifications',
                Icons.phone_android_outlined,
                _pushNotifications,
                (value) => setState(() => _pushNotifications = value),
              ),
              _buildSwitchTile(
                'Low Stock Alerts',
                'Get notified when stock is low',
                Icons.warning_amber_outlined,
                _lowStockAlerts,
                (value) => setState(() => _lowStockAlerts = value),
              ),
              _buildSwitchTile(
                'Forecast Alerts',
                'Get notified about forecast updates',
                Icons.analytics_outlined,
                _forecastAlerts,
                (value) => setState(() => _forecastAlerts = value),
              ),
            ],

            const SizedBox(height: AppDimensions.spacing16),

            // Security section
            _buildSectionHeader('Security'),
            _buildSwitchTile(
              'Biometric Authentication',
              'Use fingerprint or face ID',
              Icons.fingerprint,
              _biometricAuth,
              (value) => setState(() => _biometricAuth = value),
            ),
            _buildActionTile(
              'Change Password',
              'Update your account password',
              Icons.lock_outline,
              _changePassword,
            ),
            _buildActionTile(
              'Two-Factor Authentication',
              'Add an extra layer of security',
              Icons.security_outlined,
              _setupTwoFactor,
            ),
            _buildActionTile(
              'Active Sessions',
              'Manage your logged-in devices',
              Icons.devices_outlined,
              _viewSessions,
            ),

            const SizedBox(height: AppDimensions.spacing16),

            // Data section
            _buildSectionHeader('Data & Storage'),
            _buildActionTile(
              'Export Data',
              'Download your data as CSV or JSON',
              Icons.download_outlined,
              _exportData,
            ),
            _buildActionTile(
              'Clear Cache',
              'Free up storage space',
              Icons.cleaning_services_outlined,
              _clearCache,
            ),
            _buildActionTile(
              'Sync Settings',
              'Configure data synchronization',
              Icons.sync_outlined,
              _syncSettings,
            ),

            const SizedBox(height: AppDimensions.spacing16),

            // Danger zone
            _buildSectionHeader('Danger Zone'),
            _buildDangerTile(
              'Delete All Data',
              'Permanently delete all forecasts and products',
              Icons.delete_forever_outlined,
              _deleteAllData,
            ),
            _buildDangerTile(
              'Delete Account',
              'Permanently delete your account',
              Icons.person_off_outlined,
              _deleteAccount,
            ),

            const SizedBox(height: AppDimensions.spacing32),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(
        AppDimensions.spacing16,
        AppDimensions.spacing16,
        AppDimensions.spacing16,
        AppDimensions.spacing8,
      ),
      child: Text(
        title,
        style: AppTextStyles.labelLarge.copyWith(
          color: AppColors.primary,
        ),
      ),
    );
  }

  Widget _buildSwitchTile(
    String title,
    String subtitle,
    IconData icon,
    bool value,
    ValueChanged<bool> onChanged,
  ) {
    return Container(
      margin: const EdgeInsets.symmetric(
        horizontal: AppDimensions.spacing16,
        vertical: AppDimensions.spacing4,
      ),
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
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: AppTextStyles.labelMedium),
                const SizedBox(height: 2),
                Text(subtitle, style: AppTextStyles.caption),
              ],
            ),
          ),
          Switch(
            value: value,
            onChanged: onChanged,
            activeColor: AppColors.primary,
          ),
        ],
      ),
    );
  }

  Widget _buildDropdownTile(
    String title,
    String value,
    IconData icon,
    List<String> options,
    ValueChanged<String?> onChanged,
  ) {
    return Container(
      margin: const EdgeInsets.symmetric(
        horizontal: AppDimensions.spacing16,
        vertical: AppDimensions.spacing4,
      ),
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
          DropdownButton<String>(
            value: value,
            underline: const SizedBox(),
            items: options.map((option) {
              return DropdownMenuItem(
                value: option,
                child: Text(option, style: AppTextStyles.bodyMedium),
              );
            }).toList(),
            onChanged: onChanged,
          ),
        ],
      ),
    );
  }

  Widget _buildActionTile(
    String title,
    String subtitle,
    IconData icon,
    VoidCallback onTap,
  ) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.symmetric(
          horizontal: AppDimensions.spacing16,
          vertical: AppDimensions.spacing4,
        ),
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
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: AppTextStyles.labelMedium),
                  const SizedBox(height: 2),
                  Text(subtitle, style: AppTextStyles.caption),
                ],
              ),
            ),
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

  Widget _buildDangerTile(
    String title,
    String subtitle,
    IconData icon,
    VoidCallback onTap,
  ) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.symmetric(
          horizontal: AppDimensions.spacing16,
          vertical: AppDimensions.spacing4,
        ),
        padding: const EdgeInsets.all(AppDimensions.spacing12),
        decoration: BoxDecoration(
          color: AppColors.error.withValues(alpha: 0.05),
          borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
          border: Border.all(color: AppColors.error.withValues(alpha: 0.3)),
        ),
        child: Row(
          children: [
            Icon(icon, color: AppColors.error, size: 22),
            const SizedBox(width: AppDimensions.spacing12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: AppTextStyles.labelMedium.copyWith(
                      color: AppColors.error,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(subtitle, style: AppTextStyles.caption),
                ],
              ),
            ),
            const Icon(
              Icons.chevron_right,
              color: AppColors.error,
              size: 20,
            ),
          ],
        ),
      ),
    );
  }

  void _changePassword() {
    _showActionDialog(
      'Change Password',
      'Enter your current password and a new password.',
    );
  }

  void _setupTwoFactor() {
    _showActionDialog(
      'Two-Factor Authentication',
      'Scan the QR code with your authenticator app.',
    );
  }

  void _viewSessions() {
    _showActionDialog(
      'Active Sessions',
      'You are currently logged in on 2 devices.',
    );
  }

  void _exportData() {
    _showActionDialog(
      'Export Data',
      'Your data export will be ready shortly.',
    );
  }

  void _clearCache() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Clear Cache'),
        content: const Text('This will clear all cached data. Continue?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Cache cleared successfully'),
                  backgroundColor: AppColors.success,
                ),
              );
            },
            child: const Text('Clear'),
          ),
        ],
      ),
    );
  }

  void _syncSettings() {
    _showActionDialog(
      'Sync Settings',
      'Configure how often your data syncs.',
    );
  }

  void _deleteAllData() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(
          'Delete All Data',
          style: TextStyle(color: AppColors.error),
        ),
        content: const Text(
          'This will permanently delete all your forecasts, products, and settings. This action cannot be undone.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              // Perform delete
            },
            child: Text(
              'Delete',
              style: TextStyle(color: AppColors.error),
            ),
          ),
        ],
      ),
    );
  }

  void _deleteAccount() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(
          'Delete Account',
          style: TextStyle(color: AppColors.error),
        ),
        content: const Text(
          'This will permanently delete your account and all associated data. This action cannot be undone.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              // Perform account deletion
            },
            child: Text(
              'Delete Account',
              style: TextStyle(color: AppColors.error),
            ),
          ),
        ],
      ),
    );
  }

  void _showActionDialog(String title, String message) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(title),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('OK'),
          ),
        ],
      ),
    );
  }
}
