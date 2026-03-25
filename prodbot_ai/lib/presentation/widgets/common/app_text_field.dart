import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../../core/theme/theme.dart';

/// Custom text field widget based on Figma design
/// Supports various states: normal, error, success, disabled
class AppTextField extends StatefulWidget {
  final String? label;
  final String? hintText;
  final String? helperText;
  final String? errorText;
  final TextEditingController? controller;
  final FocusNode? focusNode;
  final bool obscureText;
  final bool enabled;
  final bool readOnly;
  final bool autofocus;
  final int? maxLines;
  final int? minLines;
  final int? maxLength;
  final TextInputType? keyboardType;
  final TextInputAction? textInputAction;
  final TextCapitalization textCapitalization;
  final List<TextInputFormatter>? inputFormatters;
  final ValueChanged<String>? onChanged;
  final VoidCallback? onTap;
  final VoidCallback? onEditingComplete;
  final ValueChanged<String>? onFieldSubmitted;
  final FormFieldValidator<String>? validator;
  final Widget? prefixIcon;
  final Widget? suffixIcon;
  final bool showPasswordToggle;
  final bool showClearButton;
  final bool isSuccess;
  final EdgeInsets? contentPadding;

  const AppTextField({
    super.key,
    this.label,
    this.hintText,
    this.helperText,
    this.errorText,
    this.controller,
    this.focusNode,
    this.obscureText = false,
    this.enabled = true,
    this.readOnly = false,
    this.autofocus = false,
    this.maxLines = 1,
    this.minLines,
    this.maxLength,
    this.keyboardType,
    this.textInputAction,
    this.textCapitalization = TextCapitalization.none,
    this.inputFormatters,
    this.onChanged,
    this.onTap,
    this.onEditingComplete,
    this.onFieldSubmitted,
    this.validator,
    this.prefixIcon,
    this.suffixIcon,
    this.showPasswordToggle = false,
    this.showClearButton = false,
    this.isSuccess = false,
    this.contentPadding,
  });

  // Email field preset
  factory AppTextField.email({
    Key? key,
    String? label,
    String? hintText,
    String? errorText,
    TextEditingController? controller,
    FocusNode? focusNode,
    bool enabled = true,
    ValueChanged<String>? onChanged,
    ValueChanged<String>? onFieldSubmitted,
    FormFieldValidator<String>? validator,
  }) {
    return AppTextField(
      key: key,
      label: label ?? 'Email',
      hintText: hintText ?? 'Enter your email',
      errorText: errorText,
      controller: controller,
      focusNode: focusNode,
      enabled: enabled,
      keyboardType: TextInputType.emailAddress,
      textInputAction: TextInputAction.next,
      onChanged: onChanged,
      onFieldSubmitted: onFieldSubmitted,
      validator: validator,
      prefixIcon: const Icon(Icons.email_outlined),
    );
  }

  // Password field preset
  factory AppTextField.password({
    Key? key,
    String? label,
    String? hintText,
    String? errorText,
    TextEditingController? controller,
    FocusNode? focusNode,
    bool enabled = true,
    ValueChanged<String>? onChanged,
    ValueChanged<String>? onFieldSubmitted,
    FormFieldValidator<String>? validator,
    TextInputAction? textInputAction,
  }) {
    return AppTextField(
      key: key,
      label: label ?? 'Password',
      hintText: hintText ?? 'Enter your password',
      errorText: errorText,
      controller: controller,
      focusNode: focusNode,
      enabled: enabled,
      obscureText: true,
      showPasswordToggle: true,
      keyboardType: TextInputType.visiblePassword,
      textInputAction: textInputAction ?? TextInputAction.done,
      onChanged: onChanged,
      onFieldSubmitted: onFieldSubmitted,
      validator: validator,
      prefixIcon: const Icon(Icons.lock_outline),
    );
  }

