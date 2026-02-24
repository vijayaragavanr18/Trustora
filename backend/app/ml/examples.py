"""
Example usage and testing script
"""
import asyncio
from deepfake_detector import get_detector
from blockchain.trusted_capture import get_trusted_capture


async def example_image_analysis():
    """Example: Analyze an image for deepfakes"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Image Deepfake Detection")
    print("="*60 + "\n")
    
    # Get detector
    detector = get_detector()
    
    # Load models
    print("Loading AI/ML models...")
    await detector.load_models()
    print("✅ Models loaded\n")
    
    # Note: Replace with path to your test image
    image_path = "path/to/test_image.jpg"
    
    print(f"Analyzing image: {image_path}")
    
    try:
        # Analyze image
        result = await detector.analyze_image(image_path)
        
        # Display results
        print("\n--- ANALYSIS RESULTS ---")
        print(f"Deepfake Score: {result['score']:.4f}")
        print(f"Confidence: {result['confidence']:.4f}")
        print(f"Risk Level: {result['risk_level']}")
        print(f"Is Deepfake: {'YES' if result['is_deepfake'] else 'NO'}")
        print(f"Artifacts Found: {', '.join(result['artifacts_found']) if result['artifacts_found'] else 'None'}")
        
        print("\nModel Scores:")
        for model, score in result['model_scores'].items():
            print(f"  {model}: {score:.4f}")
        
    except FileNotFoundError:
        print(f"❌ Error: File not found: {image_path}")
        print("Please update the image_path variable with a valid image file")


async def example_video_analysis():
    """Example: Analyze a video for deepfakes"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Video Deepfake Detection")
    print("="*60 + "\n")
    
    detector = get_detector()
    
    # Note: Replace with path to your test video
    video_path = "path/to/test_video.mp4"
    
    print(f"Analyzing video: {video_path}")
    print("(This may take a while...)\n")
    
    try:
        # Analyze video
        result = await detector.analyze_video(video_path)
        
        # Display results
        print("\n--- ANALYSIS RESULTS ---")
        print(f"Deepfake Score: {result['score']:.4f}")
        print(f"Confidence: {result['confidence']:.4f}")
        print(f"Risk Level: {result['risk_level']}")
        print(f"Is Deepfake: {'YES' if result['is_deepfake'] else 'NO'}")
        print(f"Frames Analyzed: {result['frame_count']}")
        
        print("\nFrame Statistics:")
        print(f"  Mean Score: {result['frame_scores']['mean']:.4f}")
        print(f"  Std Dev: {result['frame_scores']['std']:.4f}")
        print(f"  Min Score: {result['frame_scores']['min']:.4f}")
        print(f"  Max Score: {result['frame_scores']['max']:.4f}")
        
        print("\nModel Scores:")
        for model, score in result['model_scores'].items():
            print(f"  {model}: {score:.4f}")
        
    except FileNotFoundError:
        print(f"❌ Error: File not found: {video_path}")
        print("Please update the video_path variable with a valid video file")


async def example_audio_analysis():
    """Example: Analyze audio for voice synthesis"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Audio Voice Synthesis Detection")
    print("="*60 + "\n")
    
    detector = get_detector()
    
    # Note: Replace with path to your test audio
    audio_path = "path/to/test_audio.mp3"
    
    print(f"Analyzing audio: {audio_path}\n")
    
    try:
        # Analyze audio
        result = await detector.analyze_audio(audio_path)
        
        # Display results
        print("\n--- ANALYSIS RESULTS ---")
        print(f"Synthesis Score: {result['score']:.4f}")
        print(f"Confidence: {result['confidence']:.4f}")
        print(f"Is Synthetic: {'YES' if result['is_synthetic'] else 'NO'}")
        
        print("\nDetailed Analysis:")
        print(f"  Spectral Analysis: {result['spectral_analysis']['score']:.4f}")
        print(f"  Synthesis Detection: {result['synthesis_detection']['score']:.4f}")
        print(f"  Compression Artifacts: {result['compression_artifacts']['score']:.4f}")
        
    except FileNotFoundError:
        print(f"❌ Error: File not found: {audio_path}")
        print("Please update the audio_path variable with a valid audio file")


async def example_trusted_capture():
    """Example: Create and verify a trusted capture"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Blockchain Trusted Capture")
    print("="*60 + "\n")
    
    tc = get_trusted_capture()
    
    # Note: Replace with path to your file
    file_path = "path/to/original_media.jpg"
    user_id = "test_user_123"
    
    print(f"Creating trusted capture for: {file_path}\n")
    
    try:
        # Create trusted capture
        result = await tc.create_trusted_capture(
            file_path=file_path,
            user_id=user_id,
            device_info={'device': 'Test Device', 'os': 'Test OS'},
            location={'city': 'Test City', 'country': 'Test Country'}
        )
        
        if result['success']:
            print("✅ Trusted capture created successfully!\n")
            print("--- CAPTURE DETAILS ---")
            print(f"Capture ID: {result['capture_id']}")
            print(f"File Hash: {result['file_hash']}")
            print(f"Blockchain Transaction: {result['blockchain_hash']}")
            print(f"Timestamp: {result['timestamp']}")
            print(f"Verification URL: {result['verification_url']}")
            
            # Verify the capture
            print("\n--- VERIFYING CAPTURE ---")
            verify_result = await tc.verify_trusted_capture(
                file_path=file_path,
                capture_id=result['capture_id']
            )
            
            if verify_result['verified']:
                print("✅ Verification successful!")
                print(f"Blockchain verification: {verify_result['blockchain_verification']}")
            else:
                print("❌ Verification failed")
                print(f"Message: {verify_result.get('message')}")
        else:
            print(f"❌ Error creating trusted capture: {result.get('error')}")
        
    except FileNotFoundError:
        print(f"❌ Error: File not found: {file_path}")
        print("Please update the file_path variable with a valid file")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\nNote: Make sure blockchain is properly configured in .env file")


async def run_all_examples():
    """Run all examples"""
    print("\n" + "="*60)
    print("DEEPFAKE DETECTION & TRUSTED CAPTURE EXAMPLES")
    print("="*60)
    
    # Note: Comment out examples you don't want to run
    
    # await example_image_analysis()
    # await example_video_analysis()
    # await example_audio_analysis()
    # await example_trusted_capture()
    
    print("\n" + "="*60)
    print("EXAMPLES COMPLETE")
    print("="*60 + "\n")
    
    print("To run these examples:")
    print("1. Update the file paths in each example function")
    print("2. Uncomment the examples you want to run in run_all_examples()")
    print("3. Run: python examples.py")
    print()


if __name__ == "__main__":
    # Run examples
    asyncio.run(run_all_examples())
