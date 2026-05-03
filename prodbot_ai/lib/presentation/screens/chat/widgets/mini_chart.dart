import 'package:fl_chart/fl_chart.dart';
import 'package:flutter/material.dart';

import '../../../../core/theme/theme.dart';
import '../../../../data/models/chat_models.dart';
import '../../../../l10n/app_localizations.dart';

/// Mirrors `MiniChart` from `frontend-admin/src/pages/ChatPage.jsx`:
/// shows last 7 history points + first 7 forecast points joined visually.
class MiniChart extends StatelessWidget {
  final ChatData data;
  const MiniChart({super.key, required this.data});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final history = data.history.length > 7
        ? data.history.sublist(data.history.length - 7)
        : data.history;
    final forecast = data.forecast.length > 7
        ? data.forecast.sublist(0, 7)
        : data.forecast;

    if (history.isEmpty && forecast.isEmpty) {
      return const SizedBox.shrink();
    }

    final spotsHistory = <FlSpot>[];
    final spotsForecast = <FlSpot>[];
    final labels = <String>[];

    for (var i = 0; i < history.length; i++) {
      spotsHistory.add(FlSpot(i.toDouble(), history[i].demand));
      labels.add(_shortDate(history[i].date));
    }
    if (history.isNotEmpty && forecast.isNotEmpty) {
      // visual bridge — duplicate last history point as first forecast point.
      spotsForecast.add(FlSpot(
        (history.length - 1).toDouble(),
        history.last.demand,
      ));
    }
    for (var i = 0; i < forecast.length; i++) {
      final x = (history.length + i).toDouble();
      spotsForecast.add(FlSpot(x, forecast[i].predictedDemand));
      labels.add(_shortDate(forecast[i].date));
    }

    final avgH = history.isEmpty
        ? 0.0
        : history.map((e) => e.demand).reduce((a, b) => a + b) /
            history.length;
    final avgF = forecast.isEmpty
        ? avgH
        : forecast.map((e) => e.predictedDemand).reduce((a, b) => a + b) /
            forecast.length;
    final delta = avgH > 0 ? ((avgF - avgH) / avgH * 100) : 0.0;
    final trendUp = avgF >= avgH;

    final maxY = ([
      ...history.map((e) => e.demand),
      ...forecast.map((e) => e.predictedDemand),
      1.0,
    ]).reduce((a, b) => a > b ? a : b);

