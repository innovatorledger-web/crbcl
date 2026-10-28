import 'dart:math';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../services/connectivity_service.dart';
import '../services/db_helper.dart';
import '../services/sync_engine.dart';
import '../services/theme_service.dart';

class VisitDraftScreen extends StatefulWidget {
  const VisitDraftScreen({super.key});

  @override
  State<VisitDraftScreen> createState() => _VisitDraftScreenState();
}

class _VisitDraftScreenState extends State<VisitDraftScreen> {
  final _formKey = GlobalKey<FormState>();

  String _entityType = 'HOME_VISIT';
  final _titleController = TextEditingController(text: 'Family Home Wellness Visit');
  final _locationController = TextEditingController(text: 'Cote First Nation');
  final _notesController = TextEditingController();
  final _caseIdController = TextEditingController();

  DateTime _scheduledTime = DateTime.now().add(const Duration(hours: 1));
  bool _isSaving = false;

  @override
  void dispose() {
    _titleController.dispose();
    _locationController.dispose();
    _notesController.dispose();
    _caseIdController.dispose();
    super.dispose();
  }

  String _generateTempUuid() {
    final rand = Random.secure();
    final bytes = List<int>.generate(16, (_) => rand.nextInt(256));
    bytes[6] = (bytes[6] & 0x0f) | 0x40;
    bytes[8] = (bytes[8] & 0x3f) | 0x80;
    final hex = bytes.map((b) => b.toRadixString(16).padLeft(2, '0')).join();
    return '${hex.substring(0, 8)}-${hex.substring(8, 12)}-${hex.substring(12, 16)}-${hex.substring(16, 20)}-${hex.substring(20)}';
  }

  Future<void> _selectDateTime(BuildContext context) async {
    final date = await showDatePicker(
      context: context,
      initialDate: _scheduledTime,
      firstDate: DateTime.now().subtract(const Duration(days: 7)),
      lastDate: DateTime.now().add(const Duration(days: 90)),
    );
    if (date != null && mounted) {
      final time = await showTimePicker(
        context: context,
        initialTime: TimeOfDay.fromDateTime(_scheduledTime),
      );
      if (time != null) {
        setState(() {
          _scheduledTime = DateTime(date.year, date.month, date.day, time.hour, time.minute);
        });
      }
    }
  }

  Future<void> _saveVisitDraft() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isSaving = true);

    final tempId = _generateTempUuid();
    final title = _titleController.text.trim();
    final location = _locationController.text.trim();
    final notes = _notesController.text.trim();
    final caseId = _caseIdController.text.trim();

    final payload = {
      'temp_id': tempId,
      'title': title,
      'location': location,
      'start_at': _scheduledTime.toIso8601String(),
      'end_at': _scheduledTime.add(const Duration(hours: 1)).toIso8601String(),
      'notes': notes,
      if (caseId.isNotEmpty) 'case_id': caseId,
    };

    final isHomeVisit = _entityType == 'HOME_VISIT';

    try {
      await LocalDatabaseHelper.instance.saveDraft(
        id: tempId,
        entityType: _entityType,
        title: title,
        subtitle: '${isHomeVisit ? "Home Visit" : "Follow-up Task"} • ${DateFormat("MMM d, yyyy h:mm a").format(_scheduledTime)}',
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
                  ? '${isHomeVisit ? "Home Visit" : "Follow-up Task"} saved and synchronized with CRBCL platform!'
                  : 'Saved offline ${isHomeVisit ? "Home Visit" : "Follow-up Task"} draft.',
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
            content: Text('Failed to save visit draft: ${e.toString()}'),
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

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final isHomeVisit = _entityType == 'HOME_VISIT';

    return Scaffold(
      appBar: AppBar(
        title: Text(isHomeVisit ? 'Schedule Home Visit (Offline)' : 'Create Follow-up Task (Offline)'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Entity Type Selector Toggle
              SegmentedButton<String>(
                segments: const [
                  ButtonSegment(
                    value: 'HOME_VISIT',
                    label: Text('Home Visit'),
                    icon: Icon(Icons.home_work),
                  ),
                  ButtonSegment(
                    value: 'FOLLOW_UP',
                    label: Text('Follow-up Task'),
                    icon: Icon(Icons.assignment_turned_in),
                  ),
                ],
                selected: {_entityType},
                onSelectionChanged: (set) {
                  setState(() {
                    _entityType = set.first;
                    if (_entityType == 'HOME_VISIT' && _titleController.text.contains('Follow-up')) {
                      _titleController.text = 'Family Home Wellness Visit';
                    } else if (_entityType == 'FOLLOW_UP' && _titleController.text.contains('Home')) {
                      _titleController.text = 'Caseworker Follow-up Task';
                    }
                  });
                },
              ),
              const SizedBox(height: 16),

              TextFormField(
                controller: _titleController,
                decoration: InputDecoration(
                  labelText: isHomeVisit ? 'Visit Title *' : 'Task Title *',
                  border: const OutlineInputBorder(),
                  prefixIcon: Icon(isHomeVisit ? Icons.home : Icons.task_alt),
                ),
                validator: (val) => val == null || val.trim().isEmpty ? 'Title is required' : null,
              ),
              const SizedBox(height: 12),

              InkWell(
                onTap: () => _selectDateTime(context),
                child: InputDecorator(
                  decoration: const InputDecoration(
                    labelText: 'Scheduled Date & Time',
                    border: OutlineInputBorder(),
                    prefixIcon: Icon(Icons.access_time),
                  ),
                  child: Text(
                    DateFormat('EEEE, MMMM d, yyyy • h:mm a').format(_scheduledTime),
                    style: TextStyle(color: colorScheme.onSurface),
                  ),
                ),
              ),
              const SizedBox(height: 12),

              TextFormField(
                controller: _locationController,
                decoration: const InputDecoration(
                  labelText: 'Location / Address',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.place),
                ),
              ),
              const SizedBox(height: 12),

              TextFormField(
                controller: _caseIdController,
                decoration: const InputDecoration(
                  labelText: 'Associated Case ID (Optional)',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.folder_shared),
                ),
              ),
              const SizedBox(height: 12),

              TextFormField(
                controller: _notesController,
                maxLines: 4,
                decoration: InputDecoration(
                  labelText: isHomeVisit ? 'Observation Notes & Agenda' : 'Task Description & Action Items',
                  border: const OutlineInputBorder(),
                  alignLabelWithHint: true,
                ),
              ),
              const SizedBox(height: 24),

              ElevatedButton.icon(
                onPressed: _isSaving ? null : _saveVisitDraft,
                icon: const Icon(Icons.save),
                label: Text(_isSaving ? 'Saving Draft...' : 'Save Encrypted Local Draft'),
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
