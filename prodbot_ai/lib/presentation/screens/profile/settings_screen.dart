import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../core/theme/theme.dart';
import '../../../data/models/user_settings.dart';
import '../../../services/auth_service.dart';
import '../../../services/settings_provider.dart';

/// Mobile Settings screen — 1:1 port of the web user settings panel
/// (`frontend-admin/src/components/settings/SettingsPanel.jsx` +
///  `styles/settings.css`). Three sections: General · Notifications ·
/// Appearance, with a sticky tab bar that scroll-spies the active section.
class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  static const _sections = <_NavItem>[
    _NavItem(id: 'general', label: 'General'),
    _NavItem(id: 'notifications', label: 'Notifications'),
    _NavItem(id: 'appearance', label: 'Appearance'),
  ];

  final _scrollController = ScrollController();
  final Map<String, GlobalKey> _sectionKeys = {
    for (final s in _sections) s.id: GlobalKey(),
  };

  String _activeSection = 'general';

  @override
  void initState() {
    super.initState();
    _scrollController.addListener(_handleScroll);
  }

  @override
  void dispose() {
    _scrollController.removeListener(_handleScroll);
    _scrollController.dispose();
    super.dispose();
  }

  void _handleScroll() {
    final viewport = _scrollController.position;
    String current = _activeSection;
    for (final s in _sections) {
      final ctx = _sectionKeys[s.id]?.currentContext;
      if (ctx == null) continue;
      final box = ctx.findRenderObject() as RenderBox?;
      if (box == null) continue;
      final offset = box.localToGlobal(Offset.zero).dy;
      // Treat a section active as soon as its top crosses ~140px (header height).
      if (offset <= 140 + viewport.viewportDimension * 0.2) {
        current = s.id;
      }
    }
    if (current != _activeSection) {
      setState(() => _activeSection = current);
    }
  }

  void _scrollTo(String id) {
    setState(() => _activeSection = id);
    final ctx = _sectionKeys[id]?.currentContext;
    if (ctx == null) return;
    Scrollable.ensureVisible(
      ctx,
      duration: const Duration(milliseconds: 320),
      curve: Curves.easeOutCubic,
      alignment: 0,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: Column(
          children: [
            _buildHeader(),
            _buildTabBar(),
            const Divider(height: 1, color: AppColors.borderSubtle),
            Expanded(
              child: Consumer<SettingsProvider>(
                builder: (context, provider, _) {
                  if (provider.loading &&
                      provider.settings == UserSettings.defaults()) {
                    return const Center(
                      child: CircularProgressIndicator(
                        color: AppColors.primary,
                      ),
                    );
                  }
                  return SingleChildScrollView(
                    controller: _scrollController,
                    padding: const EdgeInsets.fromLTRB(20, 24, 20, 48),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        _GeneralSection(
                          key: _sectionKeys['general'],
                          provider: provider,
                        ),
                        const SizedBox(height: 32),
                        _NotificationsSection(
                          key: _sectionKeys['notifications'],
                          provider: provider,
                        ),
                        const SizedBox(height: 32),
                        _AppearanceSection(
                          key: _sectionKeys['appearance'],
                          provider: provider,
                        ),
                      ],
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(8, 8, 12, 8),
      child: Row(
        children: [
          IconButton(
            icon: const Icon(Icons.arrow_back_rounded, size: 22),
            color: AppColors.textSecondary,
            onPressed: () => Navigator.of(context).maybePop(),
          ),
          const SizedBox(width: 4),
          Text(
            'Settings',
            style: AppTextStyles.titleLarge.copyWith(
              fontWeight: FontWeight.w600,
            ),
          ),
          const Spacer(),
          Consumer<SettingsProvider>(
            builder: (context, p, _) {
              if (p.saving) {
                return const Padding(
                  padding: EdgeInsets.symmetric(horizontal: 12),
                  child: SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(
                      color: AppColors.primary,
                      strokeWidth: 2,
                    ),
                  ),
                );
              }
              return const SizedBox.shrink();
            },
          ),
        ],
      ),
    );
  }

  Widget _buildTabBar() {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Row(
        children: _sections.map((s) {
          final active = s.id == _activeSection;
          return Padding(
            padding: const EdgeInsets.only(right: 8),
            child: _ClaudeNavTab(
              label: s.label,
              active: active,
              onTap: () => _scrollTo(s.id),
            ),
          );
        }).toList(),
      ),
    );
  }
}

class _NavItem {
  final String id;
  final String label;
  const _NavItem({required this.id, required this.label});
}

class _ClaudeNavTab extends StatelessWidget {
  final String label;
  final bool active;
  final VoidCallback onTap;

  const _ClaudeNavTab({
    required this.label,
    required this.active,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(AppDimensions.radiusFull),
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 180),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 9),
          decoration: BoxDecoration(
            color: active ? AppColors.surfaceVariant : Colors.transparent,
            borderRadius: BorderRadius.circular(AppDimensions.radiusFull),
            border: Border.all(
              color: active ? AppColors.borderStrong : AppColors.borderSubtle,
            ),
          ),
          child: Text(
            label,
            style: AppTextStyles.labelMedium.copyWith(
              color: active ? AppColors.textPrimary : AppColors.textSecondary,
              fontWeight: FontWeight.w500,
            ),
          ),
        ),
      ),
    );
  }
}