    return Container(
      margin: const EdgeInsets.only(top: 12),
      padding: const EdgeInsets.fromLTRB(14, 14, 14, 12),
      decoration: BoxDecoration(
        color: AppColors.surfaceVariant,
        borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
        border: Border.all(color: AppColors.borderSubtle),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            children: [
              Icon(Icons.show_chart_rounded,
                  size: 16, color: AppColors.primary),
              const SizedBox(width: 6),
              Text(
                l10n.miniChartTitle,
                style: AppTextStyles.labelMedium.copyWith(
                  color: AppColors.textSecondary,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(
                    horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: (trendUp ? AppColors.success : AppColors.error)
                      .withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(999),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      trendUp
                          ? Icons.arrow_upward_rounded
                          : Icons.arrow_downward_rounded,
                      size: 12,
                      color: trendUp ? AppColors.success : AppColors.error,
                    ),
                    const SizedBox(width: 2),
                    Text(
                      '${delta.abs().toStringAsFixed(1)}%',
                      style: AppTextStyles.labelSmall.copyWith(
                        color:
                            trendUp ? AppColors.success : AppColors.error,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          SizedBox(
            height: 160,
            child: LineChart(
              LineChartData(
                gridData: FlGridData(
                  show: true,
                  drawVerticalLine: false,
                  horizontalInterval: maxY / 4,
                  getDrawingHorizontalLine: (_) => FlLine(
                    color: AppColors.borderSubtle,
                    strokeWidth: 1,
                  ),
                ),
                borderData: FlBorderData(show: false),
                titlesData: FlTitlesData(
                  topTitles: const AxisTitles(
                      sideTitles: SideTitles(showTitles: false)),
                  rightTitles: const AxisTitles(
                      sideTitles: SideTitles(showTitles: false)),
                  leftTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      reservedSize: 36,
                      getTitlesWidget: (v, _) => Text(
                        v.toStringAsFixed(0),
                        style: AppTextStyles.labelSmall.copyWith(
                          color: AppColors.textTertiary,
                          fontSize: 10,
                        ),
                      ),
                    ),
                  ),
                  bottomTitles: AxisTitles(
                    sideTitles: SideTitles(
                      showTitles: true,
                      interval: 1,
                      getTitlesWidget: (v, _) {
                        final i = v.round();
                        if (i < 0 || i >= labels.length) {
                          return const SizedBox.shrink();
                        }
                        if (i % 2 != 0) return const SizedBox.shrink();
                        return Padding(
                          padding: const EdgeInsets.only(top: 4),
                          child: Text(
                            labels[i],
                            style: AppTextStyles.labelSmall.copyWith(
                              color: AppColors.textTertiary,
                              fontSize: 10,
                            ),
                          ),
                        );
                      },
                    ),
                  ),
                ),
                lineTouchData: LineTouchData(
                  enabled: true,
                  touchTooltipData: LineTouchTooltipData(
                    getTooltipColor: (_) => AppColors.cardBackground,
                    tooltipBorder: const BorderSide(color: AppColors.border),
                    getTooltipItems: (spots) => spots
                        .map(
                          (s) => LineTooltipItem(
                            s.y.toStringAsFixed(0),
                            AppTextStyles.labelSmall.copyWith(
                              color: AppColors.textPrimary,
                            ),
                          ),
                        )
                        .toList(),
                  ),
                ),
                lineBarsData: [
                  if (spotsHistory.isNotEmpty)
                    LineChartBarData(
                      spots: spotsHistory,
                      isCurved: true,
                      color: AppColors.primary,
                      barWidth: 2.5,
                      dotData: FlDotData(
                        show: true,
                        getDotPainter: (spot, _, __, ___) =>
                            FlDotCirclePainter(
                          radius: 3,
                          color: AppColors.primary,
                          strokeColor: AppColors.background,
                          strokeWidth: 1.5,
                        ),
                      ),
                      belowBarData: BarAreaData(
                        show: true,
                        color: AppColors.primary.withValues(alpha: 0.10),
                      ),
                    ),
                  if (spotsForecast.isNotEmpty)
                    LineChartBarData(
                      spots: spotsForecast,
                      isCurved: true,
                      color: AppColors.secondary,
                      barWidth: 2.5,
                      dashArray: const [6, 4],
                      dotData: FlDotData(
                        show: true,
                        getDotPainter: (spot, _, __, ___) =>
                            FlDotCirclePainter(
                          radius: 3,
                          color: AppColors.secondary,
                          strokeColor: AppColors.background,
                          strokeWidth: 1.5,
                        ),
                      ),
                    ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 8),
          Wrap(
            alignment: WrapAlignment.center,
            spacing: 16,
            children: [
              _LegendDot(color: AppColors.primary, label: l10n.miniChartHistory),
              _LegendDot(
                color: AppColors.secondary,
                label: l10n.miniChartForecast,
                dashed: true,
              ),
            ],
          ),
        ],
      ),
    );
  }

  String _shortDate(String iso) {
    final parts = iso.split('-');
    if (parts.length >= 3) return '${parts[1]}/${parts[2]}';
    if (parts.length == 2) return '${parts[0]}/${parts[1]}';
    return iso;
  }
}

class _LegendDot extends StatelessWidget {
  final Color color;
  final String label;
  final bool dashed;
  const _LegendDot({required this.color, required this.label, this.dashed = false});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 14,
          height: 2.5,
          decoration: BoxDecoration(
            color: dashed ? null : color,
            borderRadius: BorderRadius.circular(2),
            border: dashed ? Border.all(color: color, width: 1) : null,
          ),
        ),
        const SizedBox(width: 6),
        Text(
          label,
          style: AppTextStyles.labelSmall.copyWith(
            color: AppColors.textSecondary,
          ),
        ),
      ],
    );
  }
}
