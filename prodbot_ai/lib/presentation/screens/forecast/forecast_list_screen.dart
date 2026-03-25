import 'package:flutter/material.dart';
import '../../../core/theme/theme.dart';
import 'widgets/forecast_card.dart';
import 'forecast_detail_screen.dart';
import 'create_forecast_screen.dart';

class ForecastListScreen extends StatefulWidget {
  const ForecastListScreen({super.key});

  @override
  State<ForecastListScreen> createState() => _ForecastListScreenState();
}

class _ForecastListScreenState extends State<ForecastListScreen> {
  final TextEditingController _searchController = TextEditingController();
  String _selectedFilter = 'All';
  String _selectedSort = 'Newest';
  bool _isLoading = false;

  final List<String> _filters = ['All', 'Active', 'Completed', 'Draft'];
  final List<String> _sortOptions = ['Newest', 'Oldest', 'Accuracy', 'Product'];

  // Mock data
  final List<ForecastData> _forecasts = [
    ForecastData(
      id: '1',
      productId: 'P0001',
      productName: 'Product Alpha',
      createdAt: DateTime.now().subtract(const Duration(hours: 2)),
      horizon: 7,
      accuracy: 94.5,
      status: ForecastStatus.completed,
    ),
    ForecastData(
      id: '2',
      productId: 'P0002',
      productName: 'Product Beta',
      createdAt: DateTime.now().subtract(const Duration(days: 1)),
      horizon: 14,
      accuracy: 89.2,
      status: ForecastStatus.completed,
    ),
    ForecastData(
      id: '3',
      productId: 'P0003',
      productName: 'Product Gamma',
      createdAt: DateTime.now().subtract(const Duration(days: 3)),
      horizon: 30,
      accuracy: 91.8,
      status: ForecastStatus.active,
    ),
    ForecastData(
      id: '4',
      productId: 'P0004',
      productName: 'Product Delta',
      createdAt: DateTime.now().subtract(const Duration(days: 5)),
      horizon: 7,
      accuracy: null,
      status: ForecastStatus.draft,
    ),
  ];

