import 'package:flutter/material.dart';
import '../../../core/theme/theme.dart';
import 'widgets/product_card.dart';
import 'product_detail_screen.dart';
import 'add_product_screen.dart';

class ProductsScreen extends StatefulWidget {
  const ProductsScreen({super.key});

  @override
  State<ProductsScreen> createState() => _ProductsScreenState();
}

class _ProductsScreenState extends State<ProductsScreen> {
  final TextEditingController _searchController = TextEditingController();
  String _selectedCategory = 'All';
  bool _isGridView = true;
  bool _isLoading = false;

  final List<String> _categories = [
    'All',
    'Electronics',
    'Clothing',
    'Food',
    'Home',
    'Sports',
  ];

  // Mock data
  final List<ProductData> _products = [
    ProductData(
      id: 'P0001',
      name: 'Product Alpha',
      category: 'Electronics',
      sku: 'SKU-001',
      price: 299.99,
      stock: 150,
      imageUrl: null,
      status: ProductStatus.active,
    ),
    ProductData(
      id: 'P0002',
      name: 'Product Beta',
      category: 'Electronics',
      sku: 'SKU-002',
      price: 149.99,
      stock: 75,
      imageUrl: null,
      status: ProductStatus.active,
    ),
    ProductData(
      id: 'P0003',
      name: 'Product Gamma',
      category: 'Clothing',
      sku: 'SKU-003',
      price: 49.99,
      stock: 200,
      imageUrl: null,
      status: ProductStatus.active,
    ),
    ProductData(
      id: 'P0004',
      name: 'Product Delta',
      category: 'Food',
      sku: 'SKU-004',
      price: 19.99,
      stock: 0,
      imageUrl: null,
      status: ProductStatus.outOfStock,
    ),
    ProductData(
      id: 'P0005',
      name: 'Product Epsilon',
      category: 'Home',
      sku: 'SKU-005',
      price: 89.99,
      stock: 25,
      imageUrl: null,
      status: ProductStatus.lowStock,
    ),
    ProductData(
      id: 'P0006',
      name: 'Product Zeta',
      category: 'Sports',
      sku: 'SKU-006',
      price: 129.99,
      stock: 50,
      imageUrl: null,
      status: ProductStatus.inactive,
    ),
  ];

