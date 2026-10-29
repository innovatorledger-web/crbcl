"""Audit platform inventory: models, endpoints, routers, teams, departments, roles, permissions, workspaces, and routes."""

import json
import os
import re
import sys

sys.path.insert(0, r"C:\Users\Shilley Pc\crbcl\backend")

inventory = {}

# 1. Models
from app.core.database import Base
import app.models
mapped_entities = [m.class_.__name__ for m in Base.registry.mappers]
inventory["total_mapped_models"] = len(mapped_entities)

# 2. Endpoints & Routers
from app import main
fastapi_app = main.app
endpoints = []
for r in fastapi_app.routes:
    if hasattr(r, "methods") and hasattr(r, "path"):
        for m in r.methods:
            if m not in ("HEAD", "OPTIONS"):
                endpoints.append(f"{m} {r.path}")
inventory["total_fastapi_endpoints"] = len(endpoints)

# 3. Permissions in Permissions enum
from app.permissions.constants import Permissions
inventory["total_permissions_enum"] = len(Permissions)

# 4. Roles in seed.py
from app.core import seed
inventory["total_seed_roles"] = len(seed.ROLES_DATA)
inventory["seed_roles"] = [r.get("name") for r in seed.ROLES_DATA]
inventory["total_seed_teams"] = len(seed.TEAMS_DATA)
inventory["seed_teams"] = [t.get("name") for t in seed.TEAMS_DATA]

# 5. Admin Canonical Workspaces in dashboard_registry_service.py
from app.services.dashboard_registry_service import CANONICAL_WORKSPACES
inventory["total_canonical_workspaces"] = len(CANONICAL_WORKSPACES)
inventory["canonical_workspaces"] = [w.get("name") for w in CANONICAL_WORKSPACES]

# 6. Team Dashboard definitions in src/pages/TeamDashboard.jsx
with open(r"C:\Users\Shilley Pc\crbcl\src\pages\TeamDashboard.jsx", "r", encoding="utf-8") as f:
    team_dash_content = f.read()

# Look for TEAMS array in TeamDashboard.jsx
team_matches = re.findall(r"id:\s*(\d+),\s*name:\s*['\"]([^'\"]+)['\"]", team_dash_content)
inventory["team_dashboard_jsx_teams_count"] = len(team_matches)
inventory["team_dashboard_jsx_teams"] = [{"id": m[0], "name": m[1]} for m in team_matches]

# 7. Frontend routes in src/App.jsx
with open(r"C:\Users\Shilley Pc\crbcl\src\App.jsx", "r", encoding="utf-8") as f:
    app_jsx = f.read()

route_matches = re.findall(r"<Route\s+path=[\"']([^\"']+)[\"']", app_jsx)
inventory["frontend_routes_count"] = len(route_matches)
inventory["frontend_routes"] = route_matches

# 8. Migrations count
mig_dir = r"C:\Users\Shilley Pc\crbcl\backend\migrations\versions"
inventory["total_alembic_migrations"] = len([f for f in os.listdir(mig_dir) if f.endswith(".py")])

with open(r"C:\Users\Shilley Pc\crbcl\scripts\platform_inventory.json", "w", encoding="utf-8") as out:
    json.dump(inventory, out, indent=2)

print("Inventory audit completed successfully:")
print(f"Mapped SQLAlchemy Models: {inventory['total_mapped_models']}")
print(f"FastAPI Endpoints: {inventory['total_fastapi_endpoints']}")
print(f"Permissions (Enum): {inventory['total_permissions_enum']}")
print(f"Roles (Seed): {inventory['total_seed_roles']}")
print(f"Teams (Seed): {inventory['total_seed_teams']}")
print(f"Admin Canonical Workspaces: {inventory['total_canonical_workspaces']}")
print(f"TeamDashboard.jsx Teams: {inventory['team_dashboard_jsx_teams_count']}")
print(f"Frontend Routes (App.jsx): {inventory['frontend_routes_count']}")
print(f"Alembic Migrations: {inventory['total_alembic_migrations']}")
