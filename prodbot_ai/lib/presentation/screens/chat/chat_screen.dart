import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../../core/theme/theme.dart';
import '../../../services/chat_service.dart';
import '../../../data/models/chat_models.dart';
import '../../widgets/common/widgets.dart';
import 'widgets/chat_message.dart';

// ─────────────────────────────────────────────────────────────
//  Model definitions for selector
// ─────────────────────────────────────────────────────────────

class _ModelOption {
  final String id;
  final String label;
  final String shortLabel;
  final String description;
  final Color color;

  const _ModelOption({
    required this.id,
    required this.label,
    required this.shortLabel,
    required this.description,
    required this.color,
  });
}

const _kModels = [
  _ModelOption(
    id: 'random_forest',
    label: 'Random Forest',
    shortLabel: 'RF',
    description: 'Тұрақты, жоғары дәлдік',
    color: Color(0xFF6366F1),
  ),
  _ModelOption(
    id: 'lightgbm',
    label: 'LightGBM',
    shortLabel: 'LGBM',
    description: 'Жылдам, градиент бустинг',
    color: Color(0xFF22C55E),
  ),
  _ModelOption(
    id: 'xgboost',
    label: 'XGBoost',
    shortLabel: 'XGB',
    description: 'Күшті, терең талдау',
    color: Color(0xFFF59E0B),
  ),
];

// ─────────────────────────────────────────────────────────────
//  Model Selector Widget
// ─────────────────────────────────────────────────────────────

class _ModelSelector extends StatefulWidget {
  final String selectedId;
  final ValueChanged<String> onChanged;

  const _ModelSelector({
    required this.selectedId,
    required this.onChanged,
  });

  @override
  State<_ModelSelector> createState() => _ModelSelectorState();
}

class _ModelSelectorState extends State<_ModelSelector> {
  bool _open = false;
  final LayerLink _layerLink = LayerLink();
  OverlayEntry? _overlay;

  _ModelOption get _current => _kModels.firstWhere(
        (m) => m.id == widget.selectedId,
        orElse: () => _kModels.first,
      );

  void _toggleDropdown() {
    if (_open) {
      _closeDropdown();
    } else {
      _openDropdown();
    }
  }

  void _openDropdown() {
    final renderBox = context.findRenderObject() as RenderBox;
    final size = renderBox.size;

    _overlay = OverlayEntry(
      builder: (context) => Stack(
        children: [
          Positioned.fill(
            child: GestureDetector(
              onTap: _closeDropdown,
              child: Container(color: Colors.transparent),
            ),
          ),
          CompositedTransformFollower(
            link: _layerLink,
            showWhenUnlinked: false,
            offset: Offset(0, -(size.height + 8 + 3 * 72.0)),
            child: Material(
              color: Colors.transparent,
              child: Container(
                width: 240,
                decoration: BoxDecoration(
                  color: AppColors.cardBackground,
                  borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
                  border: Border.all(color: AppColors.border, width: 1),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withValues(alpha: 0.5),
                      blurRadius: 24,
                      offset: const Offset(0, 12),
                    ),
                  ],
                ),
                padding: const EdgeInsets.all(4),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: _kModels.map((model) {
                    final isSelected = model.id == widget.selectedId;
                    return InkWell(
                      onTap: () {
                        widget.onChanged(model.id);
                        _closeDropdown();
                      },
                      borderRadius: BorderRadius.circular(8),
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 10,
                          vertical: 9,
                        ),
                        decoration: BoxDecoration(
                          color: isSelected
                              ? AppColors.primary10
                              : Colors.transparent,
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Row(
                          children: [
                            Container(
                              width: 30,
                              height: 30,
                              decoration: BoxDecoration(
                                color: model.color.withValues(alpha: 0.15),
                                borderRadius: BorderRadius.circular(8),
                                border: Border.all(
                                  color: model.color.withValues(alpha: 0.35),
                                ),
                              ),
                              child: Center(
                                child: Text(
                                  model.shortLabel,
                                  style: AppTextStyles.caption.copyWith(
                                    fontSize: 9,
                                    fontWeight: FontWeight.w800,
                                    color: model.color,
                                  ),
                                ),
                              ),
                            ),
                            const SizedBox(width: 10),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    model.label,
                                    style: AppTextStyles.labelMedium.copyWith(
                                      color: AppColors.textPrimary,
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                  const SizedBox(height: 2),
                                  Text(
                                    model.description,
                                    style: AppTextStyles.caption.copyWith(
                                      color: AppColors.textSecondary,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            if (isSelected)
                              const Icon(
                                Icons.check_circle_rounded,
                                size: 16,
                                color: AppColors.primary,
                              ),
                          ],
                        ),
                      ),
                    );
                  }).toList(),
                ),
              ),
            ),
          ),
        ],
      ),
    );

