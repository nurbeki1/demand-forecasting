import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';

import '../../../../core/theme/theme.dart';
import '../../../../data/models/chat_models.dart';
import '../../../../l10n/app_localizations.dart';

/// In-message product carousel with arrow controls and rating row.
/// Mirrors `ProductCarousel` / `ProductCard` from `ChatPage.jsx`.
class ProductCarousel extends StatefulWidget {
  final List<ProductImage> images;
  const ProductCarousel({super.key, required this.images});

  @override
  State<ProductCarousel> createState() => _ProductCarouselState();
}

class _ProductCarouselState extends State<ProductCarousel> {
  int _index = 0;

  void _go(int delta) {
    final n = widget.images.length;
    setState(() => _index = (_index + delta + n) % n);
  }

  @override
  Widget build(BuildContext context) {
    if (widget.images.isEmpty) return const SizedBox.shrink();
    final l10n = AppLocalizations.of(context)!;
    final p = widget.images[_index];
    return Container(
      margin: const EdgeInsets.only(top: 12),
      decoration: BoxDecoration(
        color: AppColors.surfaceVariant,
        borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
        border: Border.all(color: AppColors.borderSubtle),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(14, 12, 8, 8),
            child: Row(
              children: [
                Text(
                  l10n.productsCarouselTitle(widget.images.length),
                  style: AppTextStyles.labelMedium.copyWith(
                    color: AppColors.textSecondary,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const Spacer(),
                _CarouselButton(
                  icon: Icons.chevron_left_rounded,
                  onTap: () => _go(-1),
                ),
                const SizedBox(width: 6),
                Text(
                  '${_index + 1} / ${widget.images.length}',
                  style: AppTextStyles.labelSmall.copyWith(
                    color: AppColors.textSecondary,
                  ),
                ),
                const SizedBox(width: 6),
                _CarouselButton(
                  icon: Icons.chevron_right_rounded,
                  onTap: () => _go(1),
                ),
              ],
            ),
          ),
          ClipRRect(
            borderRadius:
                const BorderRadius.vertical(bottom: Radius.circular(12)),
            child: AspectRatio(
              aspectRatio: 16 / 9,
              child: p.imageUrl.isEmpty
                  ? _placeholder()
                  : CachedNetworkImage(
                      imageUrl: p.imageUrl,
                      fit: BoxFit.cover,
                      placeholder: (_, __) => Container(
                        color: AppColors.surface,
                        child: const Center(
                          child: SizedBox(
                            width: 24,
                            height: 24,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          ),
                        ),
                      ),
                      errorWidget: (_, __, ___) => _placeholder(),
                    ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.fromLTRB(14, 12, 14, 14),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  p.name,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: AppTextStyles.bodyLarge.copyWith(
                    fontWeight: FontWeight.w600,
                    color: AppColors.textPrimary,
                  ),
                ),
                const SizedBox(height: 6),
                Row(
                  children: [
                    Text(
                      p.price > 0
                          ? '₸${_formatNumber(p.price)}'
                          : l10n.productPriceUnknown,
                      style: AppTextStyles.titleSmall.copyWith(
                        color: AppColors.primary,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    const Spacer(),
                    if (p.rating > 0)
                      Row(
                        children: [
                          Icon(Icons.star_rounded,
                              size: 16, color: AppColors.warning),
                          const SizedBox(width: 2),
                          Text(
                            p.rating.toStringAsFixed(1),
                            style: AppTextStyles.labelMedium.copyWith(
                              color: AppColors.textSecondary,
                            ),
                          ),
                        ],
                      ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _placeholder() => Container(
        color: AppColors.surface,
        alignment: Alignment.center,
        child: Icon(
          Icons.inventory_2_outlined,
          size: 36,
          color: AppColors.textTertiary,
        ),
      );

  String _formatNumber(double v) {
    final s = v.toStringAsFixed(0);
    final buf = StringBuffer();
    for (int i = 0; i < s.length; i++) {
      buf.write(s[i]);
      final left = s.length - i - 1;
      if (left > 0 && left % 3 == 0) buf.write(' ');
    }
    return buf.toString();
  }
}

class _CarouselButton extends StatelessWidget {
  final IconData icon;
  final VoidCallback onTap;
  const _CarouselButton({required this.icon, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        width: 28,
        height: 28,
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: AppColors.borderSubtle),
        ),
        child: Icon(icon, size: 18, color: AppColors.textPrimary),
      ),
    );
  }
}