// =====================================================================
// SECTION: General
// =====================================================================
class _GeneralSection extends StatefulWidget {
  final SettingsProvider provider;
  const _GeneralSection({super.key, required this.provider});

  @override
  State<_GeneralSection> createState() => _GeneralSectionState();
}

class _GeneralSectionState extends State<_GeneralSection> {
  late final TextEditingController _nameController;

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController(
      text: widget.provider.settings.profile.fullName,
    );
  }

  @override
  void didUpdateWidget(covariant _GeneralSection oldWidget) {
    super.didUpdateWidget(oldWidget);
    final remoteName = widget.provider.settings.profile.fullName;
    if (remoteName != _nameController.text && !_nameController.text.startsWith(remoteName) ) {
      _nameController.text = remoteName;
    }
  }

  @override
  void dispose() {
    _nameController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final settings = widget.provider.settings;
    final auth = context.watch<AuthService>();
    final email = auth.currentUserEmail ?? settings.profile.email;

    return _SettingsSection(
      groups: [
        _SettingsGroup(
          title: 'Profile',
          rows: [
            _SettingsRow(
              title: 'Full name',
              child: _ClaudeTextField(
                controller: _nameController,
                placeholder: 'Enter your name',
                onSubmitted: (v) =>
                    widget.provider.updateProfile(fullName: v.trim()),
                onEditingComplete: () => widget.provider
                    .updateProfile(fullName: _nameController.text.trim()),
              ),
            ),
            _SettingsRow(
              title: 'Email',
              child: _ClaudeTextField(
                value: email,
                disabled: true,
              ),
            ),
            _SettingsRow(
              title: 'Language',
              child: _ClaudeDropdown<String>(
                value: settings.profile.language,
                items: const [
                  _DropdownItem('kk', 'Қазақша'),
                  _DropdownItem('ru', 'Русский'),
                  _DropdownItem('en', 'English'),
                ],
                onChanged: (v) {
                  if (v != null) widget.provider.updateProfile(language: v);
                },
              ),
            ),
          ],
        ),
        _SettingsGroup(
          title: 'Forecast',
          rows: [
            _SettingsRow(
              title: 'Default horizon',
              description: 'Forecast period in days',
              child: _ClaudeDropdown<int>(
                value: settings.forecast.defaultHorizon,
                items: const [
                  _DropdownItem(7, '7 days'),
                  _DropdownItem(14, '14 days'),
                  _DropdownItem(30, '30 days'),
                ],
                onChanged: (v) {
                  if (v != null) {
                    widget.provider.updateForecast(defaultHorizon: v);
                  }
                },
              ),
            ),
            _SettingsRow(
              title: 'Show confidence',
              description: 'Display 95% confidence interval',
              child: _ClaudeSwitch(
                value: settings.forecast.showConfidence,
                onChanged: (v) =>
                    widget.provider.updateForecast(showConfidence: v),
              ),
            ),
            _SettingsRow(
              title: 'Show explanation',
              description: 'Show why the model made this prediction',
              child: _ClaudeSwitch(
                value: settings.forecast.showExplanation,
                onChanged: (v) =>
                    widget.provider.updateForecast(showExplanation: v),
              ),
            ),
          ],
        ),
        _SettingsGroup(
          title: 'Chat',
          rows: [
            _SettingsRow(
              title: 'Response style',
              description: 'How the AI assistant phrases answers',
              child: _ClaudeDropdown<String>(
                value: settings.chat.responseStyle,
                items: const [
                  _DropdownItem('short', 'Short'),
                  _DropdownItem('detailed', 'Detailed'),
                  _DropdownItem('analytical', 'Analytical'),
                ],
                onChanged: (v) {
                  if (v != null) widget.provider.updateChat(responseStyle: v);
                },
              ),
            ),
            _SettingsRow(
              title: 'Show suggestions',
              description: 'Display follow-up question chips',
              child: _ClaudeSwitch(
                value: settings.chat.showSuggestions,
                onChanged: (v) =>
                    widget.provider.updateChat(showSuggestions: v),
              ),
            ),
          ],
        ),
      ],
    );
  }
}

