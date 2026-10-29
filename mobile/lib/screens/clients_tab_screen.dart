import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../services/auth_service.dart';
import '../services/connectivity_service.dart';
import '../services/db_helper.dart';
import '../services/theme_service.dart';
import 'client_draft_screen.dart';

class ClientsTabScreen extends StatefulWidget {
  final VoidCallback onOpenDrawer;

  const ClientsTabScreen({super.key, required this.onOpenDrawer});

  @override
  State<ClientsTabScreen> createState() => _ClientsTabScreenState();
}

class _ClientsTabScreenState extends State<ClientsTabScreen> {
  final _dbHelper = LocalDatabaseHelper.instance;
  final _authService = MobileAuthService.instance;

  bool _isLoading = true;
  bool _canDelete = false;
  String _searchQuery = '';
  String _activeFilter = 'ALL'; // ALL, APPROVED, PENDING, OFFLINE

  List<Map<String, dynamic>> _clients = [];
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _loadClients();
  }

  Future<void> _loadClients() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final isOnline = await ConnectivityService.instance.checkConnectivity();
    final canDelete = await _authService.canDeleteClients();

    final List<Map<String, dynamic>> combinedList = [];

    // 1. Fetch Local Drafts from SQLite
    try {
      final allDrafts = await _dbHelper.getAllDrafts();
      final clientDrafts = allDrafts.where((d) => d['entity_type'] == 'CLIENT').toList();
      for (final draft in clientDrafts) {
        final payload = draft['payload'] is Map<String, dynamic>
            ? draft['payload'] as Map<String, dynamic>
            : (draft['payload'] is String ? jsonDecode(draft['payload']) : <String, dynamic>{});

        final titleParts = (draft['title']?.toString() ?? '').trim().split(' ');
        final draftFirst = titleParts.isNotEmpty && titleParts.first.isNotEmpty ? titleParts.first : 'Draft';
        final draftLast = titleParts.length > 1 ? titleParts.sublist(1).join(' ') : 'Client';

        combinedList.add({
          'id': draft['id'],
          'is_remote': false,
          'first_name': payload['first_name'] ?? draftFirst,
          'last_name': payload['last_name'] ?? draftLast,
          'person_id_number': draft['person_id_number'] ?? 'DRAFT-${draft['id']?.toString().substring(0, 8)}',
          'approval_status': 'PENDING_APPROVAL',
          'status': 'Offline Draft',
          'risk_level': payload['risk_level'] ?? 'Low',
          'band_nation': payload['band_nation'] ?? 'Cote First Nation',
          'city': payload['city'] ?? 'Regina',
          'province': payload['province'] ?? 'SK',
          'date_of_birth': payload['date_of_birth'],
          'phone': payload['phone'],
          'email': payload['email'],
          'photo_url': payload['photo_path'],
          'submission_notes': payload['notes'],
          'raw_payload': payload,
          'sync_status': draft['sync_status'] ?? 'PENDING',
        });
      }
    } catch (e) {
      // Local SQLite read warning
    }

    // 2. Fetch Central Platform Clients if online
    if (isOnline) {
      try {
        final serverUrl = (await _authService.getServerUrl()).replaceAll(RegExp(r'/+$'), '');
        final token = await _authService.getAccessToken();

        if (token != null && token.isNotEmpty) {
          // A. Fetch Active Clients
          final uri = Uri.parse('$serverUrl/api/v1/clients?limit=100');
          final response = await http.get(
            uri,
            headers: {
              'Content-Type': 'application/json',
              'Authorization': 'Bearer $token',
            },
          ).timeout(const Duration(seconds: 15));

          if (response.statusCode == 200) {
            final data = jsonDecode(response.body);
            final items = data is Map && data['items'] is List
                ? data['items'] as List
                : (data is List ? data : []);

            for (final item in items) {
              if (item is Map) {
                final mapItem = Map<String, dynamic>.from(item);
                combinedList.add({
                  'id': mapItem['id'],
                  'is_remote': true,
                  'is_trash': false,
                  'first_name': mapItem['first_name'] ?? '',
                  'last_name': mapItem['last_name'] ?? '',
                  'middle_name': mapItem['middle_name'],
                  'preferred_name': mapItem['preferred_name'],
                  'aliases': mapItem['aliases'],
                  'person_id': mapItem['person_id'],
                  'person_id_number': mapItem['person_id_number'] ?? 'PENDING-ID',
                  'approval_status': (mapItem['approval_status'] ?? 'APPROVED').toString().toUpperCase(),
                  'status': mapItem['status'] ?? 'Active',
                  'risk_level': mapItem['risk_level'] ?? 'Low',
                  'band_nation': mapItem['band_nation'] ?? 'First Nations',
                  'city': mapItem['city'] ?? 'Regina',
                  'province': mapItem['province'] ?? 'SK',
                  'date_of_birth': mapItem['date_of_birth'],
                  'gender': mapItem['gender'],
                  'phone': mapItem['phone'],
                  'email': mapItem['email'],
                  'photo_url': mapItem['photo_url'],
                  'submission_notes': mapItem['submission_notes'],
                  'submitted_by_name': mapItem['submitted_by_name'],
                  'decided_by_name': mapItem['decided_by_name'],
                  'raw_payload': mapItem,
                  'sync_status': 'SYNCED',
                });
              }
            }
          }

          // B. Fetch Trash Clients (soft-deleted in last 45 days) — restricted to supervisors upward
          if (canDelete) {
            try {
              final trashUri = Uri.parse('$serverUrl/api/v1/clients?trash=true&limit=100');
              final trashResponse = await http.get(
                trashUri,
                headers: {
                  'Content-Type': 'application/json',
                  'Authorization': 'Bearer $token',
                },
              ).timeout(const Duration(seconds: 15));

              if (trashResponse.statusCode == 200) {
                final trashData = jsonDecode(trashResponse.body);
                final trashItems = trashData is Map && trashData['items'] is List
                    ? trashData['items'] as List
                    : (trashData is List ? trashData : []);

                for (final item in trashItems) {
                  if (item is Map) {
                    final mapItem = Map<String, dynamic>.from(item);
                    combinedList.add({
                      'id': mapItem['id'],
                      'is_remote': true,
                      'is_trash': true,
                      'days_until_purge': mapItem['days_until_purge'] ?? 45,
                      'deleted_at': mapItem['deleted_at'],
                      'first_name': mapItem['first_name'] ?? '',
                      'last_name': mapItem['last_name'] ?? '',
                      'middle_name': mapItem['middle_name'],
                      'preferred_name': mapItem['preferred_name'],
                      'aliases': mapItem['aliases'],
                      'person_id': mapItem['person_id'],
                      'person_id_number': mapItem['person_id_number'] ?? 'PENDING-ID',
                      'approval_status': (mapItem['approval_status'] ?? 'APPROVED').toString().toUpperCase(),
                      'status': 'In Trash',
                      'risk_level': mapItem['risk_level'] ?? 'Low',
                      'band_nation': mapItem['band_nation'] ?? 'First Nations',
                      'city': mapItem['city'] ?? 'Regina',
                      'province': mapItem['province'] ?? 'SK',
                      'date_of_birth': mapItem['date_of_birth'],
                      'gender': mapItem['gender'],
                      'phone': mapItem['phone'],
                      'email': mapItem['email'],
                      'photo_url': mapItem['photo_url'],
                      'submission_notes': mapItem['submission_notes'],
                      'submitted_by_name': mapItem['submitted_by_name'],
                      'decided_by_name': mapItem['decided_by_name'],
                      'raw_payload': mapItem,
                      'sync_status': 'TRASH',
                    });
                  }
                }
              }
            } catch (_) {
              // Trash query error fallback
            }
          }
        }
      } catch (err) {
        _errorMessage = 'Could not load platform clients: $err';
      }
    }

    if (mounted) {
      setState(() {
        _canDelete = canDelete;
        if (!canDelete && _activeFilter == 'TRASH') {
          _activeFilter = 'ALL';
        }
        _clients = combinedList;
        _isLoading = false;
      });
    }
  }

  Future<void> _deleteClient(Map<String, dynamic> client) async {
    final clientName = '${client['first_name']} ${client['last_name']}';
    final clientId = client['id']?.toString() ?? '';
    final isRemote = client['is_remote'] == true;

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Row(
          children: const [
            Icon(Icons.delete_outline, color: Colors.red),
            SizedBox(width: 8),
            Text('Move Client to Trash?'),
          ],
        ),
        content: Text(
          'Are you sure you want to move $clientName (#${client['person_id_number']}) to the Trash?\n\n'
          '${isRemote ? "The record will be kept in Trash for 45 days before permanent purge, and can be restored at any time." : "This will remove the local offline draft."}',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red, foregroundColor: Colors.white),
            child: const Text('Move to Trash'),
          ),
        ],
      ),
    );

    if (confirmed != true) return;

    setState(() => _isLoading = true);

    try {
      if (isRemote) {
        final serverUrl = (await _authService.getServerUrl()).replaceAll(RegExp(r'/+$'), '');
        final token = await _authService.getAccessToken();

        if (token != null && token.isNotEmpty) {
          final uri = Uri.parse('$serverUrl/api/v1/clients/$clientId');
          final response = await http.delete(
            uri,
            headers: {
              'Content-Type': 'application/json',
              'Authorization': 'Bearer $token',
            },
          ).timeout(const Duration(seconds: 15));

          if (response.statusCode != 200 && response.statusCode != 204) {
            throw Exception('Failed with status code ${response.statusCode}');
          }
        }
      } else {
        await _dbHelper.deleteDraft(clientId);
      }

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Client $clientName moved to Trash (held for 45 days).'),
            backgroundColor: CrbclTokens.statusSuccess,
          ),
        );
      }
      await _loadClients();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to delete client: $e'),
            backgroundColor: CrbclTokens.statusError,
          ),
        );
        setState(() => _isLoading = false);
      }
    }
  }

  Future<void> _restoreClient(Map<String, dynamic> client) async {
    final clientName = '${client['first_name']} ${client['last_name']}';
    final clientId = client['id']?.toString() ?? '';

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Row(
          children: const [
            Icon(Icons.restore, color: Colors.green),
            SizedBox(width: 8),
            Text('Restore Client Profile?'),
          ],
        ),
        content: Text(
          'Restore $clientName (#${client['person_id_number']}) back to active directories?\n\n'
          'The client will immediately reappear in the active clients directory and field rosters.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.green.shade700, foregroundColor: Colors.white),
            child: const Text('Restore Client'),
          ),
        ],
      ),
    );

    if (confirmed != true) return;

    setState(() => _isLoading = true);

    try {
      final serverUrl = (await _authService.getServerUrl()).replaceAll(RegExp(r'/+$'), '');
      final token = await _authService.getAccessToken();

      if (token != null && token.isNotEmpty) {
        final uri = Uri.parse('$serverUrl/api/v1/clients/$clientId/restore');
        final response = await http.post(
          uri,
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer $token',
          },
        ).timeout(const Duration(seconds: 15));

        if (response.statusCode != 200 && response.statusCode != 204) {
          throw Exception('Failed with status code ${response.statusCode}');
        }
      }

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Client $clientName successfully restored from Trash.'),
            backgroundColor: CrbclTokens.statusSuccess,
          ),
        );
      }
      await _loadClients();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to restore client: $e'),
            backgroundColor: CrbclTokens.statusError,
          ),
        );
        setState(() => _isLoading = false);
      }
    }
  }

  Future<void> _permanentDeleteClient(Map<String, dynamic> client) async {
    final clientName = '${client['first_name']} ${client['last_name']}';
    final clientId = client['id']?.toString() ?? '';

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Row(
          children: const [
            Icon(Icons.warning_amber_rounded, color: Colors.red),
            SizedBox(width: 8),
            Text('Permanently Delete?'),
          ],
        ),
        content: Text(
          '⚠️ WARNING: Are you sure you want to permanently delete $clientName (#${client['person_id_number']})?\n\n'
          'This action is IRREVERSIBLE. All canonical data and records will be permanently erased.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red.shade800, foregroundColor: Colors.white),
            child: const Text('Permanently Delete'),
          ),
        ],
      ),
    );

    if (confirmed != true) return;

    setState(() => _isLoading = true);

    try {
      final serverUrl = (await _authService.getServerUrl()).replaceAll(RegExp(r'/+$'), '');
      final token = await _authService.getAccessToken();

      if (token != null && token.isNotEmpty) {
        final uri = Uri.parse('$serverUrl/api/v1/clients/$clientId/permanent');
        final response = await http.delete(
          uri,
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer $token',
          },
        ).timeout(const Duration(seconds: 15));

        if (response.statusCode != 200 && response.statusCode != 204) {
          throw Exception('Failed with status code ${response.statusCode}');
        }
      }

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Client $clientName permanently deleted.'),
            backgroundColor: CrbclTokens.statusSuccess,
          ),
        );
      }
      await _loadClients();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to permanently delete client: $e'),
            backgroundColor: CrbclTokens.statusError,
          ),
        );
        setState(() => _isLoading = false);
      }
    }
  }

  void _viewClientProfile(Map<String, dynamic> client) {
    final colorScheme = Theme.of(context).colorScheme;

    final clientName = '${client['first_name']} ${client['last_name']}';
    final personIdNumber = client['person_id_number'] ?? 'PENDING-ID';
    final status = client['approval_status'] ?? 'APPROVED';
    final raw = client['raw_payload'] as Map<String, dynamic>? ?? {};

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) => DraggableScrollableSheet(
        initialChildSize: 0.85,
        minChildSize: 0.5,
        maxChildSize: 0.95,
        expand: false,
        builder: (_, scrollController) => Scaffold(
          appBar: AppBar(
            title: Text(clientName),
            leading: IconButton(
              icon: const Icon(Icons.close),
              onPressed: () => Navigator.pop(ctx),
            ),
            actions: [
              if (client['is_trash'] == true && _canDelete) ...[
                IconButton(
                  icon: const Icon(Icons.restore, color: Colors.green),
                  tooltip: 'Restore Client',
                  onPressed: () {
                    Navigator.pop(ctx);
                    _restoreClient(client);
                  },
                ),
                IconButton(
                  icon: const Icon(Icons.delete_forever, color: Colors.red),
                  tooltip: 'Permanently Delete',
                  onPressed: () {
                    Navigator.pop(ctx);
                    _permanentDeleteClient(client);
                  },
                ),
              ] else if (client['is_trash'] != true) ...[
                IconButton(
                  icon: const Icon(Icons.edit_outlined),
                  tooltip: 'Edit Client',
                  onPressed: () {
                    Navigator.pop(ctx);
                    _editClient(client);
                  },
                ),
                if (_canDelete)
                  IconButton(
                    icon: const Icon(Icons.delete_outline, color: Colors.red),
                    tooltip: 'Move to Trash',
                    onPressed: () {
                      Navigator.pop(ctx);
                      _deleteClient(client);
                    },
                  ),
              ],
            ],
          ),
          body: SingleChildScrollView(
            controller: scrollController,
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                if (client['is_trash'] == true) ...[
                  Container(
                    margin: const EdgeInsets.only(bottom: 14),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.red.withValues(alpha: 0.12),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: Colors.red.shade300),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.delete_outline, color: Colors.red, size: 22),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                'This client is in Trash (${client['days_until_purge'] ?? 45} days remaining)',
                                style: const TextStyle(color: Colors.red, fontWeight: FontWeight.bold, fontSize: 13),
                              ),
                              const SizedBox(height: 2),
                              Text(
                                'Soft-deleted records are retained for 45 days. You can restore or permanently delete this profile.',
                                style: TextStyle(color: Colors.red.shade900, fontSize: 11),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
                // Header Profile Info
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    CircleAvatar(
                      radius: 36,
                      backgroundColor: colorScheme.primary.withValues(alpha: 0.15),
                      backgroundImage: client['photo_url'] != null && client['photo_url'].toString().startsWith('http')
                          ? NetworkImage(client['photo_url'])
                          : null,
                      child: client['photo_url'] == null || !client['photo_url'].toString().startsWith('http')
                          ? Text(
                              '${client['first_name']?.toString().isNotEmpty == true ? client['first_name'][0] : ""}${client['last_name']?.toString().isNotEmpty == true ? client['last_name'][0] : ""}',
                              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: colorScheme.primary),
                            )
                          : null,
                    ),
                    const SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            clientName,
                            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                          ),
                          const SizedBox(height: 4),
                          Wrap(
                            spacing: 6,
                            runSpacing: 4,
                            children: [
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                                decoration: BoxDecoration(
                                  color: colorScheme.surfaceContainerHighest,
                                  borderRadius: BorderRadius.circular(6),
                                  border: Border.all(color: colorScheme.outlineVariant),
                                ),
                                child: Text(
                                  '#$personIdNumber',
                                  style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, fontFamily: 'monospace'),
                                ),
                              ),
                              _buildApprovalBadge(status),
                              _buildRiskBadge(client['risk_level'] ?? 'Low'),
                            ],
                          ),
                          const SizedBox(height: 6),
                          Text(
                            '${client['band_nation'] ?? "First Nations"} • ${client['city'] ?? "Regina"}, ${client['province'] ?? "SK"}',
                            style: TextStyle(fontSize: 12, color: colorScheme.onSurface.withValues(alpha: 0.7)),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 20),
                const Divider(),

                // Demographics & Contact Card
                _buildProfileSection(
                  title: 'Demographics & Contact Information',
                  icon: Icons.person_pin_outlined,
                  colorScheme: colorScheme,
                  items: [
                    {'label': 'Legal Name', 'value': '$clientName ${raw['middle_name'] != null ? "(${raw['middle_name']})" : ""}'},
                    {'label': 'Preferred / Alias', 'value': raw['preferred_name'] ?? raw['aliases'] ?? 'None'},
                    {'label': 'Date of Birth', 'value': client['date_of_birth'] ?? 'Not recorded'},
                    {'label': 'Gender Identity', 'value': client['gender'] ?? raw['gender'] ?? 'Not specified'},
                    {'label': 'Phone Number', 'value': client['phone'] ?? 'None on file'},
                    {'label': 'Email Address', 'value': client['email'] ?? 'None on file'},
                    {'label': 'Primary Residence', 'value': '${raw['primary_address']?['address_line_1'] ?? raw['address'] ?? "Regina"}, ${client['city'] ?? "Regina"}, ${client['province'] ?? "SK"}'},
                    {'label': 'Emergency Contact', 'value': raw['emergency_contact_name'] != null ? '${raw['emergency_contact_name']} (${raw['emergency_contact_phone'] ?? "No phone"})' : 'None listed'},
                  ],
                ),

                const SizedBox(height: 16),
                // Indigenous & Cultural Profile
                _buildProfileSection(
                  title: 'Indigenous Profile & Cultural Roots',
                  icon: Icons.flag_outlined,
                  colorScheme: colorScheme,
                  items: [
                    {'label': 'Band / Nation', 'value': client['band_nation'] ?? 'Cote First Nation'},
                    {'label': 'Treaty / Status Card #', 'value': raw['treaty_number'] ?? 'None recorded'},
                    {'label': 'Indigenous Identity', 'value': raw['indigenous_identity'] ?? 'First Nations'},
                    {'label': 'Cultural Connections', 'value': raw['cultural_profile']?['cultural_connections'] ?? 'None recorded'},
                    {'label': 'Ceremonies', 'value': raw['cultural_profile']?['ceremonies'] ?? 'None recorded'},
                    {'label': 'Elders Connected', 'value': raw['cultural_profile']?['elders_connected'] ?? 'None recorded'},
                  ],
                ),

                const SizedBox(height: 16),
                // Health & Physical Profile
                _buildProfileSection(
                  title: 'Health & Identifying Features',
                  icon: Icons.medical_services_outlined,
                  colorScheme: colorScheme,
                  items: [
                    {'label': 'Health Services Card (HSN)', 'value': raw['health_card_number'] ?? 'Not provided'},
                    {'label': 'Height / Weight', 'value': '${raw['physical_description']?['height_cm'] != null ? "${raw['physical_description']['height_cm']} cm" : "--"} / ${raw['physical_description']?['weight_kg'] != null ? "${raw['physical_description']['weight_kg']} kg" : "--"}'},
                    {'label': 'Eye / Hair Colour', 'value': '${raw['physical_description']?['eye_colour'] ?? "--"} / ${raw['physical_description']?['hair_colour'] ?? "--"}'},
                    {'label': 'Marks & Tattoos', 'value': raw['physical_description']?['distinguishing_marks'] ?? 'None flagged'},
                  ],
                ),

                if (client['submission_notes'] != null && client['submission_notes'].toString().isNotEmpty) ...[
                  const SizedBox(height: 16),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: colorScheme.surfaceContainerHighest.withValues(alpha: 0.5),
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: colorScheme.outlineVariant),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('Submission Rationale & Field Notes', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
                        const SizedBox(height: 4),
                        Text(client['submission_notes'].toString(), style: const TextStyle(fontSize: 12, fontStyle: FontStyle.italic)),
                      ],
                    ),
                  ),
                ],
                const SizedBox(height: 24),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildProfileSection({
    required String title,
    required IconData icon,
    required ColorScheme colorScheme,
    required List<Map<String, String>> items,
  }) {
    return Card(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: colorScheme.outlineVariant.withValues(alpha: 0.5)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(14.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, size: 16, color: colorScheme.primary),
                const SizedBox(width: 8),
                Text(
                  title,
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: colorScheme.primary),
                ),
              ],
            ),
            const SizedBox(height: 12),
            ...items.map((it) => Padding(
                  padding: const EdgeInsets.only(bottom: 8.0),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      SizedBox(
                        width: 130,
                        child: Text(
                          it['label']!,
                          style: TextStyle(fontSize: 12, color: colorScheme.onSurface.withValues(alpha: 0.6)),
                        ),
                      ),
                      Expanded(
                        child: Text(
                          it['value']!,
                          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w500),
                        ),
                      ),
                    ],
                  ),
                )),
          ],
        ),
      ),
    );
  }

  Future<void> _editClient(Map<String, dynamic> client) async {
    final updated = await Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => ClientDraftScreen(initialClient: client['raw_payload'] ?? client),
      ),
    );
    if (updated == true) {
      _loadClients();
    }
  }

  Widget _buildApprovalBadge(String status) {
    Color bg = CrbclTokens.statusSuccess.withValues(alpha: 0.15);
    Color fg = CrbclTokens.statusSuccess;
    String label = 'Approved';

    if (status == 'PENDING_APPROVAL' || status == 'PENDING') {
      bg = Colors.amber.withValues(alpha: 0.15);
      fg = Colors.amber.shade800;
      label = 'Pending Review';
    } else if (status == 'RETURNED') {
      bg = Colors.orange.withValues(alpha: 0.15);
      fg = Colors.orange.shade800;
      label = 'Returned';
    } else if (status == 'DECLINED') {
      bg = Colors.red.withValues(alpha: 0.15);
      fg = Colors.red.shade700;
      label = 'Declined';
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2.5),
      decoration: BoxDecoration(color: bg, borderRadius: BorderRadius.circular(5)),
      child: Text(label, style: TextStyle(color: fg, fontSize: 10, fontWeight: FontWeight.bold)),
    );
  }

  Widget _buildRiskBadge(String risk) {
    Color bg = Colors.blue.withValues(alpha: 0.12);
    Color fg = Colors.blue.shade800;
    final r = risk.toUpperCase();

    if (r.contains('HIGH')) {
      bg = Colors.red.withValues(alpha: 0.15);
      fg = Colors.red.shade800;
    } else if (r.contains('MED')) {
      bg = Colors.orange.withValues(alpha: 0.15);
      fg = Colors.orange.shade800;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2.5),
      decoration: BoxDecoration(color: bg, borderRadius: BorderRadius.circular(5)),
      child: Text('$risk Risk', style: TextStyle(color: fg, fontSize: 10, fontWeight: FontWeight.bold)),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final isDark = theme.brightness == Brightness.dark;

    final activeClients = _clients.where((c) => c['is_trash'] != true).toList();
    final approvedCount = activeClients.where((c) => c['approval_status'] == 'APPROVED').length;
    final pendingCount = activeClients.where((c) => c['approval_status'] == 'PENDING_APPROVAL').length;
    final returnedCount = activeClients.where((c) => c['approval_status'] == 'RETURNED').length;
    final offlineCount = activeClients.where((c) => c['is_remote'] == false).length;
    final trashCount = _clients.where((c) => c['is_trash'] == true).length;

    final filtered = _clients.where((c) {
      final isTrash = c['is_trash'] == true;
      if (_activeFilter == 'TRASH') {
        if (!isTrash) return false;
      } else {
        if (isTrash) return false;
        if (_activeFilter == 'APPROVED' && c['approval_status'] != 'APPROVED') return false;
        if (_activeFilter == 'PENDING' && c['approval_status'] != 'PENDING_APPROVAL') return false;
        if (_activeFilter == 'RETURNED' && c['approval_status'] != 'RETURNED') return false;
        if (_activeFilter == 'OFFLINE' && c['is_remote'] == true) return false;
      }

      // Search query
      if (_searchQuery.trim().isEmpty) return true;
      final q = _searchQuery.toLowerCase();
      final name = '${c['first_name']} ${c['last_name']}'.toLowerCase();
      final pid = (c['person_id_number'] ?? '').toString().toLowerCase();
      final nation = (c['band_nation'] ?? '').toString().toLowerCase();
      final email = (c['email'] ?? '').toString().toLowerCase();
      final phone = (c['phone'] ?? '').toString().toLowerCase();

      return name.contains(q) || pid.contains(q) || nation.contains(q) || email.contains(q) || phone.contains(q);
    }).toList();

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.menu),
          tooltip: 'Open navigation menu',
          onPressed: widget.onOpenDrawer,
        ),
        title: const Text('Clients • Field Directory'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Refresh Clients',
            onPressed: _loadClients,
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () async {
          final created = await Navigator.pushNamed(context, '/client-draft');
          if (created == true) _loadClients();
        },
        backgroundColor: colorScheme.primary,
        foregroundColor: colorScheme.onPrimary,
        icon: const Icon(Icons.person_add),
        label: const Text('Register Client'),
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadClients,
              child: SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // Search box
                    TextField(
                      decoration: InputDecoration(
                        hintText: 'Search by name, #ID, nation, email, phone...',
                        prefixIcon: const Icon(Icons.search),
                        isDense: true,
                        filled: true,
                        fillColor: isDark ? colorScheme.surfaceContainerHighest : Colors.white,
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                      onChanged: (val) => setState(() => _searchQuery = val),
                    ),
                    const SizedBox(height: 12),

                    // Filter Chips Row
                    SingleChildScrollView(
                      scrollDirection: Axis.horizontal,
                      child: Row(
                        children: [
                          ChoiceChip(
                            label: Text('All (${activeClients.length})'),
                            selected: _activeFilter == 'ALL',
                            onSelected: (_) => setState(() => _activeFilter = 'ALL'),
                          ),
                          const SizedBox(width: 8),
                          ChoiceChip(
                            label: Text('Approved ($approvedCount)'),
                            selected: _activeFilter == 'APPROVED',
                            onSelected: (_) => setState(() => _activeFilter = 'APPROVED'),
                          ),
                          const SizedBox(width: 8),
                          ChoiceChip(
                            label: Text('Pending ($pendingCount)'),
                            selected: _activeFilter == 'PENDING',
                            onSelected: (_) => setState(() => _activeFilter = 'PENDING'),
                          ),
                          const SizedBox(width: 8),
                          ChoiceChip(
                            label: Text('Returned ($returnedCount)'),
                            selected: _activeFilter == 'RETURNED',
                            onSelected: (_) => setState(() => _activeFilter = 'RETURNED'),
                          ),
                          const SizedBox(width: 8),
                          ChoiceChip(
                            label: Text('Offline Drafts ($offlineCount)'),
                            selected: _activeFilter == 'OFFLINE',
                            onSelected: (_) => setState(() => _activeFilter = 'OFFLINE'),
                          ),
                          if (_canDelete) ...[
                            const SizedBox(width: 8),
                            ChoiceChip(
                              avatar: Icon(
                                Icons.delete_outline,
                                size: 15,
                                color: _activeFilter == 'TRASH' ? Colors.white : Colors.red.shade700,
                              ),
                              label: Text(
                                'Trash ($trashCount)',
                                style: TextStyle(
                                  color: _activeFilter == 'TRASH' ? Colors.white : Colors.red.shade700,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              selected: _activeFilter == 'TRASH',
                              selectedColor: Colors.red.shade700,
                              onSelected: (_) => setState(() => _activeFilter = 'TRASH'),
                            ),
                          ],
                        ],
                      ),
                    ),
                    const SizedBox(height: 14),

                    // Error warning if any
                    if (_errorMessage != null) ...[
                      Container(
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: Colors.amber.withValues(alpha: 0.15),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: Colors.amber.shade700),
                        ),
                        child: Row(
                          children: [
                            Icon(Icons.wifi_off, size: 16, color: Colors.amber.shade800),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                _errorMessage!,
                                style: TextStyle(fontSize: 12, color: Colors.amber.shade900),
                              ),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 12),
                    ],

                    // Empty State
                    if (filtered.isEmpty)
                      Card(
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                          side: BorderSide(
                            color: isDark ? colorScheme.outlineVariant : CrbclTokens.lightBorder,
                            width: 1,
                          ),
                        ),
                        color: colorScheme.surfaceContainer,
                        child: Padding(
                          padding: const EdgeInsets.symmetric(vertical: 40.0, horizontal: 16.0),
                          child: Column(
                            children: [
                              Icon(
                                Icons.people_outline,
                                size: 48,
                                color: colorScheme.onSurface.withValues(alpha: 0.4),
                              ),
                              const SizedBox(height: 12),
                              Text(
                                _searchQuery.isEmpty ? 'No clients found' : 'No clients matching "$_searchQuery"',
                                style: TextStyle(
                                  fontWeight: FontWeight.bold,
                                  fontSize: 14,
                                  color: colorScheme.onSurface.withValues(alpha: 0.7),
                                ),
                              ),
                              const SizedBox(height: 6),
                              Text(
                                'Tap "+ Register Client" to record a new client record.',
                                style: TextStyle(
                                  fontSize: 12,
                                  color: colorScheme.onSurface.withValues(alpha: 0.5),
                                ),
                                textAlign: TextAlign.center,
                              ),
                            ],
                          ),
                        ),
                      )
                    else
                      ListView.separated(
                        shrinkWrap: true,
                        physics: const NeverScrollableScrollPhysics(),
                        itemCount: filtered.length,
                        separatorBuilder: (_, __) => const SizedBox(height: 10),
                        itemBuilder: (context, index) {
                          final client = filtered[index];
                          final clientName = '${client['first_name']} ${client['last_name']}';
                          final personIdNumber = client['person_id_number'] ?? 'PENDING-ID';
                          final status = client['approval_status'] ?? 'APPROVED';
                          final isRemote = client['is_remote'] == true;

                          return Card(
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(12),
                              side: BorderSide(
                                color: isDark ? colorScheme.outlineVariant : CrbclTokens.lightBorder,
                                width: 1,
                              ),
                            ),
                            color: colorScheme.surfaceContainer,
                            child: Padding(
                              padding: const EdgeInsets.all(14.0),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  // Top Row: Avatar + Name + Badges
                                  Row(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      CircleAvatar(
                                        radius: 20,
                                        backgroundColor: colorScheme.primary.withValues(alpha: 0.15),
                                        backgroundImage: client['photo_url'] != null && client['photo_url'].toString().startsWith('http')
                                            ? NetworkImage(client['photo_url'])
                                            : null,
                                        child: client['photo_url'] == null || !client['photo_url'].toString().startsWith('http')
                                            ? Text(
                                                '${client['first_name']?.toString().isNotEmpty == true ? client['first_name'][0] : ""}${client['last_name']?.toString().isNotEmpty == true ? client['last_name'][0] : ""}',
                                                style: TextStyle(
                                                  fontWeight: FontWeight.bold,
                                                  color: colorScheme.primary,
                                                  fontSize: 13,
                                                ),
                                              )
                                            : null,
                                      ),
                                      const SizedBox(width: 10),
                                      Expanded(
                                        child: Column(
                                          crossAxisAlignment: CrossAxisAlignment.start,
                                          children: [
                                            Row(
                                              children: [
                                                Expanded(
                                                  child: Text(
                                                    clientName,
                                                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                                                    maxLines: 1,
                                                    overflow: TextOverflow.ellipsis,
                                                  ),
                                                ),
                                                if (client['is_trash'] == true)
                                                  Container(
                                                    padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2.5),
                                                    decoration: BoxDecoration(
                                                      color: Colors.red.withValues(alpha: 0.15),
                                                      borderRadius: BorderRadius.circular(5),
                                                      border: Border.all(color: Colors.red.shade300),
                                                    ),
                                                    child: Row(
                                                      mainAxisSize: MainAxisSize.min,
                                                      children: [
                                                        Icon(Icons.delete_outline, size: 11, color: Colors.red.shade800),
                                                        const SizedBox(width: 3),
                                                        Text(
                                                          'Trash (${client['days_until_purge'] ?? 45}d)',
                                                          style: TextStyle(color: Colors.red.shade900, fontSize: 10, fontWeight: FontWeight.bold),
                                                        ),
                                                      ],
                                                    ),
                                                  )
                                                else
                                                  _buildApprovalBadge(status),
                                              ],
                                            ),
                                            const SizedBox(height: 4),
                                            Wrap(
                                              spacing: 6,
                                              runSpacing: 4,
                                              children: [
                                                Container(
                                                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                                  decoration: BoxDecoration(
                                                    color: colorScheme.surfaceContainerHighest,
                                                    borderRadius: BorderRadius.circular(4),
                                                    border: Border.all(color: colorScheme.outlineVariant.withValues(alpha: 0.5)),
                                                  ),
                                                  child: Text(
                                                    '#$personIdNumber',
                                                    style: const TextStyle(fontSize: 10, fontFamily: 'monospace', fontWeight: FontWeight.bold),
                                                  ),
                                                ),
                                                _buildRiskBadge(client['risk_level'] ?? 'Low'),
                                                if (!isRemote)
                                                  Container(
                                                    padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 2),
                                                    decoration: BoxDecoration(
                                                      color: Colors.blue.withValues(alpha: 0.12),
                                                      borderRadius: BorderRadius.circular(4),
                                                    ),
                                                    child: const Text('Offline Draft', style: TextStyle(fontSize: 10, color: Colors.blue)),
                                                  ),
                                              ],
                                            ),
                                          ],
                                        ),
                                      ),
                                    ],
                                  ),

                                  // Location & Metadata
                                  const SizedBox(height: 10),
                                  Text(
                                    '${client['band_nation'] ?? "First Nations"} • ${client['city'] ?? "Regina"}, ${client['province'] ?? "SK"}',
                                    style: TextStyle(fontSize: 12, color: colorScheme.onSurface.withValues(alpha: 0.7)),
                                  ),

                                  if (client['date_of_birth'] != null || client['phone'] != null) ...[
                                    const SizedBox(height: 4),
                                    Text(
                                      'DOB: ${client['date_of_birth'] ?? "Unknown"} ${client['phone'] != null ? "• ${client['phone']}" : ""}',
                                      style: TextStyle(fontSize: 11, color: colorScheme.onSurface.withValues(alpha: 0.55)),
                                    ),
                                  ],

                                  // Action Bar: Delete, Edit, View Profile
                                  const SizedBox(height: 12),
                                  const Divider(height: 1),
                                  const SizedBox(height: 8),

                                  if (client['is_trash'] == true && _canDelete) ...[
                                    Row(
                                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                      children: [
                                        // Permanent Delete Button
                                        OutlinedButton.icon(
                                          onPressed: () => _permanentDeleteClient(client),
                                          icon: const Icon(Icons.delete_forever, size: 15, color: Colors.red),
                                          label: const Text(
                                            'Delete Permanently',
                                            maxLines: 1,
                                            softWrap: false,
                                            style: TextStyle(color: Colors.red, fontSize: 11),
                                          ),
                                          style: OutlinedButton.styleFrom(
                                            side: BorderSide(color: Colors.red.shade300),
                                            visualDensity: VisualDensity.compact,
                                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                          ),
                                        ),

                                        // Restore & View Profile Buttons
                                        Row(
                                          children: [
                                            ElevatedButton.icon(
                                              onPressed: () => _restoreClient(client),
                                              icon: const Icon(Icons.restore, size: 15),
                                              label: const Text(
                                                'Restore',
                                                maxLines: 1,
                                                softWrap: false,
                                                style: TextStyle(fontSize: 12),
                                              ),
                                              style: ElevatedButton.styleFrom(
                                                backgroundColor: Colors.green.shade700,
                                                foregroundColor: Colors.white,
                                                visualDensity: VisualDensity.compact,
                                                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                                              ),
                                            ),
                                            const SizedBox(width: 4),
                                            IconButton(
                                              icon: const Icon(Icons.info_outline, size: 18),
                                              tooltip: 'View Profile',
                                              visualDensity: VisualDensity.compact,
                                              onPressed: () => _viewClientProfile(client),
                                            ),
                                          ],
                                        ),
                                      ],
                                    ),
                                  ] else ...[
                                    Row(
                                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                      children: [
                                        // Delete Button (Supervisors upward only)
                                        if (_canDelete)
                                          IconButton(
                                            icon: const Icon(Icons.delete_outline, size: 20, color: Colors.red),
                                            tooltip: 'Move to Trash',
                                            visualDensity: VisualDensity.compact,
                                            onPressed: () => _deleteClient(client),
                                          )
                                        else
                                          const SizedBox.shrink(),

                                        // Edit and View Profile Buttons
                                        Row(
                                          children: [
                                            TextButton.icon(
                                              onPressed: () => _editClient(client),
                                              icon: const Icon(Icons.edit_outlined, size: 16),
                                              label: const Text('Edit', maxLines: 1, softWrap: false, style: TextStyle(fontSize: 12)),
                                              style: TextButton.styleFrom(visualDensity: VisualDensity.compact),
                                            ),
                                            const SizedBox(width: 4),
                                            ElevatedButton.icon(
                                              onPressed: () => _viewClientProfile(client),
                                              icon: const Icon(Icons.arrow_forward, size: 14),
                                              label: const Text(
                                                'View Profile',
                                                maxLines: 1,
                                                softWrap: false,
                                                style: TextStyle(fontSize: 12),
                                              ),
                                              style: ElevatedButton.styleFrom(
                                                backgroundColor: colorScheme.primary,
                                                foregroundColor: colorScheme.onPrimary,
                                                visualDensity: VisualDensity.compact,
                                                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                                              ),
                                            ),
                                          ],
                                        ),
                                      ],
                                    ),
                                  ],
                                ],
                              ),
                            ),
                          );
                        },
                      ),
                    const SizedBox(height: 40),
                  ],
                ),
              ),
            ),
    );
  }
}
