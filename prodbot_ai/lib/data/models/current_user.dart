/// Mirrors backend `UserResponse` (`GET/PATCH /auth/me`).
class CurrentUser {
  final int id;
  final String email;
  final bool isAdmin;
  final String? fullName;
  final String? avatarUrl;
  final DateTime? createdAt;

  const CurrentUser({
    required this.id,
    required this.email,
    required this.isAdmin,
    this.fullName,
    this.avatarUrl,
    this.createdAt,
  });

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
      fullName: json['full_name'] as String?,
      avatarUrl: json['avatar_url'] as String?,
      createdAt: created,
    );
  }

  Map<String, dynamic> toStorageMap() {
    return {
      'email': email,
      'id': id.toString(),
      if (fullName != null && fullName!.isNotEmpty) 'full_name': fullName,
      if (avatarUrl != null && avatarUrl!.isNotEmpty) 'avatar_url': avatarUrl,
      'is_admin': isAdmin,
      if (createdAt != null) 'created_at': createdAt!.toIso8601String(),
    };
  }
}
