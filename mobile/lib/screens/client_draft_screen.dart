import 'dart:convert';
import 'dart:io';
import 'dart:math';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import 'package:intl/intl.dart';
import '../services/auth_service.dart';
import '../services/connectivity_service.dart';
import '../services/db_helper.dart';
import '../services/image_security.dart';
import '../services/sync_engine.dart';
import '../services/theme_service.dart';

class ClientDraftScreen extends StatefulWidget {
  final Map<String, dynamic>? initialClient;

  const ClientDraftScreen({super.key, this.initialClient});

  @override
  State<ClientDraftScreen> createState() => _ClientDraftScreenState();
}

class _ClientDraftScreenState extends State<ClientDraftScreen> {
  final _formKey = GlobalKey<FormState>();
  final _picker = ImagePicker();

  // Basic Identity
  final _firstNameController = TextEditingController();
  final _middleNameController = TextEditingController();
  final _lastNameController = TextEditingController();
  final _preferredNameController = TextEditingController();
  final _aliasesController = TextEditingController();

  // Demographics
  DateTime? _selectedDob;
  String _selectedGender = 'Prefer not to say';
  final _placeOfBirthController = TextEditingController();
  String _selectedLanguage = 'English';

  // Indigenous Profile & Culture
  String _selectedIndigenousIdentity = 'First Nations';
  final _treatyController = TextEditingController();
  final _bandNationController = TextEditingController(text: 'Cote First Nation');
  final _culturalConnectionsController = TextEditingController();
  final _ceremoniesController = TextEditingController();
  final _eldersConnectedController = TextEditingController();
  final _landActivitiesController = TextEditingController();

  // Contact & Emergency
  final _phoneController = TextEditingController();
  final _emailController = TextEditingController();
  final _emergNameController = TextEditingController();
  final _emergPhoneController = TextEditingController();
  final _emergRelController = TextEditingController();

  // Address
  final _address1Controller = TextEditingController();
  final _address2Controller = TextEditingController();
  final _cityController = TextEditingController(text: 'Kamsack');
  final _provinceController = TextEditingController(text: 'Saskatchewan');
  final _postalCodeController = TextEditingController();
  bool _isOnReserve = false;

  // Health & Physical Description
  final _healthCardController = TextEditingController();
  final _eyeColourController = TextEditingController();
  final _hairColourController = TextEditingController();
  final _heightController = TextEditingController();
  final _weightController = TextEditingController();
  final _distinguishingMarksController = TextEditingController();

  // Intake / Proposal Context
  String _selectedRiskLevel = 'Low';
  final _notesController = TextEditingController();

  // Photo
  File? _photoFile;
  String? _existingPhotoUrl;
  bool _isSaving = false;

  final List<String> _genderOptions = [
    'Female',
    'Male',
    'Two-Spirit',
    'Non-Binary',
    'Prefer not to say',
    'Other',
  ];

  final List<String> _languageOptions = [
    'English',
    'Cree',
    'Saulteaux',
    'Dene',
    'Dakota',
    'Lakota',
    'Michif',
    'French',
    'Other',
  ];

  final List<String> _indigenousIdentityOptions = [
    'First Nations',
    'Métis',
    'Inuit',
    'Non-Indigenous',
    'Other',
  ];

