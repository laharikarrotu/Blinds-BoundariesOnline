#!/usr/bin/env python3
"""
Check Azure App Service configuration and retrieve Computer Vision credentials.
This script provides proof of what's configured (or not configured).
"""

import subprocess
import json
import sys

def run_az_command(cmd):
    """Run Azure CLI command and return JSON result."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            print(f"Error: {result.stderr}", file=sys.stderr)
            return None
    except Exception as e:
        print(f"Exception: {e}", file=sys.stderr)
        return None

def check_app_service_settings():
    """Check App Service application settings."""
    print("=" * 70)
    print("CHECKING AZURE APP SERVICE CONFIGURATION")
    print("=" * 70)
    print()
    
    cmd = "az webapp config appsettings list --name blinds-boundaries-api --resource-group blinds-boundaries-rg --output json"
    settings = run_az_command(cmd)
    
    if not settings:
        print("❌ Could not retrieve App Service settings")
        print("   This might mean:")
        print("   - Azure CLI not authenticated")
        print("   - App Service name/resource group incorrect")
        print("   - Network/permission issues")
        return False
    
    print("✅ Retrieved App Service settings")
    print()
    
    # Check for Azure Vision settings
    settings_dict = {s['name']: s.get('value', '') for s in settings}
    
    vision_key = settings_dict.get('AZURE_VISION_KEY', None)
    vision_endpoint = settings_dict.get('AZURE_VISION_ENDPOINT', None)
    
    print("AZURE COMPUTER VISION CONFIGURATION:")
    print("-" * 70)
    
    if vision_key:
        print(f"✅ AZURE_VISION_KEY: SET")
        print(f"   Length: {len(vision_key)} characters")
        print(f"   Preview: {vision_key[:10]}...{vision_key[-4:]}")
    else:
        print(f"❌ AZURE_VISION_KEY: NOT SET")
        print(f"   ⚠️ This is why Azure CV is not responding!")
    
    print()
    
    if vision_endpoint:
        print(f"✅ AZURE_VISION_ENDPOINT: SET")
        print(f"   Endpoint: {vision_endpoint}")
    else:
        print(f"❌ AZURE_VISION_ENDPOINT: NOT SET")
        print(f"   ⚠️ This is why Azure CV is not responding!")
    
    print()
    print("-" * 70)
    print()
    
    # Show all settings (for reference)
    print("ALL APP SERVICE SETTINGS:")
    print("-" * 70)
    for key in sorted(settings_dict.keys()):
        value = settings_dict[key]
        if value:
            # Mask sensitive values
            if 'KEY' in key or 'SECRET' in key or 'PASSWORD' in key:
                display = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "***"
            else:
                display = value[:50] + "..." if len(value) > 50 else value
            print(f"  {key}: {display}")
        else:
            print(f"  {key}: (empty)")
    
    print()
    print("=" * 70)
    
    # Summary
    if vision_key and vision_endpoint:
        print("✅ RESULT: Azure CV credentials ARE configured!")
        print("   If it's still not working, check:")
        print("   - App Service was restarted after adding settings")
        print("   - Credentials are correct")
        print("   - Computer Vision resource is active")
        return True
    else:
        print("❌ RESULT: Azure CV credentials are NOT configured!")
        print("   This is PROOF that credentials are missing.")
        print()
        print("   Missing:")
        if not vision_key:
            print("   - AZURE_VISION_KEY")
        if not vision_endpoint:
            print("   - AZURE_VISION_ENDPOINT")
        return False

def find_computer_vision_resources():
    """Find Computer Vision resources in subscription."""
    print()
    print("=" * 70)
    print("SEARCHING FOR COMPUTER VISION RESOURCES")
    print("=" * 70)
    print()
    
    cmd = "az cognitiveservices account list --query \"[?kind=='ComputerVision'].{Name:name, ResourceGroup:resourceGroup, Location:location}\" --output json"
    resources = run_az_command(cmd)
    
    if not resources:
        print("❌ Could not retrieve Computer Vision resources")
        return None
    
    if len(resources) == 0:
        print("⚠️ No Computer Vision resources found in subscription")
        return None
    
    print(f"✅ Found {len(resources)} Computer Vision resource(s):")
    print()
    for i, resource in enumerate(resources, 1):
        print(f"{i}. {resource['Name']}")
        print(f"   Resource Group: {resource['ResourceGroup']}")
        print(f"   Location: {resource['Location']}")
        print()
    
    return resources

def get_computer_vision_credentials(resource_name, resource_group):
    """Get Computer Vision API key and endpoint."""
    print()
    print("=" * 70)
    print(f"RETRIEVING CREDENTIALS FOR: {resource_name}")
    print("=" * 70)
    print()
    
    # Get endpoint
    cmd = f"az cognitiveservices account show --name {resource_name} --resource-group {resource_group} --query properties.endpoint --output tsv"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    endpoint = result.stdout.strip() if result.returncode == 0 else None
    
    # Get key
    cmd = f"az cognitiveservices account keys list --name {resource_name} --resource-group {resource_group} --query key1 --output tsv"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
    key = result.stdout.strip() if result.returncode == 0 else None
    
    if endpoint and key:
        print("✅ CREDENTIALS RETRIEVED:")
        print()
        print(f"AZURE_VISION_ENDPOINT={endpoint}")
        print(f"AZURE_VISION_KEY={key[:4]}...{key[-4:]} (masked for security)")
        print()
        print("=" * 70)
        print("TO FIX: Add these to App Service Configuration:")
        print("=" * 70)
        print()
        print("Run these commands:")
        print()
        print(f'az webapp config appsettings set \\')
        print(f'  --name blinds-boundaries-api \\')
        print(f'  --resource-group blinds-boundaries-rg \\')
        print(f'  --settings AZURE_VISION_KEY="{key}" AZURE_VISION_ENDPOINT="{endpoint}"')
        print()
        return key, endpoint
    else:
        print("❌ Could not retrieve credentials")
        if not endpoint:
            print("   - Endpoint retrieval failed")
        if not key:
            print("   - Key retrieval failed")
        return None, None

def main():
    """Main function."""
    print()
    print("🔍 AZURE COMPUTER VISION CONFIGURATION CHECKER")
    print()
    
    # Check App Service settings
    is_configured = check_app_service_settings()
    
    # If not configured, try to find and retrieve credentials
    if not is_configured:
        print()
        print("🔧 ATTEMPTING TO RETRIEVE CREDENTIALS...")
        print()
        
        resources = find_computer_vision_resources()
        
        if resources:
            # Try first resource (usually the one we want)
            resource = resources[0]
            key, endpoint = get_computer_vision_credentials(
                resource['Name'],
                resource['ResourceGroup']
            )
            
            if key and endpoint:
                print()
                print("✅ SUCCESS! Credentials retrieved.")
                print("   Copy the command above to configure App Service.")
        else:
            print()
            print("⚠️ Could not find Computer Vision resources")
            print("   You may need to create one or check the resource name.")
    
    print()
    print("=" * 70)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()

