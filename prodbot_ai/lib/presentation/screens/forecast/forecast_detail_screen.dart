import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';
import '../../../core/theme/theme.dart';
import 'widgets/forecast_card.dart';

class ForecastDetailScreen extends StatefulWidget {
  final ForecastData forecast;

  const ForecastDetailScreen({
    super.key,
    required this.forecast,
  });

  @override
  State<ForecastDetailScreen> createState() => _ForecastDetailScreenState();
}

class _ForecastDetailScreenState extends State<ForecastDetailScreen> {
  bool _showConfidenceInterval = true;

  // Mock chart data
  final List<FlSpot> _historicalData = [
    const FlSpot(0, 45),
    const FlSpot(1, 52),
    const FlSpot(2, 48),
    const FlSpot(3, 55),
    const FlSpot(4, 60),
    const FlSpot(5, 58),
    const FlSpot(6, 62),
  ];

  final List<FlSpot> _forecastData = [
    const FlSpot(6, 62),
    const FlSpot(7, 65),
    const FlSpot(8, 68),
    const FlSpot(9, 70),
    const FlSpot(10, 72),
    const FlSpot(11, 74),
    const FlSpot(12, 75),
  ];

  // Confidence interval bounds
  final List<FlSpot> _upperBound = [
    const FlSpot(6, 62),
    const FlSpot(7, 70),
    const FlSpot(8, 75),
    const FlSpot(9, 78),
    const FlSpot(10, 82),
    const FlSpot(11, 85),
    const FlSpot(12, 88),
  ];

  final List<FlSpot> _lowerBound = [
    const FlSpot(6, 62),
    const FlSpot(7, 60),
    const FlSpot(8, 61),
    const FlSpot(9, 62),
    const FlSpot(10, 62),
    const FlSpot(11, 63),
    const FlSpot(12, 62),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: Text(widget.forecast.productName),
        actions: [
          IconButton(
            icon: const Icon(Icons.share_outlined),
            onPressed: _shareForecast,
          ),
          PopupMenuButton<String>(
            onSelected: _handleMenuAction,
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: 'export_pdf',
                child: Row(
                  children: [
                    Icon(Icons.picture_as_pdf_outlined),
                    SizedBox(width: 12),
                    Text('Export PDF'),
                  ],
                ),
              ),
              const PopupMenuItem(
                value: 'export_excel',
                child: Row(
                  children: [
                    Icon(Icons.table_chart_outlined),
                    SizedBox(width: 12),
                    Text('Export Excel'),
                  ],
                ),
              ),
              const PopupMenuItem(
                value: 'delete',
                child: Row(
                  children: [
                    Icon(Icons.delete_outline, color: AppColors.error),
                    SizedBox(width: 12),
                    Text('Delete', style: TextStyle(color: AppColors.error)),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Status banner
            _buildStatusBanner(),

            // Chart section
            _buildChartSection(),

            // Metrics section
            _buildMetricsSection(),

            // Insights section
            _buildInsightsSection(),

            // Details section
            _buildDetailsSection(),

            const SizedBox(height: AppDimensions.spacing32),
          ],
        ),
      ),
    );
  }

