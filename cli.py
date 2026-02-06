#!/usr/bin/env python3
"""
Mini-Cloud Storage CLI Client

A command-line interface for interacting with the Mini-Cloud Storage API.
"""

import argparse
import requests
import sys
import os
from pathlib import Path
from getpass import getpass


class MiniCloudClient:
    def __init__(self, base_url, username, password):
        self.base_url = base_url.rstrip('/')
        self.auth = (username, password)
    
    def list_files(self, path=''):
        """List files in the specified path"""
        response = requests.get(
            f"{self.base_url}/api/files",
            params={'path': path},
            auth=self.auth
        )
        response.raise_for_status()
        return response.json()
    
    def upload_file(self, file_path, remote_path=''):
        """Upload a file"""
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'rb') as f:
            files = {'file': (file_path.name, f)}
            response = requests.post(
                f"{self.base_url}/api/files/upload",
                params={'path': remote_path},
                files=files,
                auth=self.auth
            )
        response.raise_for_status()
        return response.json()
    
    def download_file(self, remote_path, local_path=None):
        """Download a file"""
        response = requests.get(
            f"{self.base_url}/api/files/download",
            params={'path': remote_path},
            auth=self.auth,
            stream=True
        )
        response.raise_for_status()
        
        if local_path is None:
            local_path = Path(remote_path).name
        
        # Check if file exists and warn user
        if Path(local_path).exists():
            import sys
            response_input = input(f"File '{local_path}' already exists. Overwrite? (y/N): ")
            if response_input.lower() not in ['y', 'yes']:
                print("Download cancelled.")
                return None
        
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return local_path
    
    def delete_file(self, path):
        """Delete a file or directory"""
        response = requests.delete(
            f"{self.base_url}/api/files",
            params={'path': path},
            auth=self.auth
        )
        response.raise_for_status()
        return response.json()
    
    def create_directory(self, path):
        """Create a new directory"""
        response = requests.post(
            f"{self.base_url}/api/directories",
            params={'path': path},
            auth=self.auth
        )
        response.raise_for_status()
        return response.json()
    
    def storage_info(self):
        """Get storage information"""
        response = requests.get(
            f"{self.base_url}/api/storage/info",
            auth=self.auth
        )
        response.raise_for_status()
        return response.json()


def format_size(bytes_size):
    """Format bytes to human-readable size"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"


def main():
    parser = argparse.ArgumentParser(
        description='Mini-Cloud Storage CLI Client',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--url', default='http://localhost:8000',
                       help='Base URL of the Mini-Cloud Storage server')
    parser.add_argument('--username', default='admin',
                       help='Username for authentication')
    parser.add_argument('--password',
                       help='Password for authentication (will prompt if not provided)')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # List command
    list_parser = subparsers.add_parser('list', aliases=['ls'], help='List files')
    list_parser.add_argument('path', nargs='?', default='', help='Path to list')
    
    # Upload command
    upload_parser = subparsers.add_parser('upload', aliases=['up'], help='Upload a file')
    upload_parser.add_argument('file', help='Local file to upload')
    upload_parser.add_argument('--path', default='', help='Remote path')
    
    # Download command
    download_parser = subparsers.add_parser('download', aliases=['dl'], help='Download a file')
    download_parser.add_argument('file', help='Remote file to download')
    download_parser.add_argument('--output', '-o', help='Local output path')
    
    # Delete command
    delete_parser = subparsers.add_parser('delete', aliases=['rm'], help='Delete a file or directory')
    delete_parser.add_argument('path', help='Path to delete')
    
    # Create directory command
    mkdir_parser = subparsers.add_parser('mkdir', help='Create a directory')
    mkdir_parser.add_argument('path', help='Directory path to create')
    
    # Info command
    info_parser = subparsers.add_parser('info', help='Show storage information')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Get password if not provided
    password = args.password
    if not password:
        password = getpass('Password: ')
    
    # Create client
    client = MiniCloudClient(args.url, args.username, password)
    
    try:
        if args.command in ['list', 'ls']:
            result = client.list_files(args.path)
            print(f"Files in '{args.path or '/'}':")
            print("-" * 80)
            for file in result['files']:
                icon = '📁' if file['is_directory'] else '📄'
                size = format_size(file['size']) if not file['is_directory'] else ''
                print(f"{icon} {file['name']:40s} {size:>15s}")
            print("-" * 80)
            print(f"Total: {len(result['files'])} items")
        
        elif args.command in ['upload', 'up']:
            print(f"Uploading {args.file}...")
            result = client.upload_file(args.file, args.path)
            print(f"✅ Uploaded successfully: {result['file']['filename']}")
            print(f"   Size: {format_size(result['file']['size'])}")
            print(f"   Path: {result['file']['path']}")
        
        elif args.command in ['download', 'dl']:
            print(f"Downloading {args.file}...")
            local_path = client.download_file(args.file, args.output)
            if local_path:
                print(f"✅ Downloaded to: {local_path}")
        
        elif args.command in ['delete', 'rm']:
            result = client.delete_file(args.path)
            print(f"✅ {result['message']}")
        
        elif args.command == 'mkdir':
            result = client.create_directory(args.path)
            print(f"✅ {result['message']}")
            print(f"   Path: {result['directory']['path']}")
        
        elif args.command == 'info':
            result = client.storage_info()
            print("Storage Information:")
            print("-" * 40)
            print(f"Total Size: {format_size(result['total_size'])}")
            print(f"File Count: {result['file_count']}")
            print(f"Storage Path: {result['storage_path']}")
        
        return 0
    
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        if e.response.status_code == 401:
            print("   Invalid credentials", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
