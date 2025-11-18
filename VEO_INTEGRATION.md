# Google Veo Video Generation Integration

## Overview

The Brand Deconstruction Station has been prepared for Google Veo video generation, which will enable AI-powered video creation from text prompts. The implementation includes full support for Veo models with intelligent fallback to enhanced mock generation.

## Current Status

### ✅ Implemented Features

1. **Veo Model Detection** - Automatically detects available Veo models (2.0, 3.0, 3.1)
2. **API Integration** - Complete REST API implementation for Veo video generation
3. **Fallback System** - Graceful degradation to enhanced mock videos when Veo is unavailable
4. **Error Handling** - Comprehensive error detection and logging
5. **Model Support** - Ready for all Veo model versions:
   - `veo-2.0-generate-001` - Stable, 5-8 seconds, silent
   - `veo-3.0-generate-001` - Stable, 8 seconds, with audio
   - `veo-3.0-fast-generate-001` - Fast generation variant
   - `veo-3.1-generate-preview` - Latest preview, 4-8 seconds, with audio
   - `veo-3.1-fast-generate-preview` - Speed-optimized preview

### ⚠️ Current Limitations

1. **API Key Status** - Current API key flagged as "leaked" by Google
2. **Access Requirements** - Veo may require allowlist access (currently in preview)
3. **Polling Not Implemented** - Long-running operation polling pending implementation

## API Requirements

### Authentication

Veo requires a valid Google API key with video generation permissions:

```bash
# Set in environment or .env file
export GOOGLE_API_KEY=your-api-key-here

# Or use Gemini key
export GEMINI_API_KEY=your-api-key-here
```

### Obtaining Valid Access

1. **Get New API Key**:
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create new API key
   - Ensure key has video generation permissions

2. **Request Veo Access**:
   - Veo is currently in limited preview
   - May require joining waitlist or allowlist
   - Check [Google AI announcements](https://ai.google.dev/gemini-api/docs/video) for availability

3. **Update Configuration**:
   ```bash
   # Update /Users/cpconnor/Desktop/keys.env
   GOOGLE_API_KEY=your-new-api-key
   ```

## Technical Implementation

### Video Generation Flow

1. **Request Initiation** (`media_generator.py:_generate_real_video`):
   - Checks for API key availability
   - Lists available Veo models
   - Prepares video generation request

2. **API Call**:
   ```python
   # REST API endpoint
   url = "https://generativelanguage.googleapis.com/v1beta/models/veo-3.1-generate-preview:predictLongRunning"

   # Parameters
   {
       "instances": [{"prompt": "video description"}],
       "parameters": {
           "duration": 8,          # 4, 6, or 8 seconds
           "aspectRatio": "16:9",  # or "9:16"
           "resolution": "720p"    # or "1080p"
       }
   }
   ```

3. **Response Handling**:
   - Success (200): Returns operation ID for polling
   - Permission Denied (403): Falls back to mock generation
   - Not Found (404): Model unavailable, uses mock

### Fallback System

When Veo is unavailable, the system automatically:
1. Logs the specific reason for unavailability
2. Falls back to enhanced mock video generation
3. Creates placeholder MP4 files with metadata
4. Maintains consistent API response format

## Testing

### Test Script

Run the Veo test script to check availability:

```bash
python test_veo.py
```

Expected output when Veo becomes available:
```
✅ google.generativeai imported successfully
✅ API key found
Found video models: ['models/veo-3.1-generate-preview', ...]
✅ Video generation started! Operation: operations/...
```

### Web Interface Testing

1. Start the application:
   ```bash
   python app.py
   ```

2. Navigate to http://localhost:3000

3. Analyze a website and generate videos

4. Check logs for Veo attempt:
   ```
   Found Veo models: [...]
   Attempting Veo video generation with model: veo-3.1-generate-preview
   ```

## Future Enhancements

### Pending Implementation

1. **Operation Polling**:
   ```python
   # Poll for video completion
   while not operation.done:
       time.sleep(10)
       operation = client.operations.get(operation)
   ```

2. **Video Download**:
   ```python
   # Download completed video
   video = operation.response.generated_videos[0]
   client.files.download(file=video.video)
   ```

3. **Advanced Features**:
   - Reference image support
   - Video extension capabilities
   - Custom aspect ratios and resolutions
   - Audio generation control

### When Veo Becomes Available

Once you have a valid API key with Veo access:

1. Update the API key in `/Users/cpconnor/Desktop/keys.env`
2. Restart the application
3. Videos will automatically use Veo instead of mock generation
4. Generated videos will be saved to `/static/generated/`

## Resources

- [Veo API Documentation](https://ai.google.dev/gemini-api/docs/video)
- [Google AI Studio](https://makersuite.google.com/)
- [API Pricing](https://ai.google.dev/gemini-api/docs/pricing#veo-3.1)
- [Model Comparison](https://ai.google.dev/gemini-api/docs/models/gemini)

## Support

For issues or questions:
1. Check logs in the application console
2. Run `test_veo.py` for diagnostics
3. Verify API key permissions
4. Monitor Google AI announcements for Veo availability updates