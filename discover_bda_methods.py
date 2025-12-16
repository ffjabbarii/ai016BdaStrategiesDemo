#!/usr/bin/env python3
"""
Discover what methods are actually available on the BDA client
"""

import boto3
import json

def discover_bda_methods():
    """Discover available methods on BDA clients"""
    
    print("🔍 DISCOVERING BDA CLIENT METHODS")
    print("=" * 50)
    
    try:
        # Create BDA client
        bda_client = boto3.client('bedrock-data-automation', region_name='us-east-1')
        print(f"✅ BDA client created: {type(bda_client).__name__}")
        
        # Get all methods
        methods = [method for method in dir(bda_client) if not method.startswith('_')]
        
        print(f"\n📋 Available methods ({len(methods)}):")
        
        # Categorize methods
        profile_methods = []
        project_methods = []
        other_methods = []
        
        for method in sorted(methods):
            if 'profile' in method.lower():
                profile_methods.append(method)
            elif 'project' in method.lower():
                project_methods.append(method)
            else:
                other_methods.append(method)
        
        # Show profile methods (most important)
        if profile_methods:
            print(f"\n🎯 PROFILE METHODS:")
            for method in profile_methods:
                print(f"   ✅ {method}")
        else:
            print(f"\n❌ No profile methods found")
        
        # Show project methods
        if project_methods:
            print(f"\n📋 PROJECT METHODS:")
            for method in project_methods:
                print(f"   📋 {method}")
        
        # Show other important methods
        print(f"\n🔧 OTHER METHODS:")
        important_keywords = ['list', 'create', 'get', 'describe']
        for method in other_methods:
            if any(keyword in method.lower() for keyword in important_keywords):
                print(f"   🔧 {method}")
        
        # Test some methods to see what they do
        print(f"\n🧪 TESTING KEY METHODS:")
        
        # Try list methods
        list_methods = [m for m in methods if m.startswith('list_')]
        for method_name in list_methods:
            try:
                method = getattr(bda_client, method_name)
                print(f"\n🧪 Testing {method_name}...")
                
                # Try calling with no parameters
                result = method()
                print(f"   ✅ Success: {type(result)} with keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
                
                # Show some results if available
                if isinstance(result, dict):
                    for key, value in result.items():
                        if isinstance(value, list) and len(value) > 0:
                            print(f"   📋 {key}: {len(value)} items")
                            if len(value) > 0:
                                print(f"      Sample: {value[0] if len(str(value[0])) < 100 else str(value[0])[:100]+'...'}")
                        else:
                            print(f"   📋 {key}: {value}")
                
            except Exception as e:
                error_type = type(e).__name__
                error_msg = str(e)
                print(f"   ❌ {method_name} failed: {error_type} - {error_msg[:100]}")
        
        return bda_client
        
    except Exception as e:
        print(f"❌ Failed to create BDA client: {str(e)}")
        return None

def discover_bda_runtime_methods():
    """Discover BDA runtime client methods"""
    
    print(f"\n🔍 DISCOVERING BDA RUNTIME CLIENT METHODS")
    print("=" * 50)
    
    try:
        # Create BDA runtime client
        runtime_client = boto3.client('bedrock-data-automation-runtime', region_name='us-east-1')
        print(f"✅ BDA runtime client created: {type(runtime_client).__name__}")
        
        # Get all methods
        methods = [method for method in dir(runtime_client) if not method.startswith('_')]
        
        print(f"\n📋 Available runtime methods ({len(methods)}):")
        
        # Show important methods
        important_methods = []
        for method in sorted(methods):
            if any(keyword in method.lower() for keyword in ['invoke', 'automation', 'async', 'get', 'list']):
                important_methods.append(method)
                print(f"   🚀 {method}")
        
        # Test the invoke method
        if 'invoke_data_automation_async' in methods:
            print(f"\n🧪 TESTING invoke_data_automation_async parameters...")
            
            try:
                # Get operation model
                operation_model = runtime_client._service_model.operation_model('InvokeDataAutomationAsync')
                input_shape = operation_model.input_shape
                
                print(f"   📋 Required parameters:")
                for param_name in input_shape.required_members:
                    print(f"      ✅ {param_name} (required)")
                
                print(f"   📋 Optional parameters:")
                for param_name, param_shape in input_shape.members.items():
                    if param_name not in input_shape.required_members:
                        print(f"      ⚪ {param_name} (optional)")
                
            except Exception as e:
                print(f"   ❌ Failed to get operation model: {str(e)}")
        
        return runtime_client
        
    except Exception as e:
        print(f"❌ Failed to create BDA runtime client: {str(e)}")
        return None

def test_profile_creation(bda_client):
    """Test if we can create profiles"""
    
    if not bda_client:
        return
    
    print(f"\n🧪 TESTING PROFILE CREATION")
    print("=" * 40)
    
    # Look for create profile methods
    methods = [method for method in dir(bda_client) if 'create' in method.lower() and 'profile' in method.lower()]
    
    if methods:
        for method_name in methods:
            print(f"🧪 Found profile creation method: {method_name}")
            
            try:
                method = getattr(bda_client, method_name)
                
                # Try to get help/documentation
                operation_model = bda_client._service_model.operation_model(
                    ''.join(word.capitalize() for word in method_name.split('_'))
                )
                
                print(f"   📋 Parameters for {method_name}:")
                for param_name, param_shape in operation_model.input_shape.members.items():
                    required = param_name in operation_model.input_shape.required_members
                    print(f"      {'✅' if required else '⚪'} {param_name} ({param_shape.type_name})")
                
            except Exception as e:
                print(f"   ❌ Error getting method info: {str(e)}")
    else:
        print("❌ No profile creation methods found")

def main():
    print("🚀 BDA METHOD DISCOVERY")
    print("=" * 30)
    
    # Discover BDA client methods
    bda_client = discover_bda_methods()
    
    # Discover BDA runtime methods
    runtime_client = discover_bda_runtime_methods()
    
    # Test profile creation
    test_profile_creation(bda_client)
    
    print(f"\n" + "=" * 50)
    print(f"🎯 SUMMARY:")
    print(f"Now we know exactly what BDA methods are available!")
    print(f"Look for profile-related methods above to create/manage profiles.")

if __name__ == "__main__":
    main()