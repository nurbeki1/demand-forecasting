import 'package:flutter/material.dart';

import '../../../../core/theme/theme.dart';

/// Lightweight markdown renderer that mirrors the parser implemented inline
/// in `frontend-admin/src/pages/ChatPage.jsx::renderMarkdown`.
///
/// Supports:
/// - `# / ## / ###` headings
/// - `-` and `*` unordered lists, plus `1.` ordered lists
/// - `**bold**` inline emphasis
/// - `---` horizontal rule
/// - GitHub-flavoured pipe tables (`|cell|cell|`)
class MarkdownView extends StatelessWidget {
  final String text;
  final TextStyle? baseStyle;

  const MarkdownView({super.key, required this.text, this.baseStyle});

  @override
  Widget build(BuildContext context) {
    final base = baseStyle ??
        AppTextStyles.bodyMedium.copyWith(
          color: AppColors.textPrimary,
          height: 1.55,
        );
    final blocks = _parseBlocks(text);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: blocks.map((b) => _buildBlock(b, base)).toList(),
    );
  }

  Widget _buildBlock(_Block block, TextStyle base) {
    switch (block.type) {
      case _BlockType.h1:
        return Padding(
          padding: const EdgeInsets.only(top: 8, bottom: 6),
          child: _inline(block.text!,
              style: base.copyWith(
                fontSize: 22,
                fontWeight: FontWeight.w700,
                color: AppColors.textPrimary,
              )),
        );
      case _BlockType.h2:
        return Padding(
          padding: const EdgeInsets.only(top: 8, bottom: 4),
          child: _inline(block.text!,
              style: base.copyWith(
                fontSize: 18,
                fontWeight: FontWeight.w700,
                color: AppColors.textPrimary,
              )),
        );
      case _BlockType.h3:
        return Padding(
          padding: const EdgeInsets.only(top: 6, bottom: 4),
          child: _inline(block.text!,
              style: base.copyWith(
                fontSize: 15,
                fontWeight: FontWeight.w700,
                color: AppColors.textPrimary,
              )),
        );
      case _BlockType.divider:
        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 8),
          child: Container(height: 1, color: AppColors.borderSubtle),
        );
      case _BlockType.list:
        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 4),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: block.items!
                .map(
                  (line) => Padding(
                    padding: const EdgeInsets.symmetric(vertical: 2),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Padding(
                          padding: const EdgeInsets.only(top: 7, right: 8),
                          child: Container(
                            width: 4,
                            height: 4,
                            decoration: const BoxDecoration(
                              color: AppColors.primary,
                              shape: BoxShape.circle,
                            ),
                          ),
                        ),
                        Expanded(child: _inline(line, style: base)),
                      ],
                    ),
                  ),
                )
                .toList(),
          ),
        );
      case _BlockType.table:
        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 8),
          child: SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: _MarkdownTable(
              header: block.tableHeader!,
              rows: block.tableRows!,
              base: base,
            ),
          ),
        );
      case _BlockType.paragraph:
        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 4),
          child: _inline(block.text!, style: base),
        );
    }
  }

  Widget _inline(String raw, {required TextStyle style}) {
    return RichText(
      text: TextSpan(style: style, children: _parseInline(raw, style)),
    );
  }
}

class _MarkdownTable extends StatelessWidget {
  const _MarkdownTable({
    required this.header,
    required this.rows,
    required this.base,
  });

  final List<String> header;
  final List<List<String>> rows;
  final TextStyle base;

  @override
  Widget build(BuildContext context) {
    Color? rowTint(List<String> row) {
      final joined = row.join(' ');
      if (joined.contains('🟢')) return AppColors.success.withValues(alpha: 0.06);
      if (joined.contains('🔴')) return AppColors.error.withValues(alpha: 0.06);
      if (joined.contains('🟡')) return AppColors.warning.withValues(alpha: 0.06);
      return null;
    }

    return Container(
      decoration: BoxDecoration(
        color: AppColors.surfaceVariant,
        borderRadius: BorderRadius.circular(AppDimensions.radiusSm),
        border: Border.all(color: AppColors.borderSubtle),
      ),
      child: Table(
        defaultColumnWidth: const IntrinsicColumnWidth(),
        border: TableBorder(
          horizontalInside:
              BorderSide(color: AppColors.borderSubtle, width: 0.5),
        ),
        children: [
          TableRow(
            decoration: const BoxDecoration(color: AppColors.surface),
            children: header
                .map(
                  (c) => Padding(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 12, vertical: 10),
                    child: Text(
                      c.trim(),
                      style: base.copyWith(
                        fontWeight: FontWeight.w600,
                        color: AppColors.textPrimary,
                      ),
                    ),
                  ),
                )
                .toList(),
          ),
          ...rows.map(
            (row) => TableRow(
              decoration: BoxDecoration(color: rowTint(row)),
              children: row
                  .map(
                    (c) => Padding(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 12, vertical: 9),
                      child: RichText(
                        text: TextSpan(
                          style: base.copyWith(color: AppColors.textPrimary),
                          children: _parseInline(c.trim(), base),
                        ),
                      ),
                    ),
                  )
                  .toList(),
            ),
          ),
        ],
      ),
    );
  }
}