    Overlay.of(context).insert(_overlay!);
    setState(() => _open = true);
  }

  void _closeDropdown() {
    _overlay?.remove();
    _overlay = null;
    if (mounted) setState(() => _open = false);
  }

  @override
  void dispose() {
    _overlay?.remove();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final model = _current;
    return CompositedTransformTarget(
      link: _layerLink,
      child: GestureDetector(
        onTap: _toggleDropdown,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
          decoration: BoxDecoration(
            color: model.color.withValues(alpha: 0.14),
            borderRadius: BorderRadius.circular(999),
            border: Border.all(
              color: model.color.withValues(alpha: 0.32),
            ),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                model.shortLabel,
                style: AppTextStyles.caption.copyWith(
                  fontSize: 11,
                  fontWeight: FontWeight.w800,
                  color: model.color,
                ),
              ),
              const SizedBox(width: 4),
              AnimatedRotation(
                turns: _open ? 0.5 : 0.0,
                duration: const Duration(milliseconds: 200),
                child: Icon(
                  Icons.keyboard_arrow_down_rounded,
                  size: 16,
                  color: model.color,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────
//  Chat Screen
// ─────────────────────────────────────────────────────────────

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final ChatService _chatService = ChatService();

  bool _isLoading = false;
  bool _isLoadingHistory = true;
  List<ChatMessageData> _messages = [];
  List<FlSpot> _historySpots = [];
  List<FlSpot> _forecastSpots = [];
  List<String> _currentSuggestions = [];
  String _selectedModel = 'random_forest';

  @override
  void initState() {
    super.initState();
    _loadHistory();
  }

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  Future<void> _loadHistory() async {
    try {
      final history = await _chatService.getHistory(limit: 20);

      if (history.isEmpty) {
        _addBotMessage(
          'Сәлем! Мен сізге сұраныс болжамын талдауға көмектесе аламын. Өнімдер, трендтер немесе салыстырмалар туралы сұраңыз.',
          showSuggestions: true,
          suggestions: [
            'P0001 болжамы',
            'Үздік 5 өнім',
            'Шығыс пен батысты салыстыру',
            'Қандай категориялар бар?',
          ],
        );
      } else {
        setState(() {
          for (final msg in history) {
            _messages.add(ChatMessageData(
              text: msg.content,
              isUser: msg.isUser,
              timestamp: DateTime.tryParse(msg.timestamp),
              intent: msg.intent,
              images: msg.images,
            ));

            if (msg.isAssistant && msg.data != null) {
              _updateChartData(msg.data!);
            }
          }
        });
      }
    } catch (e) {
      _addBotMessage(
        'Сәлем! Мен сізге сұраныс болжамын талдауға көмектесе аламын.',
        showSuggestions: true,
      );
    } finally {
      setState(() => _isLoadingHistory = false);
      _scrollToBottom();
    }
  }

  void _addBotMessage(
    String text, {
    bool showSuggestions = false,
    List<String>? suggestions,
    String? intent,
    List<ProductImage>? images,
  }) {
    setState(() {
      _messages.add(ChatMessageData(
        text: text,
        isUser: false,
        showSuggestions: showSuggestions,
        suggestions: suggestions,
        intent: intent,
        images: images,
      ));
      if (suggestions != null) {
        _currentSuggestions = suggestions;
      }
    });
    _scrollToBottom();
  }

  void _addUserMessage(String text) {
    setState(() {
      _messages.add(ChatMessageData(text: text, isUser: true));
    });
    _scrollToBottom();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  void _updateChartData(ChatData data) {
    setState(() {
      _historySpots = List.generate(
        data.history.length,
        (i) => FlSpot(i.toDouble(), data.history[i].demand),
      );

      _forecastSpots = List.generate(
        data.forecast.length,
        (i) => FlSpot(
          (data.history.length + i).toDouble(),
          data.forecast[i].predictedDemand,
        ),
      );
    });
  }

  Future<void> _sendMessage() async {
    final text = _messageController.text.trim();
    if (text.isEmpty) return;

    _addUserMessage(text);
    _messageController.clear();

    setState(() => _isLoading = true);

    try {
      final response = await _chatService.sendMessage(
        text,
        language: 'kk',
        modelType: _selectedModel,
      );

      if (response.data != null) {
        _updateChartData(response.data!);
      }

      _addBotMessage(
        response.reply,
        showSuggestions: response.suggestions.isNotEmpty,
        suggestions: response.suggestions,
        intent: response.intent,
        images: response.images,
      );
    } catch (e) {
      _addBotMessage(
        'Кешіріңіз, қате орын алды. Қайтадан көріңіз.',
        showSuggestions: true,
        suggestions: _currentSuggestions.isNotEmpty
            ? _currentSuggestions
            : ['P0001 болжамы', 'Үздік 5 өнім'],
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _onSuggestionTap(String suggestion) {
    _messageController.text = suggestion;
    _sendMessage();
  }

  Future<void> _clearHistory() async {
    try {
      await _chatService.clearHistory();
      setState(() {
        _messages.clear();
        _historySpots.clear();
        _forecastSpots.clear();
      });
      _addBotMessage(
        'Чат тарихы тазартылды. Сізге қалай көмектесе аламын?',
        showSuggestions: true,
        suggestions: [
          'P0001 болжамы',
          'Үздік 5 өнім',
          'Шығыс пен батысты салыстыру',
        ],
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Тарихты тазалау сәтсіз аяқталды')),
      );
    }
  }

  String _buildInsightText() {
    if (_historySpots.isEmpty || _forecastSpots.isEmpty) return '';

    final last = _historySpots.last.y;
    final avg = _forecastSpots.map((e) => e.y).reduce((a, b) => a + b) /
        _forecastSpots.length;
    final diff = avg - last;

    if (diff > 5) {
      return 'Сұраныс өсуі күтілуде. Қорды арттыруды қарастырыңыз.';
    } else if (diff < -5) {
      return 'Сұраныс төмендеуі күтілуде. Қорды азайтуды қарастырыңыз.';
    }
    return 'Сұраныс тұрақты болып қалады деп күтілуде.';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: Column(
          children: [
            _buildHeader(),
            const Divider(height: 1, color: AppColors.borderSubtle),
            if (_isLoadingHistory)
              const Expanded(
                child: Center(
                  child: CircularProgressIndicator(color: AppColors.primary),
                ),
              )
            else
              Expanded(
                child: ListView.builder(
                  controller: _scrollController,
                  padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
                  itemCount:
                      _messages.length + (_historySpots.isNotEmpty ? 1 : 0),
                  itemBuilder: (context, index) {
                    if (index < _messages.length) {
                      final message = _messages[index];
                      return ChatMessage(
                        data: message,
                        onSuggestionTap: _onSuggestionTap,
                      );
                    }
                    return _buildChart();
                  },
                ),
              ),
            if (_isLoading) _buildTypingIndicator(),
            _buildInputField(),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Row(
        children: [
          const BrandLogo(
            size: 36,
            radius: 10,
            icon: Icons.auto_awesome_rounded,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Prodbot AI', style: AppTextStyles.titleMedium),
                Row(
                  children: [
                    Container(
                      width: 6,
                      height: 6,
                      decoration: const BoxDecoration(
                        color: AppColors.success,
                        shape: BoxShape.circle,
                      ),
                    ),
                    const SizedBox(width: 6),
                    Text(
                      'Қосулы · сұраныс болжам көмекшісі',
                      style: AppTextStyles.caption.copyWith(
                        color: AppColors.textSecondary,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          _IconBubble(
            icon: Icons.delete_outline_rounded,
            tooltip: 'Тарихты тазалау',
            onTap: _clearHistory,
          ),
        ],
      ),
    );
  }

  Widget _buildTypingIndicator() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 4, 16, 8),
      child: Row(
        children: [
          const BrandLogo(
            size: 32,
            radius: 9,
            icon: Icons.auto_awesome_rounded,
          ),
          const SizedBox(width: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
            decoration: BoxDecoration(
              color: AppColors.surfaceVariant,
              borderRadius: const BorderRadius.only(
                topLeft: Radius.circular(4),
                topRight: Radius.circular(18),
                bottomLeft: Radius.circular(18),
                bottomRight: Radius.circular(18),
              ),
              border: Border.all(color: AppColors.border, width: 1),
            ),
            child: const _TypingDots(),
          ),
        ],
      ),
    );
  }

  Widget _buildInputField() {
    return Container(
      padding: const EdgeInsets.fromLTRB(12, 10, 12, 12),
      decoration: const BoxDecoration(
        color: AppColors.background,
        border: Border(
          top: BorderSide(color: AppColors.borderSubtle, width: 1),
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          Expanded(
            child: Container(
              decoration: BoxDecoration(
                color: AppColors.surfaceVariant,
                borderRadius: BorderRadius.circular(999),
                border: Border.all(color: AppColors.border, width: 1),
              ),
              padding: const EdgeInsets.fromLTRB(16, 4, 6, 4),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  Expanded(
                    child: TextField(
                      controller: _messageController,
                      decoration: InputDecoration(
                        hintText: 'Хабарлама жазыңыз...',
                        hintStyle: AppTextStyles.bodyMedium.copyWith(
                          color: AppColors.textHint,
                        ),
                        border: InputBorder.none,
                        contentPadding:
                            const EdgeInsets.symmetric(vertical: 12),
                        isDense: true,
                      ),
                      style: AppTextStyles.bodyMedium.copyWith(
                        color: AppColors.textPrimary,
                      ),
                      maxLines: 4,
                      minLines: 1,
                      textInputAction: TextInputAction.send,
                      onSubmitted: (_) => _sendMessage(),
                      enabled: !_isLoading,
                    ),
                  ),
                  _ModelSelector(
                    selectedId: _selectedModel,
                    onChanged: (id) => setState(() => _selectedModel = id),
                  ),
                  const SizedBox(width: 4),
                  const Icon(
                    Icons.mic_none_rounded,
                    color: AppColors.textHint,
                    size: 20,
                  ),
                  const SizedBox(width: 6),
                ],
              ),
            ),
          ),
          const SizedBox(width: 10),
          GestureDetector(
            onTap: _isLoading ? null : _sendMessage,
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              width: 46,
              height: 46,
              decoration: BoxDecoration(
                gradient: _isLoading ? null : AppColors.primaryGradient,
                color: _isLoading ? AppColors.surfaceVariant : null,
                shape: BoxShape.circle,
                boxShadow: _isLoading
                    ? null
                    : [
                        BoxShadow(
                          color: AppColors.primary.withValues(alpha: 0.4),
                          blurRadius: 16,
                          offset: const Offset(0, 4),
                        ),
                      ],
              ),
              child: Icon(
                Icons.arrow_upward_rounded,
                color: _isLoading ? AppColors.textHint : AppColors.white,
                size: 22,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildChart() {
    if (_historySpots.isEmpty || _forecastSpots.isEmpty) {
      return const SizedBox.shrink();
    }

    return Container(
      margin: const EdgeInsets.only(top: 8, bottom: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.cardBackground,
        borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
        border: Border.all(color: AppColors.border, width: 1),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 28,
                height: 28,
                decoration: BoxDecoration(
                  color: AppColors.primary.withValues(alpha: 0.14),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(
                    color: AppColors.primary.withValues(alpha: 0.32),
                  ),
                ),
                child: const Icon(
                  Icons.show_chart_rounded,
                  size: 14,
                  color: AppColors.primary,
                ),
              ),
              const SizedBox(width: 8),
              Text('Сұраныс талдауы', style: AppTextStyles.titleSmall),
            ],
          ),
          const SizedBox(height: 16),
          SizedBox(
            height: 180,
            child: LineChart(
              LineChartData(
                gridData: FlGridData(
                  show: true,
                  drawHorizontalLine: true,
                  drawVerticalLine: false,
                  horizontalInterval: 20,
                  getDrawingHorizontalLine: (value) => const FlLine(
                    color: AppColors.borderSubtle,
                    strokeWidth: 1,
                  ),
                ),
                borderData: FlBorderData(show: false),
                titlesData: const FlTitlesData(show: false),
                lineBarsData: [
                  LineChartBarData(
                    spots: _historySpots,
                    isCurved: true,
                    color: AppColors.primary,
                    barWidth: 2,
                    dotData: const FlDotData(show: false),
                    belowBarData: BarAreaData(
                      show: true,
                      color: AppColors.primary.withValues(alpha: 0.12),
                    ),
                  ),
                  LineChartBarData(
                    spots: _forecastSpots,
                    isCurved: true,
                    color: AppColors.secondary,
                    barWidth: 2,
                    dotData: const FlDotData(show: true),
                    dashArray: [6, 4],
                    belowBarData: BarAreaData(
                      show: true,
                      color: AppColors.secondary.withValues(alpha: 0.12),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: const [
              _ChartLegendItem(color: AppColors.primary, label: 'Тарихи'),
              SizedBox(width: 16),
              _ChartLegendItem(
                color: AppColors.secondary,
                label: 'Болжам',
                isDashed: true,
              ),
            ],
          ),
          if (_buildInsightText().isNotEmpty) ...[
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppColors.primary10,
                borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
                border: Border.all(
                  color: AppColors.primary.withValues(alpha: 0.28),
                ),
              ),
              child: Row(
                children: [
                  const Icon(
                    Icons.insights_rounded,
                    size: 16,
                    color: AppColors.primary,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      _buildInsightText(),
                      style: AppTextStyles.bodySmall.copyWith(
                        color: AppColors.textPrimary,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────
//  Chart Legend Item
// ─────────────────────────────────────────────────────────────

class _ChartLegendItem extends StatelessWidget {
  final Color color;
  final String label;
  final bool isDashed;

  const _ChartLegendItem({
    required this.color,
    required this.label,
    this.isDashed = false,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Container(
          width: 16,
          height: 3,
          decoration: BoxDecoration(
            color: isDashed ? null : color,
            borderRadius: BorderRadius.circular(2),
          ),
          child: isDashed
              ? CustomPaint(painter: _DashedLinePainter(color: color))
              : null,
        ),
        const SizedBox(width: 6),
        Text(
          label,
          style: AppTextStyles.caption.copyWith(
            color: AppColors.textSecondary,
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }
}

class _DashedLinePainter extends CustomPainter {
  final Color color;
  _DashedLinePainter({required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..strokeWidth = 3
      ..strokeCap = StrokeCap.round;

    double startX = 0;
    while (startX < size.width) {
      canvas.drawLine(
        Offset(startX, size.height / 2),
        Offset(startX + 4.0, size.height / 2),
        paint,
      );
      startX += 6.0;
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

// ─────────────────────────────────────────────────────────────
//  Typing indicator dots
// ─────────────────────────────────────────────────────────────

class _TypingDots extends StatefulWidget {
  const _TypingDots();

  @override
  State<_TypingDots> createState() => _TypingDotsState();
}

class _TypingDotsState extends State<_TypingDots>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    )..repeat();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        _buildDot(0),
        const SizedBox(width: 4),
        _buildDot(1),
        const SizedBox(width: 4),
        _buildDot(2),
      ],
    );
  }

  Widget _buildDot(int index) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        final delay = index * 0.2;
        final progress = ((_controller.value + 1.0 - delay) % 1.0);
        final scale = 0.6 + (0.4 * _bounce(progress));
        final opacity = 0.4 + (0.6 * _bounce(progress));

        return Transform.scale(
          scale: scale,
          child: Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(
              color: AppColors.primary.withValues(alpha: opacity),
              shape: BoxShape.circle,
            ),
          ),
        );
      },
    );
  }

  double _bounce(double t) {
    if (t < 0.5) return 4 * t * t * t;
    return 1 - ((-2 * t + 2) * (-2 * t + 2) * (-2 * t + 2)) / 2;
  }
}

class _IconBubble extends StatelessWidget {
  final IconData icon;
  final VoidCallback onTap;
  final String? tooltip;
  const _IconBubble({required this.icon, required this.onTap, this.tooltip});

  @override
  Widget build(BuildContext context) {
    final btn = Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(AppDimensions.radiusSm),
        child: Container(
          width: 38,
          height: 38,
          decoration: BoxDecoration(
            color: AppColors.surfaceVariant,
            borderRadius: BorderRadius.circular(AppDimensions.radiusSm),
            border: Border.all(color: AppColors.border, width: 1),
          ),
          child: Icon(icon, size: 18, color: AppColors.textSecondary),
        ),
      ),
    );
    if (tooltip != null) {
      return Tooltip(message: tooltip!, child: btn);
    }
    return btn;
  }
}
