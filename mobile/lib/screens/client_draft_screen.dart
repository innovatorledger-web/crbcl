import 'dart:math';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../services/connectivity_service.dart';
import '../services/db_helper.dart';
import '../services/sync_engine.dart';
import '../services/theme_service.dart';

class ClientDraftScreen extends StatefulWidget {
  const ClientDraftScreen({super.key});

  @override
  State<ClientDraftScreen> createState() => _ClientDraftScreenState();
}

class _ClientDraftScreenState extends State<ClientDraftScreen> {
  final _formKey = GlobalKey<FormState>();

  final _firstNameController = TextEditingController();
  final _lastNameController = TextEditingController();
  final _phoneController = TextEditingController();
  final _emailController = TextEditingController();
  final _addressController = TextEditingController();
  final _cityController = TextEditingController(text: 'Kamsack');
  final _treatyController = TextEditingController();
  final _bandNationController = TextEditingController(text: 'Cote First Nation');
  final _notesController = TextEditingController();

  DateTime? _selectedDob;
  String _selectedGender = 'Prefer not to say';
  bool _isSaving = false;

  final List<String> _genderOptions = [
    'Female',
    'Male',
    'Two-Spirit',
    'Non-Binary',
    'Prefer not to say',
    'Other',
  ];

  @override
  void dispose() {
    _firstNameController.dispose();
    _lastNameController.dispose();
    _phoneController.dispose();
    _emailController.dispose();
    _addressController.dispose();
    _cityController.dispose();
    _treatyController.dispose();
    _bandNationController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  String _generateTempUuid() {
    final rand = Random.secure();
    final bytes = List<int>.generate(16, (_) => rand.nextInt(256));
    // Set UUID version 4
    bytes[6] = (bytes[6] & 0x0f) | 0x40;
    bytes[8] = (bytes[8] & 0x3f) | 0x80;
    final hex = bytes.map((b) => b.toRadixString(16).padLeft(2, '0')).join();
    return '${hex.substring(0, 8)}-${hex.substring(8, 12)}-${hex.substring(12, 16)}-${hex.substring(16, 20)}-${hex.substring(20)}';
  }

  Future<void> _selectDob(BuildContext context) async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _selectedDob ?? DateTime(2005, 1, 1),
      firstDate: DateTime(1920),
      lastDate: DateTime.now(),
    );
    if (picked != null) {
      setState(() => _selectedDob = picked);
    }
  }

  Future<void> _saveClientDraft() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isSaving = true);

    final tempId = _generateTempUuid();
    final firstName = _firstNameController.text.trim();
    final lastName = _lastNameController.text.trim();

    final payload = {
      'temp_id': tempId,
      'first_name': firstName,
      'last_name': lastName,
      'date_of_birth': _selectedDob != null ? DateFormat('yyyy-MM-dd').format(_selectedDob!) : null,
      'gender': _selectedGender,
      'phone': _phoneController.text.trim(),
      'email': _emailController.text.trim(),
      'address': _addressController.text.trim(),
      'city': _cityController.text.trim(),
      'province': 'Saskatchewan',
      'treaty_number': _treatyController.text.trim(),
      'band_nation': _bandNationController.text.trim(),
      'indigenous_identity': 'First Nations',
      'notes': _notesController.text.trim(),
    };

    try {
      await LocalDatabaseHelper.instance.saveDraft(
        id: tempId,
        entityType: 'CLIENT',
        title: '$firstName $lastName',
        subtitle: 'Draft Client • Treaty: ${_treatyController.text.trim().isNotEmpty ? _treatyController.text.trim() : "None"}',
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
      } catch (_) {
        // Safe offline preservation
      }

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              syncedOnline
                  ? 'Client $firstName $lastName saved and synchronized with CRBCL platform!'
                  : 'Saved local draft for $firstName $lastName. Permanent ID will be assigned on sync.',
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
            content: Text('Failed to save client draft: ${e.toString()}'),
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
        title: const Text('New Client Draft (Offline)'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Notice banner
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
                        'Temporary identifier assigned locally. Authoritative 10-digit CRBCL Person ID will be assigned upon synchronization.',
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
                controller: _firstNameController,
                decoration: const InputDecoration(
                  labelText: 'First Name *',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.person),
                ),
                validator: (val) => val == null || val.trim().isEmpty ? 'First name is required' : null,
              ),
              const SizedBox(height: 12),

              TextFormField(
                controller: _lastNameController,
                decoration: const InputDecoration(
                  labelText: 'Last Name *',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.person_outline),
                ),
                validator: (val) => val == null || val.trim().isEmpty ? 'Last name is required' : null,
              ),
              const SizedBox(height: 12),

              // Date of Birth picker
              InkWell(
                onTap: () => _selectDob(context),
                child: InputDecorator(
                  decoration: const InputDecoration(
                    labelText: 'Date of Birth',
                    border: OutlineInputBorder(),
                    prefixIcon: Icon(Icons.calendar_today),
                  ),
                  child: Text(
                    _selectedDob != null ? DateFormat('MMMM d, yyyy').format(_selectedDob!) : 'Select Date of Birth',
                    style: TextStyle(
                      color: _selectedDob != null
                          ? colorScheme.onSurface
                          : colorScheme.onSurface.withValues(alpha: 0.5),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 12),

              DropdownButtonFormField<String>(
                initialValue: _selectedGender,
                decoration: const InputDecoration(
                  labelText: 'Gender',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.wc),
                ),
                dropdownColor: isDark ? CrbclTokens.darkCard : Colors.white,
                items: _genderOptions
                    .map((g) => DropdownMenuItem(
                          value: g,
                          child: Text(g, style: TextStyle(color: colorScheme.onSurface)),
                        ))
                    .toList(),
                onChanged: (val) {
                  if (val != null) setState(() => _selectedGender = val);
                },
              ),
              const SizedBox(height: 12),

              TextFormField(
                controller: _phoneController,
                keyboardType: TextInputType.phone,
                decoration: const InputDecoration(
                  labelText: 'Phone Number',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.phone),
                ),
              ),
              const SizedBox(height: 12),

              TextFormField(
                controller: _emailController,
                keyboardType: TextInputType.emailAddress,
                decoration: const InputDecoration(
                  labelText: 'Email Address',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.email),
                ),
              ),
              const SizedBox(height: 12),

              TextFormField(
                controller: _addressController,
                decoration: const InputDecoration(
                  labelText: 'Street Address',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.home),
                ),
              ),
              const SizedBox(height: 12),

              TextFormField(
                controller: _cityController,
                decoration: const InputDecoration(
                  labelText: 'City / Community',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.location_city),
                ),
              ),
              const SizedBox(height: 12),

              TextFormField(
                controller: _treatyController,
                decoration: const InputDecoration(
                  labelText: 'Treaty / Status Card Number',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.badge),
                ),
              ),
              const SizedBox(height: 12),

              TextFormField(
                controller: _bandNationController,
                decoration: const InputDecoration(
                  labelText: 'Band / First Nation',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.flag),
                ),
              ),
              const SizedBox(height: 12),

              TextFormField(
                controller: _notesController,
                maxLines: 3,
                decoration: const InputDecoration(
                  labelText: 'Field Notes & Observations',
                  border: OutlineInputBorder(),
                  alignLabelWithHint: true,
                ),
              ),
              const SizedBox(height: 24),

              ElevatedButton.icon(
                onPressed: _isSaving ? null : _saveClientDraft,
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
