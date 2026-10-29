import 'package:flutter/material.dart';
import '../services/auth_service.dart';
import 'crbcl_logo.dart';

/// Professional Navigation Drawer for CRBCL Mobile Field Platform.
/// Groups supported mobile workflows into logical groups:
/// - MAIN
/// - FIELD OPERATIONS
/// - ACCOUNT
class AppDrawer extends StatefulWidget {
  final int? currentTabIndex;
  final ValueChanged<int>? onTabSelected;

  const AppDrawer({
    super.key,
    this.currentTabIndex,
    this.onTabSelected,
  });

  @override
  State<AppDrawer> createState() => _AppDrawerState();
}

class _AppDrawerState extends State<AppDrawer> {
  final _authService = MobileAuthService.instance;
  Map<String, dynamic> _user = {};

  @override
  void initState() {
    super.initState();
    _loadUser();
  }

  Future<void> _loadUser() async {
    final user = await _authService.getCurrentUser();
    if (mounted) {
      setState(() => _user = user);
    }
  }

  String _getRoleLabel(Map<String, dynamic> user, List<String> roles) {
    final r = (user['role'] as String? ?? '').toLowerCase();
    if (r.contains('ceo') || roles.contains('ceo')) return 'CEO';
    if (r.contains('executive') || roles.contains('executive_director')) return 'Executive Director';
    return 'IT Admin';
  }

  void _navigateToTab(int index) {
    Navigator.pop(context); // Close drawer
    if (widget.onTabSelected != null) {
      widget.onTabSelected!(index);
    } else {
      Navigator.pushReplacementNamed(context, '/dashboard');
    }
  }

