import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../../../core/theme/theme.dart';
import '../../../../data/models/chat_models.dart';
import 'suggestion_card.dart';

class ChatMessageData {
  final String text;
  final bool isUser;
  final bool showSuggestions;
  final DateTime? timestamp;
  final List<String>? suggestions;
  final String? intent;
  final List<ProductImage>? images;

  ChatMessageData({
    required this.text,
    required this.isUser,
    this.showSuggestions = false,
    this.timestamp,
    this.suggestions,
    this.intent,
    this.images,
  });
}

class ChatMessage extends StatelessWidget {
  final ChatMessageData data;
  final Function(String)? onSuggestionTap;

  const ChatMessage({
    super.key,
    required this.data,
    this.onSuggestionTap,
  });

  static const List<String> _defaultSuggestions = [
    'Forecast for P0001',
    'Top 5 products',
    'Compare East and West',
  ];

  List<String> get _suggestions => data.suggestions ?? _defaultSuggestions;

  @override
  Widget build(BuildContext context) {
    if (data.isUser) {
      return _buildUserMessage();
    }
    return _buildBotMessage();
  }

  Widget _buildUserMessage() {
    return Padding(
      padding: const EdgeInsets.only(bottom: AppDimensions.spacing12),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.end,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(width: AppDimensions.spacing48),
          Flexible(
            child: Container(
              padding: const EdgeInsets.symmetric(
                horizontal: AppDimensions.spacing16,
                vertical: AppDimensions.spacing12,
              ),
              decoration: BoxDecoration(
                color: AppColors.primary,
                borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
              ),
              child: Text(
                data.text,
                style: AppTextStyles.bodyMedium.copyWith(
                  color: AppColors.white,
                ),
              ),
            ),
          ),
          const SizedBox(width: AppDimensions.spacing8),
          // User avatar
          Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              color: AppColors.primary20,
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Icon(
              Icons.person,
              size: 18,
              color: AppColors.primary,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBotMessage() {
    return Padding(
      padding: const EdgeInsets.only(bottom: AppDimensions.spacing12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Bot avatar
              Container(
                width: 32,
                height: 32,
                decoration: BoxDecoration(
                  color: AppColors.primary10,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(
                  Icons.smart_toy_rounded,
                  size: 18,
                  color: AppColors.primary,
                ),
              ),
              const SizedBox(width: AppDimensions.spacing8),
              Flexible(
                child: Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: AppDimensions.spacing16,
                    vertical: AppDimensions.spacing12,
                  ),
                  decoration: BoxDecoration(
                    color: AppColors.chatBubble,
                    borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
                  ),
                  child: _buildFormattedText(data.text),
                ),
              ),
              const SizedBox(width: AppDimensions.spacing48),
            ],
          ),

          // Show product images carousel
          if (data.images != null && data.images!.isNotEmpty) ...[
            const SizedBox(height: AppDimensions.spacing12),
            Padding(
              padding: const EdgeInsets.only(left: 40),
              child: ProductCarousel(images: data.images!),
            ),
          ],

          // Show suggestions
          if (data.showSuggestions) ...[
            const SizedBox(height: AppDimensions.spacing12),
            ..._suggestions.map((suggestion) => Padding(
                  padding: const EdgeInsets.only(
                    left: 40,
                    bottom: AppDimensions.spacing8,
                  ),
                  child: SuggestionCard(
                    text: suggestion,
                    onTap: () => onSuggestionTap?.call(suggestion),
                  ),
                )),
          ],
        ],
      ),
    );
  }

  /// Formats text with basic markdown-like styling
  Widget _buildFormattedText(String text) {
    final spans = <TextSpan>[];
    final lines = text.split('\n');

    for (int i = 0; i < lines.length; i++) {
      final line = lines[i];

      // Check for headers (lines starting with ##)
      if (line.startsWith('## ')) {
        spans.add(TextSpan(
          text: line.substring(3),
          style: AppTextStyles.titleSmall.copyWith(
            color: AppColors.textPrimary,
            fontWeight: FontWeight.bold,
          ),
        ));
      } else if (line.startsWith('**') && line.endsWith('**')) {
        // Bold text
        spans.add(TextSpan(
          text: line.substring(2, line.length - 2),
          style: AppTextStyles.bodyMedium.copyWith(
            color: AppColors.textMuted,
            fontWeight: FontWeight.bold,
          ),
        ));
      } else if (line.startsWith('- ') || line.startsWith('• ')) {
        // Bullet points
        spans.add(TextSpan(
          text: '  • ${line.substring(2)}',
          style: AppTextStyles.bodyMedium.copyWith(
            color: AppColors.textMuted,
          ),
        ));
      } else {
        // Regular text - parse inline bold
        spans.addAll(_parseInlineBold(line));
      }

      // Add newline except for last line
      if (i < lines.length - 1) {
        spans.add(const TextSpan(text: '\n'));
      }
    }

    return RichText(
      text: TextSpan(
        children: spans,
        style: AppTextStyles.bodyMedium.copyWith(
          color: AppColors.textMuted,
        ),
      ),
    );
  }

  /// Parse inline bold text (text between **)
  List<TextSpan> _parseInlineBold(String text) {
    final spans = <TextSpan>[];
    final regex = RegExp(r'\*\*(.+?)\*\*');
    int lastEnd = 0;

    for (final match in regex.allMatches(text)) {
      // Add text before the match
      if (match.start > lastEnd) {
        spans.add(TextSpan(
          text: text.substring(lastEnd, match.start),
          style: AppTextStyles.bodyMedium.copyWith(
            color: AppColors.textMuted,
          ),
        ));
      }

      // Add bold text
      spans.add(TextSpan(
        text: match.group(1),
        style: AppTextStyles.bodyMedium.copyWith(
          color: AppColors.textMuted,
          fontWeight: FontWeight.bold,
        ),
      ));

      lastEnd = match.end;
    }

    // Add remaining text
    if (lastEnd < text.length) {
      spans.add(TextSpan(
        text: text.substring(lastEnd),
        style: AppTextStyles.bodyMedium.copyWith(
          color: AppColors.textMuted,
        ),
      ));
    }

    // If no matches, return original text
    if (spans.isEmpty) {
      spans.add(TextSpan(
        text: text,
        style: AppTextStyles.bodyMedium.copyWith(
          color: AppColors.textMuted,
        ),
      ));
    }

    return spans;
  }
}

