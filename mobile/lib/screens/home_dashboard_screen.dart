import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../services/auth_service.dart';
import '../services/connectivity_service.dart';
import '../services/db_helper.dart';
import '../services/sync_engine.dart';
import '../services/theme_service.dart';
import '../widgets/crbcl_logo.dart';
import '../widgets/status_badge.dart';

class HomeDashboardScreen extends StatefulWidget {
  final VoidCallback onOpenDrawer;
  final ValueChanged<int> onNavigateTab;

  const HomeDashboardScreen({
    super.key,
    required this.onOpenDrawer,
    required this.onNavigateTab,
  });

  @override
  State<HomeDashboardScreen> createState() => _HomeDashboardScreenState();
}

class _HomeDashboardScreenState extends State<HomeDashboardScreen> {
  final _dbHelper = LocalDatabaseHelper.instance;
  final _authService = MobileAuthService.instance;
  final _connectivityService = ConnectivityService.instance;

  bool _isLoading = true;
  bool _isSyncing = false;
  late bool _isOnline;
  DateTime? _lastSyncTime;
  Map<String, int> _metrics = {'PENDING': 0, 'SYNCED': 0, 'FAILED': 0, 'NEEDS_REVIEW': 0};
  List<Map<String, dynamic>> _recentDrafts = [];
  Map<String, dynamic> _currentUser = {};

  @override
  void initState() {
    super.initState();
    _isOnline = _connectivityService.isOnline;
    _connectivityService.addListener(_onConnectivityChanged);
    _loadDashboardData();
  }

  @override
  void dispose() {
    _connectivityService.removeListener(_onConnectivityChanged);
    super.dispose();
  }

  void _onConnectivityChanged() {
    if (mounted) {
      setState(() {
        _isOnline = _connectivityService.isOnline;
      });
    }
  }

  Future<void> _loadDashboardData() async {
    try {
      final user = await _authService.getCurrentUser();
      final metrics = await _dbHelper.getSyncMetrics();
      final drafts = await _dbHelper.getAllDrafts();

      if (mounted) {
        setState(() {
          _currentUser = user;
          _metrics = metrics;
          _recentDrafts = drafts.take(5).toList();
          _isLoading = false;
        });
      }
    } catch (_) {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }

    // Check connectivity asynchronously without blocking offline render
    _checkConnectivity();
  }

  Future<void> _checkConnectivity() async {
    final status = await _connectivityService.checkConnectivity();
    if (mounted) setState(() => _isOnline = status);
  }

  Future<void> _handleSyncNow() async {
    setState(() => _isSyncing = true);

    final syncEngine = SyncEngine();
    final result = await syncEngine.pushPendingQueue();

    await _checkConnectivity();
    final metrics = await _dbHelper.getSyncMetrics();
    final drafts = await _dbHelper.getAllDrafts();

    setState(() {
      _isSyncing = false;
      _metrics = metrics;
      _recentDrafts = drafts.take(5).toList();
      if (result.success && result.totalCount > 0) {
        _lastSyncTime = DateTime.now();
      }
    });

    if (mounted) {
      if (result.success) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              result.totalCount == 0
                  ? 'Local drafts are up to date. No pending items.'
                  : 'Sync complete: ${result.syncedCount} synchronized, ${result.needsReviewCount} needs review, ${result.failedCount} failed.',
            ),
            backgroundColor: result.failedCount > 0
                ? CrbclTokens.statusWarning
                : CrbclTokens.statusSuccess,
          ),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(result.errorMessage ?? 'Sync failed. Records preserved in local encrypted storage.'),
            backgroundColor: CrbclTokens.statusError,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final isDark = theme.brightness == Brightness.dark;

