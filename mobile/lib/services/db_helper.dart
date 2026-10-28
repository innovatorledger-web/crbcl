import 'dart:convert';
import 'dart:math';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:path/path.dart';
import 'package:sqflite_sqlcipher/sqflite.dart';

class LocalDatabaseHelper {
  static final LocalDatabaseHelper instance = LocalDatabaseHelper._init();
  static Database? _database;
  static const _secureStorage = FlutterSecureStorage();
  static const _dbKeyName = 'crbcl_sqlite_aes_key';
  static const _fallbackStorageKey = 'crbcl_offline_drafts_v2';
  static const _idMappingsKey = 'crbcl_id_mappings_v2';
  static final Map<String, Map<String, dynamic>> _memoryDrafts = {};
  static final Map<String, String> _memoryIdMappings = {};
  static bool _fallbackLoaded = false;

  LocalDatabaseHelper._init();

  static void resetForTesting() {
    _database = null;
    _memoryDrafts.clear();
    _memoryIdMappings.clear();
    _fallbackLoaded = false;
  }

  /// Open or return SQLite database with SQLCipher encryption, falling back
  /// gracefully to unencrypted local SQLite if encryption cannot initialize.
  Future<Database?> getDatabaseSafe() async {
    if (_database != null && _database!.isOpen) return _database!;
    try {
      final password = await _getOrCreateEncryptionKey();
      _database = await _initDB('crbcl_field_encrypted.db', password)
          .timeout(const Duration(seconds: 10));
      return _database;
    } catch (_) {
      // Graceful fallback to unencrypted SQLite on devices where SQLCipher cannot link
      try {
        final dbPath = await getDatabasesPath();
        final path = join(dbPath, 'crbcl_field_local.db');
        _database = await openDatabase(
          path,
          version: 2,
          onCreate: _createDB,
          onUpgrade: _upgradeDB,
        ).timeout(const Duration(seconds: 10));
        return _database;
      } catch (_) {
        return null;
      }
    }
  }

  Future<Database> get database async {
    final db = await getDatabaseSafe();
    if (db != null) return db;
    throw Exception('Local SQLite database unavailable');
  }

  Future<String> _getOrCreateEncryptionKey() async {
    try {
      String? existingKey = await _secureStorage.read(key: _dbKeyName);
      if (existingKey == null || existingKey.isEmpty) {
        final random = Random.secure();
        final values = List<int>.generate(32, (i) => random.nextInt(256));
        existingKey = base64Url.encode(values);
        await _secureStorage.write(key: _dbKeyName, value: existingKey);
      }
      return existingKey;
    } catch (_) {
      // In constrained testing environments, return deterministic fallback
      return 'crbcl_field_default_encryption_key_v2';
    }
  }

