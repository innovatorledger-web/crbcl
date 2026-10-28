import 'dart:async';
import 'package:flutter/material.dart';
import '../services/connectivity_service.dart';
import '../services/db_helper.dart';
import '../services/speech_service.dart';
import '../services/sync_engine.dart';
import '../services/theme_service.dart';

class NoteDraftScreen extends StatefulWidget {
  final String? caseId;
  const NoteDraftScreen({super.key, this.caseId});

  @override
  State<NoteDraftScreen> createState() => _NoteDraftScreenState();
}

class _NoteDraftScreenState extends State<NoteDraftScreen> {
  final _titleController = TextEditingController();
  final _summaryController = TextEditingController();

  bool _isRecording = false;
  bool _isTranscribing = false;
  bool _isSaving = false;
  int _recordingSeconds = 0;
  Timer? _recordingTimer;

  @override
  void dispose() {
    _recordingTimer?.cancel();
    _titleController.dispose();
    _summaryController.dispose();
    super.dispose();
  }

  void _startDictation() {
    setState(() {
      _isRecording = true;
      _recordingSeconds = 0;
    });

    _recordingTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (mounted) {
        setState(() => _recordingSeconds++);
      }
    });
  }

  void _cancelDictation() {
    _recordingTimer?.cancel();
    setState(() {
      _isRecording = false;
      _recordingSeconds = 0;
    });
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Dictation cancelled. Existing narrative preserved.')),
    );
  }

  Future<void> _stopAndTranscribe() async {
    _recordingTimer?.cancel();
    setState(() {
      _isRecording = false;
      _isTranscribing = true;
    });

    final simulatedAudioBytes = List<int>.filled(1024, 0);

    final result = await MobileSpeechService.transcribeCaseNote(
      baseUrl: 'http://10.0.2.2:8000',
      authToken: 'mock_token',
      caseId: widget.caseId ?? 'general_intake',
      audioBytes: simulatedAudioBytes,
    );

    if (mounted) {
      setState(() => _isTranscribing = false);

      if (result.success && result.transcript.isNotEmpty) {
        final updated = MobileSpeechService.appendTranscriptToDraft(
          _summaryController.text,
          result.transcript,
        );
        setState(() {
          _summaryController.text = updated;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Transcript appended to note narrative. Review before saving.')),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(result.errorMessage ?? 'Speech transcription requires network connectivity.'),
            backgroundColor: CrbclTokens.statusWarning,
          ),
        );
      }
    }
  }

  Future<void> _saveOfflineNote() async {
    final title = _titleController.text.trim();
    final narrative = _summaryController.text.trim();

    if (title.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter a note title')),
      );
      return;
    }

    setState(() => _isSaving = true);

    final mutationId = 'note_${DateTime.now().millisecondsSinceEpoch}';
    final payload = {
      'case_id': widget.caseId ?? 'offline_case',
      'title': title,
      'summary': narrative,
      'narrative': narrative,
      'note_type': 'Progress Note',
      'created_at': DateTime.now().toIso8601String(),
    };

    try {
      await LocalDatabaseHelper.instance.saveDraft(
        id: mutationId,
        entityType: 'CASE_NOTE',
        title: title,
        subtitle: 'Case Note Draft • ${widget.caseId ?? "General"}',
        payload: payload,
      );

      bool syncedOnline = false;
      try {
        final isOnline = await ConnectivityService.instance.checkConnectivity();
        if (isOnline) {
          final syncRes = await SyncEngine().pushPendingQueue();
          if (syncRes.success && syncRes.syncedCount > 0) {
            syncedOnline = true;
          }
        }
      } catch (_) {}

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              syncedOnline
                  ? 'Case note saved and synchronized with CRBCL platform!'
                  : 'Note draft saved to encrypted offline storage.',
            ),
            backgroundColor: CrbclTokens.statusSuccess,
            duration: const Duration(seconds: 4),
          ),
        );
        Navigator.pop(context, true);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to save note draft: ${e.toString()}'),
            backgroundColor: CrbclTokens.statusError,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isSaving = false);
      }
    }
  }

  String _formatTimer(int secs) {
    final m = (secs ~/ 60).toString().padLeft(2, '0');
    final s = (secs % 60).toString().padLeft(2, '0');
    return '$m:$s';
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Draft Field Case Note'),
        actions: [
          IconButton(
            icon: const Icon(Icons.check),
            tooltip: 'Save Note to Outbox',
            onPressed: _isRecording || _isTranscribing ? null : _saveOfflineNote,
          ),
        ],
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              TextField(
                controller: _titleController,
                decoration: const InputDecoration(
                  labelText: 'Note Title *',
                  border: OutlineInputBorder(),
                ),
              ),
              const SizedBox(height: 12),

              // Speech-to-Text Input Aid Banner / Controls
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                  color: _isRecording
                      ? CrbclTokens.statusError.withValues(alpha: 0.12)
                      : _isTranscribing
                          ? colorScheme.primary.withValues(alpha: 0.12)
                          : colorScheme.surfaceContainerHighest,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(
                    color: _isRecording
                        ? CrbclTokens.statusError
                        : colorScheme.outlineVariant,
                  ),
                ),
                child: Row(
                  children: [
                    if (_isRecording) ...[
                      Container(
                        width: 10,
                        height: 10,
                        decoration: const BoxDecoration(
                          color: CrbclTokens.statusError,
                          shape: BoxShape.circle,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        'Recording (${_formatTimer(_recordingSeconds)})',
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          color: CrbclTokens.statusError,
                        ),
                      ),
                      const Spacer(),
                      TextButton.icon(
                        onPressed: _stopAndTranscribe,
                        icon: const Icon(Icons.stop, size: 18, color: CrbclTokens.statusError),
                        label: const Text('Stop', style: TextStyle(color: CrbclTokens.statusError)),
                      ),
                      TextButton(
                        onPressed: _cancelDictation,
                        child: Text('Cancel', style: TextStyle(color: colorScheme.onSurface.withValues(alpha: 0.6))),
                      ),
                    ] else if (_isTranscribing) ...[
                      const SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      ),
                      const SizedBox(width: 10),
                      Text(
                        'Transcribing speech...',
                        style: TextStyle(color: colorScheme.onSurface),
                      ),
                    ] else ...[
                      Icon(Icons.mic, color: colorScheme.primary, size: 20),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'Voice Dictation Assistant',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w500,
                            color: colorScheme.onSurface,
                          ),
                        ),
                      ),
                      ElevatedButton.icon(
                        onPressed: _startDictation,
                        icon: const Icon(Icons.mic, size: 16),
                        label: const Text('Dictate', style: TextStyle(fontSize: 12)),
                        style: ElevatedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                          visualDensity: VisualDensity.compact,
                        ),
                      ),
                    ],
                  ],
                ),
              ),
              const SizedBox(height: 12),

              Expanded(
                child: TextField(
                  controller: _summaryController,
                  maxLines: null,
                  expands: true,
                  textAlignVertical: TextAlignVertical.top,
                  decoration: const InputDecoration(
                    labelText: 'Field Narrative / Observations',
                    hintText: 'Type observations or tap Dictate to transcribe speech...',
                    border: OutlineInputBorder(),
                    alignLabelWithHint: true,
                  ),
                ),
              ),
              const SizedBox(height: 10),

              Row(
                children: [
                  Icon(Icons.info_outline, size: 14, color: colorScheme.onSurface.withValues(alpha: 0.5)),
                  const SizedBox(width: 6),
                  Expanded(
                    child: Text(
                      'Speech input aids drafting. Notes are never auto-signed or auto-approved.',
                      style: TextStyle(
                        fontSize: 11,
                        color: colorScheme.onSurface.withValues(alpha: 0.5),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 10),

              ElevatedButton.icon(
                onPressed: _isRecording || _isTranscribing || _isSaving ? null : _saveOfflineNote,
                icon: _isSaving
                    ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2))
                    : const Icon(Icons.save),
                label: Text(_isSaving ? 'Saving...' : 'Save Encrypted Note Draft'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: colorScheme.primary,
                  foregroundColor: colorScheme.onPrimary,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