  void _navigateToRoute(String route) {
    Navigator.pop(context); // Close drawer
    Navigator.pushNamed(context, route);
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final isDark = theme.brightness == Brightness.dark;

    final displayName = (_user['name'] as String?)?.isNotEmpty == true
        ? _user['name'] as String
        : 'Caseworker';
    final email = (_user['email'] as String?)?.isNotEmpty == true
        ? _user['email'] as String
        : 'staff@crbcl.org';
    final roles = (_user['roles'] as List?)?.cast<String>() ?? [];

    return Drawer(
      child: SafeArea(
        top: false,
        child: Column(
          children: [
            // Drawer Branded Header
            Container(
              padding: EdgeInsets.only(
                top: MediaQuery.of(context).padding.top + 20,
                bottom: 20,
                left: 20,
                right: 20,
              ),
              decoration: BoxDecoration(
                color: isDark ? const Color(0xFF1B1512) : colorScheme.primary,
                border: Border(
                  bottom: BorderSide(
                    color: isDark ? Colors.white12 : Colors.black12,
                    width: 1,
                  ),
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(6),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: const CrbclLogo(
                          height: 32,
                          variant: CrbclLogoVariant.emblem,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: const [
                            Text(
                              'Chief Red Bear',
                              style: TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.bold,
                                fontSize: 16,
                                letterSpacing: 0.3,
                              ),
                            ),
                            Text(
                              "Children's Lodge",
                              style: TextStyle(
                                color: Colors.white70,
                                fontSize: 12,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Text(
                    displayName,
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.w600,
                      fontSize: 15,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    email,
                    style: const TextStyle(
                      color: Colors.white70,
                      fontSize: 12,
                    ),
                  ),
                  const SizedBox(height: 6),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                    decoration: BoxDecoration(
                      color: Colors.white.withValues(alpha: 0.2),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Text(
                      _getRoleLabel(_user, roles),
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 10,
                        letterSpacing: 0.5,
                      ),
                    ),
                  ),
                ],
              ),
            ),

            // Scrollable Menu Items
            Expanded(
              child: ListView(
                padding: const EdgeInsets.symmetric(vertical: 8),
                children: [
                  // MAIN
                  _buildSectionHeader('MAIN'),
                  _buildDrawerTile(
                    icon: Icons.dashboard_outlined,
                    activeIcon: Icons.dashboard,
                    label: 'Dashboard',
                    isSelected: widget.currentTabIndex == 0,
                    onTap: () => _navigateToTab(0),
                  ),
                  _buildDrawerTile(
                    icon: Icons.people_outline,
                    activeIcon: Icons.people,
                    label: 'Clients',
                    isSelected: widget.currentTabIndex == 1,
                    onTap: () => _navigateToTab(1),
                  ),
                  _buildDrawerTile(
                    icon: Icons.folder_outlined,
                    activeIcon: Icons.folder,
                    label: 'Cases',
                    isSelected: widget.currentTabIndex == 2,
                    onTap: () => _navigateToTab(2),
                  ),
                  _buildDrawerTile(
                    icon: Icons.cloud_sync_outlined,
                    activeIcon: Icons.cloud_sync,
                    label: 'Offline Workspace',
                    isSelected: widget.currentTabIndex == 3,
                    onTap: () => _navigateToTab(3),
                  ),

                  const Divider(height: 20),

                  // FIELD OPERATIONS
                  _buildSectionHeader('FIELD OPERATIONS'),
                  _buildDrawerTile(
                    icon: Icons.person_add_alt,
                    label: 'New Client Draft',
                    onTap: () => _navigateToRoute('/client-draft'),
                  ),
                  _buildDrawerTile(
                    icon: Icons.assignment_outlined,
                    label: 'Intake / Referral',
                    onTap: () => _navigateToRoute('/intake-draft'),
                  ),
                  _buildDrawerTile(
                    icon: Icons.note_add_outlined,
                    label: 'Case Note Draft',
                    onTap: () => _navigateToRoute('/note-draft'),
                  ),
                  _buildDrawerTile(
                    icon: Icons.home_work_outlined,
                    label: 'Home Visits & Tasks',
                    onTap: () => _navigateToRoute('/visit-draft'),
                  ),

                  const Divider(height: 20),

                  // ACCOUNT
                  _buildSectionHeader('ACCOUNT'),
                  _buildDrawerTile(
                    icon: Icons.person_outline,
                    activeIcon: Icons.person,
                    label: 'Profile & Settings',
                    isSelected: widget.currentTabIndex == 4,
                    onTap: () => _navigateToTab(4),
                  ),
                  _buildDrawerTile(
                    icon: Icons.palette_outlined,
                    label: 'Appearance',
                    onTap: () => _navigateToRoute('/profile'),
                  ),
                  if (roles.contains('admin') || roles.contains('it_admin') || _user['email'] == 'admin@crbcl.ca') ...[
                    _buildDrawerTile(
                      icon: Icons.admin_panel_settings_outlined,
                      activeIcon: Icons.admin_panel_settings,
                      label: 'IT Admin Console',
                      onTap: () => _navigateToRoute('/admin-dashboard'),
                    ),
                  ],
                  _buildDrawerTile(
                    icon: Icons.lock_outline,
                    label: 'Lock Vault',
                    onTap: () {
                      Navigator.pop(context);
                      Navigator.pushReplacementNamed(context, '/login');
                    },
                  ),
                ],
              ),
            ),

            // Footer
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              child: Row(
                children: [
                  Icon(
                    Icons.security,
                    size: 14,
                    color: colorScheme.outline,
                  ),
                  const SizedBox(width: 8),
                  Flexible(
                    child: Text(
                      'AES-256 SQLCipher Active',
                      style: TextStyle(
                        fontSize: 11,
                        color: colorScheme.outline,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
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

  Widget _buildSectionHeader(String title) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 6),
      child: Text(
        title,
        style: TextStyle(
          fontSize: 11,
          fontWeight: FontWeight.bold,
          letterSpacing: 0.8,
          color: theme.colorScheme.onSurface.withValues(alpha: 0.5),
        ),
      ),
    );
  }

  Widget _buildDrawerTile({
    required IconData icon,
    IconData? activeIcon,
    required String label,
    bool isSelected = false,
    required VoidCallback onTap,
  }) {
    final theme = Theme.of(context);
    final primary = theme.colorScheme.primary;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 2),
      child: ListTile(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        tileColor: isSelected ? primary.withValues(alpha: 0.12) : Colors.transparent,
        leading: Icon(
          isSelected ? (activeIcon ?? icon) : icon,
          color: isSelected ? primary : theme.colorScheme.onSurface.withValues(alpha: 0.8),
          size: 22,
        ),
        title: Text(
          label,
          style: TextStyle(
            color: isSelected ? primary : theme.colorScheme.onSurface,
            fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
            fontSize: 13,
          ),
        ),
        dense: true,
        onTap: onTap,
      ),
    );
  }
}
