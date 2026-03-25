import 'package:flutter/material.dart';
import '../../../core/theme/theme.dart';
import '../../widgets/common/widgets.dart';

class CreateForecastScreen extends StatefulWidget {
  const CreateForecastScreen({super.key});

  @override
  State<CreateForecastScreen> createState() => _CreateForecastScreenState();
}

class _CreateForecastScreenState extends State<CreateForecastScreen> {
  final PageController _pageController = PageController();
  int _currentStep = 0;
  bool _isLoading = false;

  // Step 1: Product Selection
  String? _selectedProductId;
  final List<Map<String, String>> _products = [
    {'id': 'P0001', 'name': 'Product Alpha', 'category': 'Electronics'},
    {'id': 'P0002', 'name': 'Product Beta', 'category': 'Electronics'},
    {'id': 'P0003', 'name': 'Product Gamma', 'category': 'Clothing'},
    {'id': 'P0004', 'name': 'Product Delta', 'category': 'Food'},
    {'id': 'P0005', 'name': 'Product Epsilon', 'category': 'Electronics'},
  ];

  // Step 2: Forecast Parameters
  int _horizon = 7;
  String _granularity = 'Daily';
  final List<int> _horizonOptions = [7, 14, 30, 60, 90];
  final List<String> _granularityOptions = ['Daily', 'Weekly', 'Monthly'];

  // Step 3: Model Configuration
  String _selectedModel = 'Auto';
  bool _includeSeasonality = true;
  bool _includeHolidays = true;
  bool _includeExternalFactors = false;
  final List<String> _models = ['Auto', 'Prophet', 'ARIMA', 'LSTM', 'XGBoost'];

  // Step 4: Review
  String _forecastName = '';
  final TextEditingController _nameController = TextEditingController();

  final List<String> _stepTitles = [
    'Select Product',
    'Parameters',
    'Model',
    'Review',
  ];

  @override
  void dispose() {
    _pageController.dispose();
    _nameController.dispose();
    super.dispose();
  }

  void _nextStep() {
    if (_currentStep < 3) {
      if (_validateCurrentStep()) {
        _pageController.nextPage(
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeInOut,
        );
        setState(() => _currentStep++);
      }
    } else {
      _createForecast();
    }
  }

  void _previousStep() {
    if (_currentStep > 0) {
      _pageController.previousPage(
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeInOut,
      );
      setState(() => _currentStep--);
    } else {
      Navigator.pop(context);
    }
  }

