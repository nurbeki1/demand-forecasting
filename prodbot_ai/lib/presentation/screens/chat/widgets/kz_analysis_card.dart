import 'package:flutter/material.dart';

import '../../../../core/theme/theme.dart';

/// Mobile port of `frontend-admin/src/components/kz/KZAnalysisCard.jsx`.
/// Skips the SVG Kazakhstan map (heavy graphic) but keeps the
/// price summary, warnings, best/avoid cities, markup slider,
/// city table, investment, competitor, and risk sections.
class KZAnalysisCard extends StatefulWidget {
  final Map<String, dynamic> data;
  final Future<void> Function(int markup)? onMarkupChange;

  const KZAnalysisCard({
    super.key,
    required this.data,
    this.onMarkupChange,
  });

  @override
  State<KZAnalysisCard> createState() => _KZAnalysisCardState();
}

class _KZAnalysisCardState extends State<KZAnalysisCard> {
  late int _markup;
  bool _recalculating = false;

  @override
  void initState() {
    super.initState();
    final raw = widget.data['markup_percent'];
    _markup = raw is num ? raw.round() : 25;
  }

  @override
  void didUpdateWidget(covariant KZAnalysisCard oldWidget) {
    super.didUpdateWidget(oldWidget);
    final raw = widget.data['markup_percent'];
    if (raw is num) _markup = raw.round();
  }

