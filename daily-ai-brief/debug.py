
with open("debug_result.txt", "w") as f:
    try:
        import feedparser
        f.write("feedparser imported successfully\n")
    except ImportError:
        f.write("feedparser import FAILED\n")
    f.write("Script executed.\n")
