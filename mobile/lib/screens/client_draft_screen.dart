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

class _ClientDraftScreenState extends State<ClientDraftScreen> with SingleTickerProviderStateMixin {
  final _formKey = GlobalKey<FormState>();
  final _picker = ImagePicker();
  late TabController _tabController;

  // ── Client Proposal Context ──────────────────────────────────────────
  String _selectedRiskLevel = 'Low';
  String? _selectedTeamId;
  final _notesController = TextEditingController();
  List<Map<String, dynamic>> _teams = [
    {'id': null, 'name': '-- General / Unassigned --'},
    {'id': 'team-prevention', 'name': 'Prevention & Healing Services'},
    {'id': 'team-family', 'name': 'Family Wellness & Kinship'},
    {'id': 'team-cultural', 'name': 'Cultural Support & Elders Council'},
    {'id': 'team-intake', 'name': 'Intake & First Impressions'},
    {'id': 'team-youth', 'name': 'Youth Leadership & Transitions'},
  ];

  // ── Tab 1: Identity ──────────────────────────────────────────────────
  final _firstNameController = TextEditingController();
  final _middleNameController = TextEditingController();
  final _lastNameController = TextEditingController();
  final _preferredNameController = TextEditingController();
  final _aliasesController = TextEditingController();
  DateTime? _selectedDob;
  String _selectedGender = 'Prefer Not to Disclose';
  final _placeOfBirthController = TextEditingController();
  String _selectedLanguage = 'English';
  final _treatyController = TextEditingController();
  final _bandNationController = TextEditingController(text: 'Cote First Nation');
  final _healthCardController = TextEditingController();
  File? _photoFile;
  String? _existingPhotoUrl;

  // ── Tab 2: Physical ID ───────────────────────────────────────────────
  final _eyeColourController = TextEditingController();
  final _hairColourController = TextEditingController();
  final _heightController = TextEditingController();
  final _weightController = TextEditingController();
  final _tattoosController = TextEditingController();
  final _piercingsController = TextEditingController();
  final _birthmarksController = TextEditingController();
  final _scarsController = TextEditingController();
  final _distinguishingMarksController = TextEditingController();
  bool _wearsGlasses = false;
  bool _wearsContacts = false;
  final _physicalNotesController = TextEditingController();

  // ── Tab 3: Contact & Address ─────────────────────────────────────────
  final _phoneController = TextEditingController();
  final _emailController = TextEditingController();
  final _emergNameController = TextEditingController();
  final _emergPhoneController = TextEditingController();
  final _emergRelController = TextEditingController();
  final _address1Controller = TextEditingController();
  final _address2Controller = TextEditingController();
  final _cityController = TextEditingController(text: 'Regina');
  final _provinceController = TextEditingController(text: 'Saskatchewan');
  final _postalCodeController = TextEditingController();
  bool _isOnReserve = false;

  // ── Tab 4: Cultural & Background ─────────────────────────────────────
  final _culturalConnectionsController = TextEditingController();
  final _ceremoniesController = TextEditingController();
  final _eldersConnectedController = TextEditingController();
  final _landActivitiesController = TextEditingController();
  final _dietaryController = TextEditingController();
  final _extraCurricularController = TextEditingController();
  String _selectedEmploymentStatus = '';
  final _employerController = TextEditingController();
  final _sourceOfIncomeController = TextEditingController();

  bool _isSaving = false;

  final List<String> _genderOptions = [
    'Male',
    'Female',
    'Non-Binary',
    'Two-Spirit',
    'Prefer Not to Disclose',
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

  final List<String> _riskLevels = [
    'Low',
    'Medium',
    'High',
  ];

  final List<String> _employmentStatuses = [
    'Employed Full-Time',
    'Employed Part-Time',
    'Self-Employed',
    'Unemployed / Seeking',
    'Student',
    'Retired',
    'Unable to Work',
    'Other',
  ];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    _loadTeams();

    WidgetsBinding.instance.addPostFrameCallback((_) {
      final args = ModalRoute.of(context)?.settings.arguments;
      final client = widget.initialClient ?? (args is Map<String, dynamic> ? args : null);
      if (client != null) {
        _populateFromClient(client);
      }
    });
  }

  Future<void> _loadTeams() async {
    try {
      final serverUrl = (await MobileAuthService.instance.getServerUrl()).replaceAll(RegExp(r'/+$'), '');
      final token = await MobileAuthService.instance.getAccessToken();
      if (token != null && token.isNotEmpty) {
        final uri = Uri.parse('$serverUrl/api/v1/teams');
        final res = await http.get(uri, headers: {
          'Authorization': 'Bearer $token',
        }).timeout(const Duration(seconds: 8));

        if (res.statusCode == 200) {
          final data = jsonDecode(res.body);
          if (data is List && data.isNotEmpty) {
            final loaded = <Map<String, dynamic>>[
              {'id': null, 'name': '-- General / Unassigned --'},
            ];
            for (final t in data) {
              if (t is Map) {
                loaded.add({'id': t['id']?.toString(), 'name': t['name'] ?? 'Unnamed Team'});
              }
            }
            if (mounted) {
              setState(() {
                _teams = loaded;
              });
            }
          }
        }
      }
    } catch (_) {}
  }

