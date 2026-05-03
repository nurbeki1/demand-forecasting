import 'package:flutter/material.dart';
import '../../../core/theme/theme.dart';
import '../../../services/chat_service.dart';
import '../../widgets/common/widgets.dart';

class AnalyticsScreen extends StatefulWidget {
  const AnalyticsScreen({super.key});

  @override
  State<AnalyticsScreen> createState() => _AnalyticsScreenState();
}

class _AnalyticsScreenState extends State<AnalyticsScreen> {
  final ChatService _chatService = ChatService();

  bool _isLoading = true;
  Map<String, dynamic>? _summary;
  Map<String, dynamic>? _trends;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });
    try {
      final results = await Future.wait([
        _chatService.getAnalyticsSummary(),
        _chatService.getAnalyticsTrends(),
      ]);
      if (mounted) {
        setState(() {
          _summary = results[0];
          _trends = results[1];
        });
      }
    } catch (e) {
      if (mounted) setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: Column(
          children: [
            _buildAppBar(),
            const Divider(height: 1, color: AppColors.borderSubtle),
            Expanded(
              child: _isLoading
                  ? const Center(
                      child: CircularProgressIndicator(
                        color: AppColors.primary,
                      ),
                    )
                  : _error != null
                      ? _buildError()
                      : RefreshIndicator(
                          onRefresh: _loadData,
                          color: AppColors.primary,
                          backgroundColor: AppColors.surface,
                          child: SingleChildScrollView(
                            physics: const AlwaysScrollableScrollPhysics(),
                            padding: const EdgeInsets.all(16),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                _buildOverviewCards(),
                                const SizedBox(height: 24),
                                _buildTrendsSection(),
                                const SizedBox(height: 24),
                                _buildTopProductsSection(),
                                const SizedBox(height: 24),
                                _buildDecliningSection(),
                                const SizedBox(height: 32),
                              ],
                            ),
                          ),
                        ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAppBar() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 12, 12, 12),
      child: Row(
        children: [
          Text('Аналитика', style: AppTextStyles.titleLarge),
          const Spacer(),
          _IconBubble(icon: Icons.refresh_rounded, onTap: _loadData),
        ],
      ),
    );
  }

  Widget _buildError() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Container(
            width: 72,
            height: 72,
            decoration: BoxDecoration(
              color: AppColors.surfaceVariant,
              shape: BoxShape.circle,
              border: Border.all(color: AppColors.border, width: 1),
            ),
            child: const Icon(
              Icons.cloud_off_rounded,
              color: AppColors.textSecondary,
              size: 36,
            ),
          ),
          const SizedBox(height: 16),
          Text(
            'Деректерді жүктеу сәтсіз аяқталды',
            style: AppTextStyles.titleSmall,
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 6),
          Text(
            'Бэкенд серверінің іске қосылғанын тексеріңіз',
            style: AppTextStyles.bodySmall.copyWith(
              color: AppColors.textSecondary,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 20),
          AppButton.gradient(
            text: 'Қайта жүктеу',
            prefixIcon: Icons.refresh_rounded,
            isFullWidth: false,
            onPressed: _loadData,
          ),
        ],
      ),
    );
  }

  Widget _buildOverviewCards() {
    final overview = _summary?['overview'] as Map<String, dynamic>?;

    final cards = [
      _MetricCardData(
        'Жалпы болжамдар',
        overview?['total_forecasts']?.toString() ?? '—',
        Icons.analytics_outlined,
        AppColors.primary,
      ),
      _MetricCardData(
        'Орт. дәлдік',
        overview?['avg_accuracy'] != null
            ? '${(overview!['avg_accuracy'] as num).toStringAsFixed(1)}%'
            : '—',
        Icons.show_chart_rounded,
        AppColors.success,
      ),
      _MetricCardData(
        'Өнімдер',
        overview?['total_products']?.toString() ?? '—',
        Icons.inventory_2_outlined,
        AppColors.info,
      ),
      _MetricCardData(
        'Дүкендер',
        overview?['active_stores']?.toString() ?? '—',
        Icons.store_outlined,
        AppColors.secondary,
      ),
    ];

    return GridView.count(
      crossAxisCount: 2,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisSpacing: 12,
      mainAxisSpacing: 12,
      childAspectRatio: 1.45,
      children: cards.map(_buildMetricCard).toList(),
    );
  }

  Widget _buildMetricCard(_MetricCardData c) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.cardBackground,
        borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
        border: Border.all(color: AppColors.border, width: 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(
              color: c.color.withValues(alpha: 0.14),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(
                color: c.color.withValues(alpha: 0.32),
              ),
            ),
            child: Icon(c.icon, color: c.color, size: 18),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                c.value,
                style: AppTextStyles.headlineSmall.copyWith(
                  color: AppColors.textPrimary,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                c.label,
                style: AppTextStyles.caption.copyWith(
                  color: AppColors.textSecondary,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildTrendsSection() {
    final growing = _trends?['growing'] as List<dynamic>?;
    final stable = _trends?['stable'] as List<dynamic>?;

    if ((growing == null || growing.isEmpty) &&
        (stable == null || stable.isEmpty)) {
      return const SizedBox.shrink();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Тренд талдауы', style: AppTextStyles.titleSmall),
        const SizedBox(height: 12),
        if (growing != null && growing.isNotEmpty) ...[
          _buildTrendGroup(
            'Өсіп жатқан',
            growing,
            AppColors.success,
            Icons.trending_up_rounded,
          ),
          const SizedBox(height: 10),
        ],
        if (stable != null && stable.isNotEmpty)
          _buildTrendGroup(
            'Тұрақты',
            stable,
            AppColors.warning,
            Icons.trending_flat_rounded,
          ),
      ],
    );
  }

  Widget _buildTrendGroup(
    String title,
    List<dynamic> items,
    Color color,
    IconData icon,
  ) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppColors.cardBackground,
        borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
        border: Border.all(color: AppColors.border, width: 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 26,
                height: 26,
                decoration: BoxDecoration(
                  color: color.withValues(alpha: 0.14),
                  borderRadius: BorderRadius.circular(7),
                  border: Border.all(color: color.withValues(alpha: 0.32)),
                ),
                child: Icon(icon, color: color, size: 14),
              ),
              const SizedBox(width: 8),
              Text(
                title,
                style: AppTextStyles.labelMedium.copyWith(
                  color: color,
                  fontWeight: FontWeight.w700,
                ),
              ),
              const Spacer(),
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: color.withValues(alpha: 0.14),
                  borderRadius: BorderRadius.circular(999),
                  border: Border.all(color: color.withValues(alpha: 0.3)),
                ),
                child: Text(
                  '${items.length}',
                  style: AppTextStyles.caption.copyWith(
                    color: color,
                    fontWeight: FontWeight.w700,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Wrap(
            spacing: 6,
            runSpacing: 6,
            children: items.take(8).map((item) {
              final productId =
                  (item as Map<String, dynamic>)['product_id'] as String? ?? '';
              return Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                decoration: BoxDecoration(
                  color: color.withValues(alpha: 0.08),
                  borderRadius: BorderRadius.circular(999),
                  border: Border.all(color: color.withValues(alpha: 0.25)),
                ),
                child: Text(
                  productId,
                  style: AppTextStyles.caption.copyWith(
                    color: AppColors.textPrimary,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }

  Widget _buildTopProductsSection() {
    final topByDemand = _summary?['top_by_demand'] as List<dynamic>?;
    if (topByDemand == null || topByDemand.isEmpty) {
      return const SizedBox.shrink();
    }

    final maxDemand = topByDemand
        .map((e) => (e as Map<String, dynamic>)['avg_demand'] as num? ?? 0)
        .reduce((a, b) => a > b ? a : b)
        .toDouble();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('Үздік өнімдер (сұраныс)', style: AppTextStyles.titleSmall),
        const SizedBox(height: 12),
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AppColors.cardBackground,
            borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
            border: Border.all(color: AppColors.border, width: 1),
          ),
          child: Column(
            children: topByDemand.take(5).toList().asMap().entries.map((e) {
              final index = e.key;
              final product = e.value as Map<String, dynamic>;
              final name = product['product_id'] as String? ?? '—';
              final demand = (product['avg_demand'] as num?)?.toDouble() ?? 0;
              final pct = maxDemand > 0 ? demand / maxDemand : 0.0;

              return Padding(
                padding: const EdgeInsets.only(bottom: 14),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          name,
                          style: AppTextStyles.bodyMedium.copyWith(
                            color: AppColors.textPrimary,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                        Text(
                          demand.toStringAsFixed(0),
                          style: AppTextStyles.labelSmall.copyWith(
                            color: AppColors.primary,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    ClipRRect(
                      borderRadius: BorderRadius.circular(999),
                      child: LinearProgressIndicator(
                        value: pct,
                        backgroundColor: AppColors.borderSubtle,
                        valueColor: AlwaysStoppedAnimation<Color>(
                          index == 0
                              ? AppColors.primary
                              : AppColors.primary.withValues(alpha: 0.55),
                        ),
                        minHeight: 6,
                      ),
                    ),
                  ],
                ),
              );
            }).toList(),
          ),
        ),
      ],
    );
  }

  Widget _buildDecliningSection() {
    final declining = _trends?['declining'] as List<dynamic>?;
    if (declining == null || declining.isEmpty) return const SizedBox.shrink();

    return _buildTrendGroup(
      'Төмендеп жатқан',
      declining,
      AppColors.error,
      Icons.trending_down_rounded,
    );
  }
}

class _MetricCardData {
  final String label;
  final String value;
  final IconData icon;
  final Color color;
  _MetricCardData(this.label, this.value, this.icon, this.color);
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