// =====================================================================
// SECTION: Notifications
// =====================================================================
class _NotificationsSection extends StatelessWidget {
  final SettingsProvider provider;
  const _NotificationsSection({super.key, required this.provider});

  @override
  Widget build(BuildContext context) {
    final n = provider.settings.notifications;
    return _SettingsSection(
      groups: [
        _SettingsGroup(
          title: 'Notifications',
          rows: [
            _SettingsRow(
              title: 'Demand increase',
              description: 'Notify when product demand grows',
              child: _ClaudeSwitch(
                value: n.demandIncrease,
                onChanged: (v) =>
                    provider.updateNotifications(demandIncrease: v),
              ),
            ),
            _SettingsRow(
              title: 'Demand decrease',
              description: 'Notify when product demand drops',
              child: _ClaudeSwitch(
                value: n.demandDecrease,
                onChanged: (v) =>
                    provider.updateNotifications(demandDecrease: v),
              ),
            ),
            _SettingsRow(
              title: 'Forecast change',
              description: 'Notify when a forecast is updated',
              child: _ClaudeSwitch(
                value: n.forecastChange,
                onChanged: (v) =>
                    provider.updateNotifications(forecastChange: v),
              ),
            ),
            _SettingsRow(
              title: 'Email notifications',
              description: 'Send the same alerts by email',
              child: _ClaudeSwitch(
                value: n.emailNotifications,
                onChanged: (v) =>
                    provider.updateNotifications(emailNotifications: v),
              ),
            ),
          ],
        ),
      ],
    );
  }
}

// =====================================================================
// SECTION: Appearance
// =====================================================================
class _AppearanceSection extends StatelessWidget {
  final SettingsProvider provider;
  const _AppearanceSection({super.key, required this.provider});

  @override
  Widget build(BuildContext context) {
    final ui = provider.settings.ui;
    return _SettingsSection(
      groups: [
        _SettingsGroup(
          title: 'Interface',
          rows: [
            _SettingsRow(
              title: 'Theme',
              description: 'Choose the interface color mode',
              fullWidth: true,
              child: _ThemeCardsRow(
                value: ui.theme,
                onChanged: (v) => provider.updateUi(theme: v),
              ),
            ),
            _SettingsRow(
              title: 'Animations',
              description: 'Enable smooth UI transitions',
              child: _ClaudeSwitch(
                value: ui.animations,
                onChanged: (v) => provider.updateUi(animations: v),
              ),
            ),
            _SettingsRow(
              title: 'Compact mode',
              description: 'Tighter spacing across screens',
              child: _ClaudeSwitch(
                value: ui.compactMode,
                onChanged: (v) => provider.updateUi(compactMode: v),
              ),
            ),
          ],
        ),
      ],
    );
  }
}

// =====================================================================
// PRIMITIVES — visually mirror `styles/settings.css` (claude variant)
// =====================================================================

class _SettingsSection extends StatelessWidget {
  final List<_SettingsGroup> groups;
  const _SettingsSection({required this.groups});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        for (var i = 0; i < groups.length; i++) ...[
          if (i > 0) const SizedBox(height: 24),
          groups[i],
        ],
      ],
    );
  }
}

class _SettingsGroup extends StatelessWidget {
  final String title;
  final List<_SettingsRow> rows;
  const _SettingsGroup({required this.title, required this.rows});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(left: 4, bottom: 10),
          child: Text(
            title,
            style: AppTextStyles.titleSmall.copyWith(
              fontWeight: FontWeight.w600,
              color: AppColors.textPrimary,
            ),
          ),
        ),
        Container(
          decoration: BoxDecoration(
            color: AppColors.surfaceVariant,
            borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
            border: Border.all(color: AppColors.borderSubtle),
          ),
          child: Column(
            children: [
              for (var i = 0; i < rows.length; i++) ...[
                rows[i],
                if (i != rows.length - 1)
                  const Divider(
                    height: 1,
                    thickness: 1,
                    color: AppColors.borderSubtle,
                    indent: 16,
                    endIndent: 16,
                  ),
              ],
            ],
          ),
        ),
      ],
    );
  }
}

