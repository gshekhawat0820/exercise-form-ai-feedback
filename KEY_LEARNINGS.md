# Key Learnings from Implementation

---

## Discovery 1: The Frame Extraction Bug 

### What Happened

About halfway through testing, I hit this error:

```
Error 422: Frame extraction failed: Failed to read frame at index 303
Video reports 304 frames via CAP_PROP_FRAME_COUNT
```

The weird part was that my code looked correct - extracting frames at 0%, 25%, 50%, 75%, and 100%. First four frames worked fine, but the last one always failed.

### Investigation

Testing each position individually:
- 0% (frame 0): Works
- 25% (frame 76): Works
- 50% (frame 152): Works
- 75% (frame 228): Works
- 100% (frame 303): **Fails every time**

Initially thought it was an off-by-one error in my math. Checked the calculation multiple times - it was correct. `int(1.0 * (304 - 1)) = 303` which should be valid since frames are 0-indexed.

### Root Cause

After some research and testing with different videos, turns out this is a known issue with video codecs:

1. `CAP_PROP_FRAME_COUNT` isn't always accurate - it's an approximation
2. Many codecs don't reliably support seeking to the very last frame
3. Variable frame rate videos make this worse
4. Different container formats handle this differently

Basically, never trust that you can read frame N-1 even if the video reports N frames.

### Solution

Two-part fix:

**Part 1: Cap at 98% instead of 100%**
```python
positions = [i / (num_frames - 1) for i in range(num_frames)]
positions = [min(pos, 0.98) for pos in positions]  # Don't go past 98%
```

**Part 2: Add fallback**
```python
if not ret and idx > 0:
    # If we can't read the frame, try the previous one
    cap.set(cv2.CAP_PROP_POS_FRAMES, idx - 1)
    ret, frame = cap.read()
```

This makes the extraction much more robust. Tested with multiple video formats and it handles codec quirks gracefully.

### Takeaway

Real-world video processing is messier than the docs suggest. Always test with actual video files, not just synthetic test data. Also, graceful degradation is worth the extra lines of code - getting 4 frames is better than failing completely.

---

## Discovery 2: Retry Logic for External APIs

### Decision Point

When implementing the OpenAI API integration, had to decide whether to add retry logic or keep it simple.

Decided to add it upfront using the `tenacity` library:

```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def call_openai_vision_api(frames_base64: List[str]) -> str:
    # API call here
```

### Why This Mattered

During testing, hit rate limits a few times. Without retry logic, these would have been failed requests. With exponential backoff, they automatically retried after waiting and succeeded.

Retry schedule: immediate, then 2s, then 4s, then 8s (capped at 10s).

Also helps with transient network issues and temporary service degradation.

### Takeaway

For any external API call, retry logic is very important, especially in
production software.

---

## Discovery 3: Resource Cleanup with Finally Blocks

### The Problem

Video uploads get saved to temporary files for processing. These need to be cleaned up even if something goes wrong during processing.

### Initial Approach vs Final

Could have done this:

```python
temp_file = tempfile.NamedTemporaryFile(delete=False)
process_video(temp_file.name)
os.unlink(temp_file.name)
```

But if `process_video()` raises an exception, the temp file never gets deleted. Over time, this leads to disk space leaks.

### Better Approach

```python
temp_file_path = None
try:
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file_path = temp_file.name
        # processing...
finally:
    if temp_file_path and os.path.exists(temp_file_path):
        try:
            os.unlink(temp_file_path)
        except Exception as e:
            logger.warning(f"Cleanup failed: {e}")
```

The `finally` block ensures cleanup happens regardless of exceptions. Nested try-catch ensures cleanup errors don't crash the request.

### Takeaway

Resource cleanup needs to be bulletproof. Always use `finally` blocks, and don't let cleanup failures propagate.

---

## Discovery 4: Error Message Quality

### Observation

Noticed that helpful error messages made debugging much faster. Instead of:

```python
raise HTTPException(422, detail="Invalid input")
```

Writing specific messages:

```python
raise HTTPException(
    status_code=422,
    detail=f"Unsupported video format. Allowed: .mp4, .mov, .avi"
)
```

Made a big difference when testing. When something failed, I immediately knew what was wrong without having to dig through code.

### Takeaway

Good error messages benefit everyone - myself during development, reviewers during evaluation, and users in production.

---

## Discovery 5: HTTP Status Code Mapping

### Pattern

Different exception types should map to different HTTP status codes:

- `openai.RateLimitError` → 429 (client should back off)
- `openai.APIError` → 503 (service issue, retry later)
- Validation errors → 422 (fix the request)
- File too large → 413 (reduce size)
- Unexpected errors → 500 (our bug)

This helps clients implement proper retry logic and makes debugging easier.

### Takeaway

Status codes aren't just conventions - they communicate intent.

---

## Discovery 6: Developer Experience Tools

### What I Added

Created a few helper scripts beyond the core requirements:

1. `scripts/extract_frames.py` - Extract frames from a video for testing images
2. `scripts/test_request.py` - CLI tool to test the API
3. `test_with_frames.py` - Quick test with extracted frames

