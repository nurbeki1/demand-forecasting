import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../../../core/theme/theme.dart';

/// True when user prefers reduced motion (OS / Flutter accessibility).
bool authReduceMotion(BuildContext context) {
  return MediaQuery.disableAnimationsOf(context);
}

/// Slow drifting radial glow — GPU-friendly (opacity + gradient center only).
class AuthAmbientBackdrop extends StatefulWidget {
  const AuthAmbientBackdrop({super.key});

  @override
  State<AuthAmbientBackdrop> createState() => _AuthAmbientBackdropState();
}

class _AuthAmbientBackdropState extends State<AuthAmbientBackdrop>
    with SingleTickerProviderStateMixin {
  late AnimationController _ctrl;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 16),
    );
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      if (!authReduceMotion(context)) {
        _ctrl.repeat(reverse: true);
      }
    });
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (authReduceMotion(context)) {
      return DecoratedBox(
        decoration: BoxDecoration(
          gradient: RadialGradient(
            center: const Alignment(0, -0.72),
            radius: 1.05,
            colors: [
              AppColors.primary.withValues(alpha: 0.09),
              Colors.transparent,
            ],
          ),
        ),
      );
    }

    return AnimatedBuilder(
      animation: _ctrl,
      builder: (context, _) {
        final t = Curves.easeInOut.transform(_ctrl.value);
        final topCenter = Alignment.lerp(
          const Alignment(-0.18, -0.78),
          const Alignment(0.22, -0.52),
          t,
        )!;
        final bottomGlow = Alignment.lerp(
          const Alignment(-0.25, 0.85),
          const Alignment(0.3, 0.65),
          1 - t,
        )!;
        return Stack(
          fit: StackFit.expand,
          children: [
            DecoratedBox(
              decoration: BoxDecoration(
                gradient: RadialGradient(
                  center: topCenter,
                  radius: 1.12,
                  colors: [
                    AppColors.primary.withValues(alpha: 0.05 + 0.05 * t),
                    Colors.transparent,
                  ],
                ),
              ),
            ),
            DecoratedBox(
              decoration: BoxDecoration(
                gradient: RadialGradient(
                  center: bottomGlow,
                  radius: 1.0,
                  colors: [
                    AppColors.secondary.withValues(alpha: 0.03 + 0.03 * (1 - t)),
                    Colors.transparent,
                  ],
                ),
              ),
            ),
          ],
        );
      },
    );
  }
}

/// Fade + slight slide up; [step] controls delay order (0 = first).
Widget authStaggeredChild({
  required Animation<double> parent,
  required int step,
  required Widget child,
}) {
  final start = (step * 0.065).clamp(0.0, 0.82);
  final end = (start + 0.42).clamp(0.0, 1.0);
  final curved = CurvedAnimation(
    parent: parent,
    curve: Interval(start, end, curve: Curves.easeOutCubic),
  );
  return FadeTransition(
    opacity: curved,
    child: SlideTransition(
      position: Tween<Offset>(
        begin: const Offset(0, 0.06),
        end: Offset.zero,
      ).animate(curved),
      child: child,
    ),
  );
}

/// Soft breathing scale on the logo.
class AuthLogoPulse extends StatelessWidget {
  final Animation<double> animation;
  final Widget child;

  const AuthLogoPulse({
    super.key,
    required this.animation,
    required this.child,
  });

  @override
  Widget build(BuildContext context) {
    if (authReduceMotion(context)) return child;

    return AnimatedBuilder(
      animation: animation,
      builder: (context, _) {
        final v = Curves.easeInOut.transform(animation.value);
        final scale = 1.0 + 0.035 * math.sin(v * math.pi);
        return Transform.scale(scale: scale, child: child);
      },
    );
  }
}

/// Horizontal shake when [trigger] identity changes (e.g. new error string).
class AuthShakeWrapper extends StatefulWidget {
  final Object? trigger;
  final Widget child;

  const AuthShakeWrapper({
    super.key,
    required this.trigger,
    required this.child,
  });

  @override
  State<AuthShakeWrapper> createState() => _AuthShakeWrapperState();
}

class _AuthShakeWrapperState extends State<AuthShakeWrapper>
    with SingleTickerProviderStateMixin {
  late AnimationController _shake;

  @override
  void initState() {
    super.initState();
    _shake = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 520),
    );
  }

  @override
  void didUpdateWidget(covariant AuthShakeWrapper oldWidget) {
    super.didUpdateWidget(oldWidget);
    final next = widget.trigger;
    if (next != null &&
        next.toString().isNotEmpty &&
        next != oldWidget.trigger) {
      _runShake();
    }
  }

  void _runShake() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      if (!authReduceMotion(context)) {
        _shake.forward(from: 0);
      }
    });
  }

  @override
  void dispose() {
    _shake.dispose();
    super.dispose();
  }

  double _offset(double t) {
    if (t <= 0) return 0;
    final wobble = math.sin(t * math.pi * 4.5);
    return wobble * 7 * (1 - t);
  }

  @override
  Widget build(BuildContext context) {
    if (authReduceMotion(context)) return widget.child;

    return AnimatedBuilder(
      animation: _shake,
      builder: (context, _) {
        return Transform.translate(
          offset: Offset(_offset(_shake.value), 0),
          child: widget.child,
        );
      },
    );
  }
}
