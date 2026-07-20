import { describe, expect, test } from "bun:test";
import { parseTweetId } from "./tweet-to-markdown.js";

describe("parseTweetId", () => {
  test("accepts supported X and Twitter URLs", () => {
    expect.assertions(4);
    expect(parseTweetId("https://x.com/user/status/123")).toBe("123");
    expect(parseTweetId("https://www.x.com/user/status/234")).toBe("234");
    expect(parseTweetId("https://twitter.com/user/statuses/345")).toBe("345");
    expect(parseTweetId("https://mobile.twitter.com/user/status/456")).toBe("456");
  });

  test("accepts a bare tweet ID", () => {
    expect.assertions(1);
    expect(parseTweetId("567")).toBe("567");
  });

  test("rejects lookalike and unrelated hosts", () => {
    expect.assertions(3);
    expect(parseTweetId("https://example.com/user/status/123")).toBeNull();
    expect(parseTweetId("https://x.com.example.com/user/status/234")).toBeNull();
    expect(parseTweetId("https://notx.com/user/status/345")).toBeNull();
  });
});