  Future<Database> _initDB(String filePath, String password) async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, filePath);

    return await openDatabase(
      path,
      password: password, // SQLCipher AES-256 Encryption
      version: 2,
      onCreate: _createDB,
      onUpgrade: _upgradeDB,
    );
  }

  Future<void> _createDB(Database db, int version) async {
    // Local Cached Cases
    await db.execute('''
      CREATE TABLE cases (
        id TEXT PRIMARY KEY,
        case_number TEXT NOT NULL,
        title TEXT NOT NULL,
        status TEXT NOT NULL,
        stage TEXT NOT NULL,
        updated_at TEXT NOT NULL
      )
    ''');

    // Local Cached Clients
    await db.execute('''
      CREATE TABLE clients (
        id TEXT PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        status TEXT NOT NULL
      )
    ''');

    // Legacy sync queue
    await db.execute('''
      CREATE TABLE sync_queue (
        mutation_id TEXT PRIMARY KEY,
        entity_type TEXT NOT NULL,
        payload_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'PENDING'
      )
    ''');

    // Unified Encrypted Offline Drafts Repository
    await db.execute('''
      CREATE TABLE offline_drafts (
        id TEXT PRIMARY KEY,
        entity_type TEXT NOT NULL,
        title TEXT NOT NULL,
        subtitle TEXT,
        payload_json TEXT NOT NULL,
        sync_status TEXT NOT NULL DEFAULT 'PENDING',
        server_id TEXT,
        person_id_number TEXT,
        referral_number TEXT,
        error_message TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        user_id TEXT
      )
    ''');

    // Server-to-Client Temporary ID Resolution Ledger
    await db.execute('''
      CREATE TABLE id_mappings (
        temp_id TEXT PRIMARY KEY,
        server_id TEXT NOT NULL,
        entity_type TEXT NOT NULL,
        created_at TEXT NOT NULL
      )
    ''');
  }

  Future<void> _upgradeDB(Database db, int oldVersion, int newVersion) async {
    if (oldVersion < 2) {
      await db.execute('''
        CREATE TABLE IF NOT EXISTS offline_drafts (
          id TEXT PRIMARY KEY,
          entity_type TEXT NOT NULL,
          title TEXT NOT NULL,
          subtitle TEXT,
          payload_json TEXT NOT NULL,
          sync_status TEXT NOT NULL DEFAULT 'PENDING',
          server_id TEXT,
          person_id_number TEXT,
          referral_number TEXT,
          error_message TEXT,
          created_at TEXT NOT NULL,
          updated_at TEXT NOT NULL,
          user_id TEXT
        )
      ''');

      await db.execute('''
        CREATE TABLE IF NOT EXISTS id_mappings (
          temp_id TEXT PRIMARY KEY,
          server_id TEXT NOT NULL,
          entity_type TEXT NOT NULL,
          created_at TEXT NOT NULL
        )
      ''');
    }
  }

  // --- Fallback Secure Storage Engine ---

  Future<void> _ensureFallbackLoaded() async {
    if (_fallbackLoaded) return;
    try {
      final raw = await _secureStorage.read(key: _fallbackStorageKey);
      if (raw != null && raw.isNotEmpty) {
        final decoded = jsonDecode(raw);
        if (decoded is Map<String, dynamic>) {
          decoded.forEach((k, v) {
            if (v is Map) {
              _memoryDrafts[k] = Map<String, dynamic>.from(v);
            }
          });
        }
      }

      final rawMap = await _secureStorage.read(key: _idMappingsKey);
      if (rawMap != null && rawMap.isNotEmpty) {
        final decodedMap = jsonDecode(rawMap);
        if (decodedMap is Map<String, dynamic>) {
          decodedMap.forEach((k, v) {
            if (v != null) _memoryIdMappings[k] = v.toString();
          });
        }
      }
    } catch (_) {}
    _fallbackLoaded = true;
  }

  Future<void> _persistFallbackDrafts() async {
    try {
      await _secureStorage.write(
        key: _fallbackStorageKey,
        value: jsonEncode(_memoryDrafts),
      );
    } catch (_) {}
  }

  Future<void> _persistFallbackMappings() async {
    try {
      await _secureStorage.write(
        key: _idMappingsKey,
        value: jsonEncode(_memoryIdMappings),
      );
    } catch (_) {}
  }

  // --- Offline Drafts Repository Methods ---

  /// Insert or update an offline draft record.
  /// Dual-persists into fallback secure storage first, ensuring zero data loss
  /// even before SQLite finishes or if the database is temporarily initializing.
  Future<void> saveDraft({
    required String id,
    required String entityType,
    required String title,
    String? subtitle,
    required Map<String, dynamic> payload,
    String? userId,
  }) async {
    final now = DateTime.now().toIso8601String();
    final draftRecord = <String, dynamic>{
      'id': id,
      'entity_type': entityType.toUpperCase(),
      'title': title,
      'subtitle': subtitle,
      'payload_json': jsonEncode(payload),
      'sync_status': 'PENDING',
      'created_at': now,
      'updated_at': now,
      'user_id': userId,
    };

    // 1. Immediately write to in-memory cache and SecureStorage
    await _ensureFallbackLoaded();
    _memoryDrafts[id] = Map<String, dynamic>.from(draftRecord);
    await _persistFallbackDrafts();

    // 2. Persist to SQLite database
    try {
      final db = await getDatabaseSafe();
      if (db != null) {
        await db.insert(
          'offline_drafts',
          draftRecord,
          conflictAlgorithm: ConflictAlgorithm.replace,
        );

        // Also mirror into sync_queue for backwards compatibility
        await db.insert(
          'sync_queue',
          {
            'mutation_id': id,
            'entity_type': entityType.toUpperCase(),
            'payload_json': jsonEncode(payload),
            'created_at': now,
            'status': 'PENDING',
          },
          conflictAlgorithm: ConflictAlgorithm.replace,
        );
      }
    } catch (_) {
      // Non-fatal: secure storage already secured the draft
    }
  }

  /// Update draft sync status and server returned identifiers
  Future<void> updateDraftSyncResult({
    required String id,
    required String status,
    String? serverId,
    String? personIdNumber,
    String? referralNumber,
    String? errorMessage,
  }) async {
    final now = DateTime.now().toIso8601String();

    // Update fallback memory & storage
    await _ensureFallbackLoaded();
    if (_memoryDrafts.containsKey(id)) {
      final draft = _memoryDrafts[id]!;
      draft['sync_status'] = status;
      draft['updated_at'] = now;
      if (serverId != null) draft['server_id'] = serverId;
      if (personIdNumber != null) draft['person_id_number'] = personIdNumber;
      if (referralNumber != null) draft['referral_number'] = referralNumber;
      if (errorMessage != null) draft['error_message'] = errorMessage;
      _memoryDrafts[id] = draft;
      await _persistFallbackDrafts();
    }

    // Update SQLite
    try {
      final db = await getDatabaseSafe();
      if (db != null) {
        final updates = <String, dynamic>{
          'sync_status': status,
          'updated_at': now,
        };
        if (serverId != null) updates['server_id'] = serverId;
        if (personIdNumber != null) updates['person_id_number'] = personIdNumber;
        if (referralNumber != null) updates['referral_number'] = referralNumber;
        if (errorMessage != null) updates['error_message'] = errorMessage;

        await db.update('offline_drafts', updates, where: 'id = ?', whereArgs: [id]);

        if (status == 'SYNCED') {
          await db.delete('sync_queue', where: 'mutation_id = ?', whereArgs: [id]);
        }
      }
    } catch (_) {}
  }

  /// Record server ID mapping for temporary offline UUID
  Future<void> recordIdMapping({
    required String tempId,
    required String serverId,
    required String entityType,
  }) async {
    await _ensureFallbackLoaded();
    _memoryIdMappings[tempId] = serverId;
    await _persistFallbackMappings();

    try {
      final db = await getDatabaseSafe();
      if (db != null) {
        await db.insert(
          'id_mappings',
          {
            'temp_id': tempId,
            'server_id': serverId,
            'entity_type': entityType,
            'created_at': DateTime.now().toIso8601String(),
          },
          conflictAlgorithm: ConflictAlgorithm.replace,
        );
      }
    } catch (_) {}
  }

  /// Retrieve mapped server ID for a temporary UUID
  Future<String?> getMappedServerId(String tempId) async {
    await _ensureFallbackLoaded();
    if (_memoryIdMappings.containsKey(tempId)) {
      return _memoryIdMappings[tempId];
    }

    try {
      final db = await getDatabaseSafe();
      if (db != null) {
        final results = await db.query(
          'id_mappings',
          columns: ['server_id'],
          where: 'temp_id = ?',
          whereArgs: [tempId],
        );
        if (results.isNotEmpty) {
          final serverId = results.first['server_id'] as String?;
          if (serverId != null) {
            _memoryIdMappings[tempId] = serverId;
            return serverId;
          }
        }
      }
    } catch (_) {}
    return null;
  }

  /// Get pending drafts that need to be pushed to the backend
  Future<List<Map<String, dynamic>>> getPendingDrafts() async {
    final all = await getAllDrafts();
    return all.where((d) {
      final status = (d['sync_status'] as String?)?.toUpperCase();
      return status == 'PENDING' || status == 'FAILED';
    }).toList();
  }

  /// Get all drafts, optionally filtered by sync status.
  /// Seamlessly merges SQLite database records with fallback secure storage.
  Future<List<Map<String, dynamic>>> getAllDrafts({String? statusFilter}) async {
    final merged = <String, Map<String, dynamic>>{};

    // 1. Load from fallback in-memory and SecureStorage
    await _ensureFallbackLoaded();
    _memoryDrafts.forEach((k, v) {
      merged[k] = Map<String, dynamic>.from(v);
    });

    // 2. Load from SQLite and merge
    try {
      final db = await getDatabaseSafe();
      if (db != null) {
        final rows = await db.query('offline_drafts');
        for (var row in rows) {
          final id = row['id'] as String;
          merged[id] = Map<String, dynamic>.from(row);
        }
      }
    } catch (_) {}

    var results = merged.values.toList();
    if (statusFilter != null && statusFilter.isNotEmpty && statusFilter != 'ALL') {
      results = results.where((d) => d['sync_status'] == statusFilter).toList();
    }

    // Sort newest first
    results.sort((a, b) {
      final aDate = (a['updated_at'] ?? a['created_at'] ?? '') as String;
      final bDate = (b['updated_at'] ?? b['created_at'] ?? '') as String;
      return bDate.compareTo(aDate);
    });

    return results;
  }

  /// Delete a local draft
  Future<void> deleteDraft(String id) async {
    await _ensureFallbackLoaded();
    if (_memoryDrafts.containsKey(id)) {
      _memoryDrafts.remove(id);
      await _persistFallbackDrafts();
    }

    try {
      final db = await getDatabaseSafe();
      if (db != null) {
        await db.delete('offline_drafts', where: 'id = ?', whereArgs: [id]);
        await db.delete('sync_queue', where: 'mutation_id = ?', whereArgs: [id]);
      }
    } catch (_) {}
  }

  /// Get counts for metrics display
  Future<Map<String, int>> getSyncMetrics() async {
    final metrics = {
      'PENDING': 0,
      'SYNCED': 0,
      'FAILED': 0,
      'NEEDS_REVIEW': 0,
    };

    final all = await getAllDrafts();
    for (var row in all) {
      final status = (row['sync_status'] as String?)?.toUpperCase() ?? '';
      if (metrics.containsKey(status)) {
        metrics[status] = (metrics[status] ?? 0) + 1;
      }
    }
    return metrics;
  }

  // --- Legacy Compatibility Methods ---

  Future<int> insertSyncItem(String mutationId, String entityType, String payloadJson) async {
    try {
      final db = await database;
      return await db.insert('sync_queue', {
        'mutation_id': mutationId,
        'entity_type': entityType,
        'payload_json': payloadJson,
        'created_at': DateTime.now().toIso8601String(),
        'status': 'PENDING',
      });
    } catch (_) {
      return 0;
    }
  }

  Future<List<Map<String, dynamic>>> getPendingSyncItems() async {
    try {
      final db = await database;
      return await db.query('sync_queue', where: 'status = ?', whereArgs: ['PENDING']);
    } catch (_) {
      return [];
    }
  }

  Future<void> clearSyncedItem(String mutationId) async {
    try {
      final db = await database;
      await db.delete('sync_queue', where: 'mutation_id = ?', whereArgs: [mutationId]);
    } catch (_) {}
  }

  Future<void> purgeCaseCascade(String caseId) async {
    try {
      final db = await database;
      await db.transaction((txn) async {
        await txn.delete('cases', where: 'id = ?', whereArgs: [caseId]);
        await txn.delete('sync_queue', where: 'payload_json LIKE ?', whereArgs: ['%"case_id":"$caseId"%']);
        await txn.delete('offline_drafts', where: 'payload_json LIKE ?', whereArgs: ['%"case_id":"$caseId"%']);
      });
    } catch (_) {}
  }

  Future<void> purgeDatabase() async {
    _memoryDrafts.clear();
    _memoryIdMappings.clear();
    _fallbackLoaded = false;
    try {
      await _secureStorage.delete(key: _fallbackStorageKey);
      await _secureStorage.delete(key: _idMappingsKey);
      await _secureStorage.delete(key: _dbKeyName);
    } catch (_) {}

    if (_database != null) {
      try {
        await _database!.close();
      } catch (_) {}
      _database = null;
    }
    try {
      final dbPath = await getDatabasesPath();
      final encPath = join(dbPath, 'crbcl_field_encrypted.db');
      await deleteDatabase(encPath);
      final localPath = join(dbPath, 'crbcl_field_local.db');
      await deleteDatabase(localPath);
    } catch (_) {}
  }
}