  Widget _buildStatusBanner() {
    return Container(
      margin: const EdgeInsets.all(AppDimensions.spacing16),
      padding: const EdgeInsets.all(AppDimensions.spacing16),
      decoration: BoxDecoration(
        color: widget.forecast.statusColor.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
        border: Border.all(
          color: widget.forecast.statusColor.withValues(alpha: 0.3),
        ),
      ),
      child: Row(
        children: [
          Icon(
            _getStatusIcon(),
            color: widget.forecast.statusColor,
          ),
          const SizedBox(width: AppDimensions.spacing12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  widget.forecast.statusText,
                  style: AppTextStyles.labelLarge.copyWith(
                    color: widget.forecast.statusColor,
                  ),
                ),
                Text(
                  _getStatusDescription(),
                  style: AppTextStyles.caption,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildChartSection() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: AppDimensions.spacing16),
      padding: const EdgeInsets.all(AppDimensions.spacing16),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
        border: Border.all(color: AppColors.border),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Demand Forecast', style: AppTextStyles.titleSmall),
              Row(
                children: [
                  Text(
                    'Confidence interval',
                    style: AppTextStyles.caption,
                  ),
                  const SizedBox(width: 8),
                  Switch(
                    value: _showConfidenceInterval,
                    onChanged: (value) {
                      setState(() => _showConfidenceInterval = value);
                    },
                    activeColor: AppColors.primary,
                  ),
                ],
              ),
            ],
          ),

          const SizedBox(height: AppDimensions.spacing16),

          // Chart
          SizedBox(
            height: 250,
            child: LineChart(
              LineChartData(
                gridData: FlGridData(
                  show: true,
                  drawHorizontalLine: true,
                  drawVerticalLine: false,
                  horizontalInterval: 20,
                  getDrawingHorizontalLine: (value) => FlLine(
                    color: AppColors.border,
                    strokeWidth: 1,
                  ),
                ),
                borderData: FlBorderData(show: false),
                titlesData: FlTitlesData(
                  leftTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      reservedSize: 40,
                      getTitlesWidget: (value, meta) {
                        return Text(
                          value.toInt().toString(),
                          style: AppTextStyles.caption,
                        );
                      },
                    ),
                  ),
                  bottomTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      getTitlesWidget: (value, meta) {
                        final day = value.toInt();
                        if (day % 2 == 0) {
                          return Padding(
                            padding: const EdgeInsets.only(top: 8),
                            child: Text(
                              'Day $day',
                              style: AppTextStyles.caption.copyWith(fontSize: 10),
                            ),
                          );
                        }
                        return const SizedBox.shrink();
                      },
                    ),
                  ),
                  topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                  rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
                ),
                lineBarsData: [
                  // Confidence interval (if enabled)
                  if (_showConfidenceInterval)
                    LineChartBarData(
                      spots: _upperBound,
                      isCurved: true,
                      color: Colors.transparent,
                      barWidth: 0,
                      dotData: const FlDotData(show: false),
                      belowBarData: BarAreaData(
                        show: true,
                        color: AppColors.purpleHaze.withValues(alpha: 0.1),
                      ),
                    ),
                  if (_showConfidenceInterval)
                    LineChartBarData(
                      spots: _lowerBound,
                      isCurved: true,
                      color: Colors.transparent,
                      barWidth: 0,
                      dotData: const FlDotData(show: false),
                      aboveBarData: BarAreaData(
                        show: true,
                        color: AppColors.background,
                      ),
                    ),
                  // Historical data
                  LineChartBarData(
                    spots: _historicalData,
                    isCurved: true,
                    color: AppColors.info,
                    barWidth: 3,
                    dotData: const FlDotData(show: false),
                    belowBarData: BarAreaData(
                      show: true,
                      color: AppColors.info.withValues(alpha: 0.1),
                    ),
                  ),
                  // Forecast data
                  LineChartBarData(
                    spots: _forecastData,
                    isCurved: true,
                    color: AppColors.purpleHaze,
                    barWidth: 3,
                    dotData: FlDotData(
                      show: true,
                      getDotPainter: (spot, percent, bar, index) {
                        return FlDotCirclePainter(
                          radius: 4,
                          color: AppColors.purpleHaze,
                          strokeWidth: 2,
                          strokeColor: AppColors.surface,
                        );
                      },
                    ),
                    dashArray: [8, 4],
                  ),
                ],
                lineTouchData: LineTouchData(
                  touchTooltipData: LineTouchTooltipData(
                    getTooltipItems: (touchedSpots) {
                      return touchedSpots.map((spot) {
                        return LineTooltipItem(
                          'Day ${spot.x.toInt()}\n${spot.y.toInt()} units',
                          AppTextStyles.caption.copyWith(
                            color: AppColors.white,
                          ),
                        );
                      }).toList();
                    },
                  ),
                ),
              ),
            ),
          ),

          const SizedBox(height: AppDimensions.spacing16),

          // Legend
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              _LegendItem(color: AppColors.info, label: 'Historical'),
              const SizedBox(width: AppDimensions.spacing24),
              _LegendItem(
                color: AppColors.purpleHaze,
                label: 'Forecast',
                isDashed: true,
              ),
              if (_showConfidenceInterval) ...[
                const SizedBox(width: AppDimensions.spacing24),
                _LegendItem(
                  color: AppColors.purpleHaze.withValues(alpha: 0.3),
                  label: '95% CI',
                  isArea: true,
                ),
              ],
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildMetricsSection() {
    return Padding(
      padding: const EdgeInsets.all(AppDimensions.spacing16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Performance Metrics', style: AppTextStyles.titleSmall),
          const SizedBox(height: AppDimensions.spacing12),
          Row(
            children: [
              Expanded(
                child: _MetricCard(
                  title: 'Accuracy',
                  value: '${widget.forecast.accuracy?.toStringAsFixed(1) ?? '--'}%',
                  icon: Icons.check_circle_outline,
                  color: AppColors.success,
                ),
              ),
              const SizedBox(width: AppDimensions.spacing12),
              Expanded(
                child: _MetricCard(
                  title: 'MAE',
                  value: '3.2',
                  icon: Icons.trending_flat,
                  color: AppColors.info,
                ),
              ),
            ],
          ),
          const SizedBox(height: AppDimensions.spacing12),
          Row(
            children: [
              Expanded(
                child: _MetricCard(
                  title: 'RMSE',
                  value: '4.8',
                  icon: Icons.show_chart,
                  color: AppColors.warning,
                ),
              ),
              const SizedBox(width: AppDimensions.spacing12),
              Expanded(
                child: _MetricCard(
                  title: 'MAPE',
                  value: '5.5%',
                  icon: Icons.percent,
                  color: AppColors.purpleHaze,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildInsightsSection() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: AppDimensions.spacing16),
      padding: const EdgeInsets.all(AppDimensions.spacing16),
      decoration: BoxDecoration(
        color: AppColors.primary10,
        borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(
                Icons.lightbulb_outline,
                color: AppColors.primary,
                size: 20,
              ),
              const SizedBox(width: AppDimensions.spacing8),
              Text(
                'AI Insights',
                style: AppTextStyles.labelLarge.copyWith(
                  color: AppColors.primary,
                ),
              ),
            ],
          ),
          const SizedBox(height: AppDimensions.spacing12),
          Text(
            'Demand is expected to increase by 21% over the forecast period. '
            'Consider increasing inventory levels to meet projected demand.',
            style: AppTextStyles.bodyMedium.copyWith(
              color: AppColors.textPrimary,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDetailsSection() {
    return Padding(
      padding: const EdgeInsets.all(AppDimensions.spacing16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Details', style: AppTextStyles.titleSmall),
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
                _DetailRow(label: 'Product ID', value: widget.forecast.productId),
                const Divider(height: 24),
                _DetailRow(
                  label: 'Created',
                  value: DateFormat('MMM d, yyyy HH:mm').format(widget.forecast.createdAt),
                ),
                const Divider(height: 24),
                _DetailRow(label: 'Horizon', value: '${widget.forecast.horizon} days'),
                const Divider(height: 24),
                _DetailRow(label: 'Model', value: 'ARIMA + XGBoost'),
              ],
            ),
          ),
        ],
      ),
    );
  }

  IconData _getStatusIcon() {
    switch (widget.forecast.status) {
      case ForecastStatus.active:
        return Icons.play_circle_outline;
      case ForecastStatus.completed:
        return Icons.check_circle_outline;
      case ForecastStatus.draft:
        return Icons.edit_outlined;
    }
  }

  String _getStatusDescription() {
    switch (widget.forecast.status) {
      case ForecastStatus.active:
        return 'Forecast is currently running';
      case ForecastStatus.completed:
        return 'Forecast completed successfully';
      case ForecastStatus.draft:
        return 'Draft - not yet submitted';
    }
  }

  void _shareForecast() {
    // TODO: Implement share
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Share feature coming soon')),
    );
  }

  void _handleMenuAction(String action) {
    switch (action) {
      case 'export_pdf':
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Exporting PDF...')),
        );
        break;
      case 'export_excel':
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Exporting Excel...')),
        );
        break;
      case 'delete':
        _showDeleteDialog();
        break;
    }
  }

  void _showDeleteDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Forecast'),
        content: const Text('Are you sure you want to delete this forecast?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              Navigator.pop(context);
            },
            child: const Text('Delete', style: TextStyle(color: AppColors.error)),
          ),
        ],
      ),
    );
  }
}