class _SettingsRow extends StatelessWidget {
  final String title;
  final String? description;
  final Widget child;
  final bool fullWidth;

  const _SettingsRow({
    required this.title,
    required this.child,
    this.description,
    this.fullWidth = false,
  });

  @override
  Widget build(BuildContext context) {
    if (fullWidth) {
      return Padding(
        padding: const EdgeInsets.fromLTRB(16, 14, 16, 16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              title,
              style: AppTextStyles.bodyMedium.copyWith(
                color: AppColors.textPrimary,
                fontWeight: FontWeight.w500,
              ),
            ),
            if (description != null) ...[
              const SizedBox(height: 2),
              Text(
                description!,
                style: AppTextStyles.caption.copyWith(
                  color: AppColors.textSecondary,
                ),
              ),
            ],
            const SizedBox(height: 12),
            child,
          ],
        ),
      );
    }
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 14, 12, 14),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: AppTextStyles.bodyMedium.copyWith(
                    color: AppColors.textPrimary,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                if (description != null) ...[
                  const SizedBox(height: 2),
                  Text(
                    description!,
                    style: AppTextStyles.caption.copyWith(
                      color: AppColors.textSecondary,
                      height: 1.35,
                    ),
                  ),
                ],
              ],
            ),
          ),
          const SizedBox(width: 12),
          child,
        ],
      ),
    );
  }
}

// ------- Claude-style switch (matches `.toggle-claude`) -------
class _ClaudeSwitch extends StatelessWidget {
  final bool value;
  final ValueChanged<bool> onChanged;
  const _ClaudeSwitch({required this.value, required this.onChanged});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => onChanged(!value),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        width: 42,
        height: 24,
        padding: const EdgeInsets.all(2),
        decoration: BoxDecoration(
          color: value ? AppColors.primary : AppColors.cardBackground,
          borderRadius: BorderRadius.circular(AppDimensions.radiusFull),
          border: Border.all(
            color: value ? AppColors.primary : AppColors.borderStrong,
          ),
        ),
        child: AnimatedAlign(
          duration: const Duration(milliseconds: 180),
          alignment: value ? Alignment.centerRight : Alignment.centerLeft,
          child: Container(
            width: 18,
            height: 18,
            decoration: const BoxDecoration(
              color: Colors.white,
              shape: BoxShape.circle,
            ),
          ),
        ),
      ),
    );
  }
}

// ------- Claude-style dropdown (matches `.settings-select-claude`) -------
class _DropdownItem<T> {
  final T value;
  final String label;
  const _DropdownItem(this.value, this.label);
}

class _ClaudeDropdown<T> extends StatelessWidget {
  final T value;
  final List<_DropdownItem<T>> items;
  final ValueChanged<T?> onChanged;

  const _ClaudeDropdown({
    required this.value,
    required this.items,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12),
      decoration: BoxDecoration(
        color: AppColors.cardBackground,
        borderRadius: BorderRadius.circular(AppDimensions.radiusSm),
        border: Border.all(color: AppColors.border),
      ),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<T>(
          value: value,
          isDense: true,
          icon: const Icon(
            Icons.expand_more_rounded,
            size: 18,
            color: AppColors.textSecondary,
          ),
          dropdownColor: AppColors.cardBackground,
          borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
          style: AppTextStyles.bodySmall.copyWith(
            color: AppColors.textPrimary,
          ),
          onChanged: onChanged,
          items: items
              .map(
                (i) => DropdownMenuItem<T>(
                  value: i.value,
                  child: Text(
                    i.label,
                    style: AppTextStyles.bodySmall.copyWith(
                      color: AppColors.textPrimary,
                    ),
                  ),
                ),
              )
              .toList(),
        ),
      ),
    );
  }
}

// ------- Claude-style text field (matches `.settings-input-claude`) -------
class _ClaudeTextField extends StatelessWidget {
  final TextEditingController? controller;
  final String? value;
  final String? placeholder;
  final bool disabled;
  final ValueChanged<String>? onSubmitted;
  final VoidCallback? onEditingComplete;

  const _ClaudeTextField({
    this.controller,
    this.value,
    this.placeholder,
    this.disabled = false,
    this.onSubmitted,
    this.onEditingComplete,
  });