  List<ProductData> get _filteredProducts {
    var result = _products;

    // Apply category filter
    if (_selectedCategory != 'All') {
      result = result.where((p) => p.category == _selectedCategory).toList();
    }

    // Apply search
    final query = _searchController.text.toLowerCase();
    if (query.isNotEmpty) {
      result = result.where((p) =>
          p.name.toLowerCase().contains(query) ||
          p.sku.toLowerCase().contains(query) ||
          p.id.toLowerCase().contains(query)).toList();
    }

    return result;
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  void _navigateToDetail(ProductData product) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => ProductDetailScreen(product: product),
      ),
    );
  }

  void _navigateToAdd() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => const AddProductScreen(),
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
        title: const Text('Products'),
        actions: [
          IconButton(
            icon: Icon(_isGridView ? Icons.view_list : Icons.grid_view),
            onPressed: () => setState(() => _isGridView = !_isGridView),
          ),
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

          // Category chips
          SizedBox(
            height: 40,
            child: ListView.separated(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(
                horizontal: AppDimensions.spacing16,
              ),
              itemCount: _categories.length,
              separatorBuilder: (_, __) =>
                  const SizedBox(width: AppDimensions.spacing8),
              itemBuilder: (context, index) {
                final category = _categories[index];
                final isSelected = _selectedCategory == category;
                return FilterChip(
                  label: Text(category),
                  selected: isSelected,
                  onSelected: (selected) {
                    setState(() => _selectedCategory = category);
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

          // Stats row
          Padding(
            padding: const EdgeInsets.symmetric(
              horizontal: AppDimensions.spacing16,
            ),
            child: _buildStatsRow(),
          ),

          const SizedBox(height: AppDimensions.spacing16),

          // Product list/grid
          Expanded(
            child: _filteredProducts.isEmpty
                ? _buildEmptyState()
                : RefreshIndicator(
                    onRefresh: _refresh,
                    color: AppColors.primary,
                    child: _isGridView
                        ? _buildGridView()
                        : _buildListView(),
                  ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _navigateToAdd,
        backgroundColor: AppColors.primary,
        foregroundColor: AppColors.white,
        icon: const Icon(Icons.add),
        label: const Text('Add Product'),
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
          hintText: 'Search products...',
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

  Widget _buildStatsRow() {
    final total = _filteredProducts.length;
    final active = _filteredProducts.where((p) => p.status == ProductStatus.active).length;
    final lowStock = _filteredProducts.where((p) => p.status == ProductStatus.lowStock).length;
    final outOfStock = _filteredProducts.where((p) => p.status == ProductStatus.outOfStock).length;

    return Row(
      children: [
        _buildStatChip('Total: $total', AppColors.textSecondary),
        const SizedBox(width: AppDimensions.spacing8),
        _buildStatChip('Active: $active', AppColors.success),
        const SizedBox(width: AppDimensions.spacing8),
        _buildStatChip('Low: $lowStock', AppColors.warning),
        const SizedBox(width: AppDimensions.spacing8),
        _buildStatChip('Out: $outOfStock', AppColors.error),
      ],
    );
  }

  Widget _buildStatChip(String text, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AppDimensions.spacing8,
        vertical: AppDimensions.spacing4,
      ),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(AppDimensions.radiusFull),
      ),
      child: Text(
        text,
        style: AppTextStyles.caption.copyWith(
          color: color,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }

  Widget _buildGridView() {
    return GridView.builder(
      padding: const EdgeInsets.all(AppDimensions.spacing16),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        childAspectRatio: 0.75,
        crossAxisSpacing: AppDimensions.spacing12,
        mainAxisSpacing: AppDimensions.spacing12,
      ),
      itemCount: _filteredProducts.length,
      itemBuilder: (context, index) {
        final product = _filteredProducts[index];
        return ProductCard(
          product: product,
          isGridView: true,
          onTap: () => _navigateToDetail(product),
        );
      },
    );
  }

  Widget _buildListView() {
    return ListView.separated(
      padding: const EdgeInsets.all(AppDimensions.spacing16),
      itemCount: _filteredProducts.length,
      separatorBuilder: (_, __) =>
          const SizedBox(height: AppDimensions.spacing12),
      itemBuilder: (context, index) {
        final product = _filteredProducts[index];
        return ProductCard(
          product: product,
          isGridView: false,
          onTap: () => _navigateToDetail(product),
        );
      },
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
                Icons.inventory_2_outlined,
                size: 40,
                color: AppColors.primary,
              ),
            ),
            const SizedBox(height: AppDimensions.spacing24),
            Text(
              'No products found',
              style: AppTextStyles.titleMedium,
            ),
            const SizedBox(height: AppDimensions.spacing8),
            Text(
              'Add your first product to start tracking inventory',
              style: AppTextStyles.bodyMedium.copyWith(
                color: AppColors.textSecondary,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: AppDimensions.spacing24),
            ElevatedButton.icon(
              onPressed: _navigateToAdd,
              icon: const Icon(Icons.add),
              label: const Text('Add Product'),
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
            Text('Filter by Category', style: AppTextStyles.titleMedium),
            const SizedBox(height: AppDimensions.spacing16),
            Wrap(
              spacing: AppDimensions.spacing8,
              runSpacing: AppDimensions.spacing8,
              children: _categories.map((category) {
                final isSelected = _selectedCategory == category;
                return ChoiceChip(
                  label: Text(category),
                  selected: isSelected,
                  onSelected: (selected) {
                    setState(() => _selectedCategory = category);
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
}