/// Product carousel widget for displaying multiple product cards
class ProductCarousel extends StatefulWidget {
  final List<ProductImage> images;

  const ProductCarousel({
    super.key,
    required this.images,
  });

  @override
  State<ProductCarousel> createState() => _ProductCarouselState();
}

class _ProductCarouselState extends State<ProductCarousel> {
  final PageController _pageController = PageController(viewportFraction: 0.85);
  int _currentPage = 0;

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (widget.images.length == 1) {
      return ProductCard(product: widget.images.first);
    }

    return Column(
      children: [
        SizedBox(
          height: 200,
          child: PageView.builder(
            controller: _pageController,
            itemCount: widget.images.length,
            onPageChanged: (index) {
              setState(() => _currentPage = index);
            },
            itemBuilder: (context, index) {
              return Padding(
                padding: const EdgeInsets.only(right: 12),
                child: ProductCard(product: widget.images[index]),
              );
            },
          ),
        ),
        const SizedBox(height: 8),
        // Page indicators
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: List.generate(
            widget.images.length,
            (index) => AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              margin: const EdgeInsets.symmetric(horizontal: 3),
              width: _currentPage == index ? 20 : 8,
              height: 8,
              decoration: BoxDecoration(
                color: _currentPage == index
                    ? AppColors.primary
                    : AppColors.border,
                borderRadius: BorderRadius.circular(4),
              ),
            ),
          ),
        ),
      ],
    );
  }
}

/// Individual product card widget
class ProductCard extends StatelessWidget {
  final ProductImage product;

  const ProductCard({
    super.key,
    required this.product,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
        boxShadow: AppDimensions.shadowCard,
        border: Border.all(color: AppColors.border, width: 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Product image
          ClipRRect(
            borderRadius: const BorderRadius.vertical(
              top: Radius.circular(AppDimensions.radiusMd),
            ),
            child: SizedBox(
              height: 100,
              width: double.infinity,
              child: product.imageUrl.isNotEmpty
                  ? CachedNetworkImage(
                      imageUrl: product.imageUrl,
                      fit: BoxFit.cover,
                      placeholder: (context, url) => Container(
                        color: AppColors.chatBubble,
                        child: const Center(
                          child: CircularProgressIndicator(strokeWidth: 2),
                        ),
                      ),
                      errorWidget: (context, url, error) => Container(
                        color: AppColors.chatBubble,
                        child: const Icon(
                          Icons.image_not_supported_outlined,
                          color: AppColors.textHint,
                          size: 40,
                        ),
                      ),
                    )
                  : Container(
                      color: AppColors.chatBubble,
                      child: const Icon(
                        Icons.shopping_bag_outlined,
                        color: AppColors.textHint,
                        size: 40,
                      ),
                    ),
            ),
          ),
          // Product info
          Padding(
            padding: const EdgeInsets.all(AppDimensions.spacing12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Product name
                Text(
                  product.name,
                  style: AppTextStyles.bodySmall.copyWith(
                    fontWeight: FontWeight.w600,
                    color: AppColors.textPrimary,
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 6),
                // Price and rating row
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    // Price
                    Text(
                      '\$${product.price.toStringAsFixed(2)}',
                      style: AppTextStyles.titleSmall.copyWith(
                        color: AppColors.primary,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    // Rating
                    if (product.rating > 0)
                      Row(
                        children: [
                          const Icon(
                            Icons.star,
                            size: 14,
                            color: Colors.amber,
                          ),
                          const SizedBox(width: 2),
                          Text(
                            product.rating.toStringAsFixed(1),
                            style: AppTextStyles.caption.copyWith(
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
}
