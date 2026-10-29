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

  String _formatDobWithAge(DateTime? dob) {
    if (dob == null) return 'Select Date of Birth';
    final dobStr = DateFormat('yyyy-MM-dd').format(dob);
    final now = DateTime.now();
    int age = now.year - dob.year;
    if (now.month < dob.month || (now.month == dob.month && now.day < dob.day)) {
      age--;
    }
    return '$dobStr ($age yrs)';
  }

  InputDecoration _inputDeco(
    BuildContext context, {
    required String labelText,
    String? hintText,
    Widget? prefixIcon,
    Widget? suffixIcon,
  }) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;
    final colorScheme = theme.colorScheme;

    return InputDecoration(
      labelText: labelText,
      hintText: hintText,
      prefixIcon: prefixIcon,
      suffixIcon: suffixIcon,
      filled: true,
      fillColor: isDark
          ? colorScheme.surfaceContainerHighest.withValues(alpha: 0.35)
          : const Color(0xFFF9FAFB),
      contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(
          color: isDark ? colorScheme.outlineVariant.withValues(alpha: 0.5) : const Color(0xFFE5E7EB),
        ),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(
          color: isDark ? colorScheme.outlineVariant.withValues(alpha: 0.5) : const Color(0xFFE5E7EB),
        ),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide(
          color: colorScheme.primary,
          width: 1.8,
        ),
      ),
    );
  }

  Widget _buildSectionCard({
    required BuildContext context,
    required IconData icon,
    required String title,
    String? subtitle,
    Widget? trailing,
    required List<Widget> children,
  }) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final isDark = theme.brightness == Brightness.dark;

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: isDark ? colorScheme.surfaceContainer : Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: isDark ? colorScheme.outlineVariant.withValues(alpha: 0.4) : const Color(0xFFE5E7EB),
          width: 1,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: isDark ? 0.2 : 0.03),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: colorScheme.primary.withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Icon(icon, size: 18, color: colorScheme.primary),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: const TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.bold,
                          letterSpacing: 0.3,
                        ),
                      ),
                      if (subtitle != null) ...[
                        const SizedBox(height: 2),
                        Text(
                          subtitle,
                          style: TextStyle(
                            fontSize: 11,
                            color: colorScheme.onSurface.withValues(alpha: 0.6),
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
                if (trailing != null) trailing,
              ],
            ),
            const SizedBox(height: 12),
            const Divider(height: 1),
            const SizedBox(height: 14),
            ...children,
          ],
        ),
      ),
    );
  }

  Widget _buildStepperHeader(ColorScheme colorScheme, bool isDark) {
    final steps = [
      {'title': 'Identity', 'icon': Icons.badge_outlined},
      {'title': 'Physical', 'icon': Icons.accessibility_new_outlined},
      {'title': 'Contact', 'icon': Icons.contact_phone_outlined},
      {'title': 'Cultural', 'icon': Icons.nature_people_outlined},
    ];

    final currentIndex = _tabController.index.clamp(0, 3);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
      decoration: BoxDecoration(
        color: isDark ? colorScheme.surfaceContainer : Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: isDark ? colorScheme.outlineVariant.withValues(alpha: 0.4) : const Color(0xFFE5E7EB),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: isDark ? 0.2 : 0.03),
            blurRadius: 6,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        children: [
          Row(
            children: List.generate(steps.length, (idx) {
              final isSelected = currentIndex == idx;
              final isDone = currentIndex > idx;
              final icon = steps[idx]['icon'] as IconData;
              final title = steps[idx]['title'] as String;

              return Expanded(
                child: InkWell(
                  onTap: () => _tabController.animateTo(idx),
                  borderRadius: BorderRadius.circular(10),
                  child: Container(
                    padding: const EdgeInsets.symmetric(vertical: 8),
                    decoration: BoxDecoration(
                      color: isSelected ? colorScheme.primary.withValues(alpha: 0.12) : Colors.transparent,
                      borderRadius: BorderRadius.circular(10),
                      border: isSelected
                          ? Border.all(color: colorScheme.primary.withValues(alpha: 0.5), width: 1.5)
                          : null,
                    ),
                    child: Column(
                      children: [
                        Icon(
                          isDone ? Icons.check_circle : icon,
                          size: 19,
                          color: isSelected
                              ? colorScheme.primary
                              : (isDone ? Colors.green : colorScheme.onSurface.withValues(alpha: 0.45)),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          title,
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: isSelected ? FontWeight.bold : FontWeight.w500,
                            color: isSelected
                                ? colorScheme.primary
                                : (isDone ? colorScheme.onSurface : colorScheme.onSurface.withValues(alpha: 0.6)),
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ],
                    ),
                  ),
                ),
              );
            }),
          ),
          const SizedBox(height: 8),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: (currentIndex + 1) / 4.0,
              backgroundColor: isDark ? colorScheme.surfaceContainerHighest : Colors.grey.shade200,
              valueColor: AlwaysStoppedAnimation<Color>(colorScheme.primary),
              minHeight: 4,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildNavigationFooter(ColorScheme colorScheme) {
    final currentIndex = _tabController.index.clamp(0, 3);
    final isLastStep = currentIndex == 3;
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: isDark ? colorScheme.surfaceContainer : Colors.white,
        border: Border(
          top: BorderSide(
            color: isDark ? colorScheme.outlineVariant.withValues(alpha: 0.4) : const Color(0xFFE5E7EB),
          ),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: isDark ? 0.25 : 0.05),
            blurRadius: 8,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: SafeArea(
        top: false,
        child: Row(
          children: [
            if (currentIndex > 0)
              OutlinedButton.icon(
                onPressed: () => _tabController.animateTo(currentIndex - 1),
                icon: const Icon(Icons.arrow_back, size: 16),
                label: const Text('Back'),
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
              ),
            if (currentIndex > 0) const SizedBox(width: 10),
            Expanded(
              child: ElevatedButton.icon(
                onPressed: _isSaving
                    ? null
                    : () {
                        if (isLastStep) {
                          _saveClientDraft();
                        } else {
                          _tabController.animateTo(currentIndex + 1);
                        }
                      },
                icon: _isSaving
                    ? const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                      )
                    : Icon(isLastStep ? Icons.cloud_upload_outlined : Icons.arrow_forward, size: 18),
                label: Text(
                  _isSaving
                      ? 'Saving File...'
                      : (isLastStep ? 'Save & Synchronize Dossier' : 'Next Step →'),
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: colorScheme.primary,
                  foregroundColor: colorScheme.onPrimary,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  elevation: 1,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ── Proposal Context Card ──
  Widget _buildContextCard(ColorScheme colorScheme) {
    return _buildSectionCard(
      context: context,
      icon: Icons.assignment_outlined,
      title: 'CLIENT PROPOSAL CONTEXT',
      subtitle: 'Submitted for supervisor intake review upon saving',
      trailing: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
        decoration: BoxDecoration(
          color: Colors.amber.shade100,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.amber.shade300),
        ),
        child: Text(
          'Awaiting Review',
          style: TextStyle(
            fontSize: 10,
            fontWeight: FontWeight.bold,
            color: Colors.amber.shade900,
          ),
        ),
      ),
      children: [
        Row(
          children: [
            Expanded(
              child: DropdownButtonFormField<String>(
                initialValue: _selectedRiskLevel,
                decoration: _inputDeco(
                  context,
                  labelText: 'Initial Risk Level *',
                  prefixIcon: const Icon(Icons.shield_outlined, size: 18),
                ),
                items: _riskLevels
                    .map((r) => DropdownMenuItem(value: r, child: Text('$r Risk', style: const TextStyle(fontSize: 13))))
                    .toList(),
                onChanged: (val) {
                  if (val != null) setState(() => _selectedRiskLevel = val);
                },
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: DropdownButtonFormField<String?>(
                initialValue: _selectedTeamId,
                isExpanded: true,
                decoration: _inputDeco(
                  context,
                  labelText: 'Assigned Team (Optional)',
                  prefixIcon: const Icon(Icons.groups_outlined, size: 18),
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
            ),
          ],
        ),
        const SizedBox(height: 12),
        TextFormField(
          controller: _notesController,
          maxLines: 2,
          decoration: _inputDeco(
            context,
            labelText: 'Submission Rationale / Intake Notes',
            hintText: 'Immediate safety or stabilization needs, background...',
            prefixIcon: const Icon(Icons.edit_note, size: 20),
          ),
        ),
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final isDark = theme.brightness == Brightness.dark;

    final isEditMode = widget.initialClient != null;

    return Scaffold(
      appBar: AppBar(
        title: Text(isEditMode ? 'Edit Client Record' : 'Register New Client'),
        actions: [
          TextButton.icon(
            onPressed: _isSaving ? null : _saveClientDraft,
            icon: const Icon(Icons.check, size: 18),
            label: const Text('Save', style: TextStyle(fontWeight: FontWeight.bold)),
          ),
        ],
      ),
      bottomNavigationBar: _buildNavigationFooter(colorScheme),
      body: Form(
        key: _formKey,
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // ── STEPPER PROGRESS HEADER ──
              AnimatedBuilder(
                animation: _tabController,
                builder: (context, _) => _buildStepperHeader(colorScheme, isDark),
              ),
              const SizedBox(height: 16),

              // ── PROPOSAL CONTEXT CARD ──
              _buildContextCard(colorScheme),

              // ── ACTIVE TAB CONTENT ──
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
            ],
          ),
        ),
      ),
    );
  }

  // ── Tab 1: Identity & Vital Information ──
  Widget _buildIdentityTab(ColorScheme colorScheme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Photo Avatar Card
        _buildSectionCard(
          context: context,
          icon: Icons.camera_alt_outlined,
          title: 'CLIENT PROFILE PHOTO',
          subtitle: 'EXIF metadata stripped automatically for safety & privacy',
          children: [
            Row(
              children: [
                Stack(
                  children: [
                    CircleAvatar(
                      radius: 36,
                      backgroundColor: colorScheme.primary.withValues(alpha: 0.12),
                      backgroundImage: _photoFile != null
                          ? FileImage(_photoFile!)
                          : (_existingPhotoUrl != null && _existingPhotoUrl!.isNotEmpty
                              ? NetworkImage(_existingPhotoUrl!) as ImageProvider
                              : null),
                      child: (_photoFile == null && (_existingPhotoUrl == null || _existingPhotoUrl!.isEmpty))
                          ? Text(
                              '${_firstNameController.text.isNotEmpty ? _firstNameController.text[0] : ""}${_lastNameController.text.isNotEmpty ? _lastNameController.text[0] : "?"}',
                              style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: colorScheme.primary),
                            )
                          : null,
                    ),
                    Positioned(
                      bottom: 0,
                      right: 0,
                      child: InkWell(
                        onTap: _showPhotoOptions,
                        borderRadius: BorderRadius.circular(16),
                        child: Container(
                          padding: const EdgeInsets.all(5),
                          decoration: BoxDecoration(
                            color: colorScheme.primary,
                            shape: BoxShape.circle,
                            border: Border.all(color: Colors.white, width: 2),
                          ),
                          child: const Icon(Icons.camera_alt, size: 14, color: Colors.white),
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          FilledButton.tonalIcon(
                            onPressed: _showPhotoOptions,
                            icon: const Icon(Icons.add_a_photo, size: 15),
                            label: Text(_photoFile != null || _existingPhotoUrl != null ? 'Change Photo' : 'Upload Photo'),
                            style: FilledButton.styleFrom(
                              visualDensity: VisualDensity.compact,
                              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                            ),
                          ),
                          if (_photoFile != null || _existingPhotoUrl != null) ...[
                            const SizedBox(width: 8),
                            TextButton(
                              onPressed: () => setState(() {
                                _photoFile = null;
                                _existingPhotoUrl = null;
                              }),
                              child: const Text('Remove', style: TextStyle(color: Colors.red, fontSize: 12)),
                            ),
                          ],
                        ],
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Supports Camera capture or Gallery photos (JPEG, PNG).',
                        style: TextStyle(fontSize: 11, color: colorScheme.onSurface.withValues(alpha: 0.55)),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ],
        ),

        // Legal Names Card
        _buildSectionCard(
          context: context,
          icon: Icons.person_outline,
          title: 'LEGAL IDENTITY NAMES',
          subtitle: 'Official name as recognized on provincial or treaty records',
          children: [
            Row(
              children: [
                Expanded(
                  child: TextFormField(
                    controller: _firstNameController,
                    decoration: _inputDeco(
                      context,
                      labelText: 'Legal First Name *',
                      prefixIcon: const Icon(Icons.person, size: 18),
                    ),
                    validator: (val) => val == null || val.trim().isEmpty ? 'Required' : null,
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: TextFormField(
                    controller: _lastNameController,
                    decoration: _inputDeco(
                      context,
                      labelText: 'Legal Last Name *',
                      prefixIcon: const Icon(Icons.person_outline, size: 18),
                    ),
                    validator: (val) => val == null || val.trim().isEmpty ? 'Required' : null,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _middleNameController,
              decoration: _inputDeco(
                context,
                labelText: 'Middle Name(s)',
                hintText: 'e.g. Marie or Traditional Clan Name',
                prefixIcon: const Icon(Icons.badge_outlined, size: 18),
              ),
            ),
          ],
        ),

        // Preferred & Aliases Card
        _buildSectionCard(
          context: context,
          icon: Icons.fingerprint,
          title: 'PREFERRED NAME & KNOWN ALIASES',
          subtitle: 'Used for daily kinship address and search resolution',
          children: [
            Row(
              children: [
                Expanded(
                  child: TextFormField(
                    controller: _preferredNameController,
                    decoration: _inputDeco(
                      context,
                      labelText: 'Preferred / Chosen Name',
                      hintText: 'e.g. Jay, Bear Child',
                      prefixIcon: const Icon(Icons.sentiment_satisfied_alt, size: 18),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: TextFormField(
                    controller: _aliasesController,
                    decoration: _inputDeco(
                      context,
                      labelText: 'Aliases / Former Names',
                      hintText: 'Comma-separated',
                      prefixIcon: const Icon(Icons.history_edu, size: 18),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),

        // Vital Statistics & Demographics Card
        _buildSectionCard(
          context: context,
          icon: Icons.cake_outlined,
          title: 'VITAL STATISTICS & DEMOGRAPHICS',
          subtitle: 'Birth records, gender identity, and primary communication',
          children: [
            Row(
              children: [
                Expanded(
                  child: InkWell(
                    onTap: () => _selectDob(context),
                    borderRadius: BorderRadius.circular(12),
                    child: InputDecorator(
                      decoration: _inputDeco(
                        context,
                        labelText: 'Date of Birth',
                        prefixIcon: const Icon(Icons.calendar_today, size: 18),
                      ),
                      child: Text(
                        _formatDobWithAge(_selectedDob),
                        style: TextStyle(
                          fontSize: 13,
                          fontWeight: _selectedDob != null ? FontWeight.bold : FontWeight.normal,
                          color: _selectedDob != null ? colorScheme.onSurface : colorScheme.onSurface.withValues(alpha: 0.5),
                        ),
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: DropdownButtonFormField<String>(
                    initialValue: _selectedGender,
                    decoration: _inputDeco(
                      context,
                      labelText: 'Gender',
                      prefixIcon: const Icon(Icons.wc, size: 18),
                    ),
                    items: _genderOptions
                        .map((g) => DropdownMenuItem(value: g, child: Text(g, style: const TextStyle(fontSize: 12))))
                        .toList(),
                    onChanged: (val) {
                      if (val != null) setState(() => _selectedGender = val);
                    },
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: TextFormField(
                    controller: _placeOfBirthController,
                    decoration: _inputDeco(
                      context,
                      labelText: 'Place of Birth',
                      hintText: 'e.g. Regina, SK',
                      prefixIcon: const Icon(Icons.location_city, size: 18),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: DropdownButtonFormField<String>(
                    initialValue: _selectedLanguage,
                    decoration: _inputDeco(
                      context,
                      labelText: 'Preferred Language',
                      prefixIcon: const Icon(Icons.translate, size: 18),
                    ),
                    items: _languageOptions
                        .map((l) => DropdownMenuItem(value: l, child: Text(l, style: const TextStyle(fontSize: 12))))
                        .toList(),
                    onChanged: (val) {
                      if (val != null) setState(() => _selectedLanguage = val);
                    },
                  ),
                ),
              ],
            ),
          ],
        ),

        // Official & Indigenous Identification Card
        _buildSectionCard(
          context: context,
          icon: Icons.card_membership_outlined,
          title: 'OFFICIAL & INDIGENOUS IDENTIFICATION',
          subtitle: 'Treaty card, band registry, and provincial health coverage',
          children: [
            TextFormField(
              controller: _treatyController,
              decoration: _inputDeco(
                context,
                labelText: 'Treaty / Status Card #',
                hintText: '10-digit Indian Status registration number',
                prefixIcon: const Icon(Icons.badge, size: 18),
              ),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: TextFormField(
                    controller: _bandNationController,
                    decoration: _inputDeco(
                      context,
                      labelText: 'Band / First Nation',
                      hintText: 'e.g. Cote First Nation',
                      prefixIcon: const Icon(Icons.account_balance, size: 18),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: TextFormField(
                    controller: _healthCardController,
                    decoration: _inputDeco(
                      context,
                      labelText: 'SK Health Card (HSN)',
                      hintText: '9-digit HSN',
                      prefixIcon: const Icon(Icons.medical_services_outlined, size: 18),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ],
    );
  }

  // ── Tab 2: Physical Identification & Observable Marks ──
  Widget _buildPhysicalIdTab(ColorScheme colorScheme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Biometrics Card
        _buildSectionCard(
          context: context,
          icon: Icons.straighten,
          title: 'BIOMETRIC METRICS',
          subtitle: 'Baseline physical attributes for field identification',
          children: [
            Row(
              children: [
                Expanded(
                  child: TextFormField(
                    controller: _eyeColourController,
                    decoration: _inputDeco(
                      context,
                      labelText: 'Eye Colour',
                      hintText: 'e.g. Brown',
                      prefixIcon: const Icon(Icons.remove_red_eye_outlined, size: 18),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: TextFormField(
                    controller: _hairColourController,
                    decoration: _inputDeco(
                      context,
                      labelText: 'Hair Colour',
                      hintText: 'e.g. Black',
                      prefixIcon: const Icon(Icons.face_outlined, size: 18),
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
                    decoration: _inputDeco(
                      context,
                      labelText: 'Height (cm)',
                      hintText: 'e.g. 165',
                      prefixIcon: const Icon(Icons.height, size: 18),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: TextFormField(
                    controller: _weightController,
                    keyboardType: TextInputType.number,
                    decoration: _inputDeco(
                      context,
                      labelText: 'Weight (kg)',
                      hintText: 'e.g. 60',
                      prefixIcon: const Icon(Icons.fitness_center_outlined, size: 18),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),

        // Observable Features & Marks
        _buildSectionCard(
          context: context,
          icon: Icons.draw_outlined,
          title: 'OBSERVABLE BODY MARKS & ART',
          subtitle: 'Distinguishing marks, scars, tattoos, and piercings',
          children: [
            TextFormField(
              controller: _tattoosController,
              decoration: _inputDeco(
                context,
                labelText: 'Tattoos & Body Art',
                hintText: 'Location, motifs, and descriptions',
                prefixIcon: const Icon(Icons.brush_outlined, size: 18),
              ),
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _piercingsController,
              decoration: _inputDeco(
                context,
                labelText: 'Piercings',
                hintText: 'Ears, facial, or body piercings',
                prefixIcon: const Icon(Icons.adjust_outlined, size: 18),
              ),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: TextFormField(
                    controller: _birthmarksController,
                    decoration: _inputDeco(
                      context,
                      labelText: 'Birthmarks',
                      hintText: 'Location and size',
                      prefixIcon: const Icon(Icons.circle_outlined, size: 18),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: TextFormField(
                    controller: _scarsController,
                    decoration: _inputDeco(
                      context,
                      labelText: 'Scars / Surgical Marks',
                      hintText: 'Location and appearance',
                      prefixIcon: const Icon(Icons.healing_outlined, size: 18),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _distinguishingMarksController,
              decoration: _inputDeco(
                context,
                labelText: 'Other Distinguishing Marks',
                hintText: 'Any other noticeable physical characteristics',
                prefixIcon: const Icon(Icons.visibility_outlined, size: 18),
              ),
            ),
          ],
        ),

        // Assistive Devices & Visual Aids
        _buildSectionCard(
          context: context,
          icon: Icons.visibility_outlined,
          title: 'OPTICAL AIDS & PHYSICAL NOTES',
          subtitle: 'Corrective lenses and special appearance notes',
          children: [
            Row(
              children: [
                Expanded(
                  child: SwitchListTile(
                    dense: true,
                    contentPadding: EdgeInsets.zero,
                    title: const Text('Wears Glasses', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
                    value: _wearsGlasses,
                    onChanged: (val) => setState(() => _wearsGlasses = val),
                  ),
                ),
                Expanded(
                  child: SwitchListTile(
                    dense: true,
                    contentPadding: EdgeInsets.zero,
                    title: const Text('Wears Contacts', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600)),
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
              decoration: _inputDeco(
                context,
                labelText: 'Physical Identifying Notes',
                hintText: 'Additional physical appearance notes for caseworkers...',
                prefixIcon: const Icon(Icons.notes, size: 18),
              ),
            ),
          ],
        ),
      ],
    );
  }

  // ── Tab 3: Contact & Primary Residential Address ──
  Widget _buildContactAddressTab(ColorScheme colorScheme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Direct Contact Information Card
        _buildSectionCard(
          context: context,
          icon: Icons.contact_phone_outlined,
          title: 'DIRECT CLIENT CONTACT',
          subtitle: 'Active phone and electronic communication channels',
          children: [
            Row(
              children: [
                Expanded(
                  child: TextFormField(
                    controller: _phoneController,
                    keyboardType: TextInputType.phone,
                    decoration: _inputDeco(
                      context,
                      labelText: 'Primary Phone',
                      hintText: '306-555-0100',
                      prefixIcon: const Icon(Icons.phone, size: 18),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: TextFormField(
                    controller: _emailController,
                    keyboardType: TextInputType.emailAddress,
                    decoration: _inputDeco(
                      context,
                      labelText: 'Email Address',
                      hintText: 'client@example.ca',
                      prefixIcon: const Icon(Icons.email_outlined, size: 18),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),

        // Emergency Contact Card
        _buildSectionCard(
          context: context,
          icon: Icons.contact_emergency_outlined,
          title: 'EMERGENCY CONTACT',
          subtitle: 'Immediate family or designated caregiver for urgent outreach',
          children: [
            Row(
              children: [
                Expanded(
                  flex: 5,
                  child: TextFormField(
                    controller: _emergNameController,
                    decoration: _inputDeco(
                      context,
                      labelText: 'Contact Full Name',
                      hintText: 'Full legal name',
                      prefixIcon: const Icon(Icons.person, size: 18),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  flex: 4,
                  child: TextFormField(
                    controller: _emergPhoneController,
                    keyboardType: TextInputType.phone,
                    decoration: _inputDeco(
                      context,
                      labelText: 'Phone Number',
                      hintText: '306-555-0199',
                      prefixIcon: const Icon(Icons.phone_in_talk, size: 18),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _emergRelController,
              decoration: _inputDeco(
                context,
                labelText: 'Relationship to Client',
                hintText: 'e.g. Grandmother, Auntie, Older Sibling, Foster Parent',
                prefixIcon: const Icon(Icons.family_restroom, size: 18),
              ),
            ),
          ],
        ),

        // Primary Residential Address Card
        _buildSectionCard(
          context: context,
          icon: Icons.home_outlined,
          title: 'PRIMARY RESIDENTIAL ADDRESS',
          subtitle: 'Current physical living location and territory',
          children: [
            TextFormField(
              controller: _address1Controller,
              decoration: _inputDeco(
                context,
                labelText: 'Street Address',
                hintText: '123 5th Avenue',
                prefixIcon: const Icon(Icons.signpost_outlined, size: 18),
              ),
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _address2Controller,
              decoration: _inputDeco(
                context,
                labelText: 'Address Line 2 (Apt / Suite / Unit #)',
                hintText: 'Suite 4B',
                prefixIcon: const Icon(Icons.apartment_outlined, size: 18),
              ),
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: TextFormField(
                    controller: _cityController,
                    decoration: _inputDeco(
                      context,
                      labelText: 'City',
                      prefixIcon: const Icon(Icons.location_city, size: 18),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: TextFormField(
                    controller: _provinceController,
                    decoration: _inputDeco(
                      context,
                      labelText: 'Province',
                      prefixIcon: const Icon(Icons.map_outlined, size: 18),
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
                    decoration: _inputDeco(
                      context,
                      labelText: 'Postal Code',
                      hintText: 'S4P 3Y2',
                      prefixIcon: const Icon(Icons.local_post_office_outlined, size: 18),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: _isOnReserve ? Colors.blue.withValues(alpha: 0.1) : Colors.transparent,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(
                        color: _isOnReserve ? Colors.blue.shade400 : Colors.grey.shade300,
                      ),
                    ),
                    child: SwitchListTile(
                      dense: true,
                      contentPadding: EdgeInsets.zero,
                      title: const Text('Located On-Reserve', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                      value: _isOnReserve,
                      onChanged: (val) => setState(() => _isOnReserve = val),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ],
    );
  }

  // ── Tab 4: Cultural Profile & Heritage Background ──
  Widget _buildCulturalTab(ColorScheme colorScheme) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Cultural & Customary Life Card
        _buildSectionCard(
          context: context,
          icon: Icons.nature_people_outlined,
          title: 'CULTURAL CONNECTIONS & CEREMONY',
          subtitle: 'Community kinship, ceremonial traditions, and customary practices',
          children: [
            TextFormField(
              controller: _culturalConnectionsController,
              maxLines: 2,
              decoration: _inputDeco(
                context,
                labelText: 'Cultural & Community Connections',
                hintText: 'Clan connections, band affiliations, urban Indigenous community ties...',
                prefixIcon: const Icon(Icons.groups, size: 18),
              ),
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _ceremoniesController,
              maxLines: 2,
              decoration: _inputDeco(
                context,
                labelText: 'Ceremonies & Customary Practices',
                hintText: 'Round dances, sweats, smudging, seasonal sundances, feasts...',
                prefixIcon: const Icon(Icons.wb_sunny_outlined, size: 18),
              ),
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _eldersConnectedController,
              decoration: _inputDeco(
                context,
                labelText: 'Elders / Knowledge Keepers Connected With',
                hintText: 'Names and home communities of connected Elders',
                prefixIcon: const Icon(Icons.elderly_outlined, size: 18),
              ),
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _landActivitiesController,
              decoration: _inputDeco(
                context,
                labelText: 'Land-Based Activities',
                hintText: 'Hunting, fishing, medicine picking, trapping, berry harvesting...',
                prefixIcon: const Icon(Icons.terrain_outlined, size: 18),
              ),
            ),
          ],
        ),

        // Personal Interests & Holistic Wellness
        _buildSectionCard(
          context: context,
          icon: Icons.sports_basketball_outlined,
          title: 'NUTRITION & EXTRACURRICULAR INTERESTS',
          subtitle: 'Traditional dietary preferences and recreational growth',
          children: [
            Row(
              children: [
                Expanded(
                  child: TextFormField(
                    controller: _dietaryController,
                    decoration: _inputDeco(
                      context,
                      labelText: 'Dietary Needs & Traditional Foods',
                      hintText: 'Wild meat, fish, allergies',
                      prefixIcon: const Icon(Icons.restaurant_outlined, size: 18),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: TextFormField(
                    controller: _extraCurricularController,
                    decoration: _inputDeco(
                      context,
                      labelText: 'Extracurricular Activities',
                      hintText: 'Sports, powwow, arts, music',
                      prefixIcon: const Icon(Icons.palette_outlined, size: 18),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),

        // Socioeconomic Background Card
        _buildSectionCard(
          context: context,
          icon: Icons.account_balance_wallet_outlined,
          title: 'SOCIOECONOMIC & LIVELIHOOD CONTEXT',
          subtitle: 'Employment, education, and financial stability context',
          children: [
            DropdownButtonFormField<String>(
              initialValue: _selectedEmploymentStatus.isNotEmpty ? _selectedEmploymentStatus : null,
              decoration: _inputDeco(
                context,
                labelText: 'Employment / Student Status',
                prefixIcon: const Icon(Icons.work_outline, size: 18),
              ),
              items: [
                const DropdownMenuItem(value: '', child: Text('-- Select Status --')),
                ..._employmentStatuses.map((s) => DropdownMenuItem(value: s, child: Text(s, style: const TextStyle(fontSize: 13)))),
              ],
              onChanged: (val) {
                setState(() => _selectedEmploymentStatus = val ?? '');
              },
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: TextFormField(
                    controller: _employerController,
                    decoration: _inputDeco(
                      context,
                      labelText: 'Employer / School',
                      hintText: 'Organization name',
                      prefixIcon: const Icon(Icons.school_outlined, size: 18),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: TextFormField(
                    controller: _sourceOfIncomeController,
                    decoration: _inputDeco(
                      context,
                      labelText: 'Source of Income',
                      hintText: 'Employment, SIS, SAID, EI',
                      prefixIcon: const Icon(Icons.payments_outlined, size: 18),
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ],
    );
  }
}
