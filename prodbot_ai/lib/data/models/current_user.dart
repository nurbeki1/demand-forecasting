/// Mirrors backend `UserResponse` (`GET/PATCH /auth/me`).
class CurrentUser {
  final int id;
  final String email;
  final bool isAdmin;
  final String subscriptionPlan;
  final String? fullName;
  final String? avatarUrl;
  final DateTime? createdAt;

  const CurrentUser({
    required this.id,
    required this.email,
    required this.isAdmin,
    this.subscriptionPlan = 'free',
    this.fullName,
    this.avatarUrl,
    this.createdAt,
  });

  /// Premium ML models follow `subscription_plan` only (admins are not auto-unlocked).
  bool get canUsePremiumMlModels {
    final p = subscriptionPlan.toLowerCase();
    return p == 'paid' || p == 'pro' || p == 'subscriber';
  }

  factory CurrentUser.fromJson(Map<String, dynamic> json) {
    DateTime? created;
    final raw = json['created_at'];
    if (raw is String) {
      created = DateTime.tryParse(raw);
    }

    return CurrentUser(
      id: json['id'] as int,
      email: json['email'] as String,
      isAdmin: json['is_admin'] as bool? ?? false,
      subscriptionPlan: json['subscription_plan'] as String? ?? 'free',
      fullName: json['full_name'] as String?,
      avatarUrl: json['avatar_url'] as String?,
      createdAt: created,
    );
  }

  /// Hydrate from [StorageService.getUserData] (ids may be strings).
  factory CurrentUser.fromStored(Map<String, dynamic> json) {
    DateTime? created;
    final raw = json['created_at'];
    if (raw is String) {
      created = DateTime.tryParse(raw);
    }
    final idRaw = json['id'];
    final id = idRaw is int ? idRaw : int.tryParse('$idRaw') ?? 0;

    return CurrentUser(
      id: id,
      email: json['email'] as String? ?? '',
      isAdmin: json['is_admin'] as bool? ?? false,
      subscriptionPlan: json['subscription_plan'] as String? ?? 'free',
      fullName: json['full_name'] as String?,
      avatarUrl: json['avatar_url'] as String?,
      createdAt: created,
    );
  }

  Map<String, dynamic> toStorageMap() {
    return {
      'email': email,
      'id': id.toString(),
      'is_admin': isAdmin,
      'subscription_plan': subscriptionPlan,
      if (fullName != null && fullName!.isNotEmpty) 'full_name': fullName,
      if (avatarUrl != null && avatarUrl!.isNotEmpty) 'avatar_url': avatarUrl,
      if (createdAt != null) 'created_at': createdAt!.toIso8601String(),
    };
  }
}
