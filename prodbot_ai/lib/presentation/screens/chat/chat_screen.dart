import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../../core/theme/theme.dart';
import '../../../services/chat_service.dart';
import '../../../data/models/chat_models.dart';
import 'widgets/chat_message.dart';

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
          'Hi! I can help you analyze demand forecasts. Ask me anything about products, trends, or comparisons.',
          showSuggestions: true,
          suggestions: [
            'Forecast for P0001',
            'Top 5 products',
            'Compare East and West',
            'What categories exist?',
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

            // Restore chart data from last assistant message with data
            if (msg.isAssistant && msg.data != null) {
              _updateChartData(msg.data!);
            }
          }
        });
      }
    } catch (e) {
      _addBotMessage(
        'Hi! I can help you analyze demand forecasts. Ask me anything!',
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
      final response = await _chatService.sendMessage(text);

      // Update chart if data available
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
        'Sorry, I encountered an error. Please try again.',
        showSuggestions: true,
        suggestions: _currentSuggestions.isNotEmpty
            ? _currentSuggestions
            : ['Forecast for P0001', 'Top 5 products'],
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
        'Chat history cleared. How can I help you?',
        showSuggestions: true,
        suggestions: [
          'Forecast for P0001',
          'Top 5 products',
          'Compare East and West',
        ],
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Failed to clear history')),
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
      return 'Demand is expected to increase. Consider increasing stock.';
    } else if (diff < -5) {
      return 'Demand is expected to decline. Consider reducing inventory.';
    }
    return 'Demand is expected to remain stable.';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.surface,
      body: SafeArea(
        child: Column(
          children: [
            // Header
            _buildHeader(),

            const Divider(height: 1, color: AppColors.divider),

            // Loading history indicator
            if (_isLoadingHistory)
              const Expanded(
                child: Center(
                  child: CircularProgressIndicator(),
                ),
              )
            else
              // Chat messages
              Expanded(
                child: ListView.builder(
                  controller: _scrollController,
                  padding: const EdgeInsets.all(AppDimensions.spacing16),
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
                    // Chart
                    return _buildChart();
                  },
                ),
              ),

            // Typing indicator
            if (_isLoading) _buildTypingIndicator(),

            // Input field
            _buildInputField(),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AppDimensions.spacing16,
        vertical: AppDimensions.spacing12,
      ),
      child: Row(
        children: [
          // Bot icon
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

          const SizedBox(width: AppDimensions.spacing12),

          // Title
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Prodbot AI',
                style: AppTextStyles.titleMedium,
              ),
              Text(
                'Demand Forecasting Assistant',
                style: AppTextStyles.caption.copyWith(
                  color: AppColors.textSecondary,
                ),
              ),
            ],
          ),

          const Spacer(),

          // Clear history button
          IconButton(
            onPressed: _clearHistory,
            icon: const Icon(
              Icons.delete_outline,
              color: AppColors.iconDefault,
            ),
            tooltip: 'Clear history',
          ),

          // Menu button
          IconButton(
            onPressed: () {},
            icon: const Icon(
              Icons.more_vert,
              color: AppColors.iconDefault,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTypingIndicator() {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AppDimensions.spacing16,
        vertical: AppDimensions.spacing8,
      ),
      child: Row(
        children: [
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
          Container(
            padding: const EdgeInsets.symmetric(
              horizontal: AppDimensions.spacing16,
              vertical: AppDimensions.spacing12,
            ),
            decoration: BoxDecoration(
              color: AppColors.chatBubble,
              borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
            ),
            child: const _TypingDots(),
          ),
        ],
      ),
    );
  }

  Widget _buildInputField() {
    return Container(
      padding: const EdgeInsets.all(AppDimensions.spacing16),
      decoration: BoxDecoration(
        color: AppColors.surface,
        boxShadow: [
          BoxShadow(
            color: AppColors.shadowLight,
            blurRadius: 8,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: Row(
        children: [
          // Text input
          Expanded(
            child: Container(
              decoration: BoxDecoration(
                color: AppColors.surface,
                borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
                boxShadow: AppDimensions.shadowLg,
              ),
              child: Row(
                children: [
                  // AI icon
                  Padding(
                    padding:
                        const EdgeInsets.only(left: AppDimensions.spacing12),
                    child: Icon(
                      Icons.auto_awesome,
                      size: 20,
                      color: AppColors.iconVariant.withValues(alpha: 0.6),
                    ),
                  ),

                  // Input
                  Expanded(
                    child: TextField(
                      controller: _messageController,
                      decoration: InputDecoration(
                        hintText: 'Ask about demand forecasts...',
                        hintStyle: AppTextStyles.bodyMedium.copyWith(
                          color: AppColors.textHint,
                        ),
                        border: InputBorder.none,
                        contentPadding: const EdgeInsets.symmetric(
                          horizontal: AppDimensions.spacing12,
                          vertical: AppDimensions.spacing14,
                        ),
                      ),
                      style: AppTextStyles.bodyMedium,
                      onSubmitted: (_) => _sendMessage(),
                      enabled: !_isLoading,
                    ),
                  ),

                  // Mic button
                  IconButton(
                    onPressed: () {},
                    icon: const Icon(
                      Icons.mic_none_outlined,
                      color: AppColors.primary,
                    ),
                  ),
                ],
              ),
            ),
          ),

          const SizedBox(width: AppDimensions.spacing12),

          // Send button
          GestureDetector(
            onTap: _isLoading ? null : _sendMessage,
            child: Container(
              width: 54,
              height: 54,
              decoration: BoxDecoration(
                color: _isLoading ? AppColors.textDisabled : AppColors.primary,
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.send,
                color: AppColors.white,
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
      margin: const EdgeInsets.only(top: AppDimensions.spacing16),
      padding: const EdgeInsets.all(AppDimensions.spacing16),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
        boxShadow: AppDimensions.shadowCard,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Demand Analysis',
            style: AppTextStyles.titleSmall,
          ),
          const SizedBox(height: AppDimensions.spacing16),
          SizedBox(
            height: 200,
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
                titlesData: const FlTitlesData(show: false),
                lineBarsData: [
                  // History line
                  LineChartBarData(
                    spots: _historySpots,
                    isCurved: true,
                    color: AppColors.info,
                    barWidth: 2,
                    dotData: const FlDotData(show: false),
                    belowBarData: BarAreaData(
                      show: true,
                      color: AppColors.info.withValues(alpha: 0.1),
                    ),
                  ),
                  // Forecast line
                  LineChartBarData(
                    spots: _forecastSpots,
                    isCurved: true,
                    color: AppColors.purpleHaze,
                    barWidth: 2,
                    dotData: const FlDotData(show: true),
                    dashArray: [6, 4],
                    belowBarData: BarAreaData(
                      show: true,
                      color: AppColors.purpleHaze.withValues(alpha: 0.1),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: AppDimensions.spacing12),

          // Legend
          Row(
            children: [
              _ChartLegendItem(
                color: AppColors.info,
                label: 'Historical',
              ),
              const SizedBox(width: AppDimensions.spacing16),
              _ChartLegendItem(
                color: AppColors.purpleHaze,
                label: 'Forecast',
                isDashed: true,
              ),
            ],
          ),

          const SizedBox(height: AppDimensions.spacing12),

          // Insight text
          Container(
            padding: const EdgeInsets.all(AppDimensions.spacing12),
            decoration: BoxDecoration(
              color: AppColors.primary10,
              borderRadius: BorderRadius.circular(AppDimensions.radiusSm),
            ),
            child: Row(
              children: [
                const Icon(
                  Icons.insights,
                  size: 18,
                  color: AppColors.primary,
                ),
                const SizedBox(width: AppDimensions.spacing8),
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
      ),
    );
  }
}

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
              ? CustomPaint(
                  painter: _DashedLinePainter(color: color),
                )
              : null,
        ),
        const SizedBox(width: AppDimensions.spacing6),
        Text(
          label,
          style: AppTextStyles.caption,
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

    const dashWidth = 4.0;
    const dashSpace = 2.0;
    double startX = 0;

    while (startX < size.width) {
      canvas.drawLine(
        Offset(startX, size.height / 2),
        Offset(startX + dashWidth, size.height / 2),
        paint,
      );
      startX += dashWidth + dashSpace;
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}

/// Animated typing dots indicator
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
    // Creates a bounce effect
    if (t < 0.5) {
      return 4 * t * t * t;
    } else {
      return 1 - ((-2 * t + 2) * (-2 * t + 2) * (-2 * t + 2)) / 2;
    }
  }
}