  @override
  Widget build(BuildContext context) {
    final effectiveController = controller ??
        (value != null ? TextEditingController(text: value) : null);
    return ConstrainedBox(
      constraints: const BoxConstraints(minWidth: 140, maxWidth: 220),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: disabled ? AppColors.surface : AppColors.cardBackground,
          borderRadius: BorderRadius.circular(AppDimensions.radiusSm),
          border: Border.all(color: AppColors.border),
        ),
        child: TextField(
          controller: effectiveController,
          enabled: !disabled,
          style: AppTextStyles.bodySmall.copyWith(
            color: disabled ? AppColors.textSecondary : AppColors.textPrimary,
          ),
          textAlign: TextAlign.right,
          onSubmitted: onSubmitted,
          onEditingComplete: onEditingComplete,
          decoration: InputDecoration(
            hintText: placeholder,
            hintStyle: AppTextStyles.bodySmall.copyWith(
              color: AppColors.textHint,
            ),
            isDense: true,
            border: InputBorder.none,
            enabledBorder: InputBorder.none,
            disabledBorder: InputBorder.none,
            focusedBorder: InputBorder.none,
            contentPadding: EdgeInsets.zero,
          ),
        ),
      ),
    );
  }
}

// ------- Theme cards (matches `.color-mode-cards` on web) -------
class _ThemeCardsRow extends StatelessWidget {
  final String value;
  final ValueChanged<String> onChanged;

  const _ThemeCardsRow({required this.value, required this.onChanged});

  static const _options = [
    _ThemeOption('light', 'Light'),
    _ThemeOption('auto', 'Auto'),
    _ThemeOption('dark', 'Dark'),
  ];

  @override
  Widget build(BuildContext context) {
    return Row(
      children: _options
          .map(
            (o) => Expanded(
              child: Padding(
                padding: EdgeInsets.only(
                  right: o == _options.last ? 0 : 8,
                ),
                child: _ThemeCard(
                  option: o,
                  selected: o.id == value,
                  onTap: () => onChanged(o.id),
                ),
              ),
            ),
          )
          .toList(),
    );
  }
}

class _ThemeOption {
  final String id;
  final String label;
  const _ThemeOption(this.id, this.label);
}

class _ThemeCard extends StatelessWidget {
  final _ThemeOption option;
  final bool selected;
  final VoidCallback onTap;

  const _ThemeCard({
    required this.option,
    required this.selected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final preview = _previewFor(option.id);
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
        child: Container(
          padding: const EdgeInsets.fromLTRB(8, 8, 8, 10),
          decoration: BoxDecoration(
            color: selected
                ? AppColors.primary10
                : AppColors.cardBackground,
            borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
            border: Border.all(
              color: selected ? AppColors.primary : AppColors.border,
              width: selected ? 1.4 : 1,
            ),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              AspectRatio(
                aspectRatio: 16 / 9,
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(AppDimensions.radiusSm),
                  child: preview,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                option.label,
                textAlign: TextAlign.center,
                style: AppTextStyles.labelSmall.copyWith(
                  color: selected
                      ? AppColors.textPrimary
                      : AppColors.textSecondary,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _previewFor(String id) {
    switch (id) {
      case 'light':
        return _PreviewSurface(
          background: const Color(0xFFF7F7F8),
          sidebar: const Color(0xFFE6E6EA),
          line1: const Color(0xFFC5C5CA),
          line2: const Color(0xFFD8D8DC),
        );
      case 'auto':
        return Row(children: [
          Expanded(
            child: _PreviewSurface(
              background: const Color(0xFFF7F7F8),
              sidebar: const Color(0xFFE6E6EA),
              line1: const Color(0xFFC5C5CA),
              line2: const Color(0xFFD8D8DC),
            ),
          ),
          Expanded(
            child: _PreviewSurface(
              background: AppColors.background,
              sidebar: AppColors.surface,
              line1: AppColors.borderStrong,
              line2: AppColors.border,
            ),
          ),
        ]);
      default:
        return _PreviewSurface(
          background: AppColors.background,
          sidebar: AppColors.surface,
          line1: AppColors.borderStrong,
          line2: AppColors.border,
        );
    }
  }
}

class _PreviewSurface extends StatelessWidget {
  final Color background;
  final Color sidebar;
  final Color line1;
  final Color line2;

  const _PreviewSurface({
    required this.background,
    required this.sidebar,
    required this.line1,
    required this.line2,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      color: background,
      child: Row(
        children: [
          Container(width: 18, color: sidebar),
          const SizedBox(width: 6),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 4),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(height: 4, color: line1),
                  const SizedBox(height: 6),
                  Container(height: 4, width: 30, color: line2),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