  bool _validateCurrentStep() {
    switch (_currentStep) {
      case 0:
        if (_selectedProductId == null) {
          _showError('Please select a product');
          return false;
        }
        return true;
      case 1:
        return true;
      case 2:
        return true;
      case 3:
        if (_nameController.text.trim().isEmpty) {
          _showError('Please enter a forecast name');
          return false;
        }
        return true;
      default:
        return true;
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: AppColors.error,
      ),
    );
  }

  Future<void> _createForecast() async {
    setState(() => _isLoading = true);

    // Simulate API call
    await Future.delayed(const Duration(seconds: 2));

    setState(() => _isLoading = false);

    if (mounted) {
      // Show success and navigate back
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Forecast created successfully!'),
          backgroundColor: AppColors.success,
        ),
      );
      Navigator.pop(context);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Create Forecast'),
        leading: IconButton(
          icon: const Icon(Icons.close),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: Column(
        children: [
          // Progress indicator
          _buildProgressIndicator(),

          // Step content
          Expanded(
            child: PageView(
              controller: _pageController,
              physics: const NeverScrollableScrollPhysics(),
              children: [
                _buildProductSelectionStep(),
                _buildParametersStep(),
                _buildModelConfigStep(),
                _buildReviewStep(),
              ],
            ),
          ),

          // Navigation buttons
          _buildNavigationButtons(),
        ],
      ),
    );
  }

  Widget _buildProgressIndicator() {
    return Container(
      padding: const EdgeInsets.all(AppDimensions.spacing16),
      child: Column(
        children: [
          // Step indicators
          Row(
            children: List.generate(4, (index) {
              final isCompleted = index < _currentStep;
              final isCurrent = index == _currentStep;

              return Expanded(
                child: Row(
                  children: [
                    // Circle
                    Container(
                      width: 32,
                      height: 32,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: isCompleted
                            ? AppColors.success
                            : isCurrent
                                ? AppColors.primary
                                : AppColors.surface,
                        border: Border.all(
                          color: isCompleted
                              ? AppColors.success
                              : isCurrent
                                  ? AppColors.primary
                                  : AppColors.border,
                          width: 2,
                        ),
                      ),
                      child: Center(
                        child: isCompleted
                            ? const Icon(
                                Icons.check,
                                size: 16,
                                color: AppColors.white,
                              )
                            : Text(
                                '${index + 1}',
                                style: AppTextStyles.labelMedium.copyWith(
                                  color: isCurrent
                                      ? AppColors.white
                                      : AppColors.textSecondary,
                                ),
                              ),
                      ),
                    ),

                    // Line
                    if (index < 3)
                      Expanded(
                        child: Container(
                          height: 2,
                          color: isCompleted
                              ? AppColors.success
                              : AppColors.border,
                        ),
                      ),
                  ],
                ),
              );
            }),
          ),

          const SizedBox(height: AppDimensions.spacing12),

          // Step titles
          Row(
            children: List.generate(4, (index) {
              final isCurrent = index == _currentStep;
              return Expanded(
                child: Text(
                  _stepTitles[index],
                  textAlign: TextAlign.center,
                  style: AppTextStyles.caption.copyWith(
                    color: isCurrent
                        ? AppColors.primary
                        : AppColors.textSecondary,
                    fontWeight: isCurrent ? FontWeight.w600 : FontWeight.normal,
                  ),
                ),
              );
            }),
          ),
        ],
      ),
    );
  }

  Widget _buildProductSelectionStep() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppDimensions.spacing16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Select a Product',
            style: AppTextStyles.titleMedium,
          ),
          const SizedBox(height: AppDimensions.spacing8),
          Text(
            'Choose the product you want to create a demand forecast for',
            style: AppTextStyles.bodyMedium.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
          const SizedBox(height: AppDimensions.spacing24),

          // Search field
          AppTextField.search(
            hintText: 'Search products...',
          ),

          const SizedBox(height: AppDimensions.spacing16),

          // Product list
          ...(_products.map((product) => _buildProductTile(product))),
        ],
      ),
    );
  }

  Widget _buildProductTile(Map<String, String> product) {
    final isSelected = _selectedProductId == product['id'];

    return GestureDetector(
      onTap: () {
        setState(() => _selectedProductId = product['id']);
      },
      child: Container(
        margin: const EdgeInsets.only(bottom: AppDimensions.spacing12),
        padding: const EdgeInsets.all(AppDimensions.spacing16),
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
          border: Border.all(
            color: isSelected ? AppColors.primary : AppColors.border,
            width: isSelected ? 2 : 1,
          ),
        ),
        child: Row(
          children: [
            // Product icon
            Container(
              width: 44,
              height: 44,
              decoration: BoxDecoration(
                color: AppColors.primary10,
                borderRadius: BorderRadius.circular(AppDimensions.radiusSm),
              ),
              child: const Icon(
                Icons.inventory_2_outlined,
                color: AppColors.primary,
              ),
            ),

            const SizedBox(width: AppDimensions.spacing12),

            // Product info
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    product['name']!,
                    style: AppTextStyles.labelLarge,
                  ),
                  const SizedBox(height: 2),
                  Text(
                    '${product['id']} • ${product['category']}',
                    style: AppTextStyles.caption,
                  ),
                ],
              ),
            ),

            // Check icon
            if (isSelected)
              Container(
                width: 24,
                height: 24,
                decoration: const BoxDecoration(
                  shape: BoxShape.circle,
                  color: AppColors.primary,
                ),
                child: const Icon(
                  Icons.check,
                  size: 16,
                  color: AppColors.white,
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildParametersStep() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppDimensions.spacing16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Forecast Parameters',
            style: AppTextStyles.titleMedium,
          ),
          const SizedBox(height: AppDimensions.spacing8),
          Text(
            'Configure the forecast horizon and granularity',
            style: AppTextStyles.bodyMedium.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
          const SizedBox(height: AppDimensions.spacing24),

          // Horizon selection
          Text('Forecast Horizon', style: AppTextStyles.labelLarge),
          const SizedBox(height: AppDimensions.spacing12),
          Wrap(
            spacing: AppDimensions.spacing8,
            children: _horizonOptions.map((days) {
              final isSelected = _horizon == days;
              return ChoiceChip(
                label: Text('$days days'),
                selected: isSelected,
                onSelected: (selected) {
                  setState(() => _horizon = days);
                },
                selectedColor: AppColors.primary10,
                labelStyle: AppTextStyles.labelMedium.copyWith(
                  color: isSelected ? AppColors.primary : AppColors.textSecondary,
                ),
              );
            }).toList(),
          ),

          const SizedBox(height: AppDimensions.spacing24),

          // Granularity selection
          Text('Granularity', style: AppTextStyles.labelLarge),
          const SizedBox(height: AppDimensions.spacing12),
          Wrap(
            spacing: AppDimensions.spacing8,
            children: _granularityOptions.map((option) {
              final isSelected = _granularity == option;
              return ChoiceChip(
                label: Text(option),
                selected: isSelected,
                onSelected: (selected) {
                  setState(() => _granularity = option);
                },
                selectedColor: AppColors.primary10,
                labelStyle: AppTextStyles.labelMedium.copyWith(
                  color: isSelected ? AppColors.primary : AppColors.textSecondary,
                ),
              );
            }).toList(),
          ),

          const SizedBox(height: AppDimensions.spacing32),

          // Info card
          Container(
            padding: const EdgeInsets.all(AppDimensions.spacing16),
            decoration: BoxDecoration(
              color: AppColors.info.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
              border: Border.all(color: AppColors.info.withValues(alpha: 0.3)),
            ),
            child: Row(
              children: [
                const Icon(
                  Icons.info_outline,
                  color: AppColors.info,
                  size: 20,
                ),
                const SizedBox(width: AppDimensions.spacing12),
                Expanded(
                  child: Text(
                    'Longer horizons may have lower accuracy. We recommend starting with shorter periods.',
                    style: AppTextStyles.bodySmall.copyWith(
                      color: AppColors.info,
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

  Widget _buildModelConfigStep() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppDimensions.spacing16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Model Configuration',
            style: AppTextStyles.titleMedium,
          ),
          const SizedBox(height: AppDimensions.spacing8),
          Text(
            'Choose the forecasting model and additional features',
            style: AppTextStyles.bodyMedium.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
          const SizedBox(height: AppDimensions.spacing24),

          // Model selection
          Text('Forecasting Model', style: AppTextStyles.labelLarge),
          const SizedBox(height: AppDimensions.spacing12),
          ...(_models.map((model) => _buildModelOption(model))),

          const SizedBox(height: AppDimensions.spacing24),

          // Additional features
          Text('Additional Features', style: AppTextStyles.labelLarge),
          const SizedBox(height: AppDimensions.spacing12),

          _buildFeatureSwitch(
            'Include Seasonality',
            'Account for seasonal patterns in demand',
            _includeSeasonality,
            (value) => setState(() => _includeSeasonality = value),
          ),

          _buildFeatureSwitch(
            'Include Holidays',
            'Consider holiday effects on demand',
            _includeHolidays,
            (value) => setState(() => _includeHolidays = value),
          ),

          _buildFeatureSwitch(
            'External Factors',
            'Include weather, promotions, and events',
            _includeExternalFactors,
            (value) => setState(() => _includeExternalFactors = value),
          ),
        ],
      ),
    );
  }

  Widget _buildModelOption(String model) {
    final isSelected = _selectedModel == model;
    final descriptions = {
      'Auto': 'Automatically select the best model',
      'Prophet': 'Best for data with strong seasonality',
      'ARIMA': 'Classic time series forecasting',
      'LSTM': 'Deep learning for complex patterns',
      'XGBoost': 'Gradient boosting for feature-rich data',
    };

    return GestureDetector(
      onTap: () => setState(() => _selectedModel = model),
      child: Container(
        margin: const EdgeInsets.only(bottom: AppDimensions.spacing8),
        padding: const EdgeInsets.all(AppDimensions.spacing12),
        decoration: BoxDecoration(
          color: isSelected ? AppColors.primary10 : AppColors.surface,
          borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
          border: Border.all(
            color: isSelected ? AppColors.primary : AppColors.border,
          ),
        ),
        child: Row(
          children: [
            Radio<String>(
              value: model,
              groupValue: _selectedModel,
              onChanged: (value) => setState(() => _selectedModel = value!),
              activeColor: AppColors.primary,
            ),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(model, style: AppTextStyles.labelMedium),
                  Text(
                    descriptions[model]!,
                    style: AppTextStyles.caption,
                  ),
                ],
              ),
            ),
            if (model == 'Auto')
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: AppDimensions.spacing8,
                  vertical: AppDimensions.spacing4,
                ),
                decoration: BoxDecoration(
                  color: AppColors.primary,
                  borderRadius: BorderRadius.circular(AppDimensions.radiusFull),
                ),
                child: Text(
                  'Recommended',
                  style: AppTextStyles.labelSmall.copyWith(
                    color: AppColors.white,
                    fontSize: 10,
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildFeatureSwitch(
    String title,
    String subtitle,
    bool value,
    ValueChanged<bool> onChanged,
  ) {
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
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: AppTextStyles.labelMedium),
                const SizedBox(height: 2),
                Text(subtitle, style: AppTextStyles.caption),
              ],
            ),
          ),
          Switch(
            value: value,
            onChanged: onChanged,
            activeColor: AppColors.primary,
          ),
        ],
      ),
    );
  }

  Widget _buildReviewStep() {
    final selectedProduct = _products.firstWhere(
      (p) => p['id'] == _selectedProductId,
      orElse: () => {'id': '', 'name': '', 'category': ''},
    );

    return SingleChildScrollView(
      padding: const EdgeInsets.all(AppDimensions.spacing16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Review & Create',
            style: AppTextStyles.titleMedium,
          ),
          const SizedBox(height: AppDimensions.spacing8),
          Text(
            'Review your forecast configuration before creating',
            style: AppTextStyles.bodyMedium.copyWith(
              color: AppColors.textSecondary,
            ),
          ),
          const SizedBox(height: AppDimensions.spacing24),

          // Forecast name
          AppTextField(
            controller: _nameController,
            label: 'Forecast Name',
            hintText: 'Enter a name for this forecast',
            onChanged: (value) => _forecastName = value,
          ),

          const SizedBox(height: AppDimensions.spacing24),

          // Summary card
          Container(
            padding: const EdgeInsets.all(AppDimensions.spacing16),
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
              border: Border.all(color: AppColors.border),
            ),
            child: Column(
              children: [
                _buildSummaryRow('Product', selectedProduct['name']!),
                const Divider(height: AppDimensions.spacing24),
                _buildSummaryRow('Horizon', '$_horizon days'),
                const Divider(height: AppDimensions.spacing24),
                _buildSummaryRow('Granularity', _granularity),
                const Divider(height: AppDimensions.spacing24),
                _buildSummaryRow('Model', _selectedModel),
                const Divider(height: AppDimensions.spacing24),
                _buildSummaryRow(
                  'Features',
                  [
                    if (_includeSeasonality) 'Seasonality',
                    if (_includeHolidays) 'Holidays',
                    if (_includeExternalFactors) 'External Factors',
                  ].join(', '),
                ),
              ],
            ),
          ),

          const SizedBox(height: AppDimensions.spacing24),

          // Estimated time
          Container(
            padding: const EdgeInsets.all(AppDimensions.spacing16),
            decoration: BoxDecoration(
              color: AppColors.primary10,
              borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
            ),
            child: Row(
              children: [
                const Icon(
                  Icons.schedule,
                  color: AppColors.primary,
                  size: 20,
                ),
                const SizedBox(width: AppDimensions.spacing12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Estimated Processing Time',
                        style: AppTextStyles.labelMedium.copyWith(
                          color: AppColors.primary,
                        ),
                      ),
                      Text(
                        '2-5 minutes depending on data size',
                        style: AppTextStyles.caption,
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryRow(String label, String value) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: AppTextStyles.bodyMedium.copyWith(
            color: AppColors.textSecondary,
          ),
        ),
        Flexible(
          child: Text(
            value.isEmpty ? '-' : value,
            style: AppTextStyles.labelMedium,
            textAlign: TextAlign.right,
          ),
        ),
      ],
    );
  }

  Widget _buildNavigationButtons() {
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
            // Back button
            Expanded(
              child: AppButton(
                text: _currentStep == 0 ? 'Cancel' : 'Back',
                variant: AppButtonVariant.outline,
                onPressed: _previousStep,
              ),
            ),

            const SizedBox(width: AppDimensions.spacing12),

            // Next/Create button
            Expanded(
              child: AppButton(
                text: _currentStep == 3 ? 'Create Forecast' : 'Next',
                onPressed: _nextStep,
                isLoading: _isLoading,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
