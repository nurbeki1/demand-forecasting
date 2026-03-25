import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../../core/theme/theme.dart';
import '../../widgets/common/widgets.dart';
import 'widgets/product_card.dart';

class ProductDetailScreen extends StatefulWidget {
  final ProductData product;

  const ProductDetailScreen({
    super.key,
    required this.product,
  });

  @override
  State<ProductDetailScreen> createState() => _ProductDetailScreenState();
}

class _ProductDetailScreenState extends State<ProductDetailScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: CustomScrollView(
        slivers: [
          // App bar with image
          SliverAppBar(
            expandedHeight: 250,
            pinned: true,
            flexibleSpace: FlexibleSpaceBar(
              background: Container(
                color: AppColors.primary10,
                child: widget.product.imageUrl != null
                    ? Image.network(
                        widget.product.imageUrl!,
                        fit: BoxFit.cover,
                      )
                    : const Center(
                        child: Icon(
                          Icons.inventory_2_outlined,
                          size: 80,
                          color: AppColors.primary,
                        ),
                      ),
              ),
            ),
            actions: [
              IconButton(
                icon: const Icon(Icons.edit_outlined),
                onPressed: _editProduct,
              ),
              IconButton(
                icon: const Icon(Icons.more_vert),
                onPressed: _showMoreOptions,
              ),
            ],
          ),

          // Content
          SliverToBoxAdapter(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Product info header
                _buildProductHeader(),

                // Stats cards
                _buildStatsCards(),

                // Tabs
                _buildTabBar(),
              ],
            ),
          ),

          // Tab content
          SliverFillRemaining(
            child: TabBarView(
              controller: _tabController,
              children: [
                _buildOverviewTab(),
                _buildInventoryTab(),
                _buildForecastTab(),
              ],
            ),
          ),
        ],
      ),
      bottomNavigationBar: _buildBottomActions(),
    );
  }

  Widget _buildProductHeader() {
    return Padding(
      padding: const EdgeInsets.all(AppDimensions.spacing16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Status badge
          Container(
            padding: const EdgeInsets.symmetric(
              horizontal: AppDimensions.spacing10,
              vertical: AppDimensions.spacing4,
            ),
            decoration: BoxDecoration(
              color: widget.product.statusColor.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(AppDimensions.radiusFull),
            ),
            child: Text(
              widget.product.statusText,
              style: AppTextStyles.labelSmall.copyWith(
                color: widget.product.statusColor,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),

          const SizedBox(height: AppDimensions.spacing12),

          // Name
          Text(
            widget.product.name,
            style: AppTextStyles.headlineMedium,
          ),

          const SizedBox(height: AppDimensions.spacing4),

          // SKU and category
          Text(
            '${widget.product.sku} • ${widget.product.category}',
            style: AppTextStyles.bodyMedium.copyWith(
              color: AppColors.textSecondary,
            ),
          ),

          const SizedBox(height: AppDimensions.spacing16),

          // Price
          Row(
            children: [
              Text(
                '\$${widget.product.price.toStringAsFixed(2)}',
                style: AppTextStyles.headlineSmall.copyWith(
                  color: AppColors.primary,
                ),
              ),
              const SizedBox(width: AppDimensions.spacing8),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: AppDimensions.spacing8,
                  vertical: AppDimensions.spacing2,
                ),
                decoration: BoxDecoration(
                  color: AppColors.success.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(AppDimensions.radiusFull),
                ),
                child: Text(
                  '+12.5%',
                  style: AppTextStyles.caption.copyWith(
                    color: AppColors.success,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStatsCards() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: AppDimensions.spacing16),
      child: Row(
        children: [
          Expanded(
            child: _buildStatCard(
              'Stock',
              '${widget.product.stock}',
              Icons.inventory_2_outlined,
              AppColors.info,
            ),
          ),
          const SizedBox(width: AppDimensions.spacing12),
          Expanded(
            child: _buildStatCard(
              'Sales (30d)',
              '245',
              Icons.trending_up,
              AppColors.success,
            ),
          ),
          const SizedBox(width: AppDimensions.spacing12),
          Expanded(
            child: _buildStatCard(
              'Forecast',
              '312',
              Icons.analytics_outlined,
              AppColors.primary,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatCard(String label, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(AppDimensions.spacing12),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: AppDimensions.spacing8),
          Text(value, style: AppTextStyles.titleMedium),
          const SizedBox(height: AppDimensions.spacing2),
          Text(
            label,
            style: AppTextStyles.caption,
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildTabBar() {
    return Container(
      margin: const EdgeInsets.only(top: AppDimensions.spacing16),
      decoration: BoxDecoration(
        border: Border(
          bottom: BorderSide(color: AppColors.border),
        ),
      ),
      child: TabBar(
        controller: _tabController,
        labelColor: AppColors.primary,
        unselectedLabelColor: AppColors.textSecondary,
        indicatorColor: AppColors.primary,
        tabs: const [
          Tab(text: 'Overview'),
          Tab(text: 'Inventory'),
          Tab(text: 'Forecast'),
        ],
      ),
    );
  }

  Widget _buildOverviewTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppDimensions.spacing16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Description
          Text('Description', style: AppTextStyles.labelLarge),
          const SizedBox(height: AppDimensions.spacing8),
          Text(
            'High-quality product with excellent features and durability. Perfect for everyday use and suitable for a variety of applications.',
            style: AppTextStyles.bodyMedium.copyWith(
              color: AppColors.textSecondary,
            ),
          ),

          const SizedBox(height: AppDimensions.spacing24),

          // Details
          Text('Details', style: AppTextStyles.labelLarge),
          const SizedBox(height: AppDimensions.spacing12),
          _buildDetailRow('Product ID', widget.product.id),
          _buildDetailRow('SKU', widget.product.sku),
          _buildDetailRow('Category', widget.product.category),
          _buildDetailRow('Price', '\$${widget.product.price.toStringAsFixed(2)}'),
          _buildDetailRow('Status', widget.product.statusText),

          const SizedBox(height: AppDimensions.spacing24),

          // Recent activity
          Text('Recent Activity', style: AppTextStyles.labelLarge),
          const SizedBox(height: AppDimensions.spacing12),
          _buildActivityItem('Stock updated', '2 hours ago', Icons.inventory),
          _buildActivityItem('Price changed', '3 days ago', Icons.attach_money),
          _buildActivityItem('Forecast generated', '1 week ago', Icons.analytics),
        ],
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: AppDimensions.spacing12),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: AppTextStyles.bodyMedium.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
          Text(value, style: AppTextStyles.labelMedium),
        ],
      ),
    );
  }

  Widget _buildActivityItem(String title, String time, IconData icon) {
    return Container(
      margin: const EdgeInsets.only(bottom: AppDimensions.spacing12),
      padding: const EdgeInsets.all(AppDimensions.spacing12),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
        border: Border.all(color: AppColors.border),
      ),
      child: Row(
        children: [
          Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(
              color: AppColors.primary10,
              borderRadius: BorderRadius.circular(AppDimensions.radiusSm),
            ),
            child: Icon(icon, color: AppColors.primary, size: 18),
          ),
          const SizedBox(width: AppDimensions.spacing12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: AppTextStyles.labelMedium),
                Text(time, style: AppTextStyles.caption),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInventoryTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppDimensions.spacing16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Stock chart
          Text('Stock Level History', style: AppTextStyles.labelLarge),
          const SizedBox(height: AppDimensions.spacing16),
          SizedBox(
            height: 200,
            child: _buildStockChart(),
          ),

          const SizedBox(height: AppDimensions.spacing24),

          // Stock info
          Text('Current Stock', style: AppTextStyles.labelLarge),
          const SizedBox(height: AppDimensions.spacing12),

          Container(
            padding: const EdgeInsets.all(AppDimensions.spacing16),
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
              border: Border.all(color: AppColors.border),
            ),
            child: Column(
              children: [
                _buildDetailRow('Available', '${widget.product.stock} units'),
                _buildDetailRow('Reserved', '15 units'),
                _buildDetailRow('In Transit', '50 units'),
                _buildDetailRow('Reorder Point', '25 units'),
                _buildDetailRow('Safety Stock', '10 units'),
              ],
            ),
          ),

          const SizedBox(height: AppDimensions.spacing24),

          // Actions
          Row(
            children: [
              Expanded(
                child: AppButton(
                  text: 'Add Stock',
                  variant: AppButtonVariant.outline,
                  icon: Icons.add,
                  onPressed: () {},
                ),
              ),
              const SizedBox(width: AppDimensions.spacing12),
              Expanded(
                child: AppButton(
                  text: 'Adjust',
                  variant: AppButtonVariant.outline,
                  icon: Icons.edit,
                  onPressed: () {},
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStockChart() {
    return LineChart(
      LineChartData(
        gridData: FlGridData(
          show: true,
          drawVerticalLine: false,
          horizontalInterval: 50,
          getDrawingHorizontalLine: (value) => FlLine(
            color: AppColors.border,
            strokeWidth: 1,
          ),
        ),
        titlesData: FlTitlesData(
          show: true,
          rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 30,
              getTitlesWidget: (value, meta) {
                final labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
                if (value.toInt() < labels.length) {
                  return Padding(
                    padding: const EdgeInsets.only(top: 8),
                    child: Text(
                      labels[value.toInt()],
                      style: AppTextStyles.caption,
                    ),
                  );
                }
                return const SizedBox();
              },
            ),
          ),
          leftTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 40,
              getTitlesWidget: (value, meta) => Text(
                value.toInt().toString(),
                style: AppTextStyles.caption,
              ),
            ),
          ),
        ),
        borderData: FlBorderData(show: false),
        minX: 0,
        maxX: 5,
        minY: 0,
        maxY: 250,
        lineBarsData: [
          LineChartBarData(
            spots: const [
              FlSpot(0, 180),
              FlSpot(1, 150),
              FlSpot(2, 200),
              FlSpot(3, 120),
              FlSpot(4, 180),
              FlSpot(5, 150),
            ],
            isCurved: true,
            color: AppColors.primary,
            barWidth: 3,
            isStrokeCapRound: true,
            dotData: FlDotData(
              show: true,
              getDotPainter: (spot, percent, barData, index) => FlDotCirclePainter(
                radius: 4,
                color: AppColors.primary,
                strokeWidth: 2,
                strokeColor: AppColors.white,
              ),
            ),
            belowBarData: BarAreaData(
              show: true,
              color: AppColors.primary.withValues(alpha: 0.1),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildForecastTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppDimensions.spacing16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Forecast summary
          Container(
            padding: const EdgeInsets.all(AppDimensions.spacing16),
            decoration: BoxDecoration(
              color: AppColors.primary10,
              borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
            ),
            child: Row(
              children: [
                Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    color: AppColors.primary,
                    borderRadius: BorderRadius.circular(AppDimensions.radiusSm),
                  ),
                  child: const Icon(
                    Icons.analytics,
                    color: AppColors.white,
                  ),
                ),
                const SizedBox(width: AppDimensions.spacing16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Next 30 Days Forecast',
                        style: AppTextStyles.labelLarge,
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Predicted demand: 312 units',
                        style: AppTextStyles.bodyMedium.copyWith(
                          color: AppColors.textSecondary,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: AppDimensions.spacing24),

          // Forecast metrics
          Row(
            children: [
              Expanded(
                child: _buildForecastMetric(
                  'Accuracy',
                  '92.5%',
                  AppColors.success,
                ),
              ),
              const SizedBox(width: AppDimensions.spacing12),
              Expanded(
                child: _buildForecastMetric(
                  'Trend',
                  '+8.2%',
                  AppColors.info,
                ),
              ),
              const SizedBox(width: AppDimensions.spacing12),
              Expanded(
                child: _buildForecastMetric(
                  'Confidence',
                  '85%',
                  AppColors.primary,
                ),
              ),
            ],
          ),

          const SizedBox(height: AppDimensions.spacing24),

          // Recommendations
          Text('Recommendations', style: AppTextStyles.labelLarge),
          const SizedBox(height: AppDimensions.spacing12),

          _buildRecommendationCard(
            'Reorder Soon',
            'Based on current demand, consider reordering in 5 days.',
            Icons.shopping_cart_outlined,
            AppColors.warning,
          ),

          _buildRecommendationCard(
            'Optimize Pricing',
            'Demand is high. Consider adjusting price for better margins.',
            Icons.trending_up,
            AppColors.success,
          ),

          const SizedBox(height: AppDimensions.spacing24),

          // Generate new forecast button
          AppButton(
            text: 'Generate New Forecast',
            icon: Icons.refresh,
            onPressed: () {},
            fullWidth: true,
          ),
        ],
      ),
    );
  }

  Widget _buildForecastMetric(String label, String value, Color color) {
    return Container(
      padding: const EdgeInsets.all(AppDimensions.spacing12),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(
        children: [
          Text(
            value,
            style: AppTextStyles.titleMedium.copyWith(color: color),
          ),
          const SizedBox(height: AppDimensions.spacing4),
          Text(
            label,
            style: AppTextStyles.caption,
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildRecommendationCard(
    String title,
    String description,
    IconData icon,
    Color color,
  ) {
    return Container(
      margin: const EdgeInsets.only(bottom: AppDimensions.spacing12),
      padding: const EdgeInsets.all(AppDimensions.spacing12),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Row(
        children: [
          Icon(icon, color: color),
          const SizedBox(width: AppDimensions.spacing12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: AppTextStyles.labelMedium.copyWith(color: color),
                ),
                const SizedBox(height: 2),
                Text(
                  description,
                  style: AppTextStyles.caption,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBottomActions() {
    return Container(
      padding: const EdgeInsets.all(AppDimensions.spacing16),
      decoration: BoxDecoration(
        color: AppColors.surface,
        border: Border(
          top: BorderSide(color: AppColors.border),
        ),
      ),
      child: SafeArea(
        child: Row(
          children: [
            Expanded(
              child: AppButton(
                text: 'View Forecast',
                variant: AppButtonVariant.outline,
                onPressed: () {},
              ),
            ),
            const SizedBox(width: AppDimensions.spacing12),
            Expanded(
              child: AppButton(
                text: 'Create Forecast',
                onPressed: () {},
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _editProduct() {
    // Navigate to edit screen
  }

  void _showMoreOptions() {
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.symmetric(vertical: AppDimensions.spacing16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.edit_outlined),
              title: const Text('Edit Product'),
              onTap: () {
                Navigator.pop(context);
                _editProduct();
              },
            ),
            ListTile(
              leading: const Icon(Icons.copy_outlined),
              title: const Text('Duplicate'),
              onTap: () => Navigator.pop(context),
            ),
            ListTile(
              leading: const Icon(Icons.archive_outlined),
              title: const Text('Archive'),
              onTap: () => Navigator.pop(context),
            ),
            ListTile(
              leading: const Icon(Icons.delete_outline, color: AppColors.error),
              title: Text('Delete', style: TextStyle(color: AppColors.error)),
              onTap: () => Navigator.pop(context),
            ),
          ],
        ),
      ),
    );
  }
}
