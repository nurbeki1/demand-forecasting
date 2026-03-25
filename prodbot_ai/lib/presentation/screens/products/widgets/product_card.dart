import 'package:flutter/material.dart';
import '../../../../core/theme/theme.dart';

enum ProductStatus { active, inactive, lowStock, outOfStock }

class ProductData {
  final String id;
  final String name;
  final String category;
  final String sku;
  final double price;
  final int stock;
  final String? imageUrl;
  final ProductStatus status;

  ProductData({
    required this.id,
    required this.name,
    required this.category,
    required this.sku,
    required this.price,
    required this.stock,
    this.imageUrl,
    required this.status,
  });

  String get statusText {
    switch (status) {
      case ProductStatus.active:
        return 'Active';
      case ProductStatus.inactive:
        return 'Inactive';
      case ProductStatus.lowStock:
        return 'Low Stock';
      case ProductStatus.outOfStock:
        return 'Out of Stock';
    }
  }

  Color get statusColor {
    switch (status) {
      case ProductStatus.active:
        return AppColors.success;
      case ProductStatus.inactive:
        return AppColors.textSecondary;
      case ProductStatus.lowStock:
        return AppColors.warning;
      case ProductStatus.outOfStock:
        return AppColors.error;
    }
  }
}

class ProductCard extends StatelessWidget {
  final ProductData product;
  final bool isGridView;
  final VoidCallback? onTap;

  const ProductCard({
    super.key,
    required this.product,
    this.isGridView = false,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return isGridView ? _buildGridCard() : _buildListCard();
  }

  Widget _buildGridCard() {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
          border: Border.all(color: AppColors.border),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Image placeholder
            Expanded(
              flex: 3,
              child: Container(
                width: double.infinity,
                decoration: BoxDecoration(
                  color: AppColors.primary10,
                  borderRadius: const BorderRadius.vertical(
                    top: Radius.circular(AppDimensions.radiusLg),
                  ),
                ),
                child: product.imageUrl != null
                    ? ClipRRect(
                        borderRadius: const BorderRadius.vertical(
                          top: Radius.circular(AppDimensions.radiusLg),
                        ),
                        child: Image.network(
                          product.imageUrl!,
                          fit: BoxFit.cover,
                        ),
                      )
                    : const Center(
                        child: Icon(
                          Icons.inventory_2_outlined,
                          size: 40,
                          color: AppColors.primary,
                        ),
                      ),
              ),
            ),

            // Content
            Expanded(
              flex: 2,
              child: Padding(
                padding: const EdgeInsets.all(AppDimensions.spacing12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Name
                    Text(
                      product.name,
                      style: AppTextStyles.labelMedium,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),

                    const SizedBox(height: 2),

                    // SKU
                    Text(
                      product.sku,
                      style: AppTextStyles.caption,
                    ),

                    const Spacer(),

                    // Price and status
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          '\$${product.price.toStringAsFixed(2)}',
                          style: AppTextStyles.labelMedium.copyWith(
                            color: AppColors.primary,
                          ),
                        ),
                        Container(
                          width: 8,
                          height: 8,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: product.statusColor,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildListCard() {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(AppDimensions.spacing12),
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
          border: Border.all(color: AppColors.border),
        ),
        child: Row(
          children: [
            // Image placeholder
            Container(
              width: 60,
              height: 60,
              decoration: BoxDecoration(
                color: AppColors.primary10,
                borderRadius: BorderRadius.circular(AppDimensions.radiusSm),
              ),
              child: product.imageUrl != null
                  ? ClipRRect(
                      borderRadius: BorderRadius.circular(AppDimensions.radiusSm),
                      child: Image.network(
                        product.imageUrl!,
                        fit: BoxFit.cover,
                      ),
                    )
                  : const Icon(
                      Icons.inventory_2_outlined,
                      color: AppColors.primary,
                    ),
            ),

            const SizedBox(width: AppDimensions.spacing12),

            // Content
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Name and status
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          product.name,
                          style: AppTextStyles.labelMedium,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: AppDimensions.spacing8,
                          vertical: AppDimensions.spacing2,
                        ),
                        decoration: BoxDecoration(
                          color: product.statusColor.withValues(alpha: 0.1),
                          borderRadius: BorderRadius.circular(AppDimensions.radiusFull),
                        ),
                        child: Text(
                          product.statusText,
                          style: AppTextStyles.caption.copyWith(
                            color: product.statusColor,
                            fontWeight: FontWeight.w600,
                            fontSize: 10,
                          ),
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: AppDimensions.spacing4),

                  // SKU and category
                  Text(
                    '${product.sku} • ${product.category}',
                    style: AppTextStyles.caption,
                  ),

                  const SizedBox(height: AppDimensions.spacing4),

                  // Price and stock
                  Row(
                    children: [
                      Text(
                        '\$${product.price.toStringAsFixed(2)}',
                        style: AppTextStyles.labelMedium.copyWith(
                          color: AppColors.primary,
                        ),
                      ),
                      const Spacer(),
                      Icon(
                        Icons.inventory,
                        size: 14,
                        color: AppColors.iconVariant,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        '${product.stock} units',
                        style: AppTextStyles.caption,
                      ),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(width: AppDimensions.spacing8),

            const Icon(
              Icons.chevron_right,
              color: AppColors.iconVariant,
            ),
          ],
        ),
      ),
    );
  }
}