  void _populateFromClient(Map<String, dynamic> c) {
    setState(() {
      // Proposal Context
      if (_riskLevels.contains(c['risk_level'])) {
        _selectedRiskLevel = c['risk_level'];
      }
      _selectedTeamId = c['assigned_team_id']?.toString();
      _notesController.text = c['submission_notes'] ?? c['notes'] ?? '';

      // Identity
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

      _treatyController.text = c['treaty_number'] ?? '';
      _bandNationController.text = c['band_nation'] ?? 'Cote First Nation';
      _healthCardController.text = c['health_card_number'] ?? '';
      _existingPhotoUrl = c['photo_url'];

      // Physical ID
      final phys = c['physical_description'] is Map ? c['physical_description'] : (c['physical'] is Map ? c['physical'] : null);
      _eyeColourController.text = phys?['eye_colour'] ?? '';
      _hairColourController.text = phys?['hair_colour'] ?? '';
      _heightController.text = phys?['height_cm']?.toString() ?? '';
      _weightController.text = phys?['weight_kg']?.toString() ?? '';
      _tattoosController.text = phys?['tattoos'] ?? '';
      _piercingsController.text = phys?['piercings'] ?? '';
      _birthmarksController.text = phys?['birthmarks'] ?? '';
      _scarsController.text = phys?['scars'] ?? '';
      _distinguishingMarksController.text = phys?['distinguishing_marks'] ?? '';
      _wearsGlasses = phys?['glasses'] == true;
      _wearsContacts = phys?['contact_lenses'] == true;
      _physicalNotesController.text = phys?['notes'] ?? '';

      // Contact & Address
      _phoneController.text = c['phone'] ?? '';
      _emailController.text = c['email'] ?? '';
      _emergNameController.text = c['emergency_contact_name'] ?? '';
      _emergPhoneController.text = c['emergency_contact_phone'] ?? '';
      _emergRelController.text = c['emergency_contact_relationship'] ?? '';

      final addr = c['primary_address'] is Map ? c['primary_address'] : (c['address'] is Map ? c['address'] : null);
      _address1Controller.text = addr?['address_line_1'] ?? (c['address'] is String ? c['address'] : '');
      _address2Controller.text = addr?['address_line_2'] ?? '';
      _cityController.text = addr?['city'] ?? c['city'] ?? 'Regina';
      _provinceController.text = addr?['province'] ?? c['province'] ?? 'Saskatchewan';
      _postalCodeController.text = addr?['postal_code'] ?? '';
      _isOnReserve = addr?['on_reserve'] == true || c['on_reserve'] == true;

      // Cultural & Background
      final cult = c['cultural_profile'] is Map ? c['cultural_profile'] : (c['cultural'] is Map ? c['cultural'] : null);
      _culturalConnectionsController.text = cult?['cultural_connections'] ?? c['cultural_connections'] ?? '';
      _ceremoniesController.text = cult?['ceremonies'] ?? c['ceremonies'] ?? '';
      _eldersConnectedController.text = cult?['elders_connected'] ?? c['elders_connected'] ?? '';
      _landActivitiesController.text = cult?['land_based_activities'] ?? c['land_based_activities'] ?? '';
      _dietaryController.text = cult?['dietary_preferences'] ?? '';
      _extraCurricularController.text = cult?['extracurricular_activities'] ?? '';

      if (_employmentStatuses.contains(c['employment_status'])) {
        _selectedEmploymentStatus = c['employment_status'];
      }
      _employerController.text = c['employer'] ?? '';
      _sourceOfIncomeController.text = c['source_of_income'] ?? '';
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    _notesController.dispose();
    _firstNameController.dispose();
    _middleNameController.dispose();
    _lastNameController.dispose();
    _preferredNameController.dispose();
    _aliasesController.dispose();
    _placeOfBirthController.dispose();
    _treatyController.dispose();
    _bandNationController.dispose();
    _healthCardController.dispose();
    _eyeColourController.dispose();
    _hairColourController.dispose();
    _heightController.dispose();
    _weightController.dispose();
    _tattoosController.dispose();
    _piercingsController.dispose();
    _birthmarksController.dispose();
    _scarsController.dispose();
    _distinguishingMarksController.dispose();
    _physicalNotesController.dispose();
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
    _culturalConnectionsController.dispose();
    _ceremoniesController.dispose();
    _eldersConnectedController.dispose();
    _landActivitiesController.dispose();
    _dietaryController.dispose();
    _extraCurricularController.dispose();
    _employerController.dispose();
    _sourceOfIncomeController.dispose();
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
        const SnackBar(content: Text('Please complete all required fields (Legal First & Last Name).')),
      );
      _tabController.animateTo(0);
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
      'treaty_number': _treatyController.text.trim().isNotEmpty ? _treatyController.text.trim() : null,
      'band_nation': _bandNationController.text.trim().isNotEmpty ? _bandNationController.text.trim() : 'Cote First Nation',
      'health_card_number': _healthCardController.text.trim().isNotEmpty ? _healthCardController.text.trim() : null,
      'phone': _phoneController.text.trim().isNotEmpty ? _phoneController.text.trim() : null,
      'email': _emailController.text.trim().isNotEmpty ? _emailController.text.trim() : null,
      'emergency_contact_name': _emergNameController.text.trim().isNotEmpty ? _emergNameController.text.trim() : null,
      'emergency_contact_phone': _emergPhoneController.text.trim().isNotEmpty ? _emergPhoneController.text.trim() : null,
      'emergency_contact_relationship': _emergRelController.text.trim().isNotEmpty ? _emergRelController.text.trim() : null,
      'employment_status': _selectedEmploymentStatus.isNotEmpty ? _selectedEmploymentStatus : null,
      'employer': _employerController.text.trim().isNotEmpty ? _employerController.text.trim() : null,
      'source_of_income': _sourceOfIncomeController.text.trim().isNotEmpty ? _sourceOfIncomeController.text.trim() : null,
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
        'dietary_preferences': _dietaryController.text.trim().isNotEmpty ? _dietaryController.text.trim() : null,
        'extracurricular_activities': _extraCurricularController.text.trim().isNotEmpty ? _extraCurricularController.text.trim() : null,
      },
      'physical_description': {
        'eye_colour': _eyeColourController.text.trim().isNotEmpty ? _eyeColourController.text.trim() : null,
        'hair_colour': _hairColourController.text.trim().isNotEmpty ? _hairColourController.text.trim() : null,
        'height_cm': double.tryParse(_heightController.text.trim()),
        'weight_kg': double.tryParse(_weightController.text.trim()),
        'tattoos': _tattoosController.text.trim().isNotEmpty ? _tattoosController.text.trim() : null,
        'piercings': _piercingsController.text.trim().isNotEmpty ? _piercingsController.text.trim() : null,
        'birthmarks': _birthmarksController.text.trim().isNotEmpty ? _birthmarksController.text.trim() : null,
        'scars': _scarsController.text.trim().isNotEmpty ? _scarsController.text.trim() : null,
        'distinguishing_marks': _distinguishingMarksController.text.trim().isNotEmpty ? _distinguishingMarksController.text.trim() : null,
        'glasses': _wearsGlasses,
        'contact_lenses': _wearsContacts,
        'notes': _physicalNotesController.text.trim().isNotEmpty ? _physicalNotesController.text.trim() : null,
      },
    };

