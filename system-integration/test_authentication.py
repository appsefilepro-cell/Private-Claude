#!/usr/bin/env python3
"""
Microsoft 365 Authentication Test
Verify your setup before running full migration

For research, development, and educational purposes only.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
import requests
from msal import PublicClientApplication


class AuthenticationTester:
    """Test Microsoft 365 authentication and permissions"""

    def __init__(self):
        """Initialize tester"""
        load_dotenv()

        self.client_id = os.getenv('MICROSOFT365_CLIENT_ID')
        self.tenant_id = os.getenv('MICROSOFT365_TENANT_ID', 'common')
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"

        self.scopes = [
            "Files.Read.All",
            "Sites.Read.All",
            "User.Read"
        ]

        self.access_token = None
        self.headers = None
        self.test_results = []

    def print_header(self):
        """Print test header"""
        print("\n" + "="*70)
        print("  MICROSOFT 365 AUTHENTICATION TEST")
        print("="*70)
        print(f"  Client ID: {self.client_id[:20]}..." if self.client_id else "  Client ID: NOT SET")
        print(f"  Tenant ID: {self.tenant_id}")
        print(f"  Timestamp: {datetime.now().isoformat()}")
        print("="*70 + "\n")

    def test_environment(self) -> bool:
        """Test environment configuration"""
        print("📋 Testing Environment Configuration...")

        if not self.client_id:
            print("  ❌ MICROSOFT365_CLIENT_ID not set")
            print("     Set with: export MICROSOFT365_CLIENT_ID='your-client-id'")
            self.test_results.append({
                'test': 'Environment Variables',
                'status': 'FAILED',
                'error': 'Client ID not configured'
            })
            return False

        print(f"  ✅ MICROSOFT365_CLIENT_ID: {self.client_id[:20]}...")
        print(f"  ✅ MICROSOFT365_TENANT_ID: {self.tenant_id}")

        self.test_results.append({
            'test': 'Environment Variables',
            'status': 'PASSED'
        })
        return True

    def test_authentication(self) -> bool:
        """Test authentication flow"""
        print("\n🔐 Testing Authentication...")

        try:
            app = PublicClientApplication(
                self.client_id,
                authority=self.authority
            )

            # Try silent authentication first
            accounts = app.get_accounts()
            if accounts:
                print("  ℹ️  Found cached account, attempting silent authentication...")
                result = app.acquire_token_silent(self.scopes, account=accounts[0])
                if result and "access_token" in result:
                    self.access_token = result["access_token"]
                    print("  ✅ Silent authentication successful")
                else:
                    # Fall back to device code flow
                    result = None

            if not self.access_token:
                print("  ℹ️  Starting device code authentication flow...")
                flow = app.initiate_device_flow(scopes=self.scopes)

                if "user_code" not in flow:
                    print("  ❌ Failed to create device flow")
                    self.test_results.append({
                        'test': 'Authentication',
                        'status': 'FAILED',
                        'error': 'Device flow creation failed'
                    })
                    return False

                print("\n" + "-"*70)
                print(flow["message"])
                print("-"*70 + "\n")

                result = app.acquire_token_by_device_flow(flow)

                if "access_token" not in result:
                    print(f"  ❌ Authentication failed: {result.get('error_description')}")
                    self.test_results.append({
                        'test': 'Authentication',
                        'status': 'FAILED',
                        'error': result.get('error_description')
                    })
                    return False

                self.access_token = result["access_token"]

            self.headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            print("  ✅ Authentication successful")
            print(f"  ℹ️  Token expires in ~60 minutes")

            self.test_results.append({
                'test': 'Authentication',
                'status': 'PASSED'
            })
            return True

        except Exception as e:
            print(f"  ❌ Authentication error: {e}")
            self.test_results.append({
                'test': 'Authentication',
                'status': 'FAILED',
                'error': str(e)
            })
            return False

    def test_user_profile(self) -> bool:
        """Test User.Read permission"""
        print("\n👤 Testing User Profile Access...")

        try:
            url = "https://graph.microsoft.com/v1.0/me"
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                user_data = response.json()
                print(f"  ✅ User profile accessible")
                print(f"     Display Name: {user_data.get('displayName', 'N/A')}")
                print(f"     Email: {user_data.get('mail') or user_data.get('userPrincipalName', 'N/A')}")

                self.test_results.append({
                    'test': 'User Profile',
                    'status': 'PASSED',
                    'data': {
                        'displayName': user_data.get('displayName'),
                        'email': user_data.get('mail') or user_data.get('userPrincipalName')
                    }
                })
                return True
            else:
                print(f"  ❌ Failed to access user profile: {response.status_code}")
                print(f"     {response.text}")
                self.test_results.append({
                    'test': 'User Profile',
                    'status': 'FAILED',
                    'error': f"HTTP {response.status_code}"
                })
                return False

        except Exception as e:
            print(f"  ❌ Error: {e}")
            self.test_results.append({
                'test': 'User Profile',
                'status': 'FAILED',
                'error': str(e)
            })
            return False

    def test_onedrive_access(self) -> bool:
        """Test Files.Read.All permission (OneDrive)"""
        print("\n📁 Testing OneDrive Access...")

        try:
            url = "https://graph.microsoft.com/v1.0/me/drive"
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                drive_data = response.json()
                print(f"  ✅ OneDrive accessible")
                print(f"     Drive Type: {drive_data.get('driveType', 'N/A')}")

                # Get quota info
                quota = drive_data.get('quota', {})
                if quota:
                    total_gb = quota.get('total', 0) / (1024**3)
                    used_gb = quota.get('used', 0) / (1024**3)
                    remaining_gb = quota.get('remaining', 0) / (1024**3)

                    print(f"     Total Space: {total_gb:.2f} GB")
                    print(f"     Used Space: {used_gb:.2f} GB")
                    print(f"     Remaining: {remaining_gb:.2f} GB")

                # Count files
                files_url = "https://graph.microsoft.com/v1.0/me/drive/root/children?$top=100"
                files_response = requests.get(files_url, headers=self.headers)

                if files_response.status_code == 200:
                    files_data = files_response.json()
                    file_count = len([item for item in files_data.get('value', []) if 'file' in item])
                    folder_count = len([item for item in files_data.get('value', []) if 'folder' in item])

                    print(f"     Root Files: {file_count}")
                    print(f"     Root Folders: {folder_count}")

                    self.test_results.append({
                        'test': 'OneDrive Access',
                        'status': 'PASSED',
                        'data': {
                            'total_gb': total_gb,
                            'used_gb': used_gb,
                            'root_files': file_count,
                            'root_folders': folder_count
                        }
                    })
                else:
                    print(f"     ⚠️  Could not list files: {files_response.status_code}")
                    self.test_results.append({
                        'test': 'OneDrive Access',
                        'status': 'PARTIAL',
                        'warning': 'Drive accessible but could not list files'
                    })

                return True

            elif response.status_code == 403:
                print(f"  ❌ Permission denied (403)")
                print(f"     You may need to grant 'Files.Read.All' permission")
                self.test_results.append({
                    'test': 'OneDrive Access',
                    'status': 'FAILED',
                    'error': 'Permission denied - check API permissions'
                })
                return False
            else:
                print(f"  ❌ Failed to access OneDrive: {response.status_code}")
                print(f"     {response.text}")
                self.test_results.append({
                    'test': 'OneDrive Access',
                    'status': 'FAILED',
                    'error': f"HTTP {response.status_code}"
                })
                return False

        except Exception as e:
            print(f"  ❌ Error: {e}")
            self.test_results.append({
                'test': 'OneDrive Access',
                'status': 'FAILED',
                'error': str(e)
            })
            return False

    def test_sharepoint_access(self) -> bool:
        """Test Sites.Read.All permission (SharePoint)"""
        print("\n🏢 Testing SharePoint Access...")

        try:
            url = "https://graph.microsoft.com/v1.0/sites?search=*&$top=10"
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                sites_data = response.json()
                sites = sites_data.get('value', [])

                print(f"  ✅ SharePoint accessible")
                print(f"     Found {len(sites)} site(s)")

                for i, site in enumerate(sites[:5], 1):  # Show first 5
                    print(f"     {i}. {site.get('displayName', 'N/A')} ({site.get('webUrl', 'N/A')})")

                if len(sites) > 5:
                    print(f"     ... and {len(sites) - 5} more")

                self.test_results.append({
                    'test': 'SharePoint Access',
                    'status': 'PASSED',
                    'data': {
                        'site_count': len(sites),
                        'sites': [{'name': s.get('displayName'), 'url': s.get('webUrl')} for s in sites[:5]]
                    }
                })
                return True

            elif response.status_code == 403:
                print(f"  ❌ Permission denied (403)")
                print(f"     You may need to grant 'Sites.Read.All' permission")
                self.test_results.append({
                    'test': 'SharePoint Access',
                    'status': 'FAILED',
                    'error': 'Permission denied - check API permissions'
                })
                return False
            else:
                print(f"  ❌ Failed to access SharePoint: {response.status_code}")
                print(f"     {response.text}")
                self.test_results.append({
                    'test': 'SharePoint Access',
                    'status': 'FAILED',
                    'error': f"HTTP {response.status_code}"
                })
                return False

        except Exception as e:
            print(f"  ❌ Error: {e}")
            self.test_results.append({
                'test': 'SharePoint Access',
                'status': 'FAILED',
                'error': str(e)
            })
            return False

    def test_download_capability(self) -> bool:
        """Test ability to download a file"""
        print("\n⬇️  Testing Download Capability...")

        try:
            # Get first file from OneDrive
            url = "https://graph.microsoft.com/v1.0/me/drive/root/children?$top=1"
            response = requests.get(url, headers=self.headers)

            if response.status_code != 200:
                print("  ⚠️  Could not list files to test download")
                self.test_results.append({
                    'test': 'Download Capability',
                    'status': 'SKIPPED',
                    'reason': 'No files available to test'
                })
                return True

            files = response.json().get('value', [])
            files = [f for f in files if 'file' in f]

            if not files:
                print("  ℹ️  No files found in root folder - skipping download test")
                self.test_results.append({
                    'test': 'Download Capability',
                    'status': 'SKIPPED',
                    'reason': 'No files in root folder'
                })
                return True

            test_file = files[0]
            download_url = test_file.get('@microsoft.graph.downloadUrl')

            if not download_url:
                print("  ⚠️  File has no download URL")
                self.test_results.append({
                    'test': 'Download Capability',
                    'status': 'FAILED',
                    'error': 'No download URL available'
                })
                return False

            # Test download (just get headers, don't download full file)
            head_response = requests.head(download_url)

            if head_response.status_code == 200:
                print(f"  ✅ Download capability verified")
                print(f"     Test file: {test_file.get('name')}")
                print(f"     Size: {test_file.get('size', 0)} bytes")

                self.test_results.append({
                    'test': 'Download Capability',
                    'status': 'PASSED',
                    'data': {
                        'test_file': test_file.get('name'),
                        'size': test_file.get('size')
                    }
                })
                return True
            else:
                print(f"  ❌ Download test failed: {head_response.status_code}")
                self.test_results.append({
                    'test': 'Download Capability',
                    'status': 'FAILED',
                    'error': f"HTTP {head_response.status_code}"
                })
                return False

        except Exception as e:
            print(f"  ❌ Error: {e}")
            self.test_results.append({
                'test': 'Download Capability',
                'status': 'FAILED',
                'error': str(e)
            })
            return False

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*70)
        print("  TEST SUMMARY")
        print("="*70)

        passed = sum(1 for r in self.test_results if r['status'] == 'PASSED')
        failed = sum(1 for r in self.test_results if r['status'] == 'FAILED')
        skipped = sum(1 for r in self.test_results if r['status'] == 'SKIPPED')
        total = len(self.test_results)

        print(f"\n  Total Tests: {total}")
        print(f"  ✅ Passed: {passed}")
        print(f"  ❌ Failed: {failed}")
        print(f"  ⏭️  Skipped: {skipped}")

        if failed == 0:
            print("\n  🎉 All tests passed! You're ready to migrate.")
        else:
            print("\n  ⚠️  Some tests failed. Review errors above before migrating.")

        print("\n" + "="*70)

        # Save results
        results_file = Path('authentication_test_results.json')
        with open(results_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'summary': {
                    'total': total,
                    'passed': passed,
                    'failed': failed,
                    'skipped': skipped
                },
                'results': self.test_results
            }, f, indent=2)

        print(f"\n  📄 Results saved to: {results_file.absolute()}\n")

    def run_all_tests(self):
        """Run all tests"""
        self.print_header()

        # Test environment
        if not self.test_environment():
            print("\n❌ Environment test failed. Please configure your client ID.")
            print("   See MIGRATION_SETUP_GUIDE.md for setup instructions.\n")
            return False

        # Test authentication
        if not self.test_authentication():
            print("\n❌ Authentication failed. Cannot proceed with other tests.\n")
            return False

        # Run permission tests
        self.test_user_profile()
        self.test_onedrive_access()
        self.test_sharepoint_access()
        self.test_download_capability()

        # Print summary
        self.print_summary()

        return True


def main():
    """Main execution"""
    tester = AuthenticationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