  final List<String> _riskLevels = [
    'Low',
    'Medium',
    'High',
  ];

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final args = ModalRoute.of(context)?.settings.arguments;
      final client = widget.initialClient ?? (args is Map<String, dynamic> ? args : null);
      if (client != null) {
        _populateFromClient(client);
      }
    });
  }

  void _populateFromClient(Map<String, dynamic> c) {
    setState(() {
      _firstNameController.text = c['first_name'] ?? '';
      _middleNameController.text = c['middle_name'] ?? '';
      _lastNameController.text = c['last_name'] ?? '';
      _preferredNameController.text = c['preferred_name'] ?? '';
      _aliasesController.text = c['aliases'] ?? '';

      if (c['date_of_birth'] != null && c['date_of_birth'].toString().isNotEmpty) {
        try {
          _selectedDob = DateTime.parse(c['date_of_birth'].toString());
        } catch (_) {}
      }

      if (_genderOptions.contains(c['gender'])) {
        _selectedGender = c['gender'];
      }
      _placeOfBirthController.text = c['place_of_birth'] ?? '';
      if (_languageOptions.contains(c['preferred_language'])) {
        _selectedLanguage = c['preferred_language'];
      }

      if (_indigenousIdentityOptions.contains(c['indigenous_identity'])) {
        _selectedIndigenousIdentity = c['indigenous_identity'];
      }
      _treatyController.text = c['treaty_number'] ?? '';
      _bandNationController.text = c['band_nation'] ?? 'Cote First Nation';

      // Cultural
      final cult = c['cultural_profile'] is Map ? c['cultural_profile'] : null;
      _culturalConnectionsController.text = cult?['cultural_connections'] ?? c['cultural_connections'] ?? '';
      _ceremoniesController.text = cult?['ceremonies'] ?? c['ceremonies'] ?? '';
      _eldersConnectedController.text = cult?['elders_connected'] ?? c['elders_connected'] ?? '';
      _landActivitiesController.text = cult?['land_based_activities'] ?? c['land_based_activities'] ?? '';

      // Contact
      _phoneController.text = c['phone'] ?? '';
      _emailController.text = c['email'] ?? '';
      _emergNameController.text = c['emergency_contact_name'] ?? '';
      _emergPhoneController.text = c['emergency_contact_phone'] ?? '';
      _emergRelController.text = c['emergency_contact_relationship'] ?? '';

      // Address
      final addr = c['primary_address'] is Map ? c['primary_address'] : null;
      _address1Controller.text = addr?['address_line_1'] ?? c['address'] ?? '';
      _address2Controller.text = addr?['address_line_2'] ?? '';
      _cityController.text = addr?['city'] ?? c['city'] ?? 'Regina';
      _provinceController.text = addr?['province'] ?? c['province'] ?? 'Saskatchewan';
      _postalCodeController.text = addr?['postal_code'] ?? '';
      _isOnReserve = addr?['on_reserve'] == true || c['on_reserve'] == true;

      // Health & Physical
      _healthCardController.text = c['health_card_number'] ?? '';
      final phys = c['physical_description'] is Map ? c['physical_description'] : null;
      _eyeColourController.text = phys?['eye_colour'] ?? '';
      _hairColourController.text = phys?['hair_colour'] ?? '';
      _heightController.text = phys?['height_cm']?.toString() ?? '';
      _weightController.text = phys?['weight_kg']?.toString() ?? '';
      _distinguishingMarksController.text = phys?['distinguishing_marks'] ?? phys?['scars'] ?? '';

      // Proposal Context
      if (_riskLevels.contains(c['risk_level'])) {
        _selectedRiskLevel = c['risk_level'];
      }
      _notesController.text = c['submission_notes'] ?? c['notes'] ?? '';

      _existingPhotoUrl = c['photo_url'];
    });
  }

  @override
  void dispose() {
    _firstNameController.dispose();
    _middleNameController.dispose();
    _lastNameController.dispose();
    _preferredNameController.dispose();
    _aliasesController.dispose();
    _placeOfBirthController.dispose();
    _treatyController.dispose();
    _bandNationController.dispose();
    _culturalConnectionsController.dispose();
    _ceremoniesController.dispose();
    _eldersConnectedController.dispose();
    _landActivitiesController.dispose();
    _phoneController.dispose();
    _emailController.dispose();
    _emergNameController.dispose();
    _emergPhoneController.dispose();
    _emergRelController.dispose();
    _address1Controller.dispose();
    _address2Controller.dispose();
    _cityController.dispose();
    _provinceController.dispose();
    _postalCodeController.dispose();
    _healthCardController.dispose();
    _eyeColourController.dispose();
    _hairColourController.dispose();
    _heightController.dispose();
    _weightController.dispose();
    _distinguishingMarksController.dispose();
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

  Future<void> _selectDob(BuildContext context) async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _selectedDob ?? DateTime(2005, 1, 1),
      firstDate: DateTime(1915),
      lastDate: DateTime.now(),
    );
    if (picked != null) {
      setState(() => _selectedDob = picked);
    }
  }

  Future<void> _pickImage(ImageSource source) async {
    try {
      final picked = await _picker.pickImage(
        source: source,
        maxWidth: 1024,
        maxHeight: 1024,
        imageQuality: 85,
      );
      if (picked != null) {
        final rawFile = File(picked.path);
        final sanitized = await ImageSecurityHelper.stripExifMetadata(rawFile);
        setState(() {
          _photoFile = sanitized;
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Could not access photo: $e')),
        );
      }
    }
  }

  void _showPhotoOptions() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (ctx) => SafeArea(
        child: Wrap(
          children: [
            ListTile(
              leading: const Icon(Icons.camera_alt),
              title: const Text('Take Photo with Camera'),
              onTap: () {
                Navigator.pop(ctx);
                _pickImage(ImageSource.camera);
              },
            ),
            ListTile(
              leading: const Icon(Icons.photo_library),
              title: const Text('Choose from Photo Gallery'),
              onTap: () {
                Navigator.pop(ctx);
                _pickImage(ImageSource.gallery);
              },
            ),
            if (_photoFile != null || _existingPhotoUrl != null)
              ListTile(
                leading: const Icon(Icons.delete_outline, color: Colors.red),
                title: const Text('Remove Photo', style: TextStyle(color: Colors.red)),
                onTap: () {
                  Navigator.pop(ctx);
                  setState(() {
                    _photoFile = null;
                    _existingPhotoUrl = null;
                  });
                },
              ),
          ],
        ),
      ),
    );
  }

  Future<void> _saveClientDraft() async {
    if (!_formKey.currentState!.validate()) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please complete all required fields.')),
      );
      return;
    }

    setState(() => _isSaving = true);

    final firstName = _firstNameController.text.trim();
    final lastName = _lastNameController.text.trim();
    final dobStr = _selectedDob != null ? DateFormat('yyyy-MM-dd').format(_selectedDob!) : null;

    final personData = {
      'first_name': firstName,
      'middle_name': _middleNameController.text.trim().isNotEmpty ? _middleNameController.text.trim() : null,
      'last_name': lastName,
      'preferred_name': _preferredNameController.text.trim().isNotEmpty ? _preferredNameController.text.trim() : null,
      'aliases': _aliasesController.text.trim().isNotEmpty ? _aliasesController.text.trim() : null,
      'date_of_birth': dobStr,
      'gender': _selectedGender,
      'place_of_birth': _placeOfBirthController.text.trim().isNotEmpty ? _placeOfBirthController.text.trim() : null,
      'preferred_language': _selectedLanguage,
      'indigenous_identity': _selectedIndigenousIdentity,
      'treaty_number': _treatyController.text.trim().isNotEmpty ? _treatyController.text.trim() : null,
      'band_nation': _bandNationController.text.trim().isNotEmpty ? _bandNationController.text.trim() : 'Cote First Nation',
      'health_card_number': _healthCardController.text.trim().isNotEmpty ? _healthCardController.text.trim() : null,
      'phone': _phoneController.text.trim().isNotEmpty ? _phoneController.text.trim() : null,
      'email': _emailController.text.trim().isNotEmpty ? _emailController.text.trim() : null,
      'emergency_contact_name': _emergNameController.text.trim().isNotEmpty ? _emergNameController.text.trim() : null,
      'emergency_contact_phone': _emergPhoneController.text.trim().isNotEmpty ? _emergPhoneController.text.trim() : null,
      'emergency_contact_relationship': _emergRelController.text.trim().isNotEmpty ? _emergRelController.text.trim() : null,
      'primary_address': {
        'address_line_1': _address1Controller.text.trim().isNotEmpty ? _address1Controller.text.trim() : 'General Delivery',
        'address_line_2': _address2Controller.text.trim().isNotEmpty ? _address2Controller.text.trim() : null,
        'city': _cityController.text.trim().isNotEmpty ? _cityController.text.trim() : 'Regina',
        'province': _provinceController.text.trim().isNotEmpty ? _provinceController.text.trim() : 'Saskatchewan',
        'postal_code': _postalCodeController.text.trim().isNotEmpty ? _postalCodeController.text.trim() : null,
        'on_reserve': _isOnReserve,
      },
      'cultural_profile': {
        'cultural_connections': _culturalConnectionsController.text.trim().isNotEmpty ? _culturalConnectionsController.text.trim() : null,
        'ceremonies': _ceremoniesController.text.trim().isNotEmpty ? _ceremoniesController.text.trim() : null,
        'elders_connected': _eldersConnectedController.text.trim().isNotEmpty ? _eldersConnectedController.text.trim() : null,
        'land_based_activities': _landActivitiesController.text.trim().isNotEmpty ? _landActivitiesController.text.trim() : null,
      },
      'physical_description': {
        'eye_colour': _eyeColourController.text.trim().isNotEmpty ? _eyeColourController.text.trim() : null,
        'hair_colour': _hairColourController.text.trim().isNotEmpty ? _hairColourController.text.trim() : null,
        'height_cm': double.tryParse(_heightController.text.trim()),
        'weight_kg': double.tryParse(_weightController.text.trim()),
        'distinguishing_marks': _distinguishingMarksController.text.trim().isNotEmpty ? _distinguishingMarksController.text.trim() : null,
      },
    };

    final clientPayload = {
      'person': personData,
      'risk_level': _selectedRiskLevel,
      'submission_notes': _notesController.text.trim().isNotEmpty ? _notesController.text.trim() : 'Submitted from Mobile App',
    };

    bool syncedOnline = false;
    String? createdClientId;

    try {
      final isOnline = await ConnectivityService.instance.checkConnectivity();
      final token = await MobileAuthService.instance.getAccessToken();
      final serverUrl = (await MobileAuthService.instance.getServerUrl()).replaceAll(RegExp(r'/+$'), '');

      if (isOnline && token != null && token.isNotEmpty) {
        // Attempt direct submission to backend platform
        final uri = Uri.parse('$serverUrl/api/v1/clients/submit-new');
        final response = await http
            .post(
              uri,
              headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer $token',
              },
              body: jsonEncode(clientPayload),
            )
            .timeout(const Duration(seconds: 20));

        if (response.statusCode == 200 || response.statusCode == 201) {
          final resData = jsonDecode(response.body);
          createdClientId = resData['id']?.toString();
          syncedOnline = true;

          // If photo was taken/selected, upload directly to client photo endpoint
          if (_photoFile != null && createdClientId != null) {
            try {
              final photoUri = Uri.parse('$serverUrl/api/v1/clients/$createdClientId/photo');
              final request = http.MultipartRequest('POST', photoUri);
              request.headers['Authorization'] = 'Bearer $token';
              request.files.add(await http.MultipartFile.fromPath('file', _photoFile!.path));
              await request.send().timeout(const Duration(seconds: 20));
            } catch (photoErr) {
              // Non-fatal photo upload warning
            }
          }
        }
      }
    } catch (_) {
      syncedOnline = false;
    }

    // Always preserve locally in SQLite drafts
    final tempId = createdClientId ?? _generateTempUuid();
    final localDraftPayload = {
      'temp_id': tempId,
      'first_name': firstName,
      'last_name': lastName,
      'date_of_birth': dobStr,
      'gender': _selectedGender,
      'phone': _phoneController.text.trim(),
      'email': _emailController.text.trim(),
      'address': _address1Controller.text.trim(),
      'city': _cityController.text.trim(),
      'province': _provinceController.text.trim(),
      'treaty_number': _treatyController.text.trim(),
      'band_nation': _bandNationController.text.trim(),
      'indigenous_identity': _selectedIndigenousIdentity,
      'risk_level': _selectedRiskLevel,
      'notes': _notesController.text.trim(),
      'photo_path': _photoFile?.path,
    };

    try {
      await LocalDatabaseHelper.instance.saveDraft(
        id: tempId,
        entityType: 'CLIENT',
        title: '$firstName $lastName',
        subtitle: 'Treaty: ${_treatyController.text.trim().isNotEmpty ? _treatyController.text.trim() : "None"} • ${_bandNationController.text.trim()}',
        payload: localDraftPayload,
      );

      if (!syncedOnline) {
        // Trigger background sync push
        try {
          await SyncEngine().pushPendingQueue();
        } catch (_) {}
      }

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              syncedOnline
                  ? 'Client $firstName $lastName successfully saved and synced to CRBCL platform!'
                  : 'Client $firstName $lastName saved as local offline draft. Will sync when online.',
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
            content: Text('Error saving client: $e'),
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

  Widget _buildSectionHeader(String title, IconData icon, ColorScheme colorScheme) {
    return Padding(
      padding: const EdgeInsets.only(top: 20, bottom: 10),
      child: Row(
        children: [
          Icon(icon, size: 18, color: colorScheme.primary),
          const SizedBox(width: 8),
          Text(
            title,
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.bold,
              color: colorScheme.primary,
              letterSpacing: 0.3,
            ),
          ),
          const SizedBox(width: 8),
          Expanded(child: Divider(color: colorScheme.primary.withValues(alpha: 0.2))),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    final isEditMode = widget.initialClient != null;

    return Scaffold(
      appBar: AppBar(
        title: Text(isEditMode ? 'Edit Client Record' : 'Register Client • Full File'),
        actions: [
          IconButton(
            icon: const Icon(Icons.check),
            tooltip: 'Save Client',
            onPressed: _isSaving ? null : _saveClientDraft,
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Photo Upload & Avatar Preview
              Center(
                child: Column(
                  children: [
                    Stack(
                      children: [
                        CircleAvatar(
                          radius: 46,
                          backgroundColor: colorScheme.primary.withValues(alpha: 0.12),
                          backgroundImage: _photoFile != null
                              ? FileImage(_photoFile!)
                              : (_existingPhotoUrl != null && _existingPhotoUrl!.isNotEmpty
                                  ? NetworkImage(_existingPhotoUrl!) as ImageProvider
                                  : null),
                          child: (_photoFile == null && (_existingPhotoUrl == null || _existingPhotoUrl!.isEmpty))
                              ? Icon(Icons.person, size: 48, color: colorScheme.primary)
                              : null,
                        ),
                        PositionedDirectional(
                          bottom: 0,
                          end: 0,
                          child: InkWell(
                            onTap: _showPhotoOptions,
                            borderRadius: BorderRadius.circular(20),
                            child: CircleAvatar(
                              radius: 16,
                              backgroundColor: colorScheme.primary,
                              child: const Icon(Icons.camera_alt, size: 16, color: Colors.white),
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    TextButton.icon(
                      onPressed: _showPhotoOptions,
                      icon: const Icon(Icons.photo_camera, size: 16),
                      label: Text(
                        _photoFile != null || _existingPhotoUrl != null ? 'Change Client Photo' : 'Add Client Photo (Camera / Gallery)',
                        style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
                      ),
                    ),
                  ],
                ),
              ),

              // Section 1: Legal Identity & Names
              _buildSectionHeader('Legal Identity & Names', Icons.badge_outlined, colorScheme),
              TextFormField(
                controller: _firstNameController,
                decoration: const InputDecoration(
                  labelText: 'Legal First Name *',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.person),
                ),
                validator: (val) => val == null || val.trim().isEmpty ? 'Legal First Name is required' : null,
              ),
              const SizedBox(height: 12),

              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      controller: _middleNameController,
                      decoration: const InputDecoration(
                        labelText: 'Middle Name(s)',
                        border: OutlineInputBorder(),
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: TextFormField(
                      controller: _lastNameController,
                      decoration: const InputDecoration(
                        labelText: 'Legal Last Name *',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.person_outline),
                      ),
                      validator: (val) => val == null || val.trim().isEmpty ? 'Legal Last Name is required' : null,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),

              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      controller: _preferredNameController,
                      decoration: const InputDecoration(
                        labelText: 'Preferred / Chosen Name',
                        border: OutlineInputBorder(),
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: TextFormField(
                      controller: _aliasesController,
                      decoration: const InputDecoration(
                        labelText: 'Aliases / Nicknames',
                        border: OutlineInputBorder(),
                      ),
                    ),
                  ),
                ],
              ),

              // Section 2: Demographics
              _buildSectionHeader('Demographics', Icons.cake_outlined, colorScheme),
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

              Row(
                children: [
                  Expanded(
                    child: DropdownButtonFormField<String>(
                      initialValue: _selectedGender,
                      decoration: const InputDecoration(
                        labelText: 'Gender Identity',
                        border: OutlineInputBorder(),
                      ),
                      items: _genderOptions
                          .map((g) => DropdownMenuItem(value: g, child: Text(g, style: const TextStyle(fontSize: 13))))
                          .toList(),
                      onChanged: (val) {
                        if (val != null) setState(() => _selectedGender = val);
                      },
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: DropdownButtonFormField<String>(
                      initialValue: _selectedLanguage,
                      decoration: const InputDecoration(
                        labelText: 'Primary Language',
                        border: OutlineInputBorder(),
                      ),
                      items: _languageOptions
                          .map((l) => DropdownMenuItem(value: l, child: Text(l, style: const TextStyle(fontSize: 13))))
                          .toList(),
                      onChanged: (val) {
                        if (val != null) setState(() => _selectedLanguage = val);
                      },
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),

              TextFormField(
                controller: _placeOfBirthController,
                decoration: const InputDecoration(
                  labelText: 'Place of Birth (Town / City / Reserve)',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.location_on_outlined),
                ),
              ),

              // Section 3: Indigenous Identity & Heritage
              _buildSectionHeader('Indigenous Heritage & Culture', Icons.flag_outlined, colorScheme),
              DropdownButtonFormField<String>(
                initialValue: _selectedIndigenousIdentity,
                decoration: const InputDecoration(
                  labelText: 'Indigenous Identity',
                  border: OutlineInputBorder(),
                ),
                items: _indigenousIdentityOptions
                    .map((id) => DropdownMenuItem(value: id, child: Text(id, style: const TextStyle(fontSize: 13))))
                    .toList(),
                onChanged: (val) {
                  if (val != null) setState(() => _selectedIndigenousIdentity = val);
                },
              ),
              const SizedBox(height: 12),

              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      controller: _treatyController,
                      decoration: const InputDecoration(
                        labelText: 'Treaty / Status Card #',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.badge_outlined),
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: TextFormField(
                      controller: _bandNationController,
                      decoration: const InputDecoration(
                        labelText: 'Band / First Nation',
                        border: OutlineInputBorder(),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),

              TextFormField(
                controller: _culturalConnectionsController,
                maxLines: 2,
                decoration: const InputDecoration(
                  labelText: 'Cultural Connections & Teachings',
                  border: OutlineInputBorder(),
                  hintText: 'e.g. Clan, Pipe Carrier, Traditional Knowledge...',
                ),
              ),
              const SizedBox(height: 12),

              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      controller: _ceremoniesController,
                      decoration: const InputDecoration(
                        labelText: 'Ceremonies & Protocols',
                        border: OutlineInputBorder(),
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: TextFormField(
                      controller: _eldersConnectedController,
                      decoration: const InputDecoration(
                        labelText: 'Elders / Knowledge Keepers',
                        border: OutlineInputBorder(),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),

              TextFormField(
                controller: _landActivitiesController,
                decoration: const InputDecoration(
                  labelText: 'Land-Based Activities',
                  border: OutlineInputBorder(),
                  hintText: 'e.g. Hunting, Medicine Picking, Trapping, Canoeing...',
                ),
              ),

              // Section 4: Contact & Emergency
              _buildSectionHeader('Contact & Emergency Support', Icons.phone_outlined, colorScheme),
              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      controller: _phoneController,
                      keyboardType: TextInputType.phone,
                      decoration: const InputDecoration(
                        labelText: 'Primary Phone',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.phone),
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: TextFormField(
                      controller: _emailController,
                      keyboardType: TextInputType.emailAddress,
                      decoration: const InputDecoration(
                        labelText: 'Email Address',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.email_outlined),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),

              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      controller: _emergNameController,
                      decoration: const InputDecoration(
                        labelText: 'Emergency Contact Name',
                        border: OutlineInputBorder(),
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: TextFormField(
                      controller: _emergRelController,
                      decoration: const InputDecoration(
                        labelText: 'Relationship',
                        border: OutlineInputBorder(),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),

              TextFormField(
                controller: _emergPhoneController,
                keyboardType: TextInputType.phone,
                decoration: const InputDecoration(
                  labelText: 'Emergency Contact Phone',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.contact_phone_outlined),
                ),
              ),

              // Section 5: Primary Address
              _buildSectionHeader('Primary Residence', Icons.home_outlined, colorScheme),
              TextFormField(
                controller: _address1Controller,
                decoration: const InputDecoration(
                  labelText: 'Street Address / House #',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.home),
                ),
              ),
              const SizedBox(height: 12),

              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      controller: _cityController,
                      decoration: const InputDecoration(
                        labelText: 'City / Community',
                        border: OutlineInputBorder(),
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: TextFormField(
                      controller: _provinceController,
                      decoration: const InputDecoration(
                        labelText: 'Province',
                        border: OutlineInputBorder(),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),

              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      controller: _postalCodeController,
                      decoration: const InputDecoration(
                        labelText: 'Postal Code',
                        border: OutlineInputBorder(),
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: SwitchListTile(
                      dense: true,
                      contentPadding: EdgeInsets.zero,
                      title: const Text('On Reserve', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
                      value: _isOnReserve,
                      onChanged: (val) => setState(() => _isOnReserve = val),
                    ),
                  ),
                ],
              ),

              // Section 6: Health & Physical Features
              _buildSectionHeader('Health & Physical Identifiers', Icons.healing_outlined, colorScheme),
              TextFormField(
                controller: _healthCardController,
                decoration: const InputDecoration(
                  labelText: 'Health Services Card (HSN / HCR)',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.medical_services_outlined),
                ),
              ),
              const SizedBox(height: 12),

              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      controller: _eyeColourController,
                      decoration: const InputDecoration(
                        labelText: 'Eye Colour',
                        border: OutlineInputBorder(),
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: TextFormField(
                      controller: _hairColourController,
                      decoration: const InputDecoration(
                        labelText: 'Hair Colour',
                        border: OutlineInputBorder(),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),

              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      controller: _heightController,
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(
                        labelText: 'Height (cm)',
                        border: OutlineInputBorder(),
                      ),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: TextFormField(
                      controller: _weightController,
                      keyboardType: TextInputType.number,
                      decoration: const InputDecoration(
                        labelText: 'Weight (kg)',
                        border: OutlineInputBorder(),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),

              TextFormField(
                controller: _distinguishingMarksController,
                decoration: const InputDecoration(
                  labelText: 'Scars, Tattoos, Piercings & Identifying Marks',
                  border: OutlineInputBorder(),
                ),
              ),

              // Section 7: Risk & Proposal Notes
              _buildSectionHeader('Client Context & Initial Risk', Icons.shield_outlined, colorScheme),
              DropdownButtonFormField<String>(
                initialValue: _selectedRiskLevel,
                decoration: const InputDecoration(
                  labelText: 'Initial Risk Level *',
                  border: OutlineInputBorder(),
                ),
                items: _riskLevels
                    .map((r) => DropdownMenuItem(value: r, child: Text('$r Risk', style: const TextStyle(fontSize: 13))))
                    .toList(),
                onChanged: (val) {
                  if (val != null) setState(() => _selectedRiskLevel = val);
                },
              ),
              const SizedBox(height: 12),

              TextFormField(
                controller: _notesController,
                maxLines: 3,
                decoration: const InputDecoration(
                  labelText: 'Intake Rationale / Field Notes & Observations',
                  border: OutlineInputBorder(),
                  alignLabelWithHint: true,
                ),
              ),
              const SizedBox(height: 24),

              // Submit Button
              ElevatedButton.icon(
                onPressed: _isSaving ? null : _saveClientDraft,
                icon: _isSaving
                    ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                    : const Icon(Icons.cloud_upload_outlined),
                label: Text(
                  _isSaving
                      ? 'Saving & Synchronizing...'
                      : (isEditMode ? 'Update Client Record' : 'Save & Synchronize Client File'),
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: colorScheme.primary,
                  foregroundColor: colorScheme.onPrimary,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
              ),
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }
}
