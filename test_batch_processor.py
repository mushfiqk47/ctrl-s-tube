"""Quick test script for batch processor utilities."""

from app_utils.batch_processor import extract_urls, validate_url_list, deduplicate_urls

# Test URL extraction
test_text = """
Here are some YouTube videos I want to download:

1. https://www.youtube.com/watch?v=dQw4w9WgXcQ
2. Check out this one: https://youtu.be/jNQXAC9IVRw
3. https://www.youtube.com/shorts/ABC123xyz
4. Some random text here
5. https://www.youtube.com/watch?v=VIDEO_ID&list=PLAYLIST

Also this isn't a youtube link: https://www.google.com
"""

print("Testing URL extraction...")
print("=" * 60)
print("Input text:")
print(test_text)
print("=" * 60)

urls = extract_urls(test_text)
print(f"\nExtracted {len(urls)} URLs:")
for i, url in enumerate(urls, 1):
    print(f"  {i}. {url}")

print("\n" + "=" * 60)
print("Testing URL validation...")
valid, invalid = validate_url_list(urls)
print(f"Valid URLs ({len(valid)}):")
for url in valid:
    print(f"  ✓ {url}")

print(f"\nInvalid URLs ({len(invalid)}):")
for url in invalid:
    print(f"  ✗ {url}")

print("\n" + "=" * 60)
print("Testing deduplication...")
duplicate_urls = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "https://youtu.be/dQw4w9WgXcQ",  # Same video, different format
    "https://www.youtube.com/watch?v=jNQXAC9IVRw",
]
unique = deduplicate_urls(duplicate_urls)
print(f"Input: {len(duplicate_urls)} URLs")
print(f"Output: {len(unique)} unique URLs")
for url in unique:
    print(f"  {url}")

print("\n✓ All tests completed!")
