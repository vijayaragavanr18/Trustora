"""
Quick Test Script - Test blockchain integration without ML packages
"""
import sys
import asyncio

def test_imports():
    """Test if all core packages can be imported"""
    print("=" * 60)
    print("TESTING CORE PACKAGE IMPORTS")
    print("=" * 60 + "\n")
    
    tests = [
        ("web3", "Web3 (Blockchain)"),
        ("eth_account", "Ethereum Account"),
        ("fastapi", "FastAPI"),
        ("pydantic", "Pydantic"),
        ("cryptography", "Cryptography"),
        ("dotenv", "Python Dotenv"),
        ("numpy", "NumPy"),
        ("PIL", "Pillow"),
    ]
    
    passed = 0
    failed = 0
    
    for module, name in tests:
        try:
            __import__(module)
            print(f"✅ {name:30} - OK")
            passed += 1
        except ImportError as e:
            print(f"❌ {name:30} - FAILED: {e}")
            failed += 1
    
    print(f"\n{'=' * 60}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'=' * 60}\n")
    
    return failed == 0


def test_blockchain_module():
    """Test blockchain integration module"""
    print("=" * 60)
    print("TESTING BLOCKCHAIN MODULE")
    print("=" * 60 + "\n")
    
    try:
        from blockchain.blockchain_integration import BlockchainIntegration
        print("✅ BlockchainIntegration class imported")
        
        # Create instance
        bc = BlockchainIntegration()
        print("✅ BlockchainIntegration instance created")
        
        # Test file hashing
        test_data = b"Hello, Blockchain!"
        file_hash = bc.create_file_hash(test_data)
        print(f"✅ File hash created: {file_hash[:32]}...")
        
        # Test metadata sealing
        metadata = {"test": "data", "timestamp": "2026-02-17"}
        sealed = bc.seal_metadata(metadata)
        print(f"✅ Metadata sealed: {len(sealed)} bytes")
        
        print(f"\n{'=' * 60}")
        print("Blockchain module: ALL TESTS PASSED ✅")
        print(f"{'=' * 60}\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print(f"{'=' * 60}\n")
        return False


async def test_trusted_capture():
    """Test trusted capture module"""
    print("=" * 60)
    print("TESTING TRUSTED CAPTURE MODULE")
    print("=" * 60 + "\n")
    
    try:
        from blockchain.trusted_capture import TrustedCapture
        print("✅ TrustedCapture class imported")
        
        tc = TrustedCapture()
        print("✅ TrustedCapture instance created")
        
        # Note: Full blockchain functions need configuration
        print("⚠️  Full blockchain features need .env configuration")
        print("   Configure BLOCKCHAIN_PROVIDER_URL to enable all features")
        
        print(f"\n{'=' * 60}")
        print("Trusted Capture module: BASIC TESTS PASSED ✅")
        print(f"{'=' * 60}\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print(f"{'=' * 60}\n")
        import traceback
        traceback.print_exc()
        return False


def test_config():
    """Test configuration module"""
    print("=" * 60)
    print("TESTING CONFIGURATION")
    print("=" * 60 + "\n")
    
    try:
        from config import ModelConfig, BlockchainConfig, APIConfig
        print("✅ Configuration classes imported")
        
        # Test model config
        model_cfg = ModelConfig()
        print(f"✅ Model config loaded - Image size: {model_cfg.IMAGE_SIZE}")
        
        # Test blockchain config
        bc_cfg = BlockchainConfig()
        print(f"✅ Blockchain config loaded - Network: {bc_cfg.NETWORK}")
        
        # Test API config
        api_cfg = APIConfig()
        print(f"✅ API config loaded - Port: {api_cfg.PORT}")
        
        print(f"\n{'=' * 60}")
        print("Configuration: ALL TESTS PASSED ✅")
        print(f"{'=' * 60}\n")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print(f"{'=' * 60}\n")
        return False


def test_ml_packages():
    """Test if ML packages are installed (optional)"""
    print("=" * 60)
    print("TESTING ML/AI PACKAGES (Optional)")
    print("=" * 60 + "\n")
    
    ml_packages = [
        ("tensorflow", "TensorFlow"),
        ("torch", "PyTorch"),
        ("cv2", "OpenCV"),
        ("librosa", "Librosa"),
        ("sklearn", "Scikit-learn"),
    ]
    
    installed = 0
    for module, name in ml_packages:
        try:
            __import__(module)
            print(f"✅ {name:20} - Installed")
            installed += 1
        except ImportError:
            print(f"⚠️  {name:20} - Not installed (optional)")
    
    print(f"\n{'=' * 60}")
    if installed == len(ml_packages):
        print("ML Packages: ALL INSTALLED ✅")
    elif installed > 0:
        print(f"ML Packages: {installed}/{len(ml_packages)} installed")
        print("Install remaining with: pip install -r requirements-ml.txt")
    else:
        print("ML Packages: NONE INSTALLED")
        print("For detection features, install: pip install -r requirements-ml.txt")
    print(f"{'=' * 60}\n")


async def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("DEEPFAKE DETECTION SYSTEM - DIAGNOSTIC TEST")
    print("=" * 60 + "\n")
    
    results = []
    
    # Test imports
    results.append(("Core Imports", test_imports()))
    
    # Test config
    results.append(("Configuration", test_config()))
    
    # Test blockchain
    results.append(("Blockchain Module", test_blockchain_module()))
    
    # Test trusted capture
    results.append(("Trusted Capture", await test_trusted_capture()))
    
    # Test ML packages (optional)
    test_ml_packages()
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60 + "\n")
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:30} {status}")
    
    all_passed = all(result[1] for result in results)
    
    print(f"\n{'=' * 60}")
    if all_passed:
        print("🎉 ALL CORE TESTS PASSED!")
        print("\nYour system is ready for:")
        print("  - Blockchain integration")
        print("  - Trusted capture creation")
        print("  - API server (without ML endpoints)")
        print("\nTo enable deepfake detection:")
        print("  pip install -r requirements-ml.txt")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("\nPlease check the errors above and:")
        print("  1. Make sure virtual environment is activated")
        print("  2. Run: pip install -r requirements-minimal.txt")
        print("  3. Reload VS Code window")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
