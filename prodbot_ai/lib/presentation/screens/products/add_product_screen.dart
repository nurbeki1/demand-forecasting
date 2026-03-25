import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../../core/theme/theme.dart';
import '../../widgets/common/widgets.dart';

class AddProductScreen extends StatefulWidget {
  const AddProductScreen({super.key});

  @override
  State<AddProductScreen> createState() => _AddProductScreenState();
}

class _AddProductScreenState extends State<AddProductScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _skuController = TextEditingController();
  final _priceController = TextEditingController();
  final _stockController = TextEditingController();
  final _descriptionController = TextEditingController();

  String _selectedCategory = 'Electronics';
  bool _isLoading = false;

  final List<String> _categories = [
    'Electronics',
    'Clothing',
    'Food',
    'Home',
    'Sports',
    'Beauty',
    'Toys',
    'Other',
  ];

  @override
  void dispose() {
    _nameController.dispose();
    _skuController.dispose();
    _priceController.dispose();
    _stockController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  Future<void> _saveProduct() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    // Simulate API call
    await Future.delayed(const Duration(seconds: 2));

    setState(() => _isLoading = false);

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Product added successfully!'),
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
        title: const Text('Add Product'),
        leading: IconButton(
          icon: const Icon(Icons.close),
          onPressed: () => Navigator.pop(context),
        ),
        actions: [
          TextButton(
            onPressed: _isLoading ? null : _saveProduct,
            child: _isLoading
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      valueColor: AlwaysStoppedAnimation(AppColors.primary),
                    ),
                  )
                : Text(
                    'Save',
                    style: AppTextStyles.labelLarge.copyWith(
                      color: AppColors.primary,
                    ),
                  ),
          ),
        ],
      ),
      body: Form(
        key: _formKey,
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(AppDimensions.spacing16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Image upload
              _buildImageUpload(),

              const SizedBox(height: AppDimensions.spacing24),

              // Basic info section
              Text('Basic Information', style: AppTextStyles.titleSmall),
              const SizedBox(height: AppDimensions.spacing16),

              // Product name
              AppTextField(
                controller: _nameController,
                label: 'Product Name',
                hintText: 'Enter product name',
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter a product name';
                  }
                  return null;
                },
              ),

              const SizedBox(height: AppDimensions.spacing16),

              // SKU
              AppTextField(
                controller: _skuController,
                label: 'SKU',
                hintText: 'Enter SKU code',
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter a SKU';
                  }
                  return null;
                },
              ),

              const SizedBox(height: AppDimensions.spacing16),

              // Category dropdown
              Text('Category', style: AppTextStyles.labelMedium),
              const SizedBox(height: AppDimensions.spacing8),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: AppDimensions.spacing16,
                ),
                decoration: BoxDecoration(
                  color: AppColors.surface,
                  borderRadius: BorderRadius.circular(AppDimensions.radiusMd),
                  border: Border.all(color: AppColors.border),
                ),
                child: DropdownButtonHideUnderline(
                  child: DropdownButton<String>(
                    value: _selectedCategory,
                    isExpanded: true,
                    items: _categories.map((category) {
                      return DropdownMenuItem(
                        value: category,
                        child: Text(category),
                      );
                    }).toList(),
                    onChanged: (value) {
                      setState(() => _selectedCategory = value!);
                    },
                  ),
                ),
              ),

              const SizedBox(height: AppDimensions.spacing24),

              // Pricing section
              Text('Pricing & Stock', style: AppTextStyles.titleSmall),
              const SizedBox(height: AppDimensions.spacing16),

              // Price and stock row
              Row(
                children: [
                  Expanded(
                    child: AppTextField(
                      controller: _priceController,
                      label: 'Price',
                      hintText: '0.00',
                      prefixIcon: const Icon(Icons.attach_money),
                      keyboardType: const TextInputType.numberWithOptions(decimal: true),
                      inputFormatters: [
                        FilteringTextInputFormatter.allow(RegExp(r'^\d+\.?\d{0,2}')),
                      ],
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Required';
                        }
                        final price = double.tryParse(value);
                        if (price == null || price <= 0) {
                          return 'Invalid price';
                        }
                        return null;
                      },
                    ),
                  ),
                  const SizedBox(width: AppDimensions.spacing16),
                  Expanded(
                    child: AppTextField(
                      controller: _stockController,
                      label: 'Initial Stock',
                      hintText: '0',
                      prefixIcon: const Icon(Icons.inventory_2_outlined),
                      keyboardType: TextInputType.number,
                      inputFormatters: [
                        FilteringTextInputFormatter.digitsOnly,
                      ],
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Required';
                        }
                        return null;
                      },
                    ),
                  ),
                ],
              ),

              const SizedBox(height: AppDimensions.spacing24),

              // Description section
              Text('Description', style: AppTextStyles.titleSmall),
              const SizedBox(height: AppDimensions.spacing16),

              AppTextField.multiline(
                controller: _descriptionController,
                label: 'Product Description',
                hintText: 'Enter product description...',
                maxLines: 4,
              ),

              const SizedBox(height: AppDimensions.spacing24),

              // Additional settings
              Text('Additional Settings', style: AppTextStyles.titleSmall),
              const SizedBox(height: AppDimensions.spacing16),

              _buildSettingSwitch(
                'Track Inventory',
                'Enable stock tracking for this product',
                true,
              ),

              _buildSettingSwitch(
                'Enable Forecasting',
                'Include this product in demand forecasts',
                true,
              ),

              _buildSettingSwitch(
                'Low Stock Alerts',
                'Get notified when stock is running low',
                true,
              ),

              const SizedBox(height: AppDimensions.spacing32),

              // Submit button
              AppButton(
                text: 'Add Product',
                onPressed: _saveProduct,
                isLoading: _isLoading,
                fullWidth: true,
              ),

              const SizedBox(height: AppDimensions.spacing24),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildImageUpload() {
    return GestureDetector(
      onTap: _pickImage,
      child: Container(
        height: 200,
        width: double.infinity,
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
          border: Border.all(
            color: AppColors.border,
            style: BorderStyle.solid,
          ),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 64,
              height: 64,
              decoration: BoxDecoration(
                color: AppColors.primary10,
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.add_photo_alternate_outlined,
                size: 32,
                color: AppColors.primary,
              ),
            ),
            const SizedBox(height: AppDimensions.spacing12),
            Text(
              'Add Product Image',
              style: AppTextStyles.labelMedium.copyWith(
                color: AppColors.primary,
              ),
            ),
            const SizedBox(height: AppDimensions.spacing4),
            Text(
              'PNG, JPG up to 5MB',
              style: AppTextStyles.caption,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSettingSwitch(String title, String subtitle, bool initialValue) {
    return StatefulBuilder(
      builder: (context, setState) {
        bool value = initialValue;
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
                onChanged: (newValue) {
                  setState(() => value = newValue);
                },
                activeColor: AppColors.primary,
              ),
            ],
          ),
        );
      },
    );
  }

  void _pickImage() {
    // Show image picker options
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.symmetric(vertical: AppDimensions.spacing16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.camera_alt_outlined),
              title: const Text('Take Photo'),
              onTap: () {
                Navigator.pop(context);
                // TODO: Implement camera
              },
            ),
            ListTile(
              leading: const Icon(Icons.photo_library_outlined),
              title: const Text('Choose from Gallery'),
              onTap: () {
                Navigator.pop(context);
                // TODO: Implement gallery picker
              },
            ),
            ListTile(
              leading: const Icon(Icons.link),
              title: const Text('Enter URL'),
              onTap: () {
                Navigator.pop(context);
                _showUrlDialog();
              },
            ),
          ],
        ),
      ),
    );
  }

  void _showUrlDialog() {
    final urlController = TextEditingController();
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Image URL'),
        content: TextField(
          controller: urlController,
          decoration: const InputDecoration(
            hintText: 'Enter image URL',
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              // TODO: Set image URL
              Navigator.pop(context);
            },
            child: const Text('Add'),
          ),
        ],
      ),
    );
  }
}