    final clientPayload = {
      'person': personData,
      'risk_level': _selectedRiskLevel,
      'assigned_team_id': _selectedTeamId,
      'submission_notes': _notesController.text.trim().isNotEmpty ? _notesController.text.trim() : 'Submitted from Mobile App',
    };

    bool syncedOnline = false;
    String? createdClientId;

    try {
      final isOnline = await ConnectivityService.instance.checkConnectivity();
      final token = await MobileAuthService.instance.getAccessToken();
      final serverUrl = (await MobileAuthService.instance.getServerUrl()).replaceAll(RegExp(r'/+$'), '');

      if (isOnline && token != null && token.isNotEmpty) {
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

          // Upload photo if available
          if (_photoFile != null && createdClientId != null) {
            try {
              final photoUri = Uri.parse('$serverUrl/api/v1/clients/$createdClientId/photo');
              final request = http.MultipartRequest('POST', photoUri);
              request.headers['Authorization'] = 'Bearer $token';
              request.files.add(await http.MultipartFile.fromPath('file', _photoFile!.path));
              await request.send().timeout(const Duration(seconds: 20));
            } catch (_) {}
          }
        }
      }
    } catch (_) {
      syncedOnline = false;
    }

    // Save locally to SQLite drafts
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
      'risk_level': _selectedRiskLevel,
      'assigned_team_id': _selectedTeamId,
      'notes': _notesController.text.trim(),
      'photo_path': _photoFile?.path,
      'full_person': personData,
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

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final isDark = theme.brightness == Brightness.dark;

    final isEditMode = widget.initialClient != null;

    return Scaffold(
      appBar: AppBar(
        title: Text(isEditMode ? 'Edit Client Record' : 'New Client — Canonical Identity Intake'),
        actions: [
          IconButton(
            icon: const Icon(Icons.check),
            tooltip: 'Save Client',
            onPressed: _isSaving ? null : _saveClientDraft,
          ),
        ],
      ),
      body: Form(
        key: _formKey,
        child: Column(
          children: [
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // Subtitle matching web modal
                    Text(
                      'Capture the canonical identity record. A permanent 10-digit CRBCL Person ID will be automatically generated upon saving, and the client context submitted for supervisor review.',
                      style: TextStyle(
                        fontSize: 12,
                        color: colorScheme.onSurface.withValues(alpha: 0.7),
                      ),
                    ),
                    const SizedBox(height: 14),

                    // ── CLIENT PROPOSAL CONTEXT CARD (Matching Web Screenshot) ──
                    Container(
                      padding: const EdgeInsets.all(14),
                      decoration: BoxDecoration(
                        color: colorScheme.primary.withValues(alpha: 0.05),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: colorScheme.primary.withValues(alpha: 0.2)),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(
                                'CLIENT PROPOSAL CONTEXT',
                                style: TextStyle(
                                  fontSize: 11,
                                  fontWeight: FontWeight.bold,
                                  color: colorScheme.primary,
                                  letterSpacing: 0.5,
                                ),
                              ),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                decoration: BoxDecoration(
                                  color: Colors.amber.shade100,
                                  borderRadius: BorderRadius.circular(12),
                                  border: Border.all(color: Colors.amber.shade300),
                                ),
                                child: Text(
                                  'Awaiting Supervisor Review Upon Submit',
                                  style: TextStyle(
                                    fontSize: 9,
                                    fontWeight: FontWeight.w600,
                                    color: Colors.amber.shade900,
                                  ),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 12),

                          // Initial Risk Level & Assigned Team (Optional)
                          Row(
                            children: [
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    const Text('Initial Risk Level *', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
                                    const SizedBox(height: 4),
                                    DropdownButtonFormField<String>(
                                      initialValue: _selectedRiskLevel,
                                      isDense: true,
                                      decoration: const InputDecoration(
                                        border: OutlineInputBorder(),
                                        contentPadding: EdgeInsets.symmetric(horizontal: 10, vertical: 10),
                                      ),
                                      items: _riskLevels
                                          .map((r) => DropdownMenuItem(value: r, child: Text('$r Risk', style: const TextStyle(fontSize: 13))))
                                          .toList(),
                                      onChanged: (val) {
                                        if (val != null) setState(() => _selectedRiskLevel = val);
                                      },
                                    ),
                                  ],
                                ),
                              ),
                              const SizedBox(width: 10),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    const Text('Assigned Team (Optional)', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
                                    const SizedBox(height: 4),
                                    DropdownButtonFormField<String?>(
                                      initialValue: _selectedTeamId,
                                      isDense: true,
                                      isExpanded: true,
                                      decoration: const InputDecoration(
                                        border: OutlineInputBorder(),
                                        contentPadding: EdgeInsets.symmetric(horizontal: 10, vertical: 10),
                                      ),
                                      items: _teams
                                          .map((t) => DropdownMenuItem<String?>(
                                                value: t['id'],
                                                child: Text(
                                                  t['name'] ?? '',
                                                  style: const TextStyle(fontSize: 12),
                                                  overflow: TextOverflow.ellipsis,
                                                ),
                                              ))
                                          .toList(),
                                      onChanged: (val) {
                                        setState(() => _selectedTeamId = val);
                                      },
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 12),

                          // Submission Rationale / Intake Notes
                          const Text('Submission Rationale / Intake Notes', style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold)),
                          const SizedBox(height: 4),
                          TextFormField(
                            controller: _notesController,
                            maxLines: 2,
                            decoration: const InputDecoration(
                              hintText: 'Provide background, immediate safety or stabilization needs, or rationale for proposing this client...',
                              hintStyle: TextStyle(fontSize: 11, fontStyle: FontStyle.italic),
                              border: OutlineInputBorder(),
                              contentPadding: EdgeInsets.all(10),
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 16),

                    // ── 4 TABS NAVIGATION WITH ARROWS (Matching Web Screenshot) ──
                    Row(
                      children: [
                        IconButton(
                          icon: const Icon(Icons.chevron_left),
                          tooltip: 'Previous Tab',
                          visualDensity: VisualDensity.compact,
                          onPressed: () {
                            if (_tabController.index > 0) {
                              _tabController.animateTo(_tabController.index - 1);
                            }
                          },
                        ),
                        Expanded(
                          child: Container(
                            decoration: BoxDecoration(
                              color: isDark ? colorScheme.surfaceContainerHighest : Colors.grey.shade100,
                              borderRadius: BorderRadius.circular(10),
                              border: Border.all(color: colorScheme.outlineVariant.withValues(alpha: 0.5)),
                            ),
                            child: TabBar(
                              controller: _tabController,
                              isScrollable: true,
                              tabAlignment: TabAlignment.start,
                              labelColor: colorScheme.primary,
                              unselectedLabelColor: colorScheme.onSurface.withValues(alpha: 0.6),
                              labelStyle: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
                              indicatorColor: colorScheme.primary,
                              indicatorSize: TabBarIndicatorSize.tab,
                              tabs: const [
                                Tab(text: '1. Identity'),
                                Tab(text: '2. Physical ID'),
                                Tab(text: '3. Contact & Address'),
                                Tab(text: '4. Cultural'),
                              ],
                            ),
                          ),
                        ),
                        IconButton(
                          icon: const Icon(Icons.chevron_right),
                          tooltip: 'Next Tab',
                          visualDensity: VisualDensity.compact,
                          onPressed: () {
                            if (_tabController.index < 3) {
                              _tabController.animateTo(_tabController.index + 1);
                            }
                          },
                        ),
                      ],
                    ),
                    const SizedBox(height: 10),

                    // Active Section Indicator banner
                    AnimatedBuilder(
                      animation: _tabController,
                      builder: (context, _) {
                        final tabTitles = [
                          'Section 1 of 4: Identity & Vital Information',
                          'Section 2 of 4: Physical Identification & Observable Marks',
                          'Section 3 of 4: Contact & Primary Residential Address',
                          'Section 4 of 4: Cultural Profile & Heritage Background',
                        ];
                        final activeTitle = tabTitles[_tabController.index.clamp(0, 3)];
                        return Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                          decoration: BoxDecoration(
                            color: colorScheme.primary.withValues(alpha: 0.08),
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Row(
                            children: [
                              Icon(Icons.info_outline, size: 14, color: colorScheme.primary),
                              const SizedBox(width: 6),
                              Expanded(
                                child: Text(
                                  activeTitle,
                                  style: TextStyle(
                                    fontSize: 11,
                                    fontWeight: FontWeight.w600,
                                    color: colorScheme.primary,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        );
                      },
                    ),
                    const SizedBox(height: 14),

                    // ── TAB VIEWS ──
                    AnimatedBuilder(
                      animation: _tabController,
                      builder: (context, _) {
                        switch (_tabController.index) {
                          case 0:
                            return _buildIdentityTab(colorScheme);
                          case 1:
                            return _buildPhysicalIdTab(colorScheme);
                          case 2:
                            return _buildContactAddressTab(colorScheme);
                          case 3:
                            return _buildCulturalTab(colorScheme);
                          default:
                            return _buildIdentityTab(colorScheme);
                        }
                      },
                    ),

                    const SizedBox(height: 24),

                    // Save / Submit Button
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
                    const SizedBox(height: 30),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ── Tab 1: Identity ──────────────────────────────────────────────────
  Widget _buildIdentityTab(ColorScheme colorScheme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Photo Upload Box
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: colorScheme.surfaceContainerHighest.withValues(alpha: 0.3),
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: colorScheme.outlineVariant.withValues(alpha: 0.5)),
          ),
          child: Row(
            children: [
              CircleAvatar(
                radius: 30,
                backgroundColor: colorScheme.primary.withValues(alpha: 0.15),
                backgroundImage: _photoFile != null
                    ? FileImage(_photoFile!)
                    : (_existingPhotoUrl != null && _existingPhotoUrl!.isNotEmpty
                        ? NetworkImage(_existingPhotoUrl!) as ImageProvider
                        : null),
                child: (_photoFile == null && (_existingPhotoUrl == null || _existingPhotoUrl!.isEmpty))
                    ? Text(
                        '${_firstNameController.text.isNotEmpty ? _firstNameController.text[0] : ""}${_lastNameController.text.isNotEmpty ? _lastNameController.text[0] : "?"}',
                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: colorScheme.primary),
                      )
                    : null,
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Profile Photo (Optional)', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
                    const SizedBox(height: 2),
                    Text('Supported: JPEG, PNG, WebP (EXIF-stripped)', style: TextStyle(fontSize: 10, color: colorScheme.onSurface.withValues(alpha: 0.6))),
                    const SizedBox(height: 6),
                    Row(
                      children: [
                        OutlinedButton.icon(
                          onPressed: _showPhotoOptions,
                          icon: const Icon(Icons.add_a_photo, size: 14),
                          label: Text(_photoFile != null || _existingPhotoUrl != null ? 'Change' : 'Upload', style: const TextStyle(fontSize: 11)),
                          style: OutlinedButton.styleFrom(visualDensity: VisualDensity.compact),
                        ),
                        if (_photoFile != null || _existingPhotoUrl != null) ...[
                          const SizedBox(width: 8),
                          TextButton(
                            onPressed: () => setState(() {
                              _photoFile = null;
                              _existingPhotoUrl = null;
                            }),
                            child: const Text('Remove', style: TextStyle(color: Colors.red, fontSize: 11)),
                          ),
                        ],
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 14),

        // Legal First & Middle & Last Name
        Row(
          children: [
            Expanded(
              child: TextFormField(
                controller: _firstNameController,
                decoration: const InputDecoration(labelText: 'Legal First Name *', border: OutlineInputBorder()),
                validator: (val) => val == null || val.trim().isEmpty ? 'Required' : null,
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: TextFormField(
                controller: _middleNameController,
                decoration: const InputDecoration(labelText: 'Middle Name(s)', border: OutlineInputBorder()),
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: TextFormField(
                controller: _lastNameController,
                decoration: const InputDecoration(labelText: 'Legal Last Name *', border: OutlineInputBorder()),
                validator: (val) => val == null || val.trim().isEmpty ? 'Required' : null,
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),

        // Preferred & Aliases
        Row(
          children: [
            Expanded(
              child: TextFormField(
                controller: _preferredNameController,
                decoration: const InputDecoration(labelText: 'Preferred / Chosen Name', border: OutlineInputBorder()),
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: TextFormField(
                controller: _aliasesController,
                decoration: const InputDecoration(labelText: 'Aliases / Previous Names', hintText: 'Comma-separated', border: OutlineInputBorder()),
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),

        // Date of Birth & Gender
        Row(
          children: [
            Expanded(
              child: InkWell(
                onTap: () => _selectDob(context),
                child: InputDecorator(
                  decoration: const InputDecoration(labelText: 'Date of Birth', border: OutlineInputBorder(), prefixIcon: Icon(Icons.calendar_today, size: 16)),
                  child: Text(
                    _selectedDob != null ? DateFormat('yyyy-MM-dd').format(_selectedDob!) : 'Select DOB',
                    style: TextStyle(fontSize: 13, color: _selectedDob != null ? colorScheme.onSurface : colorScheme.onSurface.withValues(alpha: 0.5)),
                  ),
                ),
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: DropdownButtonFormField<String>(
                initialValue: _selectedGender,
                decoration: const InputDecoration(labelText: 'Gender', border: OutlineInputBorder()),
                items: _genderOptions.map((g) => DropdownMenuItem(value: g, child: Text(g, style: const TextStyle(fontSize: 12)))).toList(),
                onChanged: (val) {
                  if (val != null) setState(() => _selectedGender = val);
                },
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),

        // Place of Birth & Preferred Language
        Row(
          children: [
            Expanded(
              child: TextFormField(
                controller: _placeOfBirthController,
                decoration: const InputDecoration(labelText: 'Place of Birth', hintText: 'e.g. Regina, SK', border: OutlineInputBorder()),
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: DropdownButtonFormField<String>(
                initialValue: _selectedLanguage,
                decoration: const InputDecoration(labelText: 'Preferred Language', border: OutlineInputBorder()),
                items: _languageOptions.map((l) => DropdownMenuItem(value: l, child: Text(l, style: const TextStyle(fontSize: 12)))).toList(),
                onChanged: (val) {
                  if (val != null) setState(() => _selectedLanguage = val);
                },
              ),
            ),
          ],
        ),
        const SizedBox(height: 14),

        const Divider(),
        const SizedBox(height: 8),

        // Treaty, Band, and SK Health Card (Matching Web Tab 1 footer)
        TextFormField(
          controller: _treatyController,
          decoration: const InputDecoration(labelText: 'Treaty / Status Card #', hintText: '10-digit registration #', border: OutlineInputBorder(), prefixIcon: Icon(Icons.badge_outlined)),
        ),
        const SizedBox(height: 12),

        Row(
          children: [
            Expanded(
              child: TextFormField(
                controller: _bandNationController,
                decoration: const InputDecoration(labelText: 'Band / First Nation', hintText: 'e.g. Zagime Anishinabek', border: OutlineInputBorder()),
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: TextFormField(
                controller: _healthCardController,
                decoration: const InputDecoration(labelText: 'SK Health Card (HSN)', hintText: '9-digit HSN', border: OutlineInputBorder()),
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        Align(
          alignment: Alignment.centerRight,
          child: FilledButton.tonalIcon(
            onPressed: () => _tabController.animateTo(1),
            icon: const Icon(Icons.arrow_forward, size: 16),
            label: const Text('Next: 2. Physical ID →'),
          ),
        ),
      ],
    );
  }

  // ── Tab 2: Physical ID ───────────────────────────────────────────────
  Widget _buildPhysicalIdTab(ColorScheme colorScheme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          'Observable physical identifiers to assist staff in rapid and accurate client identification.',
          style: TextStyle(fontSize: 11, color: colorScheme.onSurface.withValues(alpha: 0.7)),
        ),
        const SizedBox(height: 12),

        // Eye, Hair, Height, Weight
        Row(
          children: [
            Expanded(
              child: TextFormField(
                controller: _eyeColourController,
                decoration: const InputDecoration(labelText: 'Eye Colour', hintText: 'e.g. Brown', border: OutlineInputBorder()),
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: TextFormField(
                controller: _hairColourController,
                decoration: const InputDecoration(labelText: 'Hair Colour', hintText: 'e.g. Black', border: OutlineInputBorder()),
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
                decoration: const InputDecoration(labelText: 'Height (cm)', hintText: 'e.g. 165', border: OutlineInputBorder()),
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: TextFormField(
                controller: _weightController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(labelText: 'Weight (kg)', hintText: 'e.g. 60', border: OutlineInputBorder()),
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),

        // Tattoos & Piercings
        TextFormField(
          controller: _tattoosController,
          decoration: const InputDecoration(labelText: 'Tattoos & Body Art', hintText: 'Describe locations & designs', border: OutlineInputBorder()),
        ),
        const SizedBox(height: 12),

        TextFormField(
          controller: _piercingsController,
          decoration: const InputDecoration(labelText: 'Piercings', hintText: 'Describe locations', border: OutlineInputBorder()),
        ),
        const SizedBox(height: 12),

        // Birthmarks, Scars & Distinguishing Marks
        TextFormField(
          controller: _birthmarksController,
          decoration: const InputDecoration(labelText: 'Birthmarks', hintText: 'Locations and descriptions', border: OutlineInputBorder()),
        ),
        const SizedBox(height: 12),

        TextFormField(
          controller: _scarsController,
          decoration: const InputDecoration(labelText: 'Scars & Surgical Marks', hintText: 'Locations and descriptions of visible marks', border: OutlineInputBorder()),
        ),
        const SizedBox(height: 12),

        TextFormField(
          controller: _distinguishingMarksController,
          decoration: const InputDecoration(labelText: 'Other Distinguishing Marks', hintText: 'Notable features or assistive devices', border: OutlineInputBorder()),
        ),
        const SizedBox(height: 12),

        // Wears Glasses / Contacts switches
        Row(
          children: [
            Expanded(
              child: SwitchListTile(
                dense: true,
                contentPadding: EdgeInsets.zero,
                title: const Text('Wears Glasses', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
                value: _wearsGlasses,
                onChanged: (val) => setState(() => _wearsGlasses = val),
              ),
            ),
            Expanded(
              child: SwitchListTile(
                dense: true,
                contentPadding: EdgeInsets.zero,
                title: const Text('Wears Contacts', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
                value: _wearsContacts,
                onChanged: (val) => setState(() => _wearsContacts = val),
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),

        TextFormField(
          controller: _physicalNotesController,
          maxLines: 2,
          decoration: const InputDecoration(
            labelText: 'Physical Identifying Notes',
            hintText: 'Additional appearance details or physical identifying notes...',
            border: OutlineInputBorder(),
          ),
        ),
        const SizedBox(height: 16),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            OutlinedButton.icon(
              onPressed: () => _tabController.animateTo(0),
              icon: const Icon(Icons.arrow_back, size: 16),
              label: const Text('← 1. Identity'),
            ),
            FilledButton.tonalIcon(
              onPressed: () => _tabController.animateTo(2),
              icon: const Icon(Icons.arrow_forward, size: 16),
              label: const Text('Next: 3. Contact →'),
            ),
          ],
        ),
      ],
    );
  }

  // ── Tab 3: Contact & Address ─────────────────────────────────────────
  Widget _buildContactAddressTab(ColorScheme colorScheme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Primary Phone & Email
        Row(
          children: [
            Expanded(
              child: TextFormField(
                controller: _phoneController,
                keyboardType: TextInputType.phone,
                decoration: const InputDecoration(labelText: 'Primary Phone', hintText: '306-555-0100', border: OutlineInputBorder(), prefixIcon: Icon(Icons.phone, size: 16)),
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: TextFormField(
                controller: _emailController,
                keyboardType: TextInputType.emailAddress,
                decoration: const InputDecoration(labelText: 'Email Address', hintText: 'client@example.ca', border: OutlineInputBorder(), prefixIcon: Icon(Icons.email, size: 16)),
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),

        // EMERGENCY CONTACT CARD (Matching Web Screenshot)
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: colorScheme.surfaceContainerHighest.withValues(alpha: 0.3),
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: colorScheme.outlineVariant.withValues(alpha: 0.5)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                'EMERGENCY CONTACT',
                style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: colorScheme.onSurface.withValues(alpha: 0.7), letterSpacing: 0.5),
              ),
              const SizedBox(height: 10),
              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      controller: _emergNameController,
                      decoration: const InputDecoration(labelText: 'Name', hintText: 'Full name', border: OutlineInputBorder()),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: TextFormField(
                      controller: _emergPhoneController,
                      keyboardType: TextInputType.phone,
                      decoration: const InputDecoration(labelText: 'Phone', hintText: 'Phone number', border: OutlineInputBorder()),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: TextFormField(
                      controller: _emergRelController,
                      decoration: const InputDecoration(labelText: 'Relationship', hintText: 'e.g. Grandmother, Aunt', border: OutlineInputBorder()),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),

        // PRIMARY RESIDENTIAL ADDRESS CARD (Matching Web Screenshot)
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: colorScheme.surfaceContainerHighest.withValues(alpha: 0.3),
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: colorScheme.outlineVariant.withValues(alpha: 0.5)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                'PRIMARY RESIDENTIAL ADDRESS',
                style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: colorScheme.onSurface.withValues(alpha: 0.7), letterSpacing: 0.5),
              ),
              const SizedBox(height: 10),
              TextFormField(
                controller: _address1Controller,
                decoration: const InputDecoration(labelText: 'Street Address', hintText: '123 5th Ave', border: OutlineInputBorder(), prefixIcon: Icon(Icons.home, size: 16)),
              ),
              const SizedBox(height: 10),
              TextFormField(
                controller: _address2Controller,
                decoration: const InputDecoration(labelText: 'Address Line 2 (Apt / Suite / House #)', border: OutlineInputBorder()),
              ),
              const SizedBox(height: 10),
              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      controller: _cityController,
                      decoration: const InputDecoration(labelText: 'City', border: OutlineInputBorder()),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: TextFormField(
                      controller: _provinceController,
                      decoration: const InputDecoration(labelText: 'Province', border: OutlineInputBorder()),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 10),
              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      controller: _postalCodeController,
                      decoration: const InputDecoration(labelText: 'Postal Code', hintText: 'S4P 3Y2', border: OutlineInputBorder()),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: SwitchListTile(
                      dense: true,
                      contentPadding: EdgeInsets.zero,
                      title: const Text('Located On-Reserve', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
                      value: _isOnReserve,
                      onChanged: (val) => setState(() => _isOnReserve = val),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            OutlinedButton.icon(
              onPressed: () => _tabController.animateTo(1),
              icon: const Icon(Icons.arrow_back, size: 16),
              label: const Text('← 2. Physical ID'),
            ),
            FilledButton.tonalIcon(
              onPressed: () => _tabController.animateTo(3),
              icon: const Icon(Icons.arrow_forward, size: 16),
              label: const Text('Next: 4. Cultural →'),
            ),
          ],
        ),
      ],
    );
  }

  // ── Tab 4: Cultural & Background ─────────────────────────────────────
  Widget _buildCulturalTab(ColorScheme colorScheme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          'Cultural identity, customary connections, and socioeconomic context honoring Indigenous family heritage.',
          style: TextStyle(fontSize: 11, color: colorScheme.onSurface.withValues(alpha: 0.7)),
        ),
        const SizedBox(height: 14),

        // Cultural & Community Connections
        TextFormField(
          controller: _culturalConnectionsController,
          maxLines: 2,
          decoration: const InputDecoration(
            labelText: 'Cultural & Community Connections',
            hintText: 'Band affiliations, clan, or urban Indigenous community ties...',
            border: OutlineInputBorder(),
          ),
        ),
        const SizedBox(height: 12),

        // Ceremonies & Customary Practices
        TextFormField(
          controller: _ceremoniesController,
          maxLines: 2,
          decoration: const InputDecoration(
            labelText: 'Ceremonies & Customary Practices',
            hintText: 'Round dances, sweats, smudging, seasonal gatherings...',
            border: OutlineInputBorder(),
          ),
        ),
        const SizedBox(height: 12),

        // Elders / Knowledge Keepers Connected With
        TextFormField(
          controller: _eldersConnectedController,
          decoration: const InputDecoration(
            labelText: 'Elders / Knowledge Keepers Connected With',
            hintText: 'Names or communities of connected Elders',
            border: OutlineInputBorder(),
          ),
        ),
        const SizedBox(height: 12),

        // Land-Based Activities
        TextFormField(
          controller: _landActivitiesController,
          decoration: const InputDecoration(
            labelText: 'Land-Based Activities',
            hintText: 'Hunting, fishing, medicine picking, trapping...',
            border: OutlineInputBorder(),
          ),
        ),
        const SizedBox(height: 12),

        // Dietary Needs & Extracurricular Activities
        Row(
          children: [
            Expanded(
              child: TextFormField(
                controller: _dietaryController,
                decoration: const InputDecoration(labelText: 'Dietary Needs & Preferences', hintText: 'Traditional foods, allergies', border: OutlineInputBorder()),
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: TextFormField(
                controller: _extraCurricularController,
                decoration: const InputDecoration(labelText: 'Extracurricular Activities', hintText: 'Sports, arts, music, powwow', border: OutlineInputBorder()),
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),

        // SOCIOECONOMIC BACKGROUND CARD (Matching Web Tab 4)
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: colorScheme.surfaceContainerHighest.withValues(alpha: 0.3),
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: colorScheme.outlineVariant.withValues(alpha: 0.5)),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(
                'SOCIOECONOMIC BACKGROUND',
                style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: colorScheme.onSurface.withValues(alpha: 0.7), letterSpacing: 0.5),
              ),
              const SizedBox(height: 10),
              DropdownButtonFormField<String>(
                initialValue: _selectedEmploymentStatus.isNotEmpty ? _selectedEmploymentStatus : null,
                decoration: const InputDecoration(labelText: 'Employment Status', border: OutlineInputBorder()),
                items: [
                  const DropdownMenuItem(value: '', child: Text('-- Select Status --')),
                  ..._employmentStatuses.map((s) => DropdownMenuItem(value: s, child: Text(s, style: const TextStyle(fontSize: 12)))),
                ],
                onChanged: (val) {
                  setState(() => _selectedEmploymentStatus = val ?? '');
                },
              ),
              const SizedBox(height: 10),
              Row(
                children: [
                  Expanded(
                    child: TextFormField(
                      controller: _employerController,
                      decoration: const InputDecoration(labelText: 'Employer / School', hintText: 'Organization name', border: OutlineInputBorder()),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: TextFormField(
                      controller: _sourceOfIncomeController,
                      decoration: const InputDecoration(labelText: 'Source of Income', hintText: 'e.g. Employment, SIS, SAID, EI', border: OutlineInputBorder()),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        Align(
          alignment: Alignment.centerLeft,
          child: OutlinedButton.icon(
            onPressed: () => _tabController.animateTo(2),
            icon: const Icon(Icons.arrow_back, size: 16),
            label: const Text('← 3. Contact & Address'),
          ),
        ),
      ],
    );
  }
}