Also wrote a comprehensive README and added `.env.example`.

### Why

Makes it much easier to test and demo the API. Also shows I'm thinking about the next person who uses this code.

### Takeaway

Documentation and tooling are part of code quality. They don't take that long and make
everyone's lives easier in the long term.

---

## On Using AI-Assisted Development

### My Approach

Full transparency: I used Claude Code to help build this project. But I want to be clear about how I used it - this wasn't "vibe coding" where I just accepted everything the agent suggested.

### What This Looked Like in Practice

**Initial setup and structure:** Used the agent to scaffold the project structure and generate boilerplate. This saved probably 30-45 minutes of setup time.

**Code generation:** Had the agent write initial implementations of services and API routes based on the spec. But I read through everything it generated and understood what it was doing.

**Active review process:**
- Read every file the agent created
- Tested the code myself with actual video files
- Caught several issues the agent didn't anticipate

### Specific Examples Where I Had to Step In

**The frame extraction bug:** The agent's initial implementation tried to read frames at exactly 100% position. This looked correct in theory, but when I tested with a real video file, it failed. I had to debug this myself, research the codec limitations, and implement the 98% cap solution. The agent didn't know about this edge case.

**Type hint issues:** The agent initially used `np.ndarray` for type hints, which caused linter errors. I had to recognize the issue and direct it to use `NDArray[np.uint8]` from `numpy.typing` instead.

**Dual input challenge:** The FastAPI dual-input pattern (accepting both File and JSON) didn't work as the agent initially implemented it. I spent time debugging why the JSON body wasn't being parsed, then directed the agent toward using the Request object approach.

**Testing validation:** When I ran the test scripts, several things didn't work as expected. I had to iterate on the solutions and verify that fixes actually addressed the root causes.

### Why I'm Being Transparent About This

AI-assisted development is becoming the norm, and trying to hide it seems dishonest. What matters isn't whether you use AI tools - it's whether you:

1. Understand the code that gets generated
2. Can debug when things go wrong
3. Make thoughtful architectural decisions
4. Test thoroughly and catch edge cases
5. Take ownership of the final result

The agent was a productivity tool, not a replacement for my thinking.

### What This Approach Enabled

Using AI assistance let me focus on the interesting problems:
- Figuring out the frame extraction edge case
- Designing a clean architecture
- Implementing robust error handling
- Writing good documentation

Instead of spending time on:
- Boilerplate setup
- Looking up exact Python syntax
- Remembering OpenCV function names

### Takeaway

AI coding assistants are powerful productivity tools when used thoughtfully. But "used thoughtfully" means reading the code, testing thoroughly, and being able to debug and modify when needed. The agent can write code, but only you can ensure it's correct and handles real-world edge cases.

---

## Prioritization Notes

### What I Focused On

Given time constraints, prioritized:

1. Complete working implementation (all features)
2. Clean architecture and code structure
3. Error handling and edge cases
4. Type hints and documentation
5. Some tests (infrastructure + critical paths)
6. Utility scripts and README

### What I Deprioritized

Didn't implement:
- Full test coverage (got to ~40-50%, not 80%)
- Observability/metrics (added logging but not full observability)
- Rate limiting on the API (would add in production)

### Reasoning

For a take-home assessment, better to have a complete, well-structured implementation with decent test coverage than a partial implementation with perfect tests. The goal is to demonstrate ability to ship quality code, not achieve perfection in every dimension.

Also made sure to acknowledge these trade-offs in comments (e.g., CORS configuration comment about production).

---

## General Takeaways

Things that worked well:

1. **Using AI assistance thoughtfully** - Let the agent handle boilerplate while I focused on architecture and edge cases
2. **Testing with real data early** - Found the frame extraction bug because I used an actual video file, not just trusting generated code
3. **Reading and validating AI-generated code** - Caught type hint issues, dual-input problems, and frame extraction bugs
4. **Adding production patterns upfront** - Retry logic, proper logging, resource cleanup
5. **Documenting decisions** - Comments explaining the 98% cap, why delete=False, etc.
6. **Utility scripts** - Made testing much easier

Things I'd do differently:

1. **Write tests before accepting AI-generated code** - Would have caught the frame extraction issue immediately instead of during manual testing
2. **Be more skeptical of AI suggestions initially** - The dual-input approach and type hints needed manual debugging that could have been avoided with more upfront validation
3. **Budget more time for test coverage** - 40-50% is okay but would aim for 60-70% minimum, especially when using AI to generate code

---

## Final Thoughts

Using AI assistance was helpful for productivity, but the real learning came from testing, debugging, and fixing the issues that emerged. The agent can scaffold code quickly, but it doesn't replace the need to think critically about edge cases, test thoroughly, and own the final implementation.

Overall happy with the result. The code looks clean, handles edge cases, and actually works. I tested with multiple inputs: video too short, video too long, mixed file types, etc. There's room for improvement (more tests, better observability) but it follows all the requirements outlined in the project spec.
