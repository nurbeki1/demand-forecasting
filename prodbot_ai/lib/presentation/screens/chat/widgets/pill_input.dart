import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../../../../core/theme/theme.dart';
import 'model_selector.dart';

/// Pill-shaped chat input that mirrors the web `.chat-input-box`
/// and `.empty-input-box` styles in `frontend-admin/src/styles/chat.css`.
class PillInput extends StatelessWidget {
  final TextEditingController controller;
  final String hintText;
  final bool loading;
  final bool isLarge;
  final String selectedModel;
  final ValueChanged<String> onModelChanged;
  final VoidCallback onSend;
  final FocusNode? focusNode;

  const PillInput({
    super.key,
    required this.controller,
    required this.hintText,
    required this.selectedModel,
    required this.onModelChanged,
    required this.onSend,
    this.loading = false,
    this.isLarge = false,
    this.focusNode,
  });

  @override
  Widget build(BuildContext context) {
    final radius = BorderRadius.circular(isLarge ? 28 : 22);
    return Container(
      decoration: BoxDecoration(
        color: AppColors.inputBackground,
        borderRadius: radius,
        border: Border.all(color: AppColors.border),
        boxShadow: [
          BoxShadow(
            color: AppColors.black.withValues(alpha: 0.30),
            blurRadius: 24,
            offset: const Offset(0, 12),
          ),
        ],
      ),
      padding: EdgeInsets.symmetric(
        horizontal: isLarge ? 18 : 14,
        vertical: isLarge ? 8 : 6,
      ),
      constraints: BoxConstraints(minHeight: isLarge ? 56 : 48),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Expanded(
            child: TextField(
              controller: controller,
              focusNode: focusNode,
              enabled: !loading,
              maxLines: 4,
              minLines: 1,
              textInputAction: TextInputAction.send,
              textAlignVertical: TextAlignVertical.center,
              onSubmitted: (_) => onSend(),
              style: AppTextStyles.bodyMedium.copyWith(
                color: AppColors.textPrimary,
                fontSize: isLarge ? 15 : 14,
              ),
              decoration: InputDecoration(
                isCollapsed: true,
                contentPadding: EdgeInsets.symmetric(
                  vertical: isLarge ? 12 : 10,
                  horizontal: 6,
                ),
                hintText: hintText,
                hintStyle: AppTextStyles.bodyMedium.copyWith(
                  color: AppColors.textTertiary,
                  fontSize: isLarge ? 15 : 14,
                ),
                border: InputBorder.none,
              ),
              inputFormatters: [
                FilteringTextInputFormatter.deny(RegExp(r'^\s+$')),
              ],
            ),
          ),
          ModelSelector(value: selectedModel, onChanged: onModelChanged),
          const SizedBox(width: 6),
          _SendButton(loading: loading, onTap: onSend),
        ],
      ),
    );
  }
}

class _SendButton extends StatelessWidget {
  final bool loading;
  final VoidCallback onTap;
  const _SendButton({required this.loading, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: loading ? null : onTap,
      borderRadius: BorderRadius.circular(999),
      child: Container(
        width: 36,
        height: 36,
        decoration: BoxDecoration(
          gradient: AppColors.primaryGradient,
          shape: BoxShape.circle,
          boxShadow: [
            BoxShadow(
              color: AppColors.primary.withValues(alpha: 0.40),
              blurRadius: 14,
              offset: const Offset(0, 6),
            ),
          ],
        ),
        child: loading
            ? const Padding(
                padding: EdgeInsets.all(10),
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  valueColor: AlwaysStoppedAnimation(AppColors.white),
                ),
              )
            : const Icon(
                Icons.arrow_upward_rounded,
                color: AppColors.white,
                size: 20,
              ),
      ),
    );
  }
}