  // Search field preset
  factory AppTextField.search({
    Key? key,
    String? hintText,
    TextEditingController? controller,
    FocusNode? focusNode,
    bool enabled = true,
    ValueChanged<String>? onChanged,
    ValueChanged<String>? onFieldSubmitted,
    VoidCallback? onClear,
  }) {
    return AppTextField(
      key: key,
      hintText: hintText ?? 'Search...',
      controller: controller,
      focusNode: focusNode,
      enabled: enabled,
      keyboardType: TextInputType.text,
      textInputAction: TextInputAction.search,
      onChanged: onChanged,
      onFieldSubmitted: onFieldSubmitted,
      showClearButton: true,
      prefixIcon: const Icon(Icons.search),
    );
  }

  // Multiline text field preset
  factory AppTextField.multiline({
    Key? key,
    String? label,
    String? hintText,
    String? errorText,
    TextEditingController? controller,
    FocusNode? focusNode,
    bool enabled = true,
    int maxLines = 5,
    int? minLines,
    int? maxLength,
    ValueChanged<String>? onChanged,
    FormFieldValidator<String>? validator,
  }) {
    return AppTextField(
      key: key,
      label: label,
      hintText: hintText,
      errorText: errorText,
      controller: controller,
      focusNode: focusNode,
      enabled: enabled,
      maxLines: maxLines,
      minLines: minLines ?? 3,
      maxLength: maxLength,
      keyboardType: TextInputType.multiline,
      textInputAction: TextInputAction.newline,
      onChanged: onChanged,
      validator: validator,
    );
  }

  @override
  State<AppTextField> createState() => _AppTextFieldState();
}

class _AppTextFieldState extends State<AppTextField> {
  late bool _obscured;
  late TextEditingController _controller;
  late FocusNode _focusNode;
  bool _isFocused = false;

  @override
  void initState() {
    super.initState();
    _obscured = widget.obscureText;
    _controller = widget.controller ?? TextEditingController();
    _focusNode = widget.focusNode ?? FocusNode();
    _focusNode.addListener(_onFocusChange);
  }

  @override
  void dispose() {
    _focusNode.removeListener(_onFocusChange);
    if (widget.controller == null) {
      _controller.dispose();
    }
    if (widget.focusNode == null) {
      _focusNode.dispose();
    }
    super.dispose();
  }

  void _onFocusChange() {
    setState(() {
      _isFocused = _focusNode.hasFocus;
    });
  }

  Color get _borderColor {
    if (widget.errorText != null) return AppColors.error;
    if (widget.isSuccess) return AppColors.success;
    if (_isFocused) return AppColors.primary;
    return AppColors.border;
  }