  @override
  Widget build(BuildContext context) {
    final d = widget.data;
    final isProfitable = d['is_profitable'] == true;
    final warnings = (d['warnings'] as List?)?.cast<dynamic>() ?? const [];
    final bestCities =
        (d['best_cities'] as List?)?.map((e) => e.toString()).toList() ??
            const [];
    final avoidCities =
        (d['avoid_cities'] as List?)?.map((e) => e.toString()).toList() ??
            const [];
    final cities = (d['cities'] as List?) ?? const [];
    final investment = d['investment'] as Map?;
    final competitor = d['competitor_analysis'] as Map?;

    final statusColor = isProfitable
        ? AppColors.success
        : warnings.isNotEmpty
            ? AppColors.warning
            : AppColors.error;
    final statusIcon = isProfitable
        ? Icons.check_circle_rounded
        : warnings.isNotEmpty
            ? Icons.warning_amber_rounded
            : Icons.cancel_rounded;

    return Container(
      margin: const EdgeInsets.only(top: 12),
      decoration: BoxDecoration(
        color: AppColors.surfaceVariant,
        borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
        border: Border.all(
          color: statusColor.withValues(alpha: 0.30),
          width: 1.2,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(14, 14, 14, 10),
            child: Row(
              children: [
                Container(
                  width: 36,
                  height: 36,
                  decoration: BoxDecoration(
                    color: statusColor.withValues(alpha: 0.16),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Icon(statusIcon, color: statusColor, size: 20),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        (d['product_name'] as String?) ?? 'Анализ рынка КЗ',
                        style: AppTextStyles.titleSmall.copyWith(
                          fontWeight: FontWeight.w700,
                          color: AppColors.textPrimary,
                        ),
                      ),
                      Text(
                        'Анализ рынка Казахстана',
                        style: AppTextStyles.labelSmall.copyWith(
                          color: AppColors.textSecondary,
                        ),
                      ),
                    ],
                  ),
                ),
                if (isProfitable)
                  Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: AppColors.success.withValues(alpha: 0.14),
                      borderRadius: BorderRadius.circular(999),
                    ),
                    child: Text(
                      'Выгодно',
                      style: AppTextStyles.labelSmall.copyWith(
                        color: AppColors.success,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                  ),
              ],
            ),
          ),
          _divider(),
          _priceSummary(d),
          if (warnings.isNotEmpty) ...[
            _divider(),
            _warningsBlock(warnings),
          ],
          if (bestCities.isNotEmpty || avoidCities.isNotEmpty) ...[
            _divider(),
            _citiesQuick(bestCities, avoidCities),
          ],
          _divider(),
          _markupSlider(),
          if (cities.isNotEmpty) ...[
            _divider(),
            _Collapsible(
              title: '📊 Анализ по городам',
              defaultOpen: false,
              child: _citiesTable(cities),
            ),
          ],
          if (investment != null) ...[
            _divider(),
            _Collapsible(
              title: '💰 Инвестиции',
              defaultOpen: true,
              child: _investmentGrid(
                  investment.cast<String, dynamic>()),
            ),
          ],
          if (competitor != null) ...[
            _divider(),
            _Collapsible(
              title: '🔍 Конкуренты',
              defaultOpen: false,
              child:
                  _competitorBlock(competitor.cast<String, dynamic>()),
            ),
          ],
          _divider(),
          _Collapsible(
            title: '⚡ Риски и рекомендации',
            defaultOpen: false,
            child: _risksBlock(competitor, bestCities),
          ),
        ],
      ),
    );
  }

  Widget _divider() => Divider(
        height: 1,
        thickness: 1,
        color: AppColors.borderSubtle,
      );

  Widget _priceSummary(Map<String, dynamic> d) {
    final usd = d['product_cost_usd'];
    final kzt = d['product_cost_kzt'];
    final rate = d['currency_rate'];
    final profit = d['total_potential_profit_kzt'];
    return Padding(
      padding: const EdgeInsets.fromLTRB(14, 12, 14, 14),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            child: _priceCell(
              label: 'Оптовая цена',
              primary: _formatCurrency(usd, 'USD'),
              secondary: _formatCurrency(kzt, 'KZT'),
            ),
          ),
          _vDivider(),
          Expanded(
            child: _priceCell(
              label: 'Курс USD/KZT',
              primary: rate is num ? rate.toStringAsFixed(2) : '—',
            ),
          ),
          _vDivider(),
          Expanded(
            child: _priceCell(
              label: 'Прибыль/мес',
              primary: _formatCurrency(profit, 'KZT'),
              highlight: true,
            ),
          ),
        ],
      ),
    );
  }

  Widget _vDivider() => Container(
        width: 1,
        height: 36,
        color: AppColors.borderSubtle,
        margin: const EdgeInsets.symmetric(horizontal: 8),
      );

  Widget _priceCell({
    required String label,
    required String primary,
    String? secondary,
    bool highlight = false,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: AppTextStyles.labelSmall.copyWith(
            color: AppColors.textTertiary,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          primary,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: AppTextStyles.titleSmall.copyWith(
            color: highlight ? AppColors.success : AppColors.textPrimary,
            fontWeight: FontWeight.w700,
          ),
        ),
        if (secondary != null) ...[
          const SizedBox(height: 2),
          Text(
            secondary,
            style: AppTextStyles.labelSmall.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
        ],
      ],
    );
  }

  Widget _warningsBlock(List<dynamic> warnings) {
    return Padding(
      padding: const EdgeInsets.all(14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: warnings
            .map(
              (w) => Padding(
                padding: const EdgeInsets.only(bottom: 6),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(Icons.warning_amber_rounded,
                        size: 14, color: AppColors.warning),
                    const SizedBox(width: 6),
                    Expanded(
                      child: Text(
                        w.toString(),
                        style: AppTextStyles.bodySmall.copyWith(
                          color: AppColors.textPrimary,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            )
            .toList(),
      ),
    );
  }

  Widget _citiesQuick(List<String> best, List<String> avoid) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(14, 12, 14, 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (best.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(bottom: 6),
              child: RichText(
                text: TextSpan(
                  style: AppTextStyles.bodySmall
                      .copyWith(color: AppColors.textPrimary),
                  children: [
                    TextSpan(
                      text: '🏆 Лучшие: ',
                      style: AppTextStyles.labelMedium.copyWith(
                        color: AppColors.success,
                        fontWeight: FontWeight.w700,
                      ),
                    ),
                    TextSpan(text: best.join(', ')),
                  ],
                ),
              ),
            ),
          if (avoid.isNotEmpty)
            RichText(
              text: TextSpan(
                style: AppTextStyles.bodySmall
                    .copyWith(color: AppColors.textPrimary),
                children: [
                  TextSpan(
                    text: '⛔ Избегать: ',
                    style: AppTextStyles.labelMedium.copyWith(
                      color: AppColors.error,
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  TextSpan(text: avoid.join(', ')),
                ],
              ),
            ),
        ],
      ),
    );
  }

  Widget _markupSlider() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(14, 12, 14, 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(
                'Наценка',
                style: AppTextStyles.labelMedium.copyWith(
                  fontWeight: FontWeight.w600,
                  color: AppColors.textPrimary,
                ),
              ),
              const Spacer(),
              Text(
                '$_markup%',
                style: AppTextStyles.titleSmall.copyWith(
                  color: AppColors.primary,
                  fontWeight: FontWeight.w700,
                ),
              ),
              if (_recalculating) ...[
                const SizedBox(width: 8),
                const SizedBox(
                  width: 14,
                  height: 14,
                  child: CircularProgressIndicator(strokeWidth: 1.6),
                ),
              ],
            ],
          ),
          SliderTheme(
            data: SliderTheme.of(context).copyWith(
              activeTrackColor: AppColors.primary,
              inactiveTrackColor: AppColors.borderSubtle,
              thumbColor: AppColors.primary,
              overlayColor: AppColors.primary.withValues(alpha: 0.20),
              trackHeight: 3,
              thumbShape: const RoundSliderThumbShape(enabledThumbRadius: 8),
            ),
            child: Slider(
              min: 10,
              max: 100,
              divisions: 18,
              value: _markup.toDouble().clamp(10, 100),
              label: '$_markup%',
              onChanged: _recalculating
                  ? null
                  : (v) => setState(() => _markup = v.round()),
              onChangeEnd: (v) async {
                final cb = widget.onMarkupChange;
                if (cb == null) return;
                setState(() => _recalculating = true);
                try {
                  await cb(_markup);
                } finally {
                  if (mounted) setState(() => _recalculating = false);
                }
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _citiesTable(List<dynamic> cities) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(14, 0, 14, 14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          for (final raw in cities.take(10))
            _cityRow((raw as Map).cast<String, dynamic>()),
        ],
      ),
    );
  }

  Widget _cityRow(Map<String, dynamic> c) {
    final name = c['city'] ?? c['name'] ?? '—';
    final price = c['recommended_price_kzt'] ?? c['avg_price'];
    final demand = c['demand_score'] ?? c['score'];
    return Container(
      margin: const EdgeInsets.only(bottom: 6),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: AppColors.borderSubtle),
      ),
      child: Row(
        children: [
          Expanded(
            child: Text(
              name.toString(),
              style: AppTextStyles.bodySmall.copyWith(
                fontWeight: FontWeight.w600,
                color: AppColors.textPrimary,
              ),
            ),
          ),
          if (demand != null)
            Padding(
              padding: const EdgeInsets.only(right: 10),
              child: Text(
                'Спрос: ${demand is num ? demand.toStringAsFixed(0) : demand}',
                style: AppTextStyles.labelSmall.copyWith(
                  color: AppColors.textSecondary,
                ),
              ),
            ),
          Text(
            _formatCurrency(price, 'KZT'),
            style: AppTextStyles.labelMedium.copyWith(
              color: AppColors.primary,
              fontWeight: FontWeight.w700,
            ),
          ),
        ],
      ),
    );
  }

  Widget _investmentGrid(Map<String, dynamic> inv) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(14, 0, 14, 14),
      child: Wrap(
        spacing: 8,
        runSpacing: 8,
        children: [
          if (inv['initial_investment_kzt'] != null)
            _investItem('Инвестиции',
                _formatCurrency(inv['initial_investment_kzt'], 'KZT')),
          if (inv['monthly_operating_costs'] != null)
            _investItem('Расходы/мес',
                _formatCurrency(inv['monthly_operating_costs'], 'KZT')),
          if (inv['break_even_months'] != null)
            _investItem('Окупаемость',
                '${inv['break_even_months']} мес.',
                highlight: true),
          if (inv['roi_percent'] != null)
            _investItem(
              'ROI',
              '${(inv['roi_percent'] as num).toStringAsFixed(1)}%',
              success: true,
            ),
        ],
      ),
    );
  }

  Widget _investItem(String label, String value,
      {bool highlight = false, bool success = false}) {
    return Container(
      width: 150,
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: AppColors.borderSubtle),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: AppTextStyles.labelSmall.copyWith(
              color: AppColors.textTertiary,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: AppTextStyles.titleSmall.copyWith(
              color: success
                  ? AppColors.success
                  : highlight
                      ? AppColors.primary
                      : AppColors.textPrimary,
              fontWeight: FontWeight.w700,
            ),
          ),
        ],
      ),
    );
  }

  Widget _competitorBlock(Map<String, dynamic> c) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(14, 0, 14, 14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (c['avg_market_price'] != null)
            _kvLine('Средняя цена',
                _formatCurrency(c['avg_market_price'], 'KZT')),
          if (c['price_range'] is Map)
            _kvLine(
              'Диапазон',
              '${_formatCurrency((c['price_range'] as Map)['min'], 'KZT')}'
                  ' — ${_formatCurrency((c['price_range'] as Map)['max'], 'KZT')}',
            ),
          if (c['competition_level'] != null)
            _kvLine(
              'Конкуренция',
              c['competition_level'] == 'high'
                  ? 'Высокая'
                  : c['competition_level'] == 'medium'
                      ? 'Средняя'
                      : 'Низкая',
              valueColor: c['competition_level'] == 'high'
                  ? AppColors.error
                  : c['competition_level'] == 'medium'
                      ? AppColors.warning
                      : AppColors.success,
            ),
          if (c['main_competitors'] is List &&
              (c['main_competitors'] as List).isNotEmpty) ...[
            const SizedBox(height: 6),
            Text(
              'Основные конкуренты:',
              style: AppTextStyles.labelMedium.copyWith(
                color: AppColors.textSecondary,
                fontWeight: FontWeight.w600,
              ),
            ),
            const SizedBox(height: 4),
            ...((c['main_competitors'] as List).map(
              (e) => Padding(
                padding: const EdgeInsets.only(left: 4, top: 2),
                child: Text(
                  '• $e',
                  style: AppTextStyles.bodySmall.copyWith(
                    color: AppColors.textPrimary,
                  ),
                ),
              ),
            )),
          ],
        ],
      ),
    );
  }

  Widget _kvLine(String k, String v, {Color? valueColor}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 3),
      child: Row(
        children: [
          Expanded(
            child: Text(
              k,
              style: AppTextStyles.bodySmall.copyWith(
                color: AppColors.textSecondary,
              ),
            ),
          ),
          Text(
            v,
            style: AppTextStyles.labelMedium.copyWith(
              color: valueColor ?? AppColors.textPrimary,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  Widget _risksBlock(Map? competitor, List<String> bestCities) {
    final highCompetition = competitor?['competition_level'] == 'high';
    return Padding(
      padding: const EdgeInsets.fromLTRB(14, 0, 14, 14),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Основные риски',
            style: AppTextStyles.labelMedium.copyWith(
              fontWeight: FontWeight.w700,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(height: 6),
          ..._bullets([
            'Колебания курса валют',
            'Таможенные сборы и логистика',
            'Сезонность спроса',
            if (highCompetition) 'Высокая конкуренция на рынке',
          ]),
          const SizedBox(height: 10),
          Text(
            'Рекомендации',
            style: AppTextStyles.labelMedium.copyWith(
              fontWeight: FontWeight.w700,
              color: AppColors.textPrimary,
            ),
          ),
          const SizedBox(height: 6),
          ..._bullets([
            'Начните с городов из списка "Лучшие"',
            'Отслеживайте курс валют ежедневно',
            'Учитывайте сезонные колебания спроса',
            if (bestCities.isNotEmpty)
              'Фокус на: ${bestCities.take(2).join(", ")}',
          ]),
        ],
      ),
    );
  }

  List<Widget> _bullets(List<String> items) {
    return items
        .map(
          (s) => Padding(
            padding: const EdgeInsets.symmetric(vertical: 2),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Padding(
                  padding: const EdgeInsets.only(top: 7, right: 8),
                  child: Container(
                    width: 4,
                    height: 4,
                    decoration: const BoxDecoration(
                      color: AppColors.primary,
                      shape: BoxShape.circle,
                    ),
                  ),
                ),
                Expanded(
                  child: Text(
                    s,
                    style: AppTextStyles.bodySmall.copyWith(
                      color: AppColors.textPrimary,
                    ),
                  ),
                ),
              ],
            ),
          ),
        )
        .toList();
  }
}

