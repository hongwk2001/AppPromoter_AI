import unittest
from unittest.mock import patch, MagicMock
import os
import json
import tempfile
import reddit_replier

class TestRedditReplier(unittest.TestCase):
    
    def setUp(self):
        # Sample configuration details
        self.sample_post = {
            'id': 'test1234',
            'title': 'How do I fix my early extension?',
            'content': 'I am early extending on my downswing. Any drills to keep spine angle?',
            'author': 'golf_enthusiast',
            'subreddit': 'golfswing',
            'url': 'https://reddit.com/r/golfswing/comments/test1234',
            'matched_keywords': ['early extension']
        }
        self.sample_kb = "# Golf KB\n- Keep spine angle.\n- Use SwingPro AI at https://jigsawpuzzlehelper.com/golfswingai/."
        self.temp_dir = tempfile.TemporaryDirectory()
        self.few_shots_path = os.path.join(self.temp_dir.name, "few_shots.jsonl")
        self.skipped_posts_path = os.path.join(self.temp_dir.name, "skipped_posts.jsonl")

    def tearDown(self):
        self.temp_dir.cleanup()

    @patch('requests.get')
    def test_fetch_reddit_posts(self, mock_get):
        # Mock XML response for RSS
        mock_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom">
          <entry>
            <title>Struggling with a nasty slice</title>
            <content type="html">&lt;p&gt;My swing plane is way too steep.&lt;/p></content>
            <link href="https://reddit.com/r/golfswing/comments/post1/" />
            <author>
              <name>/u/player1</name>
            </author>
            <id>post1</id>
          </entry>
          <entry>
            <title>Random post</title>
            <content type="html">Not matching any keyword.</content>
            <link href="https://reddit.com/r/golf/comments/post2/" />
            <author>
              <name>/u/player2</name>
            </author>
            <id>post2</id>
          </entry>
        </feed>
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = mock_xml.encode('utf-8')
        mock_get.return_value = mock_response
        
        posts = reddit_replier.fetch_reddit_posts(
            subreddits=['golfswing'],
            keywords=['slice', 'early extension'],
            limit=2
        )
        
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0]['id'], 'post1')
        self.assertEqual(posts[0]['title'], 'Struggling with a nasty slice')
        self.assertIn('slice', posts[0]['matched_keywords'])

    @patch('reddit_replier.genai.Client')
    def test_generate_reply_gemini(self, mock_client_class):
        # Mock Gemini client response
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.text = "This is a drafted reply based on the KB. Try using SwingPro AI."
        mock_client.models.generate_content.return_value = mock_response
        
        few_shots = [{'post_title': 'Old Title', 'post_content': 'Old content', 'approved_reply': 'Old reply'}]
        reply = reddit_replier.generate_reply_gemini(self.sample_post, self.sample_kb, few_shots)
        
        expected_reply = "This is a drafted reply based on the KB. Try using SwingPro AI.\n\n*(Drafted with the assistance of Gemini AI)*"
        self.assertEqual(reply, expected_reply)
        mock_client.models.generate_content.assert_called_once()

    @patch('requests.post')
    def test_generate_reply_ollama(self, mock_post):
        # Mock Ollama HTTP response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Local Ollama response text"}
        mock_post.return_value = mock_response
        
        reply = reddit_replier.generate_reply_ollama(self.sample_post, self.sample_kb, [], model="gemma2")
        expected_reply = "Local Ollama response text\n\n*(Drafted with the assistance of gemma2 via Ollama)*"
        self.assertEqual(reply, expected_reply)
        mock_post.assert_called_once()

    def test_save_and_load_few_shots(self):
        # Verify empty load
        self.assertEqual(reddit_replier.load_few_shots(self.few_shots_path), [])
        
        # Save one
        reddit_replier.save_to_few_shots(self.few_shots_path, self.sample_post, "Test approved reply")
        
        # Load and verify
        loaded = reddit_replier.load_few_shots(self.few_shots_path)
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0]['post_title'], self.sample_post['title'])
        self.assertEqual(loaded[0]['approved_reply'], "Test approved reply")

    def test_save_to_skipped(self):
        reddit_replier.save_to_skipped(self.skipped_posts_path, self.sample_post)
        
        self.assertTrue(os.path.exists(self.skipped_posts_path))
        with open(self.skipped_posts_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 1)
            loaded_post = json.loads(lines[0])
            self.assertEqual(loaded_post['id'], self.sample_post['id'])

    def test_load_processed_post_keys(self):
        reddit_replier.save_to_few_shots(self.few_shots_path, self.sample_post, "Reply")
        
        other_post = self.sample_post.copy()
        other_post['title'] = "Skipped post title"
        other_post['url'] = "https://reddit.com/r/golf/comments/skipped1"
        reddit_replier.save_to_skipped(self.skipped_posts_path, other_post)
        
        keys = reddit_replier.load_processed_post_keys(self.few_shots_path, self.skipped_posts_path)
        
        self.assertIn(self.sample_post['title'].lower().strip(), keys)
        self.assertIn("skipped post title", keys)
        self.assertIn("https://reddit.com/r/golf/comments/skipped1", keys)

if __name__ == '__main__':
    unittest.main()
