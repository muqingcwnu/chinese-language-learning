import os
import sys
import django
from pathlib import Path

# Add the project root directory to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from utils.deepseek_api import DeepSeekAPI
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_grammar_explanation():
    """Test the DeepSeek API grammar explanation functionality."""
    try:
        api = DeepSeekAPI()
        
        # Test English explanation
        logger.info("Testing English explanation...")
        result_en = api.get_grammar_explanation(
            title="是...的 (shì...de) construction",
            pattern="是 + Subject + Verb + 的",
            example="他是昨天来的。(Tā shì zuótiān lái de.) - He came yesterday.",
            language="en"
        )
        logger.info("English Result:")
        for key, value in result_en.items():
            logger.info(f"{key}: {value}\n")

        # Test Chinese explanation
        logger.info("\nTesting Chinese explanation...")
        result_zh = api.get_grammar_explanation(
            title="是...的 (shì...de) 结构",
            pattern="是 + 主语 + 动词 + 的",
            example="他是昨天来的。(Tā shì zuótiān lái de.)",
            language="zh"
        )
        logger.info("Chinese Result:")
        for key, value in result_zh.items():
            logger.info(f"{key}: {value}\n")

    except Exception as e:
        logger.error(f"Error in test_grammar_explanation: {str(e)}")

if __name__ == "__main__":
    test_grammar_explanation() 