List<TextSpan> _parseInline(String raw, TextStyle style) {
  final spans = <TextSpan>[];
  final regex = RegExp(r'\*\*(.+?)\*\*');
  int last = 0;
  for (final match in regex.allMatches(raw)) {
    if (match.start > last) {
      spans.add(TextSpan(text: raw.substring(last, match.start)));
    }
    spans.add(TextSpan(
      text: match.group(1),
      style: style.copyWith(fontWeight: FontWeight.w700),
    ));
    last = match.end;
  }
  if (last < raw.length) spans.add(TextSpan(text: raw.substring(last)));
  return spans.isEmpty ? [TextSpan(text: raw)] : spans;
}

enum _BlockType { paragraph, h1, h2, h3, list, divider, table }

class _Block {
  final _BlockType type;
  final String? text;
  final List<String>? items;
  final List<String>? tableHeader;
  final List<List<String>>? tableRows;

  _Block.paragraph(this.text)
      : type = _BlockType.paragraph,
        items = null,
        tableHeader = null,
        tableRows = null;
  _Block.h1(this.text)
      : type = _BlockType.h1,
        items = null,
        tableHeader = null,
        tableRows = null;
  _Block.h2(this.text)
      : type = _BlockType.h2,
        items = null,
        tableHeader = null,
        tableRows = null;
  _Block.h3(this.text)
      : type = _BlockType.h3,
        items = null,
        tableHeader = null,
        tableRows = null;
  _Block.list(this.items)
      : type = _BlockType.list,
        text = null,
        tableHeader = null,
        tableRows = null;
  _Block.divider()
      : type = _BlockType.divider,
        text = null,
        items = null,
        tableHeader = null,
        tableRows = null;
  _Block.table(this.tableHeader, this.tableRows)
      : type = _BlockType.table,
        text = null,
        items = null;
}

List<_Block> _parseBlocks(String input) {
  final lines = input.split('\n');
  final blocks = <_Block>[];

  List<String>? listBuf;
  List<String>? tableHeader;
  List<List<String>>? tableRows;
  bool tableSeen = false;

  void flushList() {
    if (listBuf != null && listBuf!.isNotEmpty) {
      blocks.add(_Block.list(listBuf));
    }
    listBuf = null;
  }

  void flushTable() {
    if (tableHeader != null) {
      blocks.add(_Block.table(tableHeader!, tableRows ?? []));
    }
    tableHeader = null;
    tableRows = null;
    tableSeen = false;
  }

  for (final raw in lines) {
    final line = raw.trimRight();
    final trimmed = line.trim();

    if (trimmed.startsWith('|') && trimmed.endsWith('|')) {
      flushList();
      final cells =
          trimmed.substring(1, trimmed.length - 1).split('|').toList();
      final isSeparator = cells.every(
        (c) => RegExp(r'^[\s:\-]+$').hasMatch(c),
      );
      if (isSeparator) {
        tableSeen = true;
        continue;
      }
      if (tableHeader == null) {
        tableHeader = cells;
        tableRows = [];
      } else {
        tableRows!.add(cells);
      }
      continue;
    }

    if (tableHeader != null && tableSeen) {
      flushTable();
    }

    if (trimmed.isEmpty) {
      flushList();
      continue;
    }

    if (trimmed.startsWith('### ')) {
      flushList();
      blocks.add(_Block.h3(trimmed.substring(4)));
    } else if (trimmed.startsWith('## ')) {
      flushList();
      blocks.add(_Block.h2(trimmed.substring(3)));
    } else if (trimmed.startsWith('# ')) {
      flushList();
      blocks.add(_Block.h1(trimmed.substring(2)));
    } else if (trimmed == '---') {
      flushList();
      blocks.add(_Block.divider());
    } else if (RegExp(r'^[-*]\s').hasMatch(trimmed)) {
      listBuf ??= [];
      listBuf!.add(trimmed.replaceFirst(RegExp(r'^[-*]\s'), ''));
    } else if (RegExp(r'^\d+\.\s').hasMatch(trimmed)) {
      listBuf ??= [];
      listBuf!.add(trimmed.replaceFirst(RegExp(r'^\d+\.\s'), ''));
    } else {
      flushList();
      blocks.add(_Block.paragraph(trimmed));
    }
  }

  flushList();
  flushTable();

  return blocks;
}