    final displayName = (_currentUser['name'] as String?)?.isNotEmpty == true
        ? _currentUser['name'] as String
        : 'System Administrator';
    final rawRoles = (_currentUser['roles'] as List?)?.cast<String>() ?? [];
    final primaryRole = rawRoles.any((r) => r.toLowerCase().contains('ceo'))
        ? 'CEO'
        : rawRoles.any((r) => r.toLowerCase().contains('executive'))
            ? 'Executive Director'
            : 'IT Admin';

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.menu),
          tooltip: 'Open navigation menu',
          onPressed: widget.onOpenDrawer,
        ),
        title: Row(
          children: [
            const CrbclLogo(height: 28, variant: CrbclLogoVariant.emblem),
            const SizedBox(width: 10),
            Flexible(
              child: Text(
                'CRBCL Staff Portal',
                style: TextStyle(
                  fontFamily: CrbclTokens.fontHeading,
                  fontWeight: FontWeight.bold,
                  fontSize: 17,
                  color: isDark ? colorScheme.onSurface : Colors.white,
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        ),
        actions: [
          // Live connectivity pill
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 12.0),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(
                color: _isOnline
                    ? CrbclTokens.statusSuccess.withValues(alpha: isDark ? 0.25 : 0.9)
                    : Colors.orange.shade800.withValues(alpha: isDark ? 0.25 : 0.9),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    width: 7,
                    height: 7,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: _isOnline ? Colors.white : Colors.white,
                    ),
                  ),
                  const SizedBox(width: 5),
                  Text(
                    _isOnline ? 'ONLINE' : 'OFFLINE',
                    style: const TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                ],
              ),
            ),
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Refresh Status',
            onPressed: _loadDashboardData,
          ),
          IconButton(
            icon: const Icon(Icons.person_outline),
            tooltip: 'Profile & Settings',
            onPressed: () => widget.onNavigateTab(4),
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadDashboardData,
              child: SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // WELCOME SECTION
                    _buildWelcomeCard(displayName, primaryRole),
                    const SizedBox(height: 16),

                    // QUICK ACTIONS SECTION
                    _buildQuickActionsHeader(),
                    const SizedBox(height: 10),
                    _buildQuickActionsGrid(),
                    const SizedBox(height: 20),

                    // OFFLINE STATUS & SYNC PANEL
                    _buildOfflineStatusPanel(),
                    const SizedBox(height: 20),

                    // RECENT FIELD ACTIVITY (Real local records only)
                    _buildRecentActivitySection(),
                  ],
                ),
              ),
            ),
    );
  }

  Widget _buildWelcomeCard(String name, String role) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final isDark = theme.brightness == Brightness.dark;

    return Card(
      elevation: isDark ? 0 : 1,
      color: colorScheme.surfaceContainer,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(14),
        side: BorderSide(
          color: isDark ? colorScheme.outlineVariant : CrbclTokens.lightBorder,
          width: 1,
        ),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  radius: 22,
                  backgroundColor: colorScheme.primary.withValues(alpha: 0.15),
                  child: Icon(
                    Icons.account_circle,
                    size: 28,
                    color: colorScheme.primary,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Welcome, $name',
                        style: TextStyle(
                          fontSize: 17,
                          fontWeight: FontWeight.bold,
                          color: colorScheme.onSurface,
                        ),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 2),
                      Wrap(
                        spacing: 8,
                        runSpacing: 4,
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 1),
                            decoration: BoxDecoration(
                              color: colorScheme.primary.withValues(alpha: 0.12),
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Text(
                              role,
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w600,
                                color: colorScheme.primary,
                              ),
                            ),
                          ),
                          Text(
                            'Cote First Nation',
                            style: TextStyle(
                              fontSize: 11,
                              color: colorScheme.onSurface.withValues(alpha: 0.65),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: _isOnline
                    ? CrbclTokens.statusSuccess.withValues(alpha: 0.1)
                    : Colors.orange.shade800.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  Icon(
                    _isOnline ? Icons.wifi : Icons.wifi_off,
                    size: 16,
                    color: _isOnline ? CrbclTokens.statusSuccess : Colors.orange.shade800,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      _isOnline
                          ? 'Connected to CRBCL Central Server. Real-time sync enabled.'
                          : 'Operating in Offline Mode. All drafts encrypted in local storage.',
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w500,
                        color: _isOnline ? CrbclTokens.statusSuccess : Colors.orange.shade800,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildQuickActionsHeader() {
    final theme = Theme.of(context);
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          'Quick Actions',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: theme.colorScheme.onSurface,
          ),
        ),
        Text(
          'Field Workflows',
          style: TextStyle(
            fontSize: 12,
            color: theme.colorScheme.onSurface.withValues(alpha: 0.5),
          ),
        ),
      ],
    );
  }

  Widget _buildQuickActionsGrid() {
    return Column(
      children: [
        Row(
          children: [
            _buildActionTile(
              title: 'Register Client',
              subtitle: 'New Person & Client draft',
              icon: Icons.person_add_alt_1,
              color: const Color(0xFF2563EB),
              onTap: () async {
                final created = await Navigator.pushNamed(context, '/client-draft');
                if (created == true) _loadDashboardData();
              },
            ),
            const SizedBox(width: 10),
            _buildActionTile(
              title: 'New Intake',
              subtitle: 'Referral & intake intake',
              icon: Icons.assignment_outlined,
              color: const Color(0xFF0D9488),
              onTap: () async {
                final created = await Navigator.pushNamed(context, '/intake-draft');
                if (created == true) _loadDashboardData();
              },
            ),
          ],
        ),
        const SizedBox(height: 10),
        Row(
          children: [
            _buildActionTile(
              title: 'Case Notes',
              subtitle: 'Progress note & dictation',
              icon: Icons.note_add_outlined,
              color: const Color(0xFF7C3AED),
              onTap: () async {
                final created = await Navigator.pushNamed(context, '/note-draft');
                if (created == true) _loadDashboardData();
              },
            ),
            const SizedBox(width: 10),
            _buildActionTile(
              title: 'Home Visits',
              subtitle: 'Visits & follow-up tasks',
              icon: Icons.home_work_outlined,
              color: const Color(0xFFD97706),
              onTap: () async {
                final created = await Navigator.pushNamed(context, '/visit-draft');
                if (created == true) _loadDashboardData();
              },
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildActionTile({
    required String title,
    required String subtitle,
    required IconData icon,
    required Color color,
    required VoidCallback onTap,
  }) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final isDark = theme.brightness == Brightness.dark;

    return Expanded(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: colorScheme.surfaceContainer,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: isDark ? colorScheme.outlineVariant : CrbclTokens.lightBorder,
              width: 1,
            ),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: color.withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(icon, color: color, size: 22),
              ),
              const SizedBox(height: 8),
              Text(
                title,
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 13,
                  color: colorScheme.onSurface,
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 2),
              Text(
                subtitle,
                style: TextStyle(
                  fontSize: 10,
                  color: colorScheme.onSurface.withValues(alpha: 0.6),
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildOfflineStatusPanel() {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final isDark = theme.brightness == Brightness.dark;

    final pending = _metrics['PENDING'] ?? 0;
    final synced = _metrics['SYNCED'] ?? 0;
    final needsReview = _metrics['NEEDS_REVIEW'] ?? 0;
    final failed = _metrics['FAILED'] ?? 0;
    final totalActionable = pending + failed;

    return Card(
      elevation: isDark ? 0 : 1,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(14),
        side: BorderSide(
          color: isDark ? colorScheme.outlineVariant : CrbclTokens.lightBorder,
          width: 1,
        ),
      ),
      color: colorScheme.surfaceContainer,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    Icon(Icons.cloud_sync, size: 20, color: colorScheme.primary),
                    const SizedBox(width: 8),
                    Text(
                      'Synchronization Ledger',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                        color: colorScheme.onSurface,
                      ),
                    ),
                  ],
                ),
                TextButton(
                  onPressed: () => widget.onNavigateTab(3),
                  style: TextButton.styleFrom(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    visualDensity: VisualDensity.compact,
                  ),
                  child: const Text('View All', style: TextStyle(fontSize: 12)),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // 4 Metrics Indicators
            Row(
              children: [
                _buildMiniMetric('Pending', pending, CrbclTokens.statusWarning),
                _buildMiniMetric('Synced', synced, CrbclTokens.statusSuccess),
                _buildMiniMetric('Review', needsReview, CrbclTokens.statusReview),
                _buildMiniMetric('Failed', failed, CrbclTokens.statusError),
              ],
            ),
            const SizedBox(height: 14),

            // Sync Action Bar
            Row(
              children: [
                Expanded(
                  child: Text(
                    _lastSyncTime != null
                        ? 'Last sync: ${DateFormat("MMM d, h:mm a").format(_lastSyncTime!)}'
                        : 'No sync completed this session',
                    style: TextStyle(
                      fontSize: 11,
                      color: colorScheme.onSurface.withValues(alpha: 0.6),
                    ),
                  ),
                ),
                ElevatedButton.icon(
                  onPressed: _isSyncing ? null : _handleSyncNow,
                  icon: _isSyncing
                      ? const SizedBox(
                          width: 14,
                          height: 14,
                          child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                        )
                      : const Icon(Icons.sync, size: 16),
                  label: Text(_isSyncing ? 'Syncing...' : 'Sync Now ($totalActionable)'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: colorScheme.primary,
                    foregroundColor: colorScheme.onPrimary,
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                    textStyle: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMiniMetric(String label, int count, Color color) {
    return Expanded(
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 3),
        padding: const EdgeInsets.symmetric(vertical: 8),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Column(
          children: [
            Text(
              '$count',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 16,
                color: color,
              ),
            ),
            Text(
              label,
              style: TextStyle(
                fontSize: 10,
                fontWeight: FontWeight.w600,
                color: color,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecentActivitySection() {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final isDark = theme.brightness == Brightness.dark;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Recent Local Drafts',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: colorScheme.onSurface,
              ),
            ),
            if (_recentDrafts.isNotEmpty)
              TextButton(
                onPressed: () => widget.onNavigateTab(3),
                child: const Text('Manage Drafts', style: TextStyle(fontSize: 12)),
              ),
          ],
        ),
        const SizedBox(height: 8),

        if (_recentDrafts.isEmpty)
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
              padding: const EdgeInsets.symmetric(vertical: 32.0, horizontal: 16.0),
              child: Center(
                child: Column(
                  children: [
                    Icon(
                      Icons.inbox_outlined,
                      size: 40,
                      color: colorScheme.onSurface.withValues(alpha: 0.4),
                    ),
                    const SizedBox(height: 10),
                    Text(
                      'No local field records yet',
                      style: TextStyle(
                        fontWeight: FontWeight.w600,
                        fontSize: 14,
                        color: colorScheme.onSurface.withValues(alpha: 0.7),
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Register a new client or create an intake using the quick actions above.',
                      style: TextStyle(
                        fontSize: 12,
                        color: colorScheme.onSurface.withValues(alpha: 0.5),
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
            ),
          )
        else
          ListView.separated(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: _recentDrafts.length,
            separatorBuilder: (_, __) => const SizedBox(height: 6),
            itemBuilder: (context, index) {
              final draft = _recentDrafts[index];
              final title = (draft['title'] as String?) ?? 'Untitled';
              final subtitle = draft['subtitle'] as String?;
              final entityType = (draft['entity_type'] as String?) ?? 'DRAFT';
              final status = (draft['sync_status'] as String?) ?? 'PENDING';

              return Card(
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(10),
                  side: BorderSide(
                    color: isDark ? colorScheme.outlineVariant : CrbclTokens.lightBorder,
                    width: 1,
                  ),
                ),
                color: colorScheme.surfaceContainer,
                child: ListTile(
                  dense: true,
                  title: Text(
                    title,
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 13,
                      color: colorScheme.onSurface,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  subtitle: subtitle != null
                      ? Text(
                          '$entityType • $subtitle',
                          style: TextStyle(
                            fontSize: 11,
                            color: colorScheme.onSurface.withValues(alpha: 0.6),
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        )
                      : Text(
                          entityType,
                          style: TextStyle(
                            fontSize: 11,
                            color: colorScheme.onSurface.withValues(alpha: 0.6),
                          ),
                        ),
                  trailing: StatusBadge(status: status, compact: true),
                  onTap: () => widget.onNavigateTab(3),
                ),
              );
            },
          ),
      ],
    );
  }
}
