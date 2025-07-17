#!/usr/bin/env python
"""
Database backup and migration management script for OneSport
Usage: python manage_db.py [command] [options]
"""

import os
import sys
import subprocess
import datetime
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional

import django
from django.conf import settings
from django.core.management import call_command
from django.db import connection

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.prod')
django.setup()


class DatabaseBackupManager:
    """Manages database backups and migrations"""
    
    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
    def create_backup(self, backup_name: Optional[str] = None) -> str:
        """Create a database backup"""
        if not backup_name:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"onesport_backup_{timestamp}"
        
        backup_path = self.backup_dir / f"{backup_name}.sql"
        
        # Get database settings
        db_settings = settings.DATABASES['default']
        
        # Create PostgreSQL backup
        if db_settings['ENGINE'] == 'django.db.backends.postgresql':
            cmd = [
                'pg_dump',
                '-h', db_settings.get('HOST', 'localhost'),
                '-p', str(db_settings.get('PORT', 5432)),
                '-U', db_settings['USER'],
                '-d', db_settings['NAME'],
                '-f', str(backup_path),
                '--verbose',
                '--clean',
                '--no-password'
            ]
            
            env = os.environ.copy()
            env['PGPASSWORD'] = db_settings['PASSWORD']
            
            try:
                subprocess.run(cmd, check=True, env=env)
                print(f"✅ Backup created successfully: {backup_path}")
                
                # Create metadata file
                metadata = {
                    'backup_name': backup_name,
                    'created_at': datetime.datetime.now().isoformat(),
                    'database': db_settings['NAME'],
                    'size': backup_path.stat().st_size
                }
                
                metadata_path = self.backup_dir / f"{backup_name}_metadata.json"
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                return str(backup_path)
                
            except subprocess.CalledProcessError as e:
                print(f"❌ Backup failed: {e}")
                return None
        
        else:
            # For other databases, use Django's dumpdata
            with open(backup_path, 'w') as f:
                call_command('dumpdata', stdout=f, indent=2)
            
            print(f"✅ Django backup created: {backup_path}")
            return str(backup_path)
    
    def restore_backup(self, backup_path: str) -> bool:
        """Restore from backup"""
        backup_file = Path(backup_path)
        
        if not backup_file.exists():
            print(f"❌ Backup file not found: {backup_path}")
            return False
        
        db_settings = settings.DATABASES['default']
        
        if db_settings['ENGINE'] == 'django.db.backends.postgresql':
            cmd = [
                'psql',
                '-h', db_settings.get('HOST', 'localhost'),
                '-p', str(db_settings.get('PORT', 5432)),
                '-U', db_settings['USER'],
                '-d', db_settings['NAME'],
                '-f', str(backup_file),
                '--quiet'
            ]
            
            env = os.environ.copy()
            env['PGPASSWORD'] = db_settings['PASSWORD']
            
            try:
                subprocess.run(cmd, check=True, env=env)
                print(f"✅ Backup restored successfully from: {backup_path}")
                return True
                
            except subprocess.CalledProcessError as e:
                print(f"❌ Restore failed: {e}")
                return False
        
        else:
            # For other databases, use Django's loaddata
            try:
                call_command('loaddata', backup_path)
                print(f"✅ Django backup restored from: {backup_path}")
                return True
            except Exception as e:
                print(f"❌ Restore failed: {e}")
                return False
    
    def list_backups(self) -> List[Dict]:
        """List all available backups"""
        backups = []
        
        for backup_file in self.backup_dir.glob("*.sql"):
            metadata_file = backup_file.with_suffix('').with_suffix('_metadata.json')
            
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                backups.append(metadata)
            else:
                # Create basic metadata
                stat = backup_file.stat()
                backups.append({
                    'backup_name': backup_file.stem,
                    'created_at': datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'size': stat.st_size
                })
        
        return sorted(backups, key=lambda x: x['created_at'], reverse=True)
    
    def cleanup_old_backups(self, keep_count: int = 10) -> None:
        """Remove old backups, keeping only the latest ones"""
        backups = self.list_backups()
        
        if len(backups) <= keep_count:
            print(f"Only {len(backups)} backups found, nothing to cleanup")
            return
        
        to_remove = backups[keep_count:]
        
        for backup in to_remove:
            backup_name = backup['backup_name']
            backup_file = self.backup_dir / f"{backup_name}.sql"
            metadata_file = self.backup_dir / f"{backup_name}_metadata.json"
            
            if backup_file.exists():
                backup_file.unlink()
            if metadata_file.exists():
                metadata_file.unlink()
            
            print(f"🗑️  Removed old backup: {backup_name}")
        
        print(f"✅ Cleanup complete, kept {keep_count} latest backups")


def main():
    """Main CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description='OneSport Database Management')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Backup commands
    backup_parser = subparsers.add_parser('backup', help='Backup management')
    backup_subparsers = backup_parser.add_subparsers(dest='backup_action')
    
    # Create backup
    create_parser = backup_subparsers.add_parser('create', help='Create backup')
    create_parser.add_argument('--name', help='Backup name')
    
    # List backups
    backup_subparsers.add_parser('list', help='List backups')
    
    # Restore backup
    restore_parser = backup_subparsers.add_parser('restore', help='Restore backup')
    restore_parser.add_argument('path', help='Backup file path')
    
    # Cleanup backups
    cleanup_parser = backup_subparsers.add_parser('cleanup', help='Cleanup old backups')
    cleanup_parser.add_argument('--keep', type=int, default=10, help='Number of backups to keep')
    
    args = parser.parse_args()
    
    if args.command == 'backup':
        backup_manager = DatabaseBackupManager()
        
        if args.backup_action == 'create':
            backup_manager.create_backup(args.name)
        
        elif args.backup_action == 'list':
            backups = backup_manager.list_backups()
            if backups:
                print("Available backups:")
                for backup in backups:
                    size_mb = backup['size'] / (1024 * 1024)
                    print(f"  {backup['backup_name']} - {backup['created_at']} ({size_mb:.2f}MB)")
            else:
                print("No backups found")
        
        elif args.backup_action == 'restore':
            backup_manager.restore_backup(args.path)
        
        elif args.backup_action == 'cleanup':
            backup_manager.cleanup_old_backups(args.keep)
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
