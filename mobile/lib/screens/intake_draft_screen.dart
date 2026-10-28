import 'dart:math';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../services/connectivity_service.dart';
import '../services/db_helper.dart';
import '../services/sync_engine.dart';
import '../services/theme_service.dart';

class IntakeDraftScreen extends StatefulWidget {
  const IntakeDraftScreen({super.key});

  @override
  State<IntakeDraftScreen> createState() => _IntakeDraftScreenState();
}

class _IntakeDraftScreenState extends State<IntakeDraftScreen> {
  final _formKey = GlobalKey<FormState>();

  final _summaryController = TextEditingController();
  final _communityController = TextEditingController(text: 'Cote First Nation');
  final _notesController = TextEditingController();

  DateTime _receivedDate = DateTime.now();
  String _receivedMethod = 'phone';
  String _priority = 'Medium';
  bool _immediateSafetyConcerns = false;
  bool _lawEnforcementInvolved = false;
  bool _isSaving = false;

  final List<String> _methodOptions = ['phone', 'in_person', 'email', 'fax', 'walk_in'];
  final List<String> _priorityOptions = ['Low', 'Medium', 'High', 'Urgent'];

  @override
  void dispose() {
    _summaryController.dispose();
    _communityController.dispose();
    _notesController.dispose();
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

  Future<void> _selectReceivedDate(BuildContext context) async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _receivedDate,
      firstDate: DateTime(2020),
      lastDate: DateTime.now(),
    );
    if (picked != null) {
      setState(() => _receivedDate = picked);
    }
  }

  Future<void> _saveIntakeDraft() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isSaving = true);

    final tempId = _generateTempUuid();
    final summary = _summaryController.text.trim();

    final payload = {
      'temp_id': tempId,
      'summary': summary,
      'received_date': DateFormat('yyyy-MM-dd').format(_receivedDate),
      'received_time': _receivedDate.toIso8601String(),
      'received_method': _receivedMethod,
      'community': _communityController.text.trim(),
      'priority': _priority,
      'risk_level': _priority == 'Urgent' ? 'High' : _priority,
      'immediate_safety_concerns': _immediateSafetyConcerns,
      'law_enforcement_involved': _lawEnforcementInvolved,
      'notes': _notesController.text.trim(),
    };

    try {
      await LocalDatabaseHelper.instance.saveDraft(
        id: tempId,
        entityType: 'INTAKE',
        title: summary.length > 40 ? '${summary.substring(0, 40)}...' : summary,
        subtitle: 'Priority: $_priority • Method: $_receivedMethod • Date: ${DateFormat('yyyy-MM-dd').format(_receivedDate)}',
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
                  ? 'Intake referral saved and synchronized with CRBCL platform!'
                  : 'Saved offline intake draft. Referral number (INT-YYYY-NNNNNN) will be assigned on sync.',
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
            content: Text('Failed to save intake draft: ${e.toString()}'),
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
    final isDark = theme.brightness == Brightness.dark;

    return Scaffold(
      appBar: AppBar(
        title: const Text('New Intake Draft (Offline)'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: colorScheme.primary.withValues(alpha: 0.08),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(
                    color: colorScheme.primary.withValues(alpha: 0.25),
                  ),
                ),
                child: Row(
                  children: [
                    Icon(Icons.info_outline, color: colorScheme.primary, size: 20),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Text(
                        'Canonical Referral Number (INT-YYYY-NNNNNN) will be allocated by the server sequence upon online synchronization.',
                        style: TextStyle(
                          fontSize: 12,
                          color: colorScheme.onSurface.withValues(alpha: 0.8),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),

              TextFormField(
                controller: _summaryController,
                maxLines: 3,
                decoration: const InputDecoration(
                  labelText: 'Intake / Referral Summary *',
                  border: OutlineInputBorder(),
                  alignLabelWithHint: true,
                ),
                validator: (val) => val == null || val.trim().isEmpty ? 'Summary is required' : null,
              ),
              const SizedBox(height: 12),

              InkWell(
                onTap: () => _selectReceivedDate(context),
                child: InputDecorator(
                  decoration: const InputDecoration(
                    labelText: 'Received Date',
                    border: OutlineInputBorder(),
                    prefixIcon: Icon(Icons.calendar_today),
                  ),
                  child: Text(
                    DateFormat('MMMM d, yyyy').format(_receivedDate),
                    style: TextStyle(color: colorScheme.onSurface),
                  ),
                ),
              ),
              const SizedBox(height: 12),

              DropdownButtonFormField<String>(
                initialValue: _receivedMethod,
                decoration: const InputDecoration(
                  labelText: 'Received Method',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.contact_phone),
                ),
                dropdownColor: isDark ? CrbclTokens.darkCard : Colors.white,
                items: _methodOptions
                    .map((m) => DropdownMenuItem(
                          value: m,
                          child: Text(
                            m.replaceAll('_', ' ').toUpperCase(),
                            style: TextStyle(color: colorScheme.onSurface),
                          ),
                        ))
                    .toList(),
                onChanged: (val) {
                  if (val != null) setState(() => _receivedMethod = val);
                },
              ),
              const SizedBox(height: 12),

              DropdownButtonFormField<String>(
                initialValue: _priority,
                decoration: const InputDecoration(
                  labelText: 'Priority Level',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.flag),
                ),
                dropdownColor: isDark ? CrbclTokens.darkCard : Colors.white,
                items: _priorityOptions
                    .map((p) => DropdownMenuItem(
                          value: p,
                          child: Text(p, style: TextStyle(color: colorScheme.onSurface)),
                        ))
                    .toList(),
                onChanged: (val) {
                  if (val != null) setState(() => _priority = val);
                },
              ),
              const SizedBox(height: 12),

              TextFormField(
                controller: _communityController,
                decoration: const InputDecoration(
                  labelText: 'Community',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.location_on),
                ),
              ),
              const SizedBox(height: 12),

              SwitchListTile(
                title: const Text('Immediate Safety Concerns'),
                subtitle: const Text('Check if child or family requires emergency intervention'),
                value: _immediateSafetyConcerns,
                activeTrackColor: colorScheme.primary,
                onChanged: (val) => setState(() => _immediateSafetyConcerns = val),
              ),
              SwitchListTile(
                title: const Text('Law Enforcement Involved'),
                subtitle: const Text('Check if RCMP / police file is linked'),
                value: _lawEnforcementInvolved,
                activeTrackColor: colorScheme.primary,
                onChanged: (val) => setState(() => _lawEnforcementInvolved = val),
              ),
              const SizedBox(height: 12),

              TextFormField(
                controller: _notesController,
                maxLines: 3,
                decoration: const InputDecoration(
                  labelText: 'Intake Notes & Next Steps',
                  border: OutlineInputBorder(),
                  alignLabelWithHint: true,
                ),
              ),
              const SizedBox(height: 24),

              ElevatedButton.icon(
                onPressed: _isSaving ? null : _saveIntakeDraft,
                icon: const Icon(Icons.save),
                label: Text(_isSaving ? 'Saving Draft...' : 'Save Encrypted Intake Draft'),
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
