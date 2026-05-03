import 'dart:async';

import 'package:flutter/material.dart';

import '../../../../core/theme/theme.dart';

/// Cycles through phrases with a typewriter animation.
/// Mirrors `TypewriterText` from `frontend-admin/src/pages/ChatPage.jsx`.
class TypewriterText extends StatefulWidget {
  final List<String> phrases;
  final TextStyle? style;
  const TypewriterText({super.key, required this.phrases, this.style});

  @override
  State<TypewriterText> createState() => _TypewriterTextState();
}

class _TypewriterTextState extends State<TypewriterText> {
  String _display = '';
  int _phraseIndex = 0;
  bool _deleting = false;
  bool _paused = false;
  Timer? _timer;
  bool _showCursor = true;
  Timer? _blinker;

  @override
  void initState() {
    super.initState();
    _scheduleNext();
    _blinker = Timer.periodic(const Duration(milliseconds: 500), (_) {
      if (!mounted) return;
      setState(() => _showCursor = !_showCursor);
    });
  }

  @override
  void dispose() {
    _timer?.cancel();
    _blinker?.cancel();
    super.dispose();
  }

  void _scheduleNext() {
    final phrase = widget.phrases[_phraseIndex];
    if (_paused) {
      _timer = Timer(const Duration(milliseconds: 2000), () {
        if (!mounted) return;
        setState(() {
          _paused = false;
          _deleting = true;
        });
        _scheduleNext();
      });
      return;
    }

    final speed =
        Duration(milliseconds: _deleting ? 30 : 50);
    _timer = Timer(speed, () {
      if (!mounted) return;
      setState(() {
        if (!_deleting) {
          if (_display.length < phrase.length) {
            _display = phrase.substring(0, _display.length + 1);
          } else {
            _paused = true;
          }
        } else {
          if (_display.isNotEmpty) {
            _display = _display.substring(0, _display.length - 1);
          } else {
            _deleting = false;
            _phraseIndex = (_phraseIndex + 1) % widget.phrases.length;
          }
        }
      });
      _scheduleNext();
    });
  }

  @override
  Widget build(BuildContext context) {
    final base = widget.style ??
        AppTextStyles.bodyLarge.copyWith(
          color: AppColors.textSecondary,
          fontSize: 16,
        );
    return RichText(
      textAlign: TextAlign.center,
      text: TextSpan(
        style: base,
        children: [
          TextSpan(text: _display),
          TextSpan(
            text: '|',
            style: base.copyWith(
              color: _showCursor
                  ? AppColors.primary
                  : AppColors.transparent,
              fontWeight: FontWeight.w300,
            ),
          ),
        ],
      ),
    );
  }
}