class _LegendItem extends StatelessWidget {
  final Color color;
  final String label;
  final bool isDashed;
  final bool isArea;

  const _LegendItem({
    required this.color,
    required this.label,
    this.isDashed = false,
    this.isArea = false,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        if (isArea)
          Container(
            width: 16,
            height: 12,
            decoration: BoxDecoration(
              color: color,
              borderRadius: BorderRadius.circular(2),
            ),
          )
        else
          Container(
            width: 16,
            height: 3,
            decoration: BoxDecoration(
              color: isDashed ? null : color,
              borderRadius: BorderRadius.circular(2),
            ),
            child: isDashed
                ? Row(
                    children: [
                      Container(width: 6, height: 3, color: color),
                      const SizedBox(width: 4),
                      Container(width: 6, height: 3, color: color),
                    ],
                  )
                : null,
          ),
        const SizedBox(width: 6),
        Text(label, style: AppTextStyles.caption),
      ],
    );
  }
}

class _MetricCard extends StatelessWidget {
  final String title;
  final String value;
  final IconData icon;
  final Color color;

  const _MetricCard({
    required this.title,
    required this.value,
    required this.icon,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(AppDimensions.spacing16),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
        border: Border.all(color: AppColors.border),
      ),
      child: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(AppDimensions.radiusSm),
            ),
            child: Icon(icon, color: color, size: 20),
          ),
          const SizedBox(width: AppDimensions.spacing12),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(title, style: AppTextStyles.caption),
              Text(
                value,
                style: AppTextStyles.titleSmall.copyWith(color: color),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _DetailRow extends StatelessWidget {
  final String label;
  final String value;

  const _DetailRow({
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: AppTextStyles.bodySmall),
        Text(value, style: AppTextStyles.labelMedium),
      ],
    );
  }
}
