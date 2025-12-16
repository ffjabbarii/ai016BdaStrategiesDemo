#!/usr/bin/env python3
"""
Update blueprint processor with the actual profile ARN from AWS Console
"""

def update_with_profile_arn(profile_arn):
    """Update blueprint processor with the real profile ARN"""
    
    print(f"🔧 UPDATING BLUEPRINT PROCESSOR")
    print(f"Profile ARN: {profile_arn}")
    print("=" * 50)
    
    # Read the current blueprint processor
    with open("python/BlueprintAPI/src/blueprint_processor.py", 'r') as f:
        content = f.read()
    
    # Find the profile ARN resolution function and replace it with the working ARN
    old_function = """    async def _get_or_create_data_automation_profile(self, project_arn: str) -> str:
        \"\"\"Get or create the correct data automation profile ARN for BDA processing\"\"\"
        try:
            print("🔍 Resolving data automation profile ARN...")
            
            # Extract account ID and region from project ARN
            # Format: arn:aws:bedrock:us-east-1:624706593351:data-automation-project/0483b44689d1
            arn_parts = project_arn.split(':')
            if len(arn_parts) >= 5:
                region = arn_parts[3]
                account_id = arn_parts[4]
            else:
                raise Exception(f"Invalid project ARN format: {project_arn}")
            
            # Try different profile ARN patterns based on AWS documentation
            profile_candidates = [
                # Standard default profile pattern
                f"arn:aws:bedrock:{region}:{account_id}:data-automation-profile/default",
                # AWS managed profile pattern  
                f"arn:aws:bedrock:{region}:aws:data-automation-profile/default",
                # Account-specific profile pattern
                f"arn:aws:bedrock:{region}:{account_id}:data-automation-profile/standard",
                # Project-based profile pattern
                f"arn:aws:bedrock:{region}:{account_id}:data-automation-profile/{project_arn.split('/')[-1]}"
            ]
            
            print(f"🔍 Testing {len(profile_candidates)} profile ARN candidates...")
            
            # Test each candidate by attempting to list profiles or validate
            for i, candidate_arn in enumerate(profile_candidates, 1):
                try:
                    print(f"🧪 Testing candidate {i}: {candidate_arn}")
                    
                    # Try to validate this profile ARN by attempting a dry-run or list operation
                    # Since there's no direct "validate profile" API, we'll try the actual call
                    # with a minimal test configuration
                    
                    # For now, return the most likely candidate based on AWS patterns
                    if "default" in candidate_arn and account_id in candidate_arn:
                        print(f"✅ Selected profile ARN: {candidate_arn}")
                        return candidate_arn
                        
                except ClientError as e:
                    error_code = e.response.get('Error', {}).get('Code', '')
                    print(f"❌ Candidate {i} failed: {error_code}")
                    continue
            
            # If no candidates work, try to create a default profile
            print("🔄 No existing profiles found, attempting to create default profile...")
            return await self._create_default_data_automation_profile(region, account_id)
            
        except Exception as e:
            print(f"❌ Failed to resolve profile ARN: {str(e)}")
            # Fallback to the most standard pattern
            fallback_arn = f"arn:aws:bedrock:{self.region_name}:aws:data-automation-profile/default"
            print(f"🔄 Using fallback profile ARN: {fallback_arn}")
            return fallback_arn"""
    
    new_function = f"""    async def _get_or_create_data_automation_profile(self, project_arn: str) -> str:
        \"\"\"Get the correct data automation profile ARN for BDA processing\"\"\"
        # Use the actual profile ARN from AWS Console
        profile_arn = "{profile_arn}"
        print(f"📋 Using configured profile ARN: {profile_arn}")
        return profile_arn"""
    
    # Replace the function
    if old_function in content:
        content = content.replace(old_function, new_function)
        print("✅ Updated _get_or_create_data_automation_profile function")
    else:
        print("⚠️ Could not find exact function to replace")
        print("   You'll need to manually update the profile ARN")
    
    # Write the updated content
    with open("python/BlueprintAPI/src/blueprint_processor.py", 'w') as f:
        f.write(content)
    
    print(f"\n✅ Blueprint processor updated with profile ARN: {profile_arn}")
    print(f"🧪 Now test with: python debug_bda_upload.py")

def main():
    print("🎯 PROFILE ARN UPDATE TOOL")
    print("=" * 40)
    print("After you create a profile in AWS Console, run:")
    print("python update_with_profile_arn.py")
    print("Then manually edit this script to include your actual profile ARN")
    print()
    print("Example usage:")
    print('update_with_profile_arn("arn:aws:bedrock:us-east-1:624706593351:data-automation-profile/your-profile-name")')
    
    # For now, show what needs to be done
    print(f"\n🔧 STEPS:")
    print(f"1. Go to AWS Console → Bedrock → Data Automation")
    print(f"2. Create a profile (note the ARN)")
    print(f"3. Edit this script with the real ARN")
    print(f"4. Run the script to update blueprint_processor.py")

if __name__ == "__main__":
    main()