class _Collapsible extends StatefulWidget {
  final String title;
  final bool defaultOpen;
  final Widget child;
  const _Collapsible({
    required this.title,
    required this.child,
    this.defaultOpen = false,
  });
  @override
  State<_Collapsible> createState() => _CollapsibleState();
}

class _CollapsibleState extends State<_Collapsible> {
  late bool _open = widget.defaultOpen;

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        InkWell(
          onTap: () => setState(() => _open = !_open),
          child: Padding(
            padding: const EdgeInsets.fromLTRB(14, 12, 14, 12),
            child: Row(
              children: [
                Expanded(
                  child: Text(
                    widget.title,
                    style: AppTextStyles.titleSmall.copyWith(
                      fontWeight: FontWeight.w600,
                      color: AppColors.textPrimary,
                    ),
                  ),
                ),
                Icon(
                  _open
                      ? Icons.remove_rounded
                      : Icons.add_rounded,
                  size: 18,
                  color: AppColors.textSecondary,
                ),
              ],
            ),
          ),
        ),
        if (_open) widget.child,
      ],
    );
  }
}

String _formatCurrency(dynamic value, String currency) {
  if (value == null) return '—';
  if (value is! num) return value.toString();
  final rounded = value.round();
  final s = rounded.toString();
  final buf = StringBuffer();
  for (int i = 0; i < s.length; i++) {
    buf.write(s[i]);
    final left = s.length - i - 1;
    if (left > 0 && left % 3 == 0) buf.write(' ');
  }
  return currency == 'KZT' ? '${buf.toString()} ₸' : '\$${buf.toString()}';
}