  List<ForecastData> get _filteredForecasts {
    var result = _forecasts;

    // Apply filter
    if (_selectedFilter != 'All') {
      result = result.where((f) {
        switch (_selectedFilter) {
          case 'Active':
            return f.status == ForecastStatus.active;
          case 'Completed':
            return f.status == ForecastStatus.completed;
          case 'Draft':
            return f.status == ForecastStatus.draft;
          default:
            return true;
        }
      }).toList();
    }

    // Apply search
    final query = _searchController.text.toLowerCase();
    if (query.isNotEmpty) {
      result = result.where((f) =>
          f.productName.toLowerCase().contains(query) ||
          f.productId.toLowerCase().contains(query)).toList();
    }

    // Apply sort
    switch (_selectedSort) {
      case 'Newest':
        result.sort((a, b) => b.createdAt.compareTo(a.createdAt));
        break;
      case 'Oldest':
        result.sort((a, b) => a.createdAt.compareTo(b.createdAt));
        break;
      case 'Accuracy':
        result.sort((a, b) => (b.accuracy ?? 0).compareTo(a.accuracy ?? 0));
        break;
      case 'Product':
        result.sort((a, b) => a.productName.compareTo(b.productName));
        break;
    }

    return result;
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  void _navigateToDetail(ForecastData forecast) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => ForecastDetailScreen(forecast: forecast),
      ),
    );
  }

  void _navigateToCreate() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => const CreateForecastScreen(),
      ),
    );
  }

  Future<void> _refresh() async {
    setState(() => _isLoading = true);
    await Future.delayed(const Duration(seconds: 1));
    setState(() => _isLoading = false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Forecasts'),
        actions: [
          IconButton(
            icon: const Icon(Icons.filter_list),
            onPressed: _showFilterBottomSheet,
          ),
        ],
      ),
      body: Column(
        children: [
          // Search bar
          Padding(
            padding: const EdgeInsets.all(AppDimensions.spacing16),
            child: _buildSearchBar(),
          ),

          // Filter chips
          SizedBox(
            height: 40,
            child: ListView.separated(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(
                horizontal: AppDimensions.spacing16,
              ),
              itemCount: _filters.length,
              separatorBuilder: (_, __) =>
                  const SizedBox(width: AppDimensions.spacing8),
              itemBuilder: (context, index) {
                final filter = _filters[index];
                final isSelected = _selectedFilter == filter;
                return FilterChip(
                  label: Text(filter),
                  selected: isSelected,
                  onSelected: (selected) {
                    setState(() => _selectedFilter = filter);
                  },
                  selectedColor: AppColors.primary10,
                  checkmarkColor: AppColors.primary,
                  labelStyle: AppTextStyles.labelMedium.copyWith(
                    color: isSelected ? AppColors.primary : AppColors.textSecondary,
                  ),
                  side: BorderSide(
                    color: isSelected ? AppColors.primary : AppColors.border,
                  ),
                );
              },
            ),
          ),

          const SizedBox(height: AppDimensions.spacing16),

          // Results count and sort
          Padding(
            padding: const EdgeInsets.symmetric(
              horizontal: AppDimensions.spacing16,
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  '${_filteredForecasts.length} forecasts',
                  style: AppTextStyles.bodySmall,
                ),
                GestureDetector(
                  onTap: _showSortBottomSheet,
                  child: Row(
                    children: [
                      Text(
                        _selectedSort,
                        style: AppTextStyles.labelMedium.copyWith(
                          color: AppColors.primary,
                        ),
                      ),
                      const SizedBox(width: 4),
                      const Icon(
                        Icons.keyboard_arrow_down,
                        size: 18,
                        color: AppColors.primary,
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: AppDimensions.spacing12),

          // List
          Expanded(
            child: _filteredForecasts.isEmpty
                ? _buildEmptyState()
                : RefreshIndicator(
                    onRefresh: _refresh,
                    color: AppColors.primary,
                    child: ListView.separated(
                      padding: const EdgeInsets.symmetric(
                        horizontal: AppDimensions.spacing16,
                        vertical: AppDimensions.spacing8,
                      ),
                      itemCount: _filteredForecasts.length,
                      separatorBuilder: (_, __) =>
                          const SizedBox(height: AppDimensions.spacing12),
                      itemBuilder: (context, index) {
                        final forecast = _filteredForecasts[index];
                        return ForecastCard(
                          forecast: forecast,
                          onTap: () => _navigateToDetail(forecast),
                        );
                      },
                    ),
                  ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _navigateToCreate,
        backgroundColor: AppColors.primary,
        foregroundColor: AppColors.white,
        icon: const Icon(Icons.add),
        label: const Text('New Forecast'),
      ),
    );
  }

  Widget _buildSearchBar() {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
        border: Border.all(color: AppColors.border),
      ),
      child: TextField(
        controller: _searchController,
        onChanged: (_) => setState(() {}),
        decoration: InputDecoration(
          hintText: 'Search forecasts...',
          hintStyle: AppTextStyles.bodyMedium.copyWith(
            color: AppColors.textHint,
          ),
          prefixIcon: const Icon(
            Icons.search,
            color: AppColors.iconVariant,
          ),
          suffixIcon: _searchController.text.isNotEmpty
              ? IconButton(
                  icon: const Icon(Icons.close, size: 20),
                  onPressed: () {
                    _searchController.clear();
                    setState(() {});
                  },
                )
              : null,
          border: InputBorder.none,
          contentPadding: const EdgeInsets.symmetric(
            horizontal: AppDimensions.spacing16,
            vertical: AppDimensions.spacing14,
          ),
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(AppDimensions.spacing32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 80,
              height: 80,
              decoration: BoxDecoration(
                color: AppColors.primary10,
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.analytics_outlined,
                size: 40,
                color: AppColors.primary,
              ),
            ),
            const SizedBox(height: AppDimensions.spacing24),
            Text(
              'No forecasts found',
              style: AppTextStyles.titleMedium,
            ),
            const SizedBox(height: AppDimensions.spacing8),
            Text(
              'Create your first forecast to get started with demand predictions',
              style: AppTextStyles.bodyMedium.copyWith(
                color: AppColors.textSecondary,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: AppDimensions.spacing24),
            ElevatedButton.icon(
              onPressed: _navigateToCreate,
              icon: const Icon(Icons.add),
              label: const Text('Create Forecast'),
            ),
          ],
        ),
      ),
    );
  }

  void _showFilterBottomSheet() {
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(AppDimensions.spacing24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Filter by Status', style: AppTextStyles.titleMedium),
            const SizedBox(height: AppDimensions.spacing16),
            Wrap(
              spacing: AppDimensions.spacing8,
              children: _filters.map((filter) {
                final isSelected = _selectedFilter == filter;
                return ChoiceChip(
                  label: Text(filter),
                  selected: isSelected,
                  onSelected: (selected) {
                    setState(() => _selectedFilter = filter);
                    Navigator.pop(context);
                  },
                );
              }).toList(),
            ),
          ],
        ),
      ),
    );
  }

  void _showSortBottomSheet() {
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(AppDimensions.spacing24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Sort by', style: AppTextStyles.titleMedium),
            const SizedBox(height: AppDimensions.spacing16),
            ..._sortOptions.map((option) {
              final isSelected = _selectedSort == option;
              return ListTile(
                title: Text(option),
                trailing: isSelected
                    ? const Icon(Icons.check, color: AppColors.primary)
                    : null,
                onTap: () {
                  setState(() => _selectedSort = option);
                  Navigator.pop(context);
                },
              );
            }),
          ],
        ),
      ),
    );
  }
}