  Color get _labelColor {
    if (widget.errorText != null) return AppColors.error;
    if (_isFocused) return AppColors.primary;
    return AppColors.textSecondary;
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        if (widget.label != null) ...[
          Text(
            widget.label!,
            style: AppTextStyles.labelMedium.copyWith(
              color: _labelColor,
            ),
          ),
          const SizedBox(height: AppDimensions.spacing8),
        ],
        TextFormField(
          controller: _controller,
          focusNode: _focusNode,
          obscureText: _obscured,
          enabled: widget.enabled,
          readOnly: widget.readOnly,
          autofocus: widget.autofocus,
          maxLines: widget.obscureText ? 1 : widget.maxLines,
          minLines: widget.minLines,
          maxLength: widget.maxLength,
          keyboardType: widget.keyboardType,
          textInputAction: widget.textInputAction,
          textCapitalization: widget.textCapitalization,
          inputFormatters: widget.inputFormatters,
          style: AppTextStyles.bodyLarge.copyWith(
            color: widget.enabled ? AppColors.textPrimary : AppColors.textDisabled,
          ),
          onChanged: widget.onChanged,
          onTap: widget.onTap,
          onEditingComplete: widget.onEditingComplete,
          onFieldSubmitted: widget.onFieldSubmitted,
          validator: widget.validator,
          decoration: InputDecoration(
            hintText: widget.hintText,
            hintStyle: AppTextStyles.bodyLarge.copyWith(
              color: AppColors.textHint,
            ),
            errorText: null, // We handle error text manually below
            contentPadding: widget.contentPadding ??
                const EdgeInsets.symmetric(
                  horizontal: AppDimensions.spacing16,
                  vertical: AppDimensions.spacing14,
                ),
            filled: true,
            fillColor: widget.enabled ? AppColors.surface : AppColors.surfaceVariant,
            prefixIcon: widget.prefixIcon != null
                ? IconTheme(
                    data: IconThemeData(
                      color: widget.errorText != null
                          ? AppColors.error
                          : _isFocused
                              ? AppColors.primary
                              : AppColors.iconVariant,
                      size: AppDimensions.iconMd,
                    ),
                    child: widget.prefixIcon!,
                  )
                : null,
            suffixIcon: _buildSuffixIcon(),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
              borderSide: BorderSide(
                color: _borderColor,
                width: AppDimensions.borderWidthThin,
              ),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
              borderSide: BorderSide(
                color: _borderColor,
                width: AppDimensions.borderWidthThin,
              ),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
              borderSide: BorderSide(
                color: _borderColor,
                width: AppDimensions.borderWidthThick,
              ),
            ),
            errorBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
              borderSide: const BorderSide(
                color: AppColors.error,
                width: AppDimensions.borderWidthThin,
              ),
            ),
            focusedErrorBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
              borderSide: const BorderSide(
                color: AppColors.error,
                width: AppDimensions.borderWidthThick,
              ),
            ),
            disabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
              borderSide: const BorderSide(
                color: AppColors.borderVariant,
                width: AppDimensions.borderWidthThin,
              ),
            ),
          ),
        ),
        if (widget.errorText != null || widget.helperText != null) ...[
          const SizedBox(height: AppDimensions.spacing6),
          Row(
            children: [
              if (widget.errorText != null) ...[
                const Icon(
                  Icons.error_outline,
                  size: AppDimensions.iconSm,
                  color: AppColors.error,
                ),
                const SizedBox(width: AppDimensions.spacing4),
                Expanded(
                  child: Text(
                    widget.errorText!,
                    style: AppTextStyles.caption.copyWith(
                      color: AppColors.error,
                    ),
                  ),
                ),
              ] else if (widget.helperText != null) ...[
                Expanded(
                  child: Text(
                    widget.helperText!,
                    style: AppTextStyles.caption.copyWith(
                      color: AppColors.textSecondary,
                    ),
                  ),
                ),
              ],
            ],
          ),
        ],
      ],
    );
  }

  Widget? _buildSuffixIcon() {
    final List<Widget> icons = [];

    // Password toggle
    if (widget.showPasswordToggle && widget.obscureText) {
      icons.add(
        GestureDetector(
          onTap: () {
            setState(() {
              _obscured = !_obscured;
            });
          },
          child: Icon(
            _obscured ? Icons.visibility_off_outlined : Icons.visibility_outlined,
            color: AppColors.iconVariant,
            size: AppDimensions.iconMd,
          ),
        ),
      );
    }

    // Clear button
    if (widget.showClearButton && _controller.text.isNotEmpty) {
      icons.add(
        GestureDetector(
          onTap: () {
            _controller.clear();
            widget.onChanged?.call('');
          },
          child: const Icon(
            Icons.close,
            color: AppColors.iconVariant,
            size: AppDimensions.iconMd,
          ),
        ),
      );
    }

    // Success icon
    if (widget.isSuccess) {
      icons.add(
        const Icon(
          Icons.check_circle_outline,
          color: AppColors.success,
          size: AppDimensions.iconMd,
        ),
      );
    }

    // Custom suffix icon
    if (widget.suffixIcon != null) {
      icons.add(
        IconTheme(
          data: IconThemeData(
            color: widget.errorText != null
                ? AppColors.error
                : AppColors.iconVariant,
            size: AppDimensions.iconMd,
          ),
          child: widget.suffixIcon!,
        ),
      );
    }

    if (icons.isEmpty) return null;

    if (icons.length == 1) {
      return Padding(
        padding: const EdgeInsets.only(right: AppDimensions.spacing12),
        child: icons.first,
      );
    }

    return Padding(
      padding: const EdgeInsets.only(right: AppDimensions.spacing12),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: icons
            .map((icon) => Padding(
                  padding: const EdgeInsets.only(left: AppDimensions.spacing8),
                  child: icon,
                ))
            .toList(),
      ),
    );
  }
